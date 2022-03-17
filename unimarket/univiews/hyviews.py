from cmath import log
from genericpath import exists
from django.shortcuts import render, redirect
from django.template import loader
from django.views.generic.base import TemplateView, View
from django.http.response import HttpResponse, HttpResponseRedirect
from scipy import rand
from unimarket.models import Item, Member, Like, Category, ReviewScore, SearchLog, Mark
from datetime import datetime
from django.db.models import Q
from unimarket.forms import FileUploadForm
import random
import logging
from django.utils.dateformat import DateFormat
from _datetime import timezone, timedelta
import json
import requests
from decimal import Decimal
import pandas as pd

logger = logging.getLogger(__name__)

from django.views.decorators.csrf import csrf_exempt


# 아이템 리스트 화면
class CategoryView(TemplateView):
    @csrf_exempt
    def get(self, request):
        dtos = Item.objects.all().order_by("-uDate")
        template = loader.get_template("uniCategory.html")
        keyword_condition = request.GET.get("kwrd")
        cate_condition = request.GET.get("cat")
        order_condition = request.GET.get("order")
        sellStat = request.GET.get("sellStat")
        memNo = request.session.get("memNo")
        cat_filter = request.GET.get("cat_filter")
        reward = request.GET.get("reward")

        # 로그인 했으면
        if memNo != None:
            memobj = Member.objects.get(memNo=memNo)
            memzone = memobj.zonecode
            # 우편번호 구까지만 가져오기
            mzone = memzone[:3]
            dtos = Item.objects.filter(zonecode__startswith=mzone)
        else:
            pass

        # <h3> 제목에 표시할 내용
        name = "모든 게시글"

        PAGE_SIZE = 20
        PAGE_BLOCK = 10

        page = request.GET.get("page")
        if not page:
            page = "1"
        page = int(page)

        start = (page - 1) * int(PAGE_SIZE)
        end = start + int(PAGE_SIZE)

        count = 0
        # sellStat
        if sellStat == None:
            dtos = dtos
            count = dtos.count()
        else:
            dtos = dtos.filter(sellStat=0)
            count = dtos.count()

        if cate_condition == "None":
            dtos = dtos
            count = dtos.count()
            if end > count:
                end = count
        elif not cate_condition:
            dtos = dtos
            count = dtos.count()
            if end > count:
                end = count
        # name : <h3> 제목 표시할 부분 (카테고리 선택시)
        else:
            dtos = dtos.filter(catNo=cate_condition)
            count = dtos.count()
            cate = Category.objects.get(catNo=cate_condition)
            name = cate.catName
            if end > count:
                end = count

        if keyword_condition == "None":
            dtos = dtos
            count = dtos.count()
        elif not keyword_condition:
            dtos = dtos
            count = dtos.count()
        # 키워드 검색한 경우
        else:
            if memNo != None:
                stay = SearchLog(
                    memNo=memobj.memNo,
                    searchKey=keyword_condition,
                    loc=memobj.loc,
                    zonecode=memobj.zonecode,
                    searchDate=datetime.now(tz=timezone.utc),
                )
                stay.save()
            if reward == "제목":
                dtos = dtos.filter(title__contains=keyword_condition)
                count = dtos.count()
                name = "검색결과 : " + '"' + keyword_condition + '"'
            elif reward == "제목+내용":
                logger.info(reward)
                dtos = dtos.filter(
                    Q(title__contains=keyword_condition)
                    | Q(info__contains=keyword_condition)
                )
                logger.info(dtos)
                count = dtos.count()
                name = "검색결과 : " + '"' + keyword_condition + '"'
            else:
                memobj = Member.objects.get(nickname=keyword_condition)
                obj_No = memobj.memNo
                dtos = dtos.filter(memNo=obj_No)
                count = dtos.count()
                name = "검색결과 : " + '"' + keyword_condition + '"'
            if cat_filter:
                if cat_filter != "전체":
                    cat_obj = Category.objects.get(catName=cat_filter)
                    catNo = cat_obj.catNo
                    dtos = dtos.filter(catNo=catNo)
                    count = dtos.count()
                    name = "검색결과 : " + '"' + keyword_condition + '"'
                else:
                    dtos = dtos
                    count = dtos.count()
                    name = "검색결과 : " + '"' + keyword_condition + '"'
            else:
                dtos = dtos
                count = dtos.count()
                name = "검색결과 : " + '"' + keyword_condition + '"'

        if order_condition == "None":
            dtos = dtos[start:end]
        elif not order_condition:
            dtos = dtos[start:end]
        else:
            dtos = dtos.order_by(order_condition)[start:end]

        number = count - (page - 1) * int(PAGE_SIZE)

        startpage = page // PAGE_BLOCK * PAGE_BLOCK + 1
        if page % PAGE_BLOCK == 0:
            startpage -= PAGE_BLOCK

        endpage = startpage + PAGE_BLOCK - 1
        pagecount = count // PAGE_SIZE
        if count % PAGE_SIZE > 0:
            pagecount += 1
        if endpage > pagecount:
            endpage = pagecount
        pages = range(startpage, endpage + 1)

        # 아이템 밑에 시간표시하도록 reDate 함수 사용함
        for dto in dtos:
            uDate = dto.uDate
            logger.info("udate :" + str(uDate))
            time = reDateType(uDate)
            logger.info("time :" + str(time))
            dto.time = time

        context = {
            "cate_condition": cate_condition,
            "order_condition": order_condition,
            "keyword_condition": keyword_condition,
            "count": count,
            "dtos": dtos,
            "page": page,
            "number": number,
            "pages": pages,
            "pageblock": PAGE_BLOCK,
            "pagecount": pagecount,
            "startpage": startpage,
            "endpage": endpage,
            "name": name,
            "sellStat": sellStat,
            "memNo": memNo,
        }
        return HttpResponse(template.render(context, request))

    def post(self, request):
        jsonobj = json.loads(request.body)
        # json에서 itemNo 가져오기
        sellStat = jsonobj["sellStat"]
        if sellStat == "0":
            sellStat = 0
        else:
            sellStat = "all"
        context = {"sellStat": sellStat}
        return HttpResponse(json.dumps(context), content_type="application/json")


def create(request):
    return render(request, "uniProducts.html")


# 아이템 등록하는 화면
# @login_required
class ProductsView(TemplateView):
    def get(self, request):
        template = loader.get_template("uniProducts.html")
        memNo = request.session.get("memNo")
        context = {"memNo": memNo}
        return HttpResponse(template.render(context, request))

    def post(self, request):
        if request.FILES.get("file") is not None:
            memNo = request.session.get("memNo")
            last = Item.objects.all().order_by("-uDate")[0]
            lastno = last.itemNo
            lastnum = int(lastno[2:])
            memobj = Member.objects.get(memNo=memNo)
            num = lastnum + 1
            item = Item(
                itemNo=str("no") + str(num),
                title=request.POST.get("title"),
                catNo=request.POST.get("category"),
                memNo=request.session.get("memNo"),
                loc=memobj.loc,
                zonecode=memobj.zonecode,
                price=request.POST.get("price"),
                info=request.POST.get("info"),
                uDate=DateFormat(datetime.now()).format("Y-m-d H:i"),
                readCnt=0,
                likeCnt=0,
                itemImg=request.FILES["itemImg"],
                sellStat=0,
                buyMemNo=0,
            )
            item.save()
            return redirect("uniCategory")
        else:
            memNo = request.session.get("memNo")
            last = Item.objects.all().order_by("-uDate")[0]
            lastno = last.itemNo
            lastnum = int(lastno[2:])
            memobj = Member.objects.get(memNo=memNo)
            num = lastnum + 1
            item = Item(
                itemNo=str("no") + str(num),
                title=request.POST.get("title"),
                catNo=request.POST.get("category"),
                memNo=request.session.get("memNo"),
                loc=memobj.loc,
                zonecode=memobj.zonecode,
                price=request.POST.get("price"),
                info=request.POST.get("info"),
                uDate=DateFormat(datetime.now()).format("Y-m-d H:i"),
                readCnt=0,
                likeCnt=0,
                sellStat=0,
                buyMemNo=0,
            )
            item.save()
            return redirect("uniCategory")


# 아이템 수정하는거
# @login_required
class editPostView(TemplateView):
    @csrf_exempt
    def get(self, request):
        template = loader.get_template("uniProductsedit.html")
        memNo = request.session.get("memNo")
        itemNo = request.GET["itemNo"]
        dto = Item.objects.get(itemNo=itemNo)
        context = {
            "itemNo": itemNo,
            "dto": dto,
            "memNo": memNo,
        }
        return HttpResponse(template.render(context, request))

    @csrf_exempt
    def post(self, request):
        itemNo = request.POST["itemNo"]
        item = Item.objects.get(itemNo=itemNo)
        memNo = request.session.get("memNo", None)
        if request.method == "POST":
            form = FileUploadForm(request.POST, request.FILES, instance=Item)
            itemNo = request.POST["itemNo"]
            item = Item.objects.get(itemNo=itemNo)
            title = request.POST["title"]
            # 가격변동 알림을 위해 기존 저장된 금액을 변수에 저장
            originalPrice = item.price

            if request.FILES.get("itemImg") != None:
                itemImg = request.FILES["itemImg"]
            else:
                itemImg = item.itemImg
            catNo = request.POST["category"]
            price = request.POST["price"]
            info = request.POST["info"]

            item.title = title
            if request.FILES.get("itemImg") != None:
                item.itemImg = itemImg
            else:
                item.itemImg = itemImg
            item.catNo = catNo
            item.price = price
            item.info = info
            item.uDate = datetime.now(tz=timezone.utc)
            item.save()

            # 사용자의 찜한물건에 한여 가격변동 알림 등록
            if int(originalPrice) != int(price):
                markcontent = ""
                if int(originalPrice) > int(price):
                    reprice = int(originalPrice) - int(price)
                    # logger.info("reprice : "+str(reprice))
                    markcontent = (
                        "상품["
                        + str(item.title)
                        + "]의 가격이  "
                        + str(reprice)
                        + "원 내려갔습니다."
                    )
                elif int(originalPrice) < int(price):
                    reprice = int(price) - int(originalPrice)
                    # logger.info("reprice : "+str(reprice))
                    markcontent = (
                        "상품["
                        + str(item.title)
                        + "]의 가격이  "
                        + str(reprice)
                        + "원 올라갔습니다."
                    )
                # logger.info("itemNo : "+str(itemNo))
                dtoLike = Like.objects.filter(itemNo=itemNo)
                # logger.info("likecount : "+str(dtoLike.count()))
                for like in dtoLike:
                    dtoMark = Mark(
                        markNo="su" + str(itemNo),
                        memNo=like.memNo,
                        markStat=8,
                        markContent=markcontent,
                    )
                    dtoMark.save()

            return HttpResponseRedirect("uniSale")
        else:
            form = FileUploadForm(instance=Item)
            return render(request, "uniSale.html", {"form": form})


# 아이템 삭제하는거지롱
# @login_required
class DeleteView(TemplateView):
    @csrf_exempt
    def get(self, request):
        memNo = request.session.get("memNo")
        itemNo = request.GET["itemNo"]
        dtos = Item.objects.get(itemNo=itemNo)

        context = {
            "itemNo": itemNo,
            "memNo": memNo,
            "dtos": dtos,
        }
        return render(request, "uniDelete.html", context)

    def post(self, request):
        pass


# 삭제하기 누르면 삭제해줌
def delete(request):
    itemNo = request.GET["itemNo"]
    dto = Item.objects.get(itemNo=itemNo)
    dto.delete()
    return HttpResponseRedirect("uniSale")


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


# 찜 화면
# @login_required
class DibsView(TemplateView):
    def get(self, request):
        template = loader.get_template("uniDibs.html")
        memNo = request.session.get("memNo")
        likes = Like.objects.filter(memNo=memNo)

        for i, like in enumerate(likes):
            itemNo = like.itemNo
            item = Item.objects.get(itemNo=itemNo)
            title = item.title
            itemImg = item.itemImg
            sellStat = item.sellStat
            # logger.info("title : "+str(title))
            likes[i].title = title
            likes[i].itemImg = itemImg
            likes[i].sellStat = sellStat
            # logger.info("likes : "+str(likes[i].title))

        context = {"likes": likes, "memNo": memNo}
        return HttpResponse(template.render(context, request))

    def post(self, request):
        memNo = request.session.get("memNo")
        logger.info("memNo :" + str(memNo))
        # json 받아온거.
        jsonobj = json.loads(request.body)
        # json에서 itemNo 가져오기
        itemNo = jsonobj["itemNo"]
        # logger.info("itemNo :"+str(itemNo))
        item = Item.objects.get(itemNo=itemNo)
        # logger.info("item :"+str(item))
        price = item.price

        # 좋아요 이미 되어있으면 좋아요 삭제하고 저장
        if Like.objects.filter(memNo=memNo, itemNo=itemNo).exists():
            Like.objects.filter(memNo=memNo, itemNo=itemNo).delete()
            item.likeCnt -= 1
            item.save()
            context = {"message": "좋아요 취소", "likeck": "0", "itemNo": itemNo}
        # 좋아요 없으면 좋아요 만들고 저장
        else:
            like = Like(memNo=memNo, itemNo=itemNo, price=price)
            like.save()
            item.likeCnt += 1
            item.save()
            context = {"message": "좋아요", "likeck": "1", "itemNo": itemNo}

        return HttpResponse(json.dumps(context), content_type="application/json")


# 내가 구매한 목록 보여줌
# @login_required
class PurchaseView(TemplateView):
    def get(self, request):
        template = loader.get_template("uniPurchase.html")
        memNo = request.session.get("memNo")

        PAGE_SIZE = 5
        PAGE_BLOCK = 10

        page = request.GET.get("page")
        if not page:
            page = "1"
        page = int(page)

        count = Item.objects.filter(buyMemNo=memNo).count()
        start = (page - 1) * int(PAGE_SIZE)
        end = start + int(PAGE_SIZE)
        if end > count:
            end = count

        dtos = Item.objects.filter(buyMemNo=memNo).order_by("-uDate")[start:end]
        number = count - (page - 1) * int(PAGE_SIZE)

        startpage = page // PAGE_BLOCK * PAGE_BLOCK + 1
        if page % PAGE_BLOCK == 0:
            startpage -= PAGE_BLOCK

        endpage = startpage + PAGE_BLOCK - 1
        pagecount = count // PAGE_SIZE
        if count % PAGE_SIZE > 0:
            pagecount += 1
        if endpage > pagecount:
            endpage = pagecount

        pages = range(startpage, endpage + 1)

        context = {
            "count": count,
            "dtos": dtos,
            "page": page,
            "number": number,
            "pages": pages,
            "pageblock": PAGE_BLOCK,
            "pagecount": pagecount,
            "startpage": startpage,
            "endpage": endpage,
            "memNo": memNo,
        }
        return HttpResponse(template.render(context, request))

    def post(self, request):
        pass


# 내가 올린 아이템 페이지
# @login_required
class SaleView(TemplateView):
    def get(self, request):
        template = loader.get_template("uniSale.html")
        memNo = request.session.get("memNo")
        count = Item.objects.filter(memNo=memNo).count()
        alC = request.GET.get("alC", None)
        if alC != None:
            readMark = Mark.objects.get(markNo=alC)
            readMark.markRead = 1
            # logger.info("delMark : "+str(readMark))
            readMark.save()

        PAGE_SIZE = 5
        PAGE_BLOCK = 10

        page = request.GET.get("page")
        if not page:
            page = "1"
        page = int(page)

        start = (page - 1) * int(PAGE_SIZE)
        end = start + int(PAGE_SIZE)
        if end > count:
            end = count

        # 판매중, 판매완료인 아이템 모두 가져오기
        dtos = Item.objects.filter(memNo=memNo).order_by("-uDate")[start:end]
        number = count - (page - 1) * int(PAGE_SIZE)

        startpage = page // PAGE_BLOCK * PAGE_BLOCK + 1
        if page % PAGE_BLOCK == 0:
            startpage -= PAGE_BLOCK

        endpage = startpage + PAGE_BLOCK - 1
        pagecount = count // PAGE_SIZE
        if count % PAGE_SIZE > 0:
            pagecount += 1
        if endpage > pagecount:
            endpage = pagecount

        pages = range(startpage, endpage + 1)

        context = {
            "count": count,
            "dtos": dtos,
            "page": page,
            "number": number,
            "pages": pages,
            "pageblock": PAGE_BLOCK,
            "pagecount": pagecount,
            "startpage": startpage,
            "endpage": endpage,
            "memNo": memNo,
        }
        return HttpResponse(template.render(context, request))

    def post(self, request):
        # json 가져오기
        jsonobj = json.loads(request.body)
        # logger.info(str(jsonobj))
        # json 중에 itemNo 가져오기
        itemNo = jsonobj["itemNo"]
        # logger.info(str(itemNo))
        item = Item.objects.get(itemNo=itemNo)
        # logger.info(str(item))

        # sellStat을 1로 해서 판매완료로 저장
        item.sellStat = 1
        item.save()
        context = {"itemNo": itemNo}
        return HttpResponse(json.dumps(context), content_type="application/json")


# 페이지 번호 생성
def pageList(pageNum, seller, stat):
    PAGE_SIZE = 20
    PAGE_BLOCK = 10

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


# 거래 판매자에 대한 만족도 조사 테이블 업데이트
# @login_required
# class ReviewView(TemplateView):
#     @csrf_exempt
#     def get(self, request):
#         template = loader.get_template("uniReview.html")
#         memNo = request.session.get("memNo")
#         itemNo = request.GET["itemNo"]
#         context = {"itemNo": itemNo, "memNo": memNo}
#         return HttpResponse(template.render(context, request))

#     @csrf_exempt
#     def post(self, request):
#         template = loader.get_template("uniReview.html")
#         jsonobj = json.loads(request.body)\
#         score = int(jsonobj["check"])
#         itemNo = jsonobj["itemNo"]
#         item = Item.objects.get(itemNo=itemNo)
#         memNo = item.memNo
#         member = Member.objects.get(memNo=memNo)
#         totalscore = float(member.rGrade)
#         count = member.reviewCnt
#         if count == 0:
#             member.rGrade = Decimal(score)
#         else:
#             member.rGrade = Decimal((totalscore * count + score) / (count + 1))

#         member.reviewCnt += 1
#         member.save()
#         item.reviewed = 1
#         item.save()

#         context = {"score": score}
#         return HttpResponse(json.dumps(context), content_type="application/json")


# 구매 후 리뷰하기
class ReviewView(TemplateView):
    @csrf_exempt
    def get(self, request):
        template = loader.get_template("uniReview.html")
        memNo = request.session.get("memNo")
        itemNo = request.GET["itemNo"]
        dto = Item.objects.get(itemNo=itemNo)
        sellMemNo = dto.memNo
        sellmem = Member.objects.get(memNo=sellMemNo)
        buymem = Member.objects.get(memNo=memNo)
        context = {
            "itemNo": itemNo,
            "sellmem": sellmem,
            "buymem": buymem,
        }
        return HttpResponse(template.render(context, request))

    @csrf_exempt
    def post(self, request):
        buymemNo = request.session.get("memNo")
        jsonobj = json.loads(request.body)
        itemNo = jsonobj["itemNo"]
        reviewlist = jsonobj["list"]
        score = int(jsonobj["selectElementsCnt"])
        item = Item.objects.get(itemNo=itemNo)
        sellmemNo = item.memNo
        sellmember = Member.objects.get(memNo=sellmemNo)
        totalscore = float(sellmember.rGrade)
        count = sellmember.reviewCnt
        if count == 0:
            sellmember.rGrade = Decimal(score)
        else:
            sellmember.rGrade = Decimal((totalscore * count + score) / (count + 1))

        sellmember.reviewCnt += 1
        sellmember.save()
        item.reviewed = 1
        item.save()

        if "1" in reviewlist:
            description = 1
        else:
            description = 0
        if "2" in reviewlist:
            condition = 1
        else:
            condition = 0
        if "3" in reviewlist:
            price = 1
        else:
            price = 0
        if "4" in reviewlist:
            attitude = 1
        else:
            attitude = 0
        if "5" in reviewlist:
            distance = 1
        else:
            distance = 0

        score = ReviewScore(
            memNo=sellmemNo,
            buyMemNo=buymemNo,
            description=description,
            condition=condition,
            priceScore=price,
            attitude=attitude,
            distance=distance,
        )
        score.save()

        context = {"itemNo": itemNo}
        return HttpResponse(json.dumps(context), content_type="application/json")
