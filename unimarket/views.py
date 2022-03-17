from datetime import datetime, timezone, timedelta
import json
import logging

from django.db.models.aggregates import Avg
from django.db.models.query_utils import Q
from django.http.response import (
    HttpResponse,
    JsonResponse,
    Http404,
    HttpResponseRedirect,
)
from django.shortcuts import render, redirect
from django.template import loader
from django.utils.dateformat import DateFormat
from django.views.decorators.csrf import csrf_exempt
from django.views.generic.base import TemplateView
from numpy.random.mtrand import randint

from unimarket.models import (
    Item,
    Category,
    Like,
    Satisfaction,
    Report,
    Member,
    Mark,
    ChatRoom,
    ChatInfo,
    StayLog,
)

import fasttext
from konlpy.tag import Okt
from sklearn.model_selection._split import train_test_split

import numpy as np
import pandas as pd


logger = logging.getLogger(__name__)


class ChatRoomSearchView(TemplateView):
    @csrf_exempt
    def get(self, request):
        pass

    def post(self, request):
        memNo = request.session.get("memNo", None)
        # jsonObj = json.loads(request.body)
        # roomSearch = jsonObj.get("roomSearch")
        roomSearch = request.POST["roomSearch"]
        logger.info("room : " + str(roomSearch))
        memList = ""
        otherList = ""
        context = {}
        # 채팅 룸이 존재하는지 검색
        roomCount = ChatRoom.objects.filter(
            Q(buyMemNo=memNo) | Q(sellMemNo=memNo)
        ).count()
        if roomCount > 0:
            dtoChatRoom = ChatRoom.objects.filter(
                Q(Q(buyMemNo=memNo) | Q(sellMemNo=memNo)) & Q(title_contains=roomSearch)
            )
            for i, dto in dtoChatRoom:
                if memNo == dto[i].sellMemNo:  # 현재 접속자가 판매자일경우
                    dtoChatRoom[i].memList = Member.objects.get(memNo=memNo).values(
                        "nickname"
                    )
                    dtoChatRoom[i].otherList = Member.objects.get(
                        memNo=dto[i].buyMemNo
                    ).values("nickname")
                else:  # 현재 접속자가 거래자일 경우
                    dtoChatRoom[i].memList = Member.objects.get(memNo=memNo).values(
                        "nickname"
                    )
                    dtoChatRoom[i].otherList = Member.objects.get(
                        memNo=dto[i].sellMemNo
                    ).values("nickname")
            context["dtoChatList"] = list(
                dtoChatRoom.values(
                    "chatNo", "sellMemNo", "buyMemNo", "itemNo", "title", "itemImg"
                )
            )
            context["Listck"] = "1"
        else:
            context["listck"] = "0"
        return HttpResponse(json.dumps(context), content_type="application/json")


class ChatInfoView(TemplateView):
    def get(self, request):
        template = loader.get_template("uniChatRoomInfo.html")
        # 거래신청 사용자
        memNo = request.session.get("memNo", None)
        chatNo = request.GET.get("chatNo", None)
        if chatNo != None:
            chatItem = Item.objects.get(itemNo=request.GET["itemNo"])
            chatContext = ChatRoom.objects.get(chatNo=chatNo)
            memList = ""
            otherList = ""
            if memNo == chatContext.sellMemNo:  # 현재 접속자가 판매자일경우
                memList = Member.objects.get(memNo=memNo)
                otherList = Member.objects.get(memNo=chatContext.buyMemNo)
            else:  # 현재 접속자가 거래자일 경우
                memList = Member.objects.get(memNo=memNo)
                otherList = Member.objects.get(memNo=chatContext.sellMemNo)
            # 현재 물품에 대한 채팅기록
            count = ChatInfo.objects.filter(chatNo=chatNo).count()
            # 다른 채팅기록
            roomCount = ChatRoom.objects.filter(
                Q(buyMemNo=memNo) | Q(sellMemNo=memNo)
            ).count()
            context = {}
            if count != 0:  # 채팅 내용이 존재할시
                dtoChat = ChatInfo.objects.filter(chatNo=chatNo).order_by("endTime")
                logger.info("dtoCaht : " + str(dtoChat))
                if roomCount != 0:  # 다른 채팅 기록이 있을 경우
                    dtoChatList = ChatRoom.objects.filter(
                        Q(buyMemNo=memNo) | Q(sellMemNo=memNo)
                    ).order_by("-sendTime")
                    context = {
                        "dtoChat": dtoChat,
                        "dtoChatList": dtoChatList,
                        "chatItem": chatItem,
                        "memList": memList,
                        "otherList": otherList,
                        "memNo": memNo,
                        "chatNo": chatNo,
                    }
                else:  # 다른 채팅 기록이 없을 경우
                    context = {
                        "dtoChat": dtoChat,
                        "dtoChatList": None,
                        "chatItem": chatItem,
                        "memList": memList,
                        "otherList": otherList,
                        "memNo": memNo,
                        "chatNo": chatNo,
                    }
            else:  # 채팅 내용이 존재하지않을 시
                if roomCount != 0:  # 다른 채팅 기록이 있을 경우
                    dtoChatList = ChatRoom.objects.filter(
                        Q(buyMemNo=memNo) | Q(sellMemNo=memNo)
                    ).order_by("-sendTime")
                    context = {
                        "dtoChat": None,
                        "dtoChatList": dtoChatList,
                        "chatItem": chatItem,
                        "memList": memList,
                        "otherList": otherList,
                        "memNo": memNo,
                        "chatNo": chatNo,
                    }
                else:  # 다른 채팅 기록이 없을 경우
                    context = {
                        "dtoChat": None,
                        "dtoChatList": None,
                        "chatItem": chatItem,
                        "memList": memList,
                        "otherList": otherList,
                        "memNo": memNo,
                        "chatNo": chatNo,
                    }
            return HttpResponse(template.render(context, request))
        else:  # 프로필에서 채팅으로 접근할 경우
            # 다른 채팅기록
            roomCount = ChatRoom.objects.filter(
                Q(buyMemNo=memNo) | Q(sellMemNo=memNo)
            ).count()
            context = {}
            if roomCount != 0:  # 다른 채팅 기록이 있을 경우
                dtoChatList = ChatRoom.objects.filter(
                    Q(buyMemNo=memNo) | Q(sellMemNo=memNo)
                ).order_by("-sendTime")
                context = {
                    "dtoChatList": dtoChatList,
                    "memNo": memNo,
                    "chatNo": None,
                }
            else:  # 다른 채팅 기록이 없을 경우
                context = {
                    "dtoChatList": None,
                    "memNo": memNo,
                    "chatNo": None,
                }
        return HttpResponse(template.render(context, request))

    def post(self, request):
        # 거래신청 사용자
        memNo = request.session.get("memNo", None)
        # 상품 판매자
        sellMemNo = request.POST["sellMemNo"]
        itemNo = request.POST["itemNo"]
        chatNo = ""
        # 채팅에 아이템 정보 저장
        dtoItem = Item.objects.get(itemNo=itemNo)
        # ChatRoom.objects.all().delete()
        # chatRoom에 저장된 거래가 하나없는지 확인
        chatCount = ChatRoom.objects.all().count()
        if chatCount == 0:  # 하나도 없을 경우
            chatNo = "ch01"
            logger.info("chatNo : " + str(chatNo))
            dtoChatRoom = ChatRoom(
                chatNo=chatNo,
                sellMemNo=sellMemNo,
                buyMemNo=memNo,
                itemNo=itemNo,
                title=dtoItem.title,
                itemImg=dtoItem.itemImg,
            )
            dtoChatRoom.save()
            # 거래신청 알림
            dtoMark = Mark(
                markNo=chatNo,
                memNo=sellMemNo,
                markStat=1,
                markContent=dtoItem.title,
            )
            dtoMark.save()
            return HttpResponseRedirect(
                "uniChatRoomInfo?chatNo=" + chatNo + "&itemNo=" + itemNo
            )
        else:  # 하나라도 있을 경우
            # 해당 상품을 거래 신청한 적이 있는지
            try:  # 거래한적 있음
                chatRoomCk = ChatRoom.objects.get(
                    sellMemNo=sellMemNo, buyMemNo=memNo, itemNo=itemNo
                )
                chatNo = chatRoomCk.chatNo
                return HttpResponseRedirect(
                    "uniChatRoomInfo?chatNo=" + chatNo + "&itemNo=" + itemNo
                )
            except:  # 해당 상품 처음거래
                chatNoCk = ChatRoom.objects.all().order_by("-chatNo")[0]
                Num = int(chatNoCk.chatNo[2:]) + 1
                strNum = ""
                if Num < 10:
                    strNum = "0" + str(Num)
                else:
                    strNum = str(Num)
                chatNo = "ch" + strNum
                dtoChatRoom = ChatRoom(
                    chatNo=chatNo,
                    sellMemNo=sellMemNo,
                    buyMemNo=memNo,
                    itemNo=itemNo,
                    title=dtoItem.title,
                    itemImg=dtoItem.itemImg,
                )
                dtoChatRoom.save()
                # 거래신청 알림
                dtoMark = Mark(
                    markNo=chatNo,
                    memNo=sellMemNo,
                    markStat=1,
                    markContent=dtoItem.title,
                )
                dtoMark.save()
                return HttpResponseRedirect(
                    "uniChatRoomInfo?chatNo=" + chatNo + "&itemNo=" + itemNo
                )


# 거래신청 및 채팅 리스트에서 해당 챗팅을 선택했을 겨웅 접속
# class ChatInfoView(TemplateView):
# def get(self, request):
# template = loader.get_template("uniChatInfo.html")
# # 거래신청 사용자
# memNo = request.session.get("memNo", None)
# chatNo = request.GET["chatNo"]
# chatItem = Item.objects.get(itemNo=request.GET["itemNo"])
# chatContext = ChatRoom.objects.get(chatNo=chatNo)
# memList =""
# otherList = ""
# if memNo == chatContext.sellMemNo : # 현재 접속자가 판매자일경우
# memList = Member.objects.get(memNo=memNo)
# otherList = Member.objects.get(memNo=chatContext.buyMemNo)
# else: # 현재 접속자가 거래자일 경우
# memList = Member.objects.get(memNo=memNo)
# otherList = Member.objects.get(memNo=chatContext.sellMemNo)
# # 현재 물품에 대한 채팅기록
# count = ChatInfo.objects.filter(chatNo=chatNo).count()
# # 다른 채팅기록
# roomCount = ChatRoom.objects.filter(buyMemNo=memNo).count()
# context={}
# if count != 0 : # 채팅 내용이 존재할시
# dtoChat = ChatInfo.objects.filter(chatNo=chatNo).order_by("endTime")
# logger.info("dtoCaht : " +str(dtoChat))
# if roomCount != 0 : # 다른 채팅 기록이 있을 경우
# dtoChatList = ChatRoom.objects.filter(buyMemNo=memNo).order_by("-sendTime")
# for i, dto in enumerate(dtoChatList) :
# logger.info("dtoBuy : " +str(dtoChatList[i]))
# dtoItem = Item.objects.get(itemNo=dtoChatList[i].itemNo)
# # order_by 명령어가 데이터가 하나일 시 오류를 발생하여 사전에 1개이상인지 확인
# if count > 1:
# dtoC = ChatInfo.objects.filter(chatNo=dtoChatList[i].chatNo, itemNo=dtoChatList[i].itemNo).order_by("-endTime")[0]
# else :
# dtoC = ChatInfo.objects.get(chatNo=dtoChatList[i].chatNo, itemNo=dtoChatList[i].itemNo)
# dtoChatList[i].title = dtoItem.title
# dtoChatList[i].itemImg = dtoItem.itemImg
# dtoChatList[i].chatContent = dtoC.chatContent
# context={
# "dtoChat" : dtoChat,
# "dtoChatList" : dtoChatList,
# "chatItem" : chatItem,
# "memList" : memList,
# "otherList" : otherList,
# "memNo" : memNo,
# "chatNo" : chatNo,
# }
# else : # 다른 채팅 기록이 없을 경우
# context={
# "dtoChat" : dtoChat,
# "dtoChatList" : None,
# "chatItem" : chatItem,
# "memList" : memList,
# "otherList" : otherList,
# "memNo" : memNo,
# "chatNo" : chatNo,
# }
# else: # 채팅 내용이 존재하지않을 시
# if roomCount != 0 : # 다른 채팅 기록이 있을 경우
# dtoChatList = ChatRoom.objects.filter(buyMemNo=memNo).order_by("-sendTime")
# for i, dto in enumerate(dtoChatList) :
# logger.info("dtoBuy : " +str(dtoChatList[i]))
# dtoItem = Item.objects.get(itemNo=dtoChatList[i].itemNo)
# dtoChatList[i].title = dtoItem.title
# dtoChatList[i].itemImg = dtoItem.itemImg
# dtoChatList[i].chatContent = None
# context={
# "dtoChat" : None,
# "dtoChatList" : dtoChatList,
# "chatItem" : chatItem,
# "memList" : memList,
# "otherList" : otherList,
# "memNo" : memNo,
# "chatNo" : chatNo,
# }
# else : # 다른 채팅 기록이 없을 경우
# context={
# "dtoChat" : None,
# "dtoChatList" : None,
# "chatItem" : chatItem,
# "memList" : memList,
# "otherList" : otherList,
# "memNo" : memNo,
# "chatNo" : chatNo,
# }
# return HttpResponse(template.render(context, request))
#
# def post(self, request):
# # 거래신청 사용자
# memNo = request.session.get("memNo", None)
# # 상품 판매자
# sellMemNo = request.POST["sellMemNo"]
# itemNo = request.POST["itemNo"]
# chatNo=""
# #ChatRoom.objects.all().delete()
# # chatRoom에 저장된 거래가 하나없는지 확인
# chatCount = ChatRoom.objects.all().count()
# if chatCount == 0: # 하나도 없을 경우
# chatNo="ch01"
# logger.info("chatNo : "+str(chatNo))
# dtoChatRoom = ChatRoom(
# chatNo = chatNo,
# sellMemNo = sellMemNo,
# buyMemNo = memNo,
# itemNo = itemNo
# )
# dtoChatRoom.save()
# else : # 하나라도 있을 경우
# # 해당 상품을 거래 신청한 적이 있는지
# try : # 거래한적 있음
# chatRoomCk = ChatRoom.objects.get(sellMemNo=sellMemNo, buyMemNo=memNo, itemNo=itemNo)
# chatNo = chatRoomCk.chatNo
# return HttpResponseRedirect("uniChatInfo?chatNo="+chatNo+"&itemNo="+itemNo)
# except : # 해당 상품 처음거래
# chatNoCk = ChatRoom.objects.all().order_by("-chatNo")[0]
# Num = int(chatNoCk.chatNo[2:])+1
# strNum=""
# if Num < 10 :
# strNum = "0"+str(Num)
# else:
# strNum = str(Num)
# chatNo = "ch"+strNum
# dtoChatRoom = ChatRoom(
# chatNo = chatNo,
# sellMemNo = sellMemNo,
# buyMemNo = memNo,
# itemNo = itemNo
# )
# dtoChatRoom.save()
# return HttpResponseRedirect("uniChatInfo?chatNo="+chatNo+"&itemNo="+itemNo)

# 채팅내역 업데이트
class UpdateChatInfoView(TemplateView):
    def get(self, request):
        pass

    def post(self, request):
        memNo = request.session.get("memNo", None)
        # ajax에서 json 타입으로 데이터를 보낼 경우 파싱 필요
        jsonObj = json.loads(request.body)
        chatNo = jsonObj.get("chatNo")
        sendContent = jsonObj.get("sendContent")
        dtoChatRoom = ChatRoom.objects.get(chatNo=chatNo)
        # logger.info("pasgeNum : "+str(pageNum))

        # 상세 채팅내용 저장
        dtoChatInfo = ChatInfo(
            chatNo=chatNo,
            itemNo=dtoChatRoom.itemNo,
            sellMemNo=dtoChatRoom.sellMemNo,
            buyMemNo=dtoChatRoom.buyMemNo,
            fromSender=memNo,
            chatContent=sendContent,
            chatRead=0,
        )
        dtoChatInfo.save()
        dtoChat = list(
            ChatInfo.objects.filter(chatNo=chatNo)
            .order_by("endTime")
            .values(
                "chatNo",
                "itemNo",
                "sellMemNo",
                "buyMemNo",
                "fromSender",
                "chatContent",
                "chatRead",
            )
        )
        memList = list(
            Member.objects.filter(memNo=memNo).values("memNo", "nickname", "proImg")
        )
        logger.info("memList : " + str(memList))
        if memNo == dtoChatRoom.sellMemNo:  # 현재 접속자가 판매자일경우
            otherList = list(
                Member.objects.filter(memNo=dtoChatRoom.buyMemNo).values(
                    "memNo", "nickname", "proImg"
                )
            )
        else:  # 현재 접속자가 거래자일 경우
            otherList = list(
                Member.objects.filter(memNo=dtoChatRoom.sellMemNo).values(
                    "memNo", "nickname", "proImg"
                )
            )
        context = {
            "dtoChat": dtoChat,
            "memList": memList,
            "otherList": otherList,
        }
        # json 타입으로 리턴
        return HttpResponse(json.dumps(context), content_type="application/json")


# 상품상세 페이지
class DetailView(TemplateView):
    def get(self, request):
        template = loader.get_template("uniDetail.html")
        memNo = request.session.get("memNo", None)
        logger.info("memNo : " + str(memNo))
        zonecode = ""
        recommendck = 0
        if memNo == None:
            itemNo = request.GET["itemNo"]
            dto = Item.objects.get(itemNo=itemNo)
            dto.readCnt += 1
            dto.save()
            # 카테고리 이름
            dtoCat = Category.objects.get(catNo=dto.catNo)
            # 추천 상품일 경우
            recommend = request.GET.get("recmd", "0")
            # 추천상품 리스트(8개)
            dtoRecmd = (
                Item.objects.exclude(itemNo=dto.itemNo)
                .filter(catNo=dto.catNo)
                .order_by("-readCnt", "-uDate")[0:8]
            )
            # 등록일 수정
            registerDate = reDateType(dto.uDate)
            # 해당 상품을 찜하였는지 확인
            likeck = -1
            # 해당 상품을 신고했는지 확인(이중신고방지)
            reportck = -1
        else:
            itemNo = request.GET["itemNo"]
            dto = Item.objects.get(itemNo=itemNo)
            dto.readCnt += 1
            dto.save()
            # 알림 내역에서 신고내역 상품을 클릭하여 들어왔을 경우
            # 알림(Mark) 테이블의 알림 읽음 표시 '1'로 업데이트
            alR = request.GET.get("alR", 0)
            if alR != "0":
                try:
                    readMark = Mark.objects.get(memNo=memNo, markNo=alR)
                    readMark.markRead = 1
                    # logger.info("delMark : "+str(readMark))
                    readMark.save()
                except:
                    pass
            # 알림 내역에서 오래된상품 알림에서 클릭하여 들어왔을 경우
            # 알림(Mark) 테이블의 알림 읽음 표시 '1'로 업데이
            alA = request.GET.get("alA", 0)
            logger.info("alA : " + str(alA))
            if alA != "0":
                try:
                    readMark = Mark.objects.get(memNo=memNo, markNo=itemNo)
                    readMark.markRead = 1
                    # logger.info("delMark : "+str(readMark))
                    readMark.save()
                except:
                    pass
            # 알림 내역에서 찜한상품 판매완료를 통하여 들어왔을 경우
            # 알림(Mark) 테이블의 알림 읽음 표시 '1'로 업데이
            alS = request.GET.get("alS", 0)
            if alS != "0":
                try:
                    readMark = Mark.objects.get(memNo=memNo, markNo="sa" + str(itemNo))
                    readMark.markRead = 1
                    # logger.info("delMark : "+str(readMark))
                    readMark.save()
                except:
                    pass
            # 알림 내역에서 찜한상품의 가격이 변동된 알람을 통해서 접근했을 경우
            # 알림(Mark) 테이블의 알림 읽음 표시 '1'로 업데이
            alU = request.GET.get("alU", 0)
            if alU != "0":
                indexNo = request.GET.get("index", 0)
                try:
                    readMark = Mark.objects.get(
                        markNo="su" + str(itemNo), indexNo=indexNo
                    )
                    readMark.markRead = 1
                    # logger.info("delMark : "+str(readMark))
                    readMark.save()
                except:
                    pass
            # 카테고리 이름
            dtoCat = Category.objects.get(catNo=dto.catNo)
            # logger.info("CatName : "+str(dtoCat.catName))
            # 추천 상품일 경우
            recommend = request.GET.get("recmd", "0")
            if recommend == "1":
                dtoS = Satisfaction.objects.filter(itemNo=itemNo, memNo=memNo).count()
                logger.info("dtoS : " + str(dtoS))
                if dtoS > 0:
                    recommendck = 1
                else:
                    recommendck = 0

            # 추천상품 리스트(8개)
            # zonecode = substr(dto.zonecode, 1, 3)
            zonecode = dto.zonecode[0:3]  # 우편번호 앞에 3자리 자르기
            # logger.info("zonecode : "+str(zonecode))
            dtoRecmdCnt = (
                Item.objects.exclude(itemNo=dto.itemNo)
                .filter(catNo=dto.catNo, zonecode__startswith=zonecode)
                .count()
            )
            if dtoRecmdCnt > 0:
                dtoRecmd = (
                    Item.objects.exclude(itemNo=dto.itemNo)
                    .filter(catNo=dto.catNo, zonecode__startswith=zonecode)
                    .order_by("-readCnt", "-uDate")[0:8]
                )
            else:
                dtoRecmd = None
            # 등록일 수정
            registerDate = reDateType(dto.uDate)
            # 해당 상품을 찜하였는지 확인
            likeck = Like.objects.filter(memNo=memNo, itemNo=itemNo).count()
            # 해당 상품을 신고했는지 확인(이중신고방지)
            reportck = Report.objects.filter(reportFrom=memNo, itemNo=itemNo).count()

            # 해당 상품 접속기록 stayLog 테이블에 저장
            # 현재 해당 상품의 접속기록이 있는지 확인위해 오늘 날짜 추출 및 데이터형 변형
            nowDate = datetime.now(tz=timezone.utc).strftime("%Y-%m-%d")
            logger.info("now: " + str(nowDate))
            dtoStayLogCnt = StayLog.objects.filter(
                memNo=memNo, itemNo=itemNo, connectDate__icontains=nowDate
            ).count()
            if dtoStayLogCnt > 0:
                try:
                    dtoStayLog = StayLog.objects.get(
                        memNo=memNo,
                        itemNo=itemNo,
                        connectDate__icontains=nowDate,
                        stayFlg=0,
                    )
                    logger.info("detailLog: " + str(dtoStayLog))
                    dtoStayLog.connectDate = datetime.now(tz=timezone.utc)
                    dtoStayLog.stayFlg = 1
                    dtoStayLog.save()
                except:
                    pass
            else:
                dtoStayLog = StayLog(memNo=memNo, itemNo=itemNo, stayCnt=1, stayFlg=1)
                dtoStayLog.save()

        context = {
            "dto": dto,
            "registerDate": registerDate,
            "catName": dtoCat.catName,
            "dtoRecmd": dtoRecmd,
            "recommend": recommend,
            "likeck": likeck,
            "memNo": memNo,
            "reportck": reportck,
            "zonecode": zonecode,
            "recommendck": recommendck,
        }
        return HttpResponse(template.render(context, request))

    def post(self, request):
        pass


# 추천상품 만족도 조사 테이블 업데이트
class UpdateRecentreviewView(TemplateView):
    @csrf_exempt
    def get(self, request):
        pass

    def post(self, request):
        memNo = request.session.get("memNo", None)
        rideoBtn = request.POST["recentreview"]
        itemNo = request.POST["recentItemNo"]
        # Satisfaction update
        dto = Satisfaction(
            memNo=memNo, itemNo=request.POST["recentItemNo"], satisfactionScore=rideoBtn
        )
        dto.save()
        # 만족도 평균 구하고 Item update
        satAvg = Satisfaction.objects.all().aggregate(Avg("satisfactionScore"))
        dtoItem = Item.objects.get(itemNo=itemNo)
        dtoItem.SatisfactionAvg = satAvg["satisfactionScore__avg"]
        dtoItem.save()

        dtoItem = Item.objects.get(itemNo=itemNo)
        sellMemNo = dtoItem.memNo
        chatNo = ""
        # ChatRoom.objects.all().delete()
        # chatRoom에 저장된 거래가 하나없는지 확인
        chatCount = ChatRoom.objects.all().count()
        if chatCount == 0:  # 하나도 없을 경우
            chatNo = "ch01"
            logger.info("chatNo : " + str(chatNo))
            dtoChatRoom = ChatRoom(
                chatNo=chatNo,
                sellMemNo=sellMemNo,
                buyMemNo=memNo,
                itemNo=itemNo,
                title=dtoItem.title,
                itemImg=dtoItem.itemImg,
            )
            dtoChatRoom.save()
            return HttpResponseRedirect(
                "uniChatRoomInfo?chatNo=" + chatNo + "&itemNo=" + itemNo
            )
        else:  # 하나라도 있을 경우
            # 해당 상품을 거래 신청한 적이 있는지
            try:  # 거래한적 있음
                chatRoomCk = ChatRoom.objects.get(
                    sellMemNo=sellMemNo, buyMemNo=memNo, itemNo=itemNo
                )
                chatNo = chatRoomCk.chatNo
                return HttpResponseRedirect(
                    "uniChatRoomInfo?chatNo=" + chatNo + "&itemNo=" + itemNo
                )
            except:  # 해당 상품 처음거래
                chatNoCk = ChatRoom.objects.all().order_by("-chatNo")[0]
                Num = int(chatNoCk.chatNo[2:]) + 1
                strNum = ""
                if Num < 10:
                    strNum = "0" + str(Num)
                else:
                    strNum = str(Num)
                chatNo = "ch" + strNum
                dtoChatRoom = ChatRoom(
                    chatNo=chatNo,
                    sellMemNo=sellMemNo,
                    buyMemNo=memNo,
                    itemNo=itemNo,
                    title=dtoItem.title,
                    itemImg=dtoItem.itemImg,
                )
                dtoChatRoom.save()
        return HttpResponseRedirect(
            "uniChatRoomInfo?chatNo=" + chatNo + "&itemNo=" + itemNo
        )


# 찜 테이블 / 상품 찜수 update
class UpdateLikeView(TemplateView):
    def get(self, request):
        pass

    def post(self, request):
        template = loader.get_template("uniDetail.html")
        memNo = request.session.get("memNo", None)
        itemNo = request.POST["itemNo"]
        count = Like.objects.filter(memNo=memNo, itemNo=itemNo).count()
        if count == 0:
            dto = Like(
                memNo=memNo, itemNo=request.POST["itemNo"], price=request.POST["price"]
            )
            dto.save()
            dtoItem = Item.objects.get(itemNo=itemNo)
            dtoItem.likeCnt += 1
            dtoItem.save()
        else:
            dto = Like.objects.filter(memNo=memNo, itemNo=itemNo)
            dto.delete()
            dtoItem = Item.objects.get(itemNo=itemNo)
            dtoItem.likeCnt -= 1
            dtoItem.save()
        return HttpResponse(dtoItem.likeCnt)


# 신고 테이블 / 멤버 신고받은수 update
class UpdateReportView(TemplateView):
    @csrf_exempt
    def get(self, request):
        pass

    def post(self, request):
        memNo = request.session.get("memNo", None)
        reportTo = request.POST["reportTo"]
        reportFrom = request.POST["reportFrom"]
        reportContent = request.POST["reportContent"]
        itemNo = request.POST["itemNo"]
        result = ""
        count = Report.objects.filter(reportFrom=memNo, itemNo=itemNo).count()
        if count == 0:
            # 신고테이블(Report)에 업데이트
            dto = Report(
                reportFrom=reportFrom,
                reportTo=reportTo,
                reportContent=reportContent,
                itemNo=itemNo,
            )
            dto.save()
            logger.info(
                "reportIndex : "
                + str(
                    Report.objects.filter(reportFrom=memNo, itemNo=itemNo).values(
                        "indexNo"
                    )
                )
            )
            # 알림테이블(Mark)에 업데이트
            dtoMark = Mark(
                markNo=Report.objects.filter(reportFrom=memNo, itemNo=itemNo).values(
                    "indexNo"
                ),
                memNo=reportTo,
                markStat=2,
                markContent=reportContent,
            )
            dtoMark.save()

            # 멤버테이블(Member)에 신고받은 유무, 총 받은 횟수 업데이트
            dtoMember = Member.objects.get(memNo=reportTo)
            dtoMember.report = 1
            dtoMember.reportCnt += 1
            dtoMember.save()
            result = "yes"
        else:
            result = "no"
        return HttpResponse(result)


# 상품상세페이지의 판매자 정보 이동
class SellerView(TemplateView):
    @csrf_exempt
    def get(self, request):  # 첫 접속 페이지 구성
        mainMemNo = request.session.get("memNo", None)
        # 판매자 memNo 보안을 위해 itemNo만 받아 서 진행
        template = loader.get_template("uniSeller.html")
        itemNo = request.GET["itemNo"]
        # 아이템 테이블에서 해당 아이템의 판매자 memNo 추출
        seller = Item.objects.filter(itemNo=itemNo).values("memNo")
        # logger.info("seller : "+str(seller[0]["memNo"]))
        dtoItem = Item.objects.filter(memNo=seller[0]["memNo"]).order_by("-uDate")
        dtoMember = Member.objects.get(memNo=seller[0]["memNo"])
        # 페이지 번호
        pageNum = request.GET.get("pageNum", 1)
        # 페이지번호 생성에 필요한 context값을 추룰하는 함수 실행
        context = pageList(pageNum, seller[0]["memNo"], "get")
        # pageList()함수에서 추출하지 못한 dtoMember context에 추가
        context["dtoMember"] = dtoMember
        context["memNo"] = mainMemNo
        return HttpResponse(template.render(context, request))

    def post(self, request):  # ajax 용으로 사용예정
        mainMemNo = request.session.get("memNo", None)
        # ajax에서 json 타입으로 데이터를 보낼 경우 파싱 필요
        jsonObj = json.loads(request.body)
        pageNum = jsonObj.get("pageNum")
        seller = jsonObj.get("sellMemNo")
        # logger.info("pasgeNum : "+str(pageNum))

        # 페이지번호 생성에 필요한 context값을 추룰하는 함수 실행
        context = pageList(pageNum, seller, "post")
        # ajax에서 json타입으로 전송시 Queryset 타입, date타입은 호환이 불가능하여
        # QuerySet는 모델 인스턴스 세트를 리턴하지만 values()메소드는 모델 인스턴스를 나타내는 사전 세트를 리턴하여 json타입으로 변환가능
        # pageList에서 value로 값을 받았지만 데이터가 적용이 되지않는 경우가 있어 다시한번 .values()하여 list()형으로 변환
        context["dtoItem"] = list(
            context["dtoItem"].values("itemNo", "itemImg", "title", "sellStat", "price")
        )
        context["memNo"] = mainMemNo
        # logger.info("contextPost : "+str(context))

        # json 타입으로 리턴
        return HttpResponse(json.dumps(context), content_type="application/json")


# 마이페이지 이동
class MypageView(TemplateView):
    def get(self, request):
        template = loader.get_template("uniMypage.html")
        memNo = request.session.get("memNo", None)
        dtoMember = Member.objects.get(memNo=memNo)
        context = {
            "dtoMember": dtoMember,
            "memNo": memNo,
        }
        return HttpResponse(template.render(context, request))

    def post(self, request):
        pass


# 알림내역 페이지 이동
class AlarmView(TemplateView):
    def get(self, request):
        template = loader.get_template("uniAlarm.html")
        memNo = request.session.get("memNo", None)
        count = Mark.objects.filter(Q(memNo=memNo) | Q(memNo="0")).count()
        context = {
            "memNo": memNo,
            "count": count,
        }
        if count != 0:  # 해당 사용자에 해당하는 알람이 있을 경우
            PAGE_SIZE = 3
            PAGE_BLOCK = 2
            # 페이지 번호
            pageNum = request.GET.get("pageNum", 1)
            pageNum = int(pageNum)
            # 해당  사용자 알림 데이터 추출
            dtoMark = Mark.objects.filter(Q(memNo=memNo) | Q(memNo="0")).order_by(
                "-markDate"
            )
            # 데이터 추출 인덱스범위 설정[start:end]
            start = (pageNum - 1) * int(PAGE_SIZE)
            end = start + int(PAGE_SIZE)
            markcount = dtoMark.count()
            if end > markcount:
                end = markcount

            for i, noticeT in enumerate(dtoMark):
                if (
                    noticeT.markStat == 0
                ):  # 공지의 경우 noticeNo에 as로 시작일 경우 일반공지, ev로 시작할 경우 이벤트 공지
                    if noticeT.markNo[:2] == "as":  # 일반공지
                        dtoMark[i].noticeStat = 0
                    else:  # 이벤트공지
                        dtoMark[i].noticeStat = 1
                elif noticeT.markStat == 1:  # 채팅의 경우
                    chatItemNo = ChatRoom.objects.filter(chatNo=noticeT.markNo).values(
                        "itemNo"
                    )
                    dtoMark[i].itemNo = chatItemNo[0]["itemNo"]
                elif noticeT.markStat == 2:  # 신고의 경우 해당 신고상품으로 바로 접속하기 위해 itemNo을 받아야함
                    reportItemNo = Report.objects.filter(
                        indexNo=noticeT.markNo, reportTo=noticeT.memNo
                    ).values("itemNo")
                    dtoMark[i].itemNo = reportItemNo[0]["itemNo"]
                elif (
                    noticeT.markStat == 4
                ):  # 거래확정 완료시 item테이블의 거래유무 업데이트를 위하여 sellMemNo을 넣어줌
                    mlist = dtoMark[i].markNo[2:].split("_")
                    dtoMark[i].itemNo = str(mlist[2])
                elif noticeT.markStat == 5:  # 거래확정 신청 거절 알림에 따른 chatNo/ itemNo 분리
                    mlist = dtoMark[i].markNo[2:].split("_")
                    dtoMark[i].itemNo = (
                        "chatNo=" + str(mlist[1]) + "&itemNo=" + str(mlist[0])
                    )
                elif noticeT.markStat == 7:  # 거래확정 신청 거절 알림에 따른 chatNo/ itemNo 분리
                    dtoMark[i].itemNo = dtoMark[i].markNo[2:]
                elif noticeT.markStat == 8:  # 가격변동 알림에 따른 itemNo 추출
                    dtoMark[i].itemNo = dtoMark[i].markNo[2:]
                else:
                    pass

                # 오늘 올라온 알림일 경우 new 아이콘을 붙이기 위해 알림이 등록된 날과 오늘날짜 비교하여 데이터 넘김
                # 알림등록일 == 오늘날짜 , 전달 데이터 today = 0
                # if DateFormat(noticeT.markDate).format('Y-m-d') == DateFormat(datetime.now()).format('Y-m-d') :
                # dtoMark[i].today = 0
                # else : # 알림등록일 != 오늘날짜 , 전달 데이터 today = 1
                # dtoMark[i].today = 1
            context["dtoMark"] = dtoMark[start:end]

            startpage = pageNum // PAGE_BLOCK * PAGE_BLOCK + 1
            if pageNum % PAGE_BLOCK == 0:
                startpage -= PAGE_BLOCK

            endpage = startpage + PAGE_BLOCK - 1
            pagecount = markcount // PAGE_SIZE
            if count % PAGE_SIZE > 0:
                pagecount += 1
            if endpage > pagecount:
                endpage = pagecount
            pages = range(startpage, endpage + 1)

            context["markcount"] = markcount
            context["pageNum"] = pageNum
            context["pages"] = pages
            context["pageblock"] = PAGE_BLOCK
            context["pagecount"] = pagecount
            context["startpage"] = startpage
            context["endpage"] = endpage

        return HttpResponse(template.render(context, request))

    def post(self, request):
        pass


class StayLogUpdate(TemplateView):
    def get(self, request):
        pass

    def post(self, request):
        memNo = request.session.get("memNo", None)
        if memNo != None:
            itemNo = request.POST["itemNo"]
            nowDate = datetime.now(tz=timezone.utc)
            nowDatestr = nowDate.strftime("%Y-%m-%d")
            logger.info("stayLogUpdateNow: " + str(nowDatestr))
            dtoStayLogCnt = StayLog.objects.filter(
                memNo=memNo, itemNo=itemNo, connectDate__icontains=nowDatestr, stayFlg=1
            ).count()
            if dtoStayLogCnt > 0:
                dtoStayLog = StayLog.objects.get(
                    memNo=memNo,
                    itemNo=itemNo,
                    connectDate__icontains=nowDatestr,
                    stayFlg=1,
                )
                connectDate = dtoStayLog.connectDate
                # 실제 머문시간 계산
                stayTime = dtoStayLog.stayTime
                stayDate = nowDate - connectDate
                staySeconds = stayTime + stayDate.seconds
                logger.info(
                    "stayTime: "
                    + str(stayDate)
                    + " / "
                    + str(stayDate.seconds)
                    + " / "
                    + str(staySeconds)
                )
                stayCnt = 1
                if int(staySeconds) >= 1200:
                    stayCnt = staySeconds // 600
                    logger.info("stayTime: " + str(stayCnt))
                dtoStayLog.stayFlg = 0
                dtoStayLog.stayTime = staySeconds
                dtoStayLog.stayCnt = stayCnt
                dtoStayLog.save()
            else:
                pass

        return HttpResponse("succese")


# class TitleckView(TemplateView):
# @csrf_exempt
# def get(self, request):
# pass
# @csrf_exempt
# def post(self, request):
# keyword = request.POST["keyword"]
# category_number_dic = {'가구/인테리어': 3, '여성패션/잡화': 5, '남성패션/잡화': 6, '유아동': 7, '뷰티/미용': 8,
# '스포츠/레저': 9, '게임/취미': 10, '도서/티켓/음반': 11, '반려동물': 12, '식물': 13, '기타': 14}
# model = fasttext.load_model("unimarket\static\modelfile\model_cate.bin")
# result = model.predict(keyword)
# category = result[0][0].replace("__label__","")
# logger.info("category : "+str(category))
# # catnum = category_number_dic.get(category)
# catnum = category
#
# return HttpResponse(catnum)


class TitleckView(TemplateView):
    @csrf_exempt
    def get(self, request):
        pass

    @csrf_exempt
    def post(self, request):
        keyword = request.POST["keyword"]
        logger.info("titleck")
        # dtoItem = Item.objects.all().values()
        # df = pd.DataFrame(dtoItem)
        # logger.info(df)
        # # df['title'] = dtoItem.title
        # # df['category'] = dtoItem.catNo
        #
        # # 특수문자 제거 후 title 크기 확인
        # df['title'] = df['title'].str.replace('[-=+,#/\?:^$.@*\"※~&%ㆍ!』\\‘|\(\)\[\]\<\>`\'…》]','',regex=True)
        # df['title'].replace('', np.nan, inplace=True)
        #
        # df2 = pd.DataFrame(columns=['category', 'title'])
        # df2['title'] = df['title']
        # df2['category'] = '__label__'+df['catNo']
        #
        # df2.to_csv('unimarket/static/modelfile/labelingtrain.txt', sep = '\t', index = False)
        # labeling = pd.read_csv("unimarket/static/modelfile/labelingtrain.txt", sep = '\t')
        #
        # model = fasttext.train_supervised('unimarket/static/modelfile/labelingtrain.txt', wordNgrams=2, epoch=300, lr=0.5, bucket=200000, dim=50, loss='ova')
        # model.save_model("unimarket/static/modelfile/model_cat.bin")

        model = fasttext.load_model("unimarket/static/modelfile/model_cat.bin")
        logger.info("titleck22222")
        result = model.predict(keyword)
        category = result[0][0].replace("__label__cat", "")
        logger.info("category : " + str(category))
        catnum = int(category)

        return HttpResponse(catnum)


# 등록일 몇분전 몇일전 표시 함수
def reDateType(uDate):
    reTime = datetime.now(tz=timezone.utc) - uDate
    # 1분을 넘기지않을 경우
    if reTime < timedelta(minutes=1):
        return "방금 전"
    # 1시간을 넘기지않을 경우
    elif reTime < timedelta(hours=1):
        return str(int(reTime.seconds / 60)) + "분 전"
    # 하루(1일)를 넘기지않을 경우
    elif reTime < timedelta(days=1):
        return str(int(reTime.seconds / 3600)) + "시간 전"
    # 일주일(7일)을 넘기지않을 경우
    elif reTime < timedelta(days=7):
        time = datetime.now(tz=timezone.utc).date() - uDate.date()
        return str(time.days) + "일 전"
    # 한달(30일)을 넘기지않을 경우
    elif reTime < timedelta(days=30):
        if reTime < timedelta(weeks=2):
            return "1주 전"
        if reTime < timedelta(weeks=3):
            return "2주 전"
        if reTime < timedelta(weeks=4):
            return "3주 전"
        if reTime < timedelta(weeks=5):
            return "4주 전"
    else:
        return "오래전"


# 페이지 번호 생성
def pageList(pageNum, seller, stat):
    PAGE_SIZE = 2
    PAGE_BLOCK = 2

    # 페이지 번호
    pageNum = int(pageNum)
    # 상품 판매자 번호를 받아 상품테이블에서 판매자 등록 상품 데이터 추출
    sellMemNo = seller
    dtos = Item.objects.filter(memNo=sellMemNo).order_by("-uDate")

    # 데이터 추출 인덱스범위 설정[start:end]
    start = (pageNum - 1) * int(PAGE_SIZE)
    end = start + int(PAGE_SIZE)
    count = dtos.count()
    if end > count:
        end = count
    dtoItem = ""
    # 추출한 인덱스 범위(page 번호기준)에 따른 상품목록 추출
    if stat == "get":  # get으로 데이터를 받을 경우
        dtoItem = dtos[start:end]
    else:  # post로 데이터를 받을 경우
        dtoItem = dtos[start:end].values(
            "itemNo", "itemImg", "title", "sellStat", "price"
        )
        # logger.info("함수dtoItem : "+str(dtoItem))

    startpage = pageNum // PAGE_BLOCK * PAGE_BLOCK + 1
    if pageNum % PAGE_BLOCK == 0:
        startpage -= PAGE_BLOCK

    endpage = startpage + PAGE_BLOCK - 1
    pagecount = count // PAGE_SIZE
    if count % PAGE_SIZE > 0:
        pagecount += 1
    if endpage > pagecount:
        endpage = pagecount

    # ajax에 json방식으로 return할 경우 range타입은 호환이 불가하여 list()로 변환
    pages = list(range(startpage, endpage + 1))

    context = {
        "count": count,
        "dtoItem": dtoItem,
        "pageNum": pageNum,
        "pages": pages,
        "pageblock": PAGE_BLOCK,
        "pagecount": pagecount,
        "startpage": startpage,
        "endpage": endpage,
    }

    return context
