from django.urls.conf import path
from unimarket import views
from unimarket.univiews import mtviews
from unimarket.univiews import Hviews
from unimarket.univiews import hyviews
from django.views.generic.base import TemplateView
from django.conf.urls.static import static
from django.conf import settings

# 지환
from unimarket.univiews.Hviews import RegisterView, LoginView

# Activate
from django.contrib import admin

from django.urls import path
from chat import views as chatviews

# from django.contrib.auth import views as auth_views

urlpatterns = [
    # 민태 urls
    path("uniBase", mtviews.BaseView.as_view(), name="uniBase"),
    path("uniMain", mtviews.MainView.as_view(), name="uniMain"),
    path("uniNotice", mtviews.NoticeView.as_view(), name="uniNotice"),
    path("uniNoticetempt", mtviews.NoticetemptView.as_view(), name="uniNoticetempt"),
    path("uniEventtempt", mtviews.EventtemptView.as_view(), name="uniEventtempt"),
    path("uniFaq", mtviews.FaqView.as_view(), name="uniFaq"),
    path("uniLogout", mtviews.LogoutView.as_view(), name="uniLogout"),
    path("uniReward", mtviews.RewardView.as_view(), name="uniReward"),
    path("uniCat", mtviews.CatView.as_view(), name="uniCat"),
    # 검색어자동완성, 팝업 ajax url
    path("uniSearch", mtviews.SearchView.as_view(), name="uniSearch"),
    # 진상 urls
    path("uniChatInfo", views.ChatInfoView.as_view(), name="uniChatInfo"),
    path("updateChatInfo", views.UpdateChatInfoView.as_view(), name="updateChatInfo"),
    # path("uniSearchMap", views.TemplateView.as_view(template_name="uniSearchMap.html")),
    path("uniDetail", views.DetailView.as_view(), name="uniDetail"),
    path(
        "uniRecentreview",
        views.TemplateView.as_view(template_name="uniRecentreview.html"),
    ),
    path(
        "updateRecentreview",
        views.UpdateRecentreviewView.as_view(),
        name="updateRecentreview",
    ),
    path("updateLike", views.UpdateLikeView.as_view(), name="updateLike"),
    path("uniReport", views.TemplateView.as_view(template_name="uniReport.html")),
    path("updateReport", views.UpdateReportView.as_view(), name="updateReport"),
    path("uniSeller", views.SellerView.as_view(), name="uniSeller"),
    path("uniMypage", views.MypageView.as_view(), name="uniMypage"),
    path("uniAlarm", views.AlarmView.as_view(), name="uniAlarm"),
    path(
        "uniChatRoomInfo", chatviews.ChatRoomInfoView.as_view(), name="uniChatRoomInfo"
    ),
    path(
        "chatRoomSearch", chatviews.ChatRoomSearchView.as_view(), name="chatRoomSearch"
    ),
    # path("uniSearchMap", chatviews.TemplateView.as_view(template_name="uniSearchMap.html"),
    path("uniSearchMap", chatviews.UniSearchMapView.as_view(), name="uniSearchMap"),
    path(
        "updateBuyComplete",
        chatviews.UpdateBuyComplete.as_view(),
        name="updateBuyComplete",
    ),
    path(
        "updateCancleComplete",
        chatviews.UpdateCancleComplete.as_view(),
        name="updateCancleComplete",
    ),
    path("stayLogUpdate", views.StayLogUpdate.as_view(), name="stayLogUpdate"),
    path("loginMain", Hviews.LoginMainView.as_view(), name="loginMain"),
    path("titleck", views.TitleckView.as_view(), name="titleck"),
    # 지환 urls
    path("uniLogin", Hviews.LoginView.as_view(), name="uniLogin"),
    path("uniRegister", Hviews.TemplateView.as_view(template_name="uniRegister.html")),
    path("uniRegisterpro", Hviews.RegisterView.as_view(), name="uniRegisterpro"),
    path("uniConfirm", Hviews.TemplateView.as_view(template_name="uniConfirm.html")),
    # path("uniCongrats", Hviews.TemplateView.as_view(template_name="uniCongrats.html")),
    path("uniEmailChk", Hviews.EmailchkView.as_view(), name="uniEmailChk"),
    path("uniLoginpro", Hviews.LoginproView.as_view(), name="uniLoginpro"),
    path("uniUpdate", Hviews.UpdateView.as_view(), name="uniUpdate"),
    path("uniUpdatepro", Hviews.UpdateproView.as_view(), name="uniUpdatepro"),
    # 사용자에게 password 초기화 이메일 발송 화면
    path(
        "password_reset_mail",
        Hviews.TemplateView.as_view(template_name="password_reset_mail.html"),
    ),
    path(
        "password_mailSend",
        Hviews.PasswordResetMailView.as_view(),
        name="password_mailSend",
    ),
    path(
        "password_resetForm",
        Hviews.PasswordResetForm.as_view(),
        name="password_resetForm",
    ),
    path("updatePassword", Hviews.UpdatePasswordView.as_view(), name="updatePassword"),
    # path('password_reset/', auth_views.PasswordResetView.as_view(template_name="password_reset.html"), name="password_reset"),
    # path('password_reset_sent/', auth_views.PasswordResetDoneView.as_view(template_name="password_reset_sent.html"), name="password_reset_done"),
    # path('password_reset_confirm/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(template_name="password_reset_complete"), name="reset_password_confirm"),
    # path('password_reset_complete/', auth_views.PasswordResetCompleteView.as_view(template_name="password_reset_form.html"), name="password_reset_complete"),
    path(
        "activatePassword/<str:uid64>/<str:token>/",
        Hviews.activatePassword,
        name="activatePassword",
    ),
    path("activate/<str:uid64>/<str:token>/", Hviews.activate, name="activate"),
    # 현영 urls
    path("uniCategory", hyviews.CategoryView.as_view(), name="uniCategory"),
    path("create", hyviews.create, name="create"),
    path("uniProducts", hyviews.ProductsView.as_view(), name="uniProducts"),
    path("uniProductsedit", hyviews.editPostView.as_view(), name="uniProductsedit"),
    path("uniDelete", hyviews.DeleteView.as_view(), name="uniDelete"),
    path("delete", hyviews.delete, name="delete"),
    path("uniDibs", hyviews.DibsView.as_view(), name="uniDibs"),
    path("uniPurchase", hyviews.PurchaseView.as_view(), name="uniPurchase"),
    path("uniSale", hyviews.SaleView.as_view(), name="uniSale"),
    path("uniReview", hyviews.ReviewView.as_view(), name="uniReview"),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
