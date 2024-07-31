from django.urls import re_path

from . import consumers

websocket_urlpatterns = [
    re_path(r"ws/room/(?P<room_uid>\w+)/$", consumers.RoomConsumer.as_asgi()),
]
