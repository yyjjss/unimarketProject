import json
import logging
from django.conf import settings

from django.db.models.query_utils import Q
from django.http.response import HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.template import loader
from django.views.decorators.csrf import csrf_exempt
from django.views.generic.base import TemplateView
from django.utils.dateformat import DateFormat
from datetime import datetime

from unimarket.models import Item, ChatRoom, Member, ChatInfo, Mark, Like


logger = logging.getLogger(__name__)

class ChatSendContentView(TemplateView):
    def get(self,request):
        pass
    def post(self,request):
        template = loader.get_template("uniChatRoomInfo.html")
        chatNo = request.POST["chatNo"]
        itemNo = request.POST["itemNo"]
        # context={
            # 'room_name': str("chatNo="+chatNo+"&itemNo="+itemNo),
            # }
        # return HttpResponse(template.render(context, request))
        return render(request, 'uniChatRoomInfo.html', {
            'room_name': str("chatNo="+chatNo+"&itemNo="+itemNo)
            })
        
class UniSearchMapView(TemplateView):
    def get(self,request):
        template = loader.get_template("uniSearchMap.html")
        context={
                    "kakao_Mapkey": settings.KAKAO_MAP,
                    }
        return HttpResponse(template.render(context, request))
    def post(self,request):
        template = loader.get_template("uniSearchMap.html")
        context={
                    "kakao_Mapkey": settings.KAKAO_MAP,
                    }
        return HttpResponse(template.render(context, request))
        
class ChatRoomInfoView(TemplateView):
    def get(self, request):
        template = loader.get_template("uniChatRoomInfo.html")
        # 거래신청 사용자
        memNo = request.session.get("memNo", None)
        chatNo = request.GET.get("chatNo", None)
        
        if chatNo != None : 
            chatItem = Item.objects.get(itemNo=request.GET["itemNo"])
            chatContext = ChatRoom.objects.get(chatNo=chatNo)
            memList =""
            otherList = ""
            if memNo == chatContext.sellMemNo : # 현재 접속자가 판매자일경우
                memList = Member.objects.get(memNo=memNo)
                otherList = Member.objects.get(memNo=chatContext.buyMemNo) 
            else: # 현재 접속자가 거래자일 경우
                memList = Member.objects.get(memNo=memNo)
                otherList = Member.objects.get(memNo=chatContext.sellMemNo)
            # 현재 물품에 대한 채팅기록
            count = ChatInfo.objects.filter(chatNo=chatNo).count()
            # 다른 채팅기록
            roomCount = ChatRoom.objects.filter(Q(buyMemNo=memNo)|Q(sellMemNo=memNo)).count()
            context={}
            if count != 0 : # 채팅 내용이 존재할시 
                dtoChat = ChatInfo.objects.filter(chatNo=chatNo).order_by("endTime")
                # logger.info("dtoCaht : " +str(dtoChat))
                if roomCount != 0 : # 다른 채팅 기록이 있을 경우 
                    dtoChatList = ChatRoom.objects.filter(Q(buyMemNo=memNo)|Q(sellMemNo=memNo)).order_by("-sendTime")
                    for i, dto in enumerate(dtoChatList):
                        dtoChatList[i].buyNick = Member.objects.get(memNo=dtoChatList[i].buyMemNo)
                        # logger.info("dtoCH: "+str(dtoChatList[i].buyNick))
                        dtoChatList[i].sellNick = Member.objects.get(memNo=dtoChatList[i].sellMemNo) 
                
                    context={
                        "dtoChat" : dtoChat,
                        "dtoChatList" : dtoChatList,
                        "chatItem" : chatItem,
                        "memList" : memList,
                        "otherList" : otherList,
                        "memNo" : memNo,
                        "chatNo" : chatNo,
                        "kakao_Mapkey": settings.KAKAO_MAP,
                        }
                else : # 다른 채팅 기록이 없을 경우 
                    context={
                        "dtoChat" : dtoChat,
                        "dtoChatList" : None,
                        "chatItem" : chatItem,
                        "memList" : memList,
                        "otherList" : otherList,
                        "memNo" : memNo,
                        "chatNo" : chatNo,
                        "kakao_Mapkey": settings.KAKAO_MAP,
                        }
                try :
                    alC = request.GET.get("alC", None)
                    indexNo = request.GET.get("index", None)
                    if alC != None :
                        readMark = Mark.objects.get(markNo=alC, indexNo=indexNo)
                        readMark.markRead = 1
                        #logger.info("delMark : "+str(readMark))
                        readMark.save()
                    else :    
                        readMark = Mark.objects.get(markNo=chatNo)
                        readMark.markRead = 1
                        #logger.info("delMark : "+str(readMark))
                        readMark.save()
                except :
                    pass
            else: # 채팅 내용이 존재하지않을 시
                if roomCount != 0 : # 다른 채팅 기록이 있을 경우 
                    dtoChatList = ChatRoom.objects.filter(Q(buyMemNo=memNo)|Q(sellMemNo=memNo)).order_by("-sendTime")
                    for i, dto in enumerate(dtoChatList):
                        dtoChatList[i].buyNick = Member.objects.get(memNo=dtoChatList[i].buyMemNo)
                        logger.info("dtoCH: "+str(dtoChatList[i].buyNick))
                        dtoChatList[i].sellNick = Member.objects.get(memNo=dtoChatList[i].sellMemNo) 
                    context={
                        "dtoChat" : None,
                        "dtoChatList" : dtoChatList,
                        "chatItem" : chatItem,
                        "memList" : memList,
                        "otherList" : otherList,
                        "memNo" : memNo,
                        "chatNo" : chatNo,
                        "kakao_Mapkey": settings.KAKAO_MAP,
                        }
                else : # 다른 채팅 기록이 없을 경우 
                    context={
                        "dtoChat" : None,
                        "dtoChatList" : None,
                        "chatItem" : chatItem,
                        "memList" : memList,
                        "otherList" : otherList,
                        "memNo" : memNo,
                        "chatNo" : chatNo,
                        "kakao_Mapkey": settings.KAKAO_MAP,
                        }
                try :    
                    readMark = Mark.objects.get(markNo=chatNo)
                    readMark.markRead = 1
                    #logger.info("delMark : "+str(readMark))
                    readMark.save()
                except :
                    pass
            return HttpResponse(template.render(context, request))
        else : # 프로필에서 채팅으로 접근할 경우 
            # 다른 채팅기록
            roomCount = ChatRoom.objects.filter(Q(buyMemNo=memNo)|Q(sellMemNo=memNo)).count()
            context={}
            if roomCount != 0 : # 다른 채팅 기록이 있을 경우 
                dtoChatList = ChatRoom.objects.filter(Q(buyMemNo=memNo)|Q(sellMemNo=memNo)).order_by("-sendTime")
                for i, dto in enumerate(dtoChatList):
                    dtoChatList[i].buyNick = Member.objects.get(memNo=dtoChatList[i].buyMemNo)
                    logger.info("dtoCH: "+str(dtoChatList[i].buyNick))
                    dtoChatList[i].sellNick = Member.objects.get(memNo=dtoChatList[i].sellMemNo)
                context={
                    "dtoChatList" : dtoChatList,
                    "memNo" : memNo,
                    "chatNo" : None,
                    "kakao_Mapkey": settings.KAKAO_MAP,
                    }
            else : # 다른 채팅 기록이 없을 경우 
                context={
                    "dtoChatList" : None,
                    "memNo" : memNo,
                    "chatNo" : None,
                    "kakao_Mapkey": settings.KAKAO_MAP,
                    }
        return HttpResponse(template.render(context, request))
    
    def post(self, request):
        pass
    
    
class ChatRoomSearchView(TemplateView):
    @csrf_exempt
    def get(self, request):
        pass
    def post(self, request):
        memNo = request.session.get("memNo", None)
        jsonObj = json.loads(request.body)
        roomSearch = jsonObj.get("roomSearch")
        #roomSearch = request.POST["roomSearch"]
        logger.info("room : "+str(roomSearch))
        memList =[]
        otherList =[]
        context ={}
        # 채팅 룸이 존재하는지 검색
        q=Q()
        q.add(Q(buyMemNo=memNo)|Q(sellMemNo=memNo),q.AND)
        q.add(Q(title__contains=roomSearch),q.AND)
        dtoChatRoom = ChatRoom.objects.filter(q)
        logger.info("dtoChatRoom : "+str(dtoChatRoom))
        roomCount = dtoChatRoom.count()
        if roomCount > 0:
            for i, dto in enumerate(dtoChatRoom):
                if memNo == dtoChatRoom[i].sellMemNo : # 현재 접속자가 판매자일경우
                    logger.info("판매자")
                    # dtoChatRoom[i].memList = Member.objects.filter(memNo=memNo).values("nickname")[0]
                    # dtoChatRoom[i].otherList = Member.objects.filter(memNo=dtoChatRoom[i].buyMemNo).values("nickname")[0]
                    memList.append(Member.objects.filter(memNo=memNo).values("nickname")[0])
                    otherList.append(Member.objects.filter(memNo=dtoChatRoom[i].buyMemNo).values("nickname")[0]) 
                else: # 현재 접속자가 거래자일 경우
                    logger.info("거래자")
                    memList.append(Member.objects.filter(memNo=memNo).values("nickname")[0])
                    otherList.append(Member.objects.filter(memNo=dtoChatRoom[i].sellMemNo).values("nickname")[0])
            context["dtoChatList"]=list(dtoChatRoom.values("chatNo","sellMemNo","buyMemNo","itemNo","title","itemImg"))
            context["memList"] = memList
            context["otherList"] = otherList
            context["listck"] = "1"
            context["kakao_Mapkey"]=settings.KAKAO_MAP
        else : 
            context["listck"] = "0"
            context["kakao_Mapkey"]=settings.KAKAO_MAP
        return HttpResponse(json.dumps(context), content_type="application/json")

# 거래 확정시 item 테이블 판매완료  물품으로 변경
class UpdateBuyComplete(TemplateView):
    def get(self, request):
        pass
    def post(self, request):
        # memNo = request.session.get("memNo", None) # 거래자
        # ajax에서 json 타입으로 데이터를 보낼 경우 파싱 필요 
        jsonObj = json.loads(request.body)
        chatNo = jsonObj.get("chatNo")
        itemNo = jsonObj.get("itemNo")
        itemTitle = jsonObj.get("itemTitle")
        sellMemNo = jsonObj.get("sellMemNo")
        buyMemNo = jsonObj.get("buyMemNo")
        dtoMember = Member.objects.get(memNo=buyMemNo)
        dtoItem = Item.objects.get(itemNo=itemNo, memNo=sellMemNo)
        dtoItem.buyMemNo = buyMemNo
        dtoItem.sellStat = 1
        dtoItem.sellDate = DateFormat(datetime.now()).format("Y-m-d H:i")
        dtoItem.save()
        
        # 알람데이터 업데이트 (거래확정 승인 알람 등록)
        dtoMark = Mark(
                    markNo = "so"+str(sellMemNo)+"_"+str(chatNo)+"_"+str(itemNo),
                    memNo = sellMemNo,  # 판매자 
                    markStat = 6,
                    markContent = "상품["+str(itemTitle)+"]의 거래확정을 거래자["+str(dtoMember.nickname)+"]님꼐서 확인하셨습니다.",
                )
        dtoMark.save()
        
        # 알람데이터 업데이트 (상품판매완료 알람 등록:해당 상품을 찜한 사람들에게 알림)
        try:
            dtoLike = Like.objects.filter(~Q(memNo=buyMemNo)&Q(itemNo=itemNo))
            logger.info("dtoLike : "+str(dtoLike.values))
            for like in dtoLike :
                dtoMark = Mark(
                        markNo = "sa"+str(itemNo),
                        memNo = like.memNo,  # 판매자 
                        markStat = 7,
                        markContent = "상품["+str(itemTitle)+"]이(가) 판매완료되었습니다.",
                    )
                dtoMark.save()
        except :
                    pass
        # 알람데이터 업데이트 (거래확정 요청 알람 삭제)
        dtoMark = Mark.objects.get(markNo="sh"+str(sellMemNo)+"_"+str(chatNo)+"_"+str(itemNo), memNo=buyMemNo)
        dtoMark.delete()
        
        return HttpResponse("succese")

# 알림내역에서 거래 확정 요청에서 거절할 경우, 해당 거절 알림 등록  
class UpdateCancleComplete(TemplateView):
    def get(self, request):
        pass
    def post(self, request):
        # ajax에서 json 타입으로 데이터를 보낼 경우 파싱 필요 
        jsonObj = json.loads(request.body)
        chatNo = jsonObj.get("chatNo")
        itemNo = jsonObj.get("itemNo")
        itemTitle = jsonObj.get("itemTitle")
        sellMemNo = jsonObj.get("sellMemNo")
        buyMemNo = jsonObj.get("buyMemNo")
        dtoMember = Member.objects.get(memNo=buyMemNo)
        logger.info("nickname: "+str(dtoMember.nickname))
        # 알람데이터 업데이트 (거래확정 거절 알람 등록)
        dtoMark = Mark(
                    markNo = "re"+str(itemNo)+"_"+str(chatNo),
                    memNo = sellMemNo,  # 거래자 
                    markStat = 5,
                    markContent = "상품 ["+str(itemTitle)+"]의 거래확정을 거래자["+str(dtoMember.nickname)+"]님께서 거절하셨습니다.",
                )
        dtoMark.save()
        
        # 알람데이터 업데이트 (거래확정 요청 알람 삭제)
        dtoMark = Mark.objects.get(markNo="sh"+str(sellMemNo)+"_"+str(chatNo)+"_"+str(itemNo), memNo=buyMemNo)
        dtoMark.delete()
        
        return HttpResponse("succese")
  
        
        