from django.urls import re_path

from . import consumers

websocket_urlpatterns = [
    # re_path(r'ws/uniChatRoomInfo?(?P<room_name>\w+)$', consumers.ChatConsumer()),
    re_path(r'ws/uniChatRoomInfo?(?P<room_name>\w+)$', consumers.ChatConsumer.as_asgi()),
    # re_path(r'ws/uniChatRoomInfo?(?P<room_name>[^/]+)$', consumers.ChatConsumer()),
    # re_path(r'ws/uniAlarm?(?P<username>\w+)$', consumers.AlarmConsumer()),
    re_path(r'ws/uniBase', consumers.AlarmConsumer().as_asgi()),
    #re_path(r'ws/chat/(?P<room_name>\w+)/$', consumers.ChatConsumer()),
    #re_path(r'ws/chat/(?P<room_name>\w+)/$', consumers.ChatConsumer.as_asgi()),
]