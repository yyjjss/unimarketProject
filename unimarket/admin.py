from django.contrib import admin

from unimarket.models import Category, Satisfaction, ChatRoom
from unimarket.models import ChatInfo
from unimarket.models import FAQ
from unimarket.models import Item
from unimarket.models import Like
from unimarket.models import Mark
from unimarket.models import Member
from unimarket.models import Notice
from unimarket.models import Report
from unimarket.models import SearchLog
from unimarket.models import StayLog
from unimarket.models import ReviewScore


class CategoryAdmin(admin.ModelAdmin):
    list_display = ("catNo", "catName", "catLogo")


admin.site.register(Category, CategoryAdmin)


class MemberAdmin(admin.ModelAdmin):
    list_display = (
        "memNo",
        "email",
        "nickname",
        "passwd",
        "bDate",
        "loc",
        "zonecode",
        "gender",
        "marrStat",
        "proImg",
        "report",
        "rGrade",
        "reportCnt",
        "memStat",
        "reviewCnt",
    )


admin.site.register(Member, MemberAdmin)


class LikeAdmin(admin.ModelAdmin):
    list_display = ("indexNo", "memNo", "itemNo", "price")


admin.site.register(Like, LikeAdmin)


class ItemAdmin(admin.ModelAdmin):
    list_display = (
        "itemNo",
        "title",
        "catNo",
        "memNo",
        "loc",
        "zonecode",
        "price",
        "info",
        "uDate",
        "readCnt",
        "likeCnt",
        "itemImg",
        "sellStat",
        "sellDate",
        "buyMemNo",
        "SatisfactionAvg",
        "reviewed",
    )


admin.site.register(Item, ItemAdmin), ""


class ChatRoomAdmin(admin.ModelAdmin):
    list_display = (
        "chatNo",
        "sellMemNo",
        "buyMemNo",
        "itemNo",
        "title",
        "itemImg",
        "sendTime",
    )


admin.site.register(ChatRoom, ChatRoomAdmin)


class ChatInfoAdmin(admin.ModelAdmin):
    list_display = (
        "chatNo",
        "itemNo",
        "sellMemNo",
        "buyMemNo",
        "fromSender",
        "chatContent",
        "chatRead",
        "endTime",
    )


admin.site.register(ChatInfo, ChatInfoAdmin)


class ReportAdmin(admin.ModelAdmin):
    list_display = (
        "indexNo",
        "reportFrom",
        "reportTo",
        "reportContent",
        "reportDate",
        "itemNo",
    )


admin.site.register(Report, ReportAdmin)


class MarkAdmin(admin.ModelAdmin):
    list_display = (
        "indexNo",
        "markNo",
        "memNo",
        "markStat",
        "markContent",
        "markDate",
        "markRead",
    )


admin.site.register(Mark, MarkAdmin)


class NoticeAdmin(admin.ModelAdmin):
    list_display = (
        "indexNo",
        "noticeNo",
        "noticeTitle",
        "noticeContent",
        "eventImg",
        "noticeDate",
    )


admin.site.register(Notice, NoticeAdmin)


class SearchLogAdmin(admin.ModelAdmin):
    list_display = ("indexNo", "memNo", "searchKey", "loc", "zonecode", "searchDate")


admin.site.register(SearchLog, SearchLogAdmin)


class StayLogAdmin(admin.ModelAdmin):
    list_display = (
        "indexNo",
        "memNo",
        "itemNo",
        "connectDate",
        "stayCnt",
        "stayTime",
        "stayFlg",
    )


admin.site.register(StayLog, StayLogAdmin)


class FAQAdmin(admin.ModelAdmin):
    list_display = ("indexNo", "questions", "answer")


admin.site.register(FAQ, FAQAdmin)


class SatisfactionAdmin(admin.ModelAdmin):
    list_display = ("indexNo", "itemNo", "memNo", "satisfactionScore")


admin.site.register(Satisfaction, SatisfactionAdmin)


class ReviewScoreAdmin(admin.ModelAdmin):
    list_display = (
        "indexNo",
        "memNo",
        "buyMemNo",
        "description",
        "condition",
        "priceScore",
        "attitude",
        "distance",
    )


admin.site.register(ReviewScore, ReviewScoreAdmin)
