from django.urls.conf import path
from chat import views
from unimarket.univiews import hyviews, mtviews

urlpatterns = [
    path("chatSendContent", views.ChatSendContentView.as_view(), name="chatSendContent"),
    path("uniSearchMap", views.TemplateView.as_view(template_name="uniSearchMap.html")),
    path("uniChatRoomInfo", views.ChatRoomInfoView.as_view() , name="uniChatRoomInfo"),
    #path("chatRoomSearch", views.ChatRoomSearchView.as_view() , name="chatRoomSearch"),
    path("uniSale", hyviews.SaleView.as_view(), name="uniSale"),
    path("uniBase", mtviews.BaseView.as_view(), name="uniBase"),
    # path("uniAlarm", views.AlarmView.as_view() , name="uniAlarm"),
    # path("uniShareMe", views.ShareMeView.as_view() , name="uniShareMe"),
    
]
        