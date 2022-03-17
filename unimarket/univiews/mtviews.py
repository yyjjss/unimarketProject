from datetime import datetime, timezone, timedelta
import json
import logging

from django.db.models import Q
from django.http.response import HttpResponse
from django.shortcuts import redirect, render
from django.template import loader
from django.utils.dateformat import DateFormat
from django.views.decorators.csrf import csrf_exempt
from django.views.generic.base import TemplateView

from unimarket.models import Member, Notice, Item, Mark, FAQ, StayLog, Category
from unimarket.views import reDateType

#<---------------------머신러닝 ----------------------------------->
from konlpy.tag import Okt
okt = Okt()

#<----------------------웹 ------------------------------------->
logger = logging.getLogger(__name__)

class BaseView(TemplateView):
    def get(self, request):
        template = loader.get_template("uniBase.html")
        # 세션에서 유저 일련번호 출력
        memNo = request.session.get("memNo", None)
        # memNo = 2
        
        # 사이드바 데이터 오래머문시간, 최신순 정렬
        srcItem = StayLog.objects.filter(memNo = memNo).order_by("stayCnt")
        sideItem = Item.objects.none()
        for i in srcItem:
            sideItem |= Item.objects.filter(itemNo=i.itemNo)

        sideItems = sideItem.order_by("-uDate")[0:4]
        #시간 함수
        for timelist in sideItems:
            timelist.registerDate = reDateType(timelist.uDate)
        
        context={
            "memNo" : memNo,
            "sideItems" : sideItems
            }
        return HttpResponse(template.render(context, request))
    @csrf_exempt
    def post(self, request):
        memNo = request.session.get("memNo", None)
        # 신고, 거래신청, 게시 일주일 지난거 총 합
        # Alcount = Mark.objects.filter(memNo=memNo).count()
        # Alcount = 3
        
        #공지 랑 이벤트 체크
        Notice = Mark.objects.filter(markStat=0)
        Ascount = 0
        Evcount = 0
        for As in Notice:
            if As.markNo[:2] == 'as' and DateFormat(As.markDate).format('Y-m')  == DateFormat(datetime.now()).format('Y-m'):
                #공지사항 숫자
                Ascount += 1
            elif As.markNo[:2] == 'ev' and DateFormat(As.markDate).format('Y-m')  == DateFormat(datetime.now()).format('Y-m'):
                #이벤트 숫자
                Evcount += 1

        
        # Evcount = 2
        
        #신고 알림 수
        Recount = Mark.objects.filter(memNo=memNo, markStat = 2, markRead = 0).count()
        #
        # #거래신청도착
        Secount = Mark.objects.filter(memNo=memNo, markStat = 1, markRead = 0).count()
        #
        # #게시 일주일 지난 상품
        items = Item.objects.filter(memNo=memNo)
        # for item in items:
            # if item.uDate < datetime.now() - datetime.timedelta(days=7):
                # Itcount += 1
        # Itcount = Mark.objects.filter(memNo=memNo, markDate__lt = datetime.now() - datetime.timedelta(days=7)).count()
        Itcount = Item.objects.filter(memNo=memNo ,uDate__lte=datetime.now()-timedelta(days=7)).count()
        #
        Alcount = Recount + Secount + Itcount
        
        constat = {
            "Alcount" : Alcount,
            "Ascount" : Ascount,
            "Evcount" : Evcount,
            "Recount" : Recount,
            "Secount" : Secount,
            "Itcount" : Itcount,
            }
        return HttpResponse(json.dumps(constat), content_type="application/json")

# 메인페이지
class MainView(TemplateView):
    def get(self, request): 
        template = loader.get_template("uniMain.html")
        # 세션에서 유저 일련번호 출력
        memNo = request.session.get("memNo")
        # memNo = 2
        # 유저 정보
        # 이벤트 배너 출력을 위한 Notice 정보
        Event = Notice.objects.filter(noticeNo__contains='ev').order_by("-indexNo")
        
        # 사이드바 데이터 오래머문시간, 최신순 정렬
        srcItem = StayLog.objects.filter(memNo = memNo).order_by("stayCnt")
        sideItem = Item.objects.none()
        for i in srcItem:
            sideItem |= Item.objects.filter(itemNo=i.itemNo)

        sideItems = sideItem.order_by("-uDate")[0:4]
        #시간 함수
        for timelist in sideItems:
            timelist.registerDate = reDateType(timelist.uDate)
       
        # 로그인이 안된 경우
        if memNo == None:
            # 전체에서 최신상품
            dto = None
            recntItem = Item.objects.all().order_by("-readCnt", "-uDate")[0:8]
            newItem = Item.objects.all().order_by("-uDate")[0:8]
            #시간 함수
            for timelist in newItem:
                timelist.registerDate = reDateType(timelist.uDate)
            for item in recntItem:
                item.registerDate = reDateType(item.uDate)
        # 로그인이 된 경우
        else: 
            dto = Member.objects.get(memNo = memNo)
            zonecode = dto.zonecode[:3]
            recntItem = Item.objects.filter(zonecode__startswith=zonecode).order_by("-readCnt", "-uDate")[0:8]
            newItem = Item.objects.filter(zonecode__startswith=zonecode).order_by("-uDate")[0:8]
            #시간 함수
            for timelist in newItem:
                timelist.registerDate = reDateType(timelist.uDate)
            for item in recntItem:
                item.registerDate = reDateType(item.uDate)
        context={   
            "memNo" : memNo,
            "dto" : dto,
            "Event" : Event,
            "recntItem" : recntItem,
            "newItem" : newItem,
            "sideItems" : sideItems,
            }
        
        return HttpResponse(template.render(context, request))
    def post(self, request):
        pass
    


class NoticeView(TemplateView):
    def get(self, request):
        memNo = request.session.get("memNo")
        template = loader.get_template("uniNotice.html")
        dtos = Notice.objects.filter(noticeNo__contains='as').order_by("-indexNo")
        # 사이드바 데이터 오래머문시간, 최신순 정렬
        srcItem = StayLog.objects.filter(memNo = memNo).order_by("stayCnt")
        sideItem = Item.objects.none()
        for i in srcItem:
            sideItem |= Item.objects.filter(itemNo=i.itemNo)

        sideItems = sideItem.order_by("-uDate")[0:4]
        #시간 함수
        for timelist in sideItems:
            timelist.registerDate = reDateType(timelist.uDate)
        context={
            "dtos" : dtos,
            "memNo" : memNo,
            "sideItems" : sideItems,
            }
        return HttpResponse(template.render(context, request))
    @csrf_exempt
    def post(self, request):
        memNo = request.session.get("memNo") # js추가 부분
        jsonobj = json.loads(request.body)
        page_value = jsonobj.get("page_value")
        if page_value == 1:
            dtos = list(Notice.objects.filter(noticeNo__contains='as').order_by("-indexNo").values("indexNo", "noticeNo", "noticeTitle", "noticeContent", "eventImg"))
        else:
            dtos = list(Notice.objects.filter(noticeNo__contains='ev').order_by("-indexNo").values("indexNo", "noticeNo", "noticeTitle", "noticeContent", "eventImg"))
        context = {
            "dtos" : dtos,
            "memNo" : memNo, # js추가부분
            }
        return HttpResponse(json.dumps(context), content_type="application/json")

    
class NoticetemptView(TemplateView):
    def get(self, request):
        template = loader.get_template("uniNoticetempt.html")
        memNo = request.session.get("memNo", None) # js추가 부분
        noticeNo = request.GET.get("noticeNo")
        dto = Notice.objects.get(noticeNo = noticeNo)
        # 사이드바 데이터 오래머문시간, 최신순 정렬
        srcItem = StayLog.objects.filter(memNo = memNo).order_by("stayCnt")
        sideItem = Item.objects.none()
        for i in srcItem:
            sideItem |= Item.objects.filter(itemNo=i.itemNo)

        sideItems = sideItem.order_by("-uDate")[0:4]
        #시간 함수
        for timelist in sideItems:
            timelist.registerDate = reDateType(timelist.uDate)
        context={
            "dto" : dto,
            "memNo" : memNo, # js추가 부분
            "sideItems" : sideItems,
            }
        return HttpResponse(template.render(context, request))
    def post(self, request):
        pass

class EventtemptView(TemplateView):
    def get(self, request):
        template = loader.get_template("uniEventtempt.html")
        memNo = request.session.get("memNo", None) # js추가 부분
        noticeNo = request.GET.get("noticeNo")
        dto = Notice.objects.get(noticeNo = noticeNo)
        items = Item.objects.filter(title__contains=dto.noticeTitle).order_by("readCnt")
        
        # 사이드바 데이터 오래머문시간, 최신순 정렬
        srcItem = StayLog.objects.filter(memNo = memNo).order_by("stayCnt")
        sideItem = Item.objects.none()
        for i in srcItem:
            sideItem |= Item.objects.filter(itemNo=i.itemNo)

        sideItems = sideItem.order_by("-uDate")[0:4]
        #시간 함수
        for timelist in sideItems:
            timelist.registerDate = reDateType(timelist.uDate)
        context={
            "dto" : dto,
            "memNo" : memNo, # js추가 부분
            "items" : items,
            "sideItems" : sideItems,
            }
        return HttpResponse(template.render(context, request))
    def post(self, request):
        pass
    
class FaqView(TemplateView):
    def get(self, request):
        template = loader.get_template("uniFaq.html")
        memNo = request.session.get("memNo", None)
        dtos = FAQ.objects.all()
        # 사이드바 데이터 오래머문시간, 최신순 정렬
        srcItem = StayLog.objects.filter(memNo = memNo).order_by("stayCnt")
        sideItem = Item.objects.none()
        for i in srcItem:
            sideItem |= Item.objects.filter(itemNo=i.itemNo)

        sideItems = sideItem.order_by("-uDate")[0:4]
        #시간 함수
        for timelist in sideItems:
            timelist.registerDate = reDateType(timelist.uDate)
        context={
            "memNo" : memNo,
            "dtos" : dtos,
            "sideItems" : sideItems,
            }
        return HttpResponse(template.render(context, request))
    def post(self, request):
        pass
    
class LogoutView(TemplateView):
    def get(self, request):
        request.session['memNo'] = None
        request.session.modified = True
        return redirect("uniMain")
    def post(self, request):
        pass

class RewardView(TemplateView):
    def get(self, request):
        pass
    @csrf_exempt
    def post(self, request):
        reward = request.POST["reward"]
        logger.info("reward : "+str(reward))
        return HttpResponse(reward)
        
class CatView(TemplateView):
    def get(self, request):
        pass
    @csrf_exempt
    def post(self, request):
        cat_filter = request.POST["cat_filter"]
        return HttpResponse(cat_filter)
    
class SearchView(TemplateView):
    def get(self, request):
        pass
    @csrf_exempt
    def post(self, request):
        
        # Ajax 통신
        jsonobj = json.loads(request.body)
        search_ward = jsonobj.get("search_ward")
        search_reward = jsonobj.get("search_reward")
        search_cat = jsonobj.get("search_cat")
        logger.info("search_ward :" +str(search_ward))
        logger.info("search_reward :" +str(search_reward))
        logger.info("search_cat :" +str(search_cat))
        
        if search_cat != "전체":
            ca_catNo = Category.objects.filter(catName = search_cat).values("catNo")
        else:
            ca_catNo = "a"
        logger.info("ca_catNo:" +str(ca_catNo[0]))

        if ca_catNo == "a":
            
            if search_reward == "제목":
                aItem = Item.objects.filter(title__contains= search_ward).order_by("readCnt").values("title")[0:4]
                
            elif search_reward == "제목+내용":
                aItem = Item.objects.filter(Q(title__contains= search_ward)|Q(info__contains=search_ward)).order_by("readCnt").values("title","info")[0:4]
                
            else:
                aItem = Member.objects.filter(nickname__contains=search_ward).order_by("rGrade")[0:4].values("nickname")
                
        elif ca_catNo != "a":
            
            if search_reward == "제목":
                aItem = Item.objects.filter(title__contains= search_ward,catNo=ca_catNo[0]["catNo"]).order_by("readCnt").values("title")[0:4]
                
            else :
                aItem = Item.objects.filter(Q(title__contains= search_ward)|Q(info__contains=search_ward),catNo=ca_catNo[0]["catNo"]).order_by("readCnt").values("title","info")[0:4]
                
        
        logger.info("aItems :" +str(aItem))
        
        kt = []
        R =""
        RQ =""
        for i in aItem:
            if search_reward == "제목":
                oktR = okt.phrases(i["title"])
                for R in oktR:
                    if search_ward in R and len(search_ward) < len(R) :
                        kt.append(R)
            elif search_reward == "제목+내용":
                oktR = okt.phrases(i["title"])
                for R in oktR:
                    if search_ward in R and len(search_ward) < len(R) :
                        kt.append(R)
                oktRQ = okt.phrases(i["info"])
                for RQ in oktRQ:
                    if search_ward in RQ and len(search_ward) < len(RQ) and RQ not in kt :
                        kt.append(RQ)
            else:
                oktR = okt.phrases(i["nickname"])
                for R in oktR:
                    if search_ward in R and len(search_ward) < len(R) :
                        kt.append(R)
        
        kt.sort()
        del kt[4:]
        logger.info("kt :" +str(kt))

        
        context = {
            "search_ward" : search_ward,
            "kt" : kt,
            }
        return HttpResponse(json.dumps(context), content_type="application/json")
    





    
    
    
    
    
    
    