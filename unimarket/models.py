from django.db import models
from decimal import Decimal


class Category(models.Model):
    catNo = models.CharField(verbose_name="카테고리번호", primary_key=True, max_length=10)
    catName = models.CharField(verbose_name="카테고리명", max_length=50, null=False)
    catLogo = models.CharField(verbose_name="카테고리로고", max_length=20, null=True)


class Member(models.Model):
    memNo = models.AutoField(verbose_name="회원번호", primary_key=True)
    email = models.EmailField(max_length=50, verbose_name="이메일", null=False)
    nickname = models.CharField(verbose_name="닉네임", max_length=20, null=False)
    passwd = models.CharField(max_length=30, verbose_name="비밀번호", null=False)
    bDate = models.DateTimeField(verbose_name="생년월일", null=False)
    loc = models.CharField(verbose_name="지역", max_length=80, null=False)
    zonecode = models.CharField(verbose_name="우편번호", max_length=10, default=0)
    gender = models.IntegerField(verbose_name="성별")
    marrStat = models.IntegerField(verbose_name="결혼유무")
    proImg = models.ImageField(
        verbose_name="프로필아이콘", null=True, blank=True, upload_to="pro/%Y/%m/%d"
    )
    report = models.IntegerField(verbose_name="신고받은유무", default=0)
    rGrade = models.DecimalField(
        verbose_name="별점평균", max_digits=2, decimal_places=1, default=Decimal("0.0")
    )
    reportCnt = models.IntegerField(verbose_name="신고받은횟수", default=0)
    memStat = models.IntegerField(verbose_name="회원상태", default=1)
    reviewCnt = models.IntegerField(verbose_name="리뷰받은횟수", default=0)
    is_active = models.BooleanField(default=False)
    # created_at = models.DateTimeField(auto_now_add=True)
    # updated_at = models.DateTimeField(auto_now=True)

    # class Meta:
    # db_table = 'members'


class Like(models.Model):
    indexNo = models.AutoField(primary_key=True, verbose_name="찜번호")
    memNo = models.IntegerField(verbose_name="회원번호", null=False)
    itemNo = models.CharField(verbose_name="상품번호", max_length=10, null=False)
    price = models.IntegerField(verbose_name="가격", null=False)


class Item(models.Model):
    itemNo = models.CharField(
        verbose_name="상품번호", max_length=10, primary_key=True, null=False
    )
    title = models.CharField(verbose_name="제목", max_length=200, null=False)
    catNo = models.CharField(verbose_name="카테고리번호", max_length=10, null=False)
    memNo = models.IntegerField(verbose_name="회원번호", null=False)
    loc = models.CharField(verbose_name="지역", max_length=80, null=False)
    zonecode = models.CharField(verbose_name="우편번호", max_length=10, default=0)
    price = models.IntegerField(verbose_name="가격", null=False)
    info = models.TextField(verbose_name="상품설명", max_length=2000, null=False)
    uDate = models.DateTimeField(auto_now_add=True, verbose_name="업로드일", null=False)
    readCnt = models.IntegerField(verbose_name="조회수", default=0)
    likeCnt = models.IntegerField(verbose_name="찜수", default=0)
    itemImg = models.ImageField(
        verbose_name="상품이미지", null=True, blank=True, upload_to="item/%Y/%m/%d"
    )
    sellStat = models.IntegerField(verbose_name="판매완료유무", default=0)
    sellDate = models.DateTimeField(verbose_name="판매완료일", null=True, blank=True)
    buyMemNo = models.IntegerField(verbose_name="구매자", default=0)
    SatisfactionAvg = models.DecimalField(
        verbose_name="추천상품만족도평균", max_digits=2, decimal_places=1, default=Decimal("0.0")
    )
    reviewed = models.IntegerField(verbose_name="리뷰완료상태", default=0)


class ChatRoom(models.Model):
    chatNo = models.CharField(
        verbose_name="챗번호", primary_key=True, max_length=20, null=False
    )
    sellMemNo = models.IntegerField(verbose_name="판매자회원번호", null=True)
    buyMemNo = models.IntegerField(verbose_name="거래자회원번호", null=True)
    itemNo = models.CharField(verbose_name="상품번호", max_length=10, default="")
    title = models.CharField(verbose_name="제목", max_length=200, default="")
    itemImg = models.ImageField(
        verbose_name="상품이미지", null=True, upload_to="item/%Y/%m/%d"
    )
    sendTime = models.DateTimeField(auto_now_add=True, verbose_name="보낸일시")


# class Chat(models.Model):
# chatNo = models.CharField(verbose_name="챗번호", primary_key=True, max_length=20, null=False)
# sellMemNo = models.IntegerField(verbose_name="판매자회원번호", null=True)
# buyMemNo = models.IntegerField(verbose_name="거래자회원번호", null=True)
# endMessage = models.TextField(max_length=2000, verbose_name="마지막챗", null=False)
# endSender = models.IntegerField(verbose_name="마지막보낸사람회원번호", null=True)
# chatRead = models.IntegerField(verbose_name="읽음여부", default=0)
# endTime = models.DateTimeField(auto_now_add=True, verbose_name="마지막보낸일시", null=False)


class ChatInfo(models.Model):
    chatNo = models.CharField(verbose_name="챗번호", max_length=20)
    itemNo = models.CharField(verbose_name="상품번호", max_length=10)
    sellMemNo = models.IntegerField(verbose_name="판매자회원번호", default=0)
    buyMemNo = models.IntegerField(verbose_name="거래자회원번호", default=0)
    fromSender = models.IntegerField(verbose_name="보낸사람회원번호", default=0)
    chatContent = models.TextField(verbose_name="챗내용", max_length=2000)
    chatRead = models.IntegerField(verbose_name="읽음여부", default=0)
    endTime = models.DateTimeField(auto_now_add=True, verbose_name="보낸일시")


class Report(models.Model):
    indexNo = models.AutoField(primary_key=True, verbose_name="신고번호")
    reportFrom = models.IntegerField(verbose_name="신고자회원번호", null=False)
    reportTo = models.IntegerField(verbose_name="신고받은회원번호", null=False)
    reportContent = models.TextField(verbose_name="신고내용", max_length=2000, null=False)
    reportDate = models.DateTimeField(auto_now_add=True, verbose_name="신고일", null=False)
    itemNo = models.CharField(verbose_name="상품번호", max_length=10, null=False)


class Mark(models.Model):
    indexNo = models.AutoField(primary_key=True, verbose_name="인덱스번호")
    markNo = models.CharField(verbose_name="알림번호", max_length=20, null=False)
    memNo = models.IntegerField(verbose_name="회원번호", null=False)
    markStat = models.IntegerField(verbose_name="알림상태", default=0)
    markContent = models.CharField(verbose_name="알림문구", max_length=80, null=False)
    markDate = models.DateTimeField(auto_now_add=True, verbose_name="알림일", null=False)
    markRead = models.IntegerField(verbose_name="읽음여부", default=0)


class Notice(models.Model):
    indexNo = models.AutoField(primary_key=True, verbose_name="인덱스번호")
    noticeNo = models.CharField(verbose_name="공지번호", max_length=20, null=False)
    noticeTitle = models.CharField(verbose_name="공지제목", max_length=200, default="공지")
    noticeContent = models.TextField(verbose_name="공지내용", max_length=2000, null=False)
    eventImg = models.ImageField(
        verbose_name="이벤트이미지", upload_to="event/%Y/%m/%d", blank=True, null=True
    )
    noticeDate = models.DateTimeField(auto_now_add=True, verbose_name="등록일", null=False)


class SearchLog(models.Model):
    indexNo = models.AutoField(primary_key=True, verbose_name="인덱스번호")
    memNo = models.IntegerField(verbose_name="회원번호", null=False)
    searchKey = models.CharField(verbose_name="키워드", max_length=30, null=False)
    loc = models.CharField(verbose_name="지역", max_length=80, null=False)
    zonecode = models.CharField(verbose_name="우편번호", max_length=10, default=0)
    searchDate = models.DateTimeField(auto_now_add=True, verbose_name="검색일", null=False)


class StayLog(models.Model):
    indexNo = models.AutoField(primary_key=True, verbose_name="인덱스번호")
    memNo = models.IntegerField(verbose_name="회원번호", null=False)
    itemNo = models.CharField(verbose_name="상품번호", max_length=10, null=False)
    connectDate = models.DateTimeField(
        auto_now_add=True, verbose_name="접속시간", null=False
    )
    stayCnt = models.IntegerField(verbose_name="10분기준머문횟수", default=0)
    stayTime = models.IntegerField(verbose_name="실제머문시간", default=0)
    stayFlg = models.IntegerField(verbose_name="새로고침여부", default=0)


class FAQ(models.Model):
    indexNo = models.AutoField(primary_key=True, verbose_name="인덱스번호")
    questions = models.CharField(verbose_name="질문", max_length=100, null=False)
    answer = models.CharField(verbose_name="답변", max_length=500, null=False)


class Satisfaction(models.Model):
    indexNo = models.AutoField(primary_key=True, verbose_name="인덱스번호")
    itemNo = models.CharField(verbose_name="상품번호", max_length=10, null=False)
    memNo = models.IntegerField(verbose_name="회원번호", null=False)
    satisfactionScore = models.IntegerField(verbose_name="만족도점수", default=0)


class ReviewScore(models.Model):
    indexNo = models.AutoField(primary_key=True, verbose_name="인덱스번호")
    memNo = models.IntegerField(verbose_name="판매회원번호", null=False)
    buyMemNo = models.IntegerField(verbose_name="구매회원번호", null=False)
    description = models.IntegerField(verbose_name="설명점수", default=0)
    condition = models.IntegerField(verbose_name="상태점수", default=0)
    priceScore = models.IntegerField(verbose_name="가격점수", default=0)
    attitude = models.IntegerField(verbose_name="태도점수", default=0)
    distance = models.IntegerField(verbose_name="거리점수", default=0)


class PerfectUpdateday(models.Model):
    indexNo = models.AutoField(primary_key=True, verbose_name="인덱스번호")
    testday = models.DateField(verbose_name="검증한날", null=False)
    testresult = models.DecimalField(
        verbose_name="검증결과", null=False, max_digits=7, decimal_places=5
    )
