from django.conf import settings
from django.core.mail import EmailMessage
from django.template.loader import render_to_string
from django.contrib.auth.models import auth, User
from django.contrib import messages
from django.contrib.sites.shortcuts import get_current_site
from unimarket.authToken import member_activation_token
from django.utils.http import urlsafe_base64_decode, urlsafe_base64_encode
from django.utils.encoding import force_str, force_bytes
from django.shortcuts import render, redirect
from django.views.generic.base import TemplateView
from django.http.response import HttpResponse, HttpResponseRedirect
from django.template import loader
from django.utils.dateformat import DateFormat
from datetime import datetime
from unimarket.models import Member, Notice, Item, Mark, StayLog
from django.views.decorators.csrf import csrf_exempt
from django.core.exceptions import ObjectDoesNotExist
from pip._vendor.distro import id
from django.db.models.query_utils import Q
from datetime import datetime
import requests
import json
from unimarket.univiews.hyviews import reDateType

from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from unimarket.forms import CustomUserChangeForm

import logging
from django.contrib.auth.views import PasswordResetView

logger = logging.getLogger(__name__)


class LoginView(TemplateView):
    def get(self, request):
        template = loader.get_template("uniLogin.html")
        memNo = request.session.get("memNo", None)
        context = {
            "memNo": memNo,
            "recaptcha_site_key": settings.V3_SITE_KEY,
        }
        return HttpResponse(template.render(context, request))

    def post(self, request):
        form = "context"
        if form.is_valid():

            recaptcha_response = request.POST.get("login-form")
            data = {"secret": settings.V3_SECRET_KEY, "response": recaptcha_response}
            r = requests.post(
                "https://www.google.com/recaptcha/api/siteverify", data=data
            )
            result = r.json()

            print(result)


class RegisterView(TemplateView):
    @csrf_exempt
    def get(self, request):
        pass

    def post(self, request):
        if request.method == "POST":
            dto = Member(
                memNo=request.session.get("memNo", None),
                email=request.POST["email"],
                passwd=request.POST["passwd"],
                nickname=request.POST["nickname"],
                # bDate = DateFormat(datetime.now()).format("Y-m-d"),
                bDate=request.POST["bDate"],
                gender=request.POST["gender"],
                marrStat=request.POST["marrStat"],
                proImg=request.POST["proImg"],
                loc=request.POST.get("location"),
                zonecode=request.POST["zonecode"],
                # report = request.POST["report"],
                # rGrade = request.POST["rGrade"],
                # reportCnt = request.POST["reportCnt"],
                # memStat = request.POST["memStat"],
            )
            dto.is_active = False
            dto.save()
            mydict = {"email": dto.email}
            # return redirect("uniMain") # 이메일 인증 이전 회원가입 완료 direct root

            current_site = get_current_site(request)
            message = render_to_string(
                "uniConfirm.html",
                {
                    "dto": dto.email,
                    "domain": current_site.domain,
                    "uid": urlsafe_base64_encode(force_bytes(dto.pk)).encode().decode(),
                    "token": member_activation_token,
                },
            )
            mail_subject = "[유니마켓] 회원가입 인증 메일입니다."
            email_from = settings.EMAIL_HOST_USER
            user_email = dto.email
            email_message = EmailMessage(mail_subject, message, to=[user_email])
            email_message.send()
            return HttpResponse(
                '<div style="font-size: 40px; width: 100%; height:100%; display:flex; text-align:center; '
                'justify-content: center; align-items: center;">'
                "입력하신 이메일로 인증 링크가 전송되었습니다."
                "</div>"
            )
            return redirect("uniConfirm")
        else:
            return render(request, "uniRegister.html")


class EmailchkView(TemplateView):
    @csrf_exempt
    def get(self, request):
        template = loader.get_template("uniEmailChk.html")
        memNo = request.session.get("memNo", None)
        user_email = request.GET.get("user_email", None)
        result = request.GET.get("result", 0)
        context = {
            "result": result,
            "user_email": user_email,
        }
        return HttpResponse(template.render(context, request))

    def post(self, request):
        memNo = request.session.get("memNo", None)
        user_email = request.POST.get("user_email", None)
        result = Member.objects.filter(email=user_email).count()
        if result == 0:
            result = "0"
        else:
            result = "1"
        return HttpResponse(
            "uniEmailChk?result=" + result + "&user_email=" + user_email
        )


class LoginMainView(TemplateView):
    @csrf_exempt
    def get(self, request):
        memNo = request.session.get("memNo", None)

        # 사이드바 데이터 오래머문시간, 최신순 정렬
        srcItem = StayLog.objects.filter(memNo=memNo).order_by("stayCnt")
        sideItem = Item.objects.none()
        for i in srcItem:
            sideItem |= Item.objects.filter(itemNo=i.itemNo)

        sideItems = sideItem.order_by("-uDate")[0:4]
        # 시간 함수
        for timelist in sideItems:
            timelist.registerDate = reDateType(timelist.uDate)

        # 이벤트 배너 출력을 위한 Notice 정보
        Event = Notice.objects.filter(noticeNo__contains="ev").order_by("-indexNo")
        dto = Member.objects.get(memNo=memNo)
        zonecode = dto.zonecode[:3]
        recntItem = Item.objects.filter(zonecode__startswith=zonecode).order_by(
            "-readCnt", "-uDate"
        )[0:8]
        newItem = Item.objects.filter(zonecode__startswith=zonecode).order_by("-uDate")[
            0:8
        ]
        # 시간 함수
        for timelist in newItem:
            timelist.registerDate = reDateType(timelist.uDate)
        for item in recntItem:
            item.registerDate = reDateType(item.uDate)

        # 해당 사용자에게 안내해야 될 알람(찜상품 가격변동, 판매완료) 데이터 추출
        # dtoMark = Mark.objects.filter(Q(memNo=dto.memNo)&Q(markStat=7)|Q(markStat=8))
        dtoMark7Cnt = Mark.objects.filter(
            Q(memNo=memNo) & Q(markStat=7) & ~Q(markRead=1)
        ).count()
        dtoMark7 = list(
            Mark.objects.filter(Q(memNo=memNo) & Q(markStat=7) & ~Q(markRead=1)).values(
                "markContent"
            )
        )
        logger.info("dtoMark7: " + str(dtoMark7))
        dtoMark8Cnt = Mark.objects.filter(
            Q(memNo=memNo) & Q(markStat=8) & ~Q(markRead=1)
        ).count()
        dtoMark8 = list(
            Mark.objects.filter(Q(memNo=memNo) & Q(markStat=8) & ~Q(markRead=1)).values(
                "markContent"
            )
        )
        logger.info("dtoMark8: " + str(dtoMark8))

        # 사용자가 가장 오래 머문 페이지 데이터
        stayPle = (
            StayLog.objects.filter(memNo=memNo).order_by("stayCnt").values("itemNo")
        )
        logger.info("stayPle: " + str(stayPle))
        if not stayPle:
            stayItem = None
            logger.info("stayItem: " + str(stayItem))
        else:
            stayItem = Item.objects.get(itemNo=stayPle[0]["itemNo"])

        template = loader.get_template("uniMain.html")

        if request.COOKIES.get("popup") is None:
            context = {
                "memNo": memNo,
                "dto": dto,
                "Event": Event,
                "recntItem": recntItem,
                "newItem": newItem,
                "dtoMark7Cnt": dtoMark7Cnt,
                "dtoMark7": dtoMark7,
                "dtoMark8Cnt": dtoMark8Cnt,
                "dtoMark8": dtoMark8,
                "maintype": "alarm",
                "sideItems": sideItems,
                "stayItem": stayItem,
            }
        else:
            context = {
                "memNo": memNo,
                "dto": dto,
                "Event": Event,
                "recntItem": recntItem,
                "newItem": newItem,
                "dtoMark7Cnt": dtoMark7Cnt,
                "dtoMark7": dtoMark7,
                "dtoMark8Cnt": dtoMark8Cnt,
                "dtoMark8": dtoMark8,
                "maintype": "alarm",
                "sideItems": sideItems,
            }

        return HttpResponse(template.render(context, request))

    def post(self, request):
        pass


class LoginproView(TemplateView):
    @csrf_exempt
    def get(self, request):
        pass

    def post(self, request):
        memNo = request.session.get("memNo", None)
        email = request.POST["email"]
        passwd = request.POST["passwd"]
        template = loader.get_template("uniLogin.html")
        try:
            dto = Member.objects.get(email=email)
            if passwd == dto.passwd:

                request.session["memNo"] = dto.memNo
                context = {
                    "memNo": request.session.get("memNo", None),
                }
                return redirect("loginMain")
            else:
                message = "입력하신 비밀번호가 다릅니다."
                # 로그인 실패
        except ObjectDoesNotExist:
            message = "입력하신 아이디가 없습니다."
        context = {"message": message}
        return HttpResponse(template.render(context, request))


class UpdateproView(TemplateView):
    @csrf_exempt
    def get(self, request):
        template = loader.get_template("uniUpdatepro.html")
        memNo = request.session.get("memNo", None)
        dto = Member.objects.get(memNo=memNo)
        context = {
            "dto": dto,
            "memNo": memNo,
        }
        return HttpResponse(template.render(context, request))

    def post(self, request):
        memNo = request.session.get("memNo", None)
        dto = Member.objects.get(memNo=memNo)
        dto.email = request.POST["email"]
        dto.passwd = request.POST["passwd"]
        dto.nickname = request.POST["nickname"]
        dto.bDate = request.POST["bDate"]
        dto.loc = request.POST["location"]
        dto.zonecode = request.POST["zonecode"]
        dto.save()
        return HttpResponseRedirect("uniMypage")


class UpdateView(TemplateView):
    @csrf_exempt
    def get(self, request):
        template = loader.get_template("uniUpdate.html")
        memNo = request.session.get("memNo", None)
        delck = request.GET.get("delck", 0)
        context = {
            "delck": delck,
            "memNo": memNo,
        }
        return HttpResponse(template.render(context, request))

    def post(self, request):
        memNo = request.session.get("memNo", None)
        passwd = request.POST["passwd"]
        delck = request.POST["delck"]
        dto = Member.objects.get(memNo=memNo)
        if passwd == dto.passwd:
            template = loader.get_template("uniUpdatepro.html")
            if delck == "1":
                dto.delete()
                request.session.clear()
                return redirect("uniMain")
            else:
                context = {
                    "dto": dto,
                    "memNo": memNo,
                }
                return HttpResponse(template.render(context, request))
        else:
            template = loader.get_template("uniUpdate.html")
            message = "입력하신 비밀번호가 다릅니다."
            context = {"message": message}
            return HttpResponse(template.render(context, request))


def activate(request, uid64, token):
    try:
        uid = force_str(urlsafe_base64_decode(uid64))
        dto = Member.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, dto.DoesNotExist):
        dto = None
    if dto is not None and member_activation_token.check_token(dto, token):
        dto.is_active = True
        dto.save()
        auth.login(request, dto)
        return redirect("uniLogin")
    else:
        return redirect("uniLogin")


class PasswordResetMailView(TemplateView):
    @csrf_exempt
    def get(self, request):
        pass

    def post(self, request):
        if request.method == "POST":
            email = request.POST["email"]
            request.session["email"] = email

            dto = Member.objects.get(email=email)
            dto.is_active = False

            current_site = get_current_site(request)
            message = render_to_string(
                "password_reset_complete.html",
                {
                    "dto": dto.email,
                    "domain": current_site.domain,
                    "uid": urlsafe_base64_encode(force_bytes(dto.pk)).encode().decode(),
                    "token": member_activation_token,
                },
            )
            mail_subject = "[유니마켓] 비밀번호 초기화 설정 메일입니다."
            email_from = settings.EMAIL_HOST_USER
            user_email = dto.email
            email_message = EmailMessage(mail_subject, message, to=[user_email])
            email_message.send()
            return HttpResponse(
                '<div style="font-size: 40px; width: 100%; height:100%; display:flex; text-align:center; '
                'justify-content: center; align-items: center;">'
                "입력하신 이메일로 비밀번호 초기화 링크가 전송되었습니다."
                "</div>"
            )
            return redirect("password_reset_form")
        else:
            return render(request, "password_reset.html")


def activatePassword(request, uid64, token):
    try:
        uid = force_str(urlsafe_base64_decode(uid64))
        dto = Member.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, dto.DoesNotExist):
        dto = None
    if dto is not None and member_activation_token.check_token(dto, token):
        dto.is_active = True
        return redirect("password_resetForm")
    else:
        dto.is_active = True
        return redirect("password_resetForm")


class UpdatePasswordView(TemplateView):
    @csrf_exempt
    def get(self, request):
        pass

    def post(self, request):
        email = request.session.get("email")
        passwd = request.POST["passwd"]

        dtoMember = Member.objects.get(email=email)
        dtoMember.passwd = passwd
        dtoMember.save()
        request.session.clear()
        return redirect("uniLogin")


class PasswordResetForm(TemplateView):
    def get(self, request):
        return render(request, "password_resetForm.html")

    def post(self, request):
        pass
