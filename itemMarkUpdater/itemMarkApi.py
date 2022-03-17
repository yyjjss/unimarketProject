from datetime import datetime, timezone, timedelta
import logging

from unimarket.models import Item, Mark, Notice

import fasttext
from konlpy.tag import Okt
from sklearn.model_selection._split import train_test_split

import numpy as np
import pandas as pd
from matplotlib import pyplot as plt
import seaborn as sns

logger = logging.getLogger(__name__)

# 자정마다 일주일 이상된 상품 정보확인하는 함수
def updateItemMark():
    # 현재날짜에서 일주일전
    sevenDay = datetime.now() - timedelta(weeks=1)
    logger.info("sevenDay : " + str(sevenDay))

    yesterday = datetime.now(tz=timezone.utc).date() - timedelta(days=1)
    # 공지(notice) 테이블에서 전날 등록된 공지가 유무 count
    nCount = Notice.objects.filter(noticeDate__gte=yesterday).count()
    if nCount > 0:  # 데이터 존재
        dtoNotice = Notice.objects.filter(noticeDate__gte=yesterday)
        for notice in dtoNotice:
            # 해당 공지에 대한 알림이 테이블에 존재하는지 확인
            markck = Mark.objects.filter(markNo=notice.noticeNo, memNo=0).count()
            if markck > 0:
                logger.info("존재하는 공지!")
                pass
            else:
                dtoMark = Mark(
                    markNo=notice.noticeNo,
                    memNo=0,
                    markStat=0,
                    markContent=notice.noticeTitle,
                )
                dtoMark.save()

    # 상품(Item) 테이블에서 현째로 부터 일주일 전 등록 상품 유무 count
    count = Item.objects.filter(uDate__lte=sevenDay).count()
    if count > 0:  # 데이터 존재
        # 상품(Item) 테이블에서 현째로 부터 일주일 전 등록 상품 추출
        dtoItem = Item.objects.filter(uDate__lte=sevenDay)
        # 일주일전 등록 상품에 대한 알림(Mark)테이블에 데이터 업로드
        for item in dtoItem:
            # 해당 상품에 대한 알림이 테이블에 존재하는지 확인
            markck = Mark.objects.filter(markNo=item.itemNo, memNo=item.memNo).count()
            if markck > 0:  # 이미 테이블에 존재할 경우
                markDck = Mark.objects.get(markNo=item.itemNo, memNo=item.memNo)
                reDate = datetime.now(tz=timezone.utc).date() - markDck.markDate.date()
                if reDate < timedelta(days=7):
                    logger.info("7일이하!")
                    pass
                else:
                    markDck.markRead = 0
                    markDck.markDate = datetime.now()
                    markDck.save()
            else:
                dtoMark = Mark(
                    markNo=item.itemNo,
                    memNo=item.memNo,
                    markStat=3,
                    markContent=item.title,
                )
                dtoMark.save()


def updateCategoryModel():
    dtoItem = Item.objects.all().values()
    df = pd.DataFrame(dtoItem)

    # 불용어 모음집
    # swdf = pd.read_table('http://itpaper.co.kr/data/korean_stopwords_100.txt', encoding='utf-8', sep='\s+', names=['불용어', '품사', '비율'])
    # print(swdf)
    # stopwords = list(swdf['불용어'])
    # print(stopwords)

    # 특수문자 제거 후 title 크기 확인
    df["title"] = df["title"].str.replace(
        "[-=+,#/\?:^$.@*\"※~&%ㆍ!』\\‘|\(\)\[\]\<\>`'…》]", "", regex=True
    )
    df["title"].replace("", np.nan, inplace=True)
    # print("data size: ", df["title"].shape)
    # 결측값 확인
    # print(df.isna().sum())

    df2 = pd.DataFrame(columns=["category", "title"])
    df2["title"] = df["title"]
    df2["category"] = "__label__" + df["catNo"]
    # print(df2)

    df2.to_csv("unimarket/static/modelfile/labelingtrain.txt", sep="\t", index=False)
    labeling = pd.read_csv("unimarket/static/modelfile/labelingtrain.txt", sep="\t")

    model = fasttext.train_supervised(
        "unimarket/static/modelfile/labelingtrain.txt",
        wordNgrams=2,
        epoch=500,
        lr=0.5,
        bucket=200000,
        dim=50,
        loss="ova",
    )
    model.save_model("unimarket/static/modelfile/model_cat.bin")


def updateCheckModel():
    df = pd.DataFrame(Item.objects.filter(sellStat=1))
    df.to_csv("df.csv", index=True)
    # gap_sec = []
    # for i in range(len(df)):
    #     delta1 = df["uDate"][i]
    #     delta2 = df["sellDate"][i]
    #     delta = delta2 - delta1
    #     gap_sec.append(delta.seconds)
    # sorted_gap_sec = gap_sec.sort()
    # diff = []
    # for i in range(0, len(sorted_gap_sec) - 1):
    #     diff.append(sorted_gap_sec[i + 1] - sorted_gap_sec[i])
    # df2 = pd.DataFrame(diff)
    # y = list(len(df2))
    # df2["index"] = y

    # sns.scatterplot(data=df2, x="x", y="gap")
    # plt.show()
