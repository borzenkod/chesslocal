from django.urls import path
from . import views

urlpatterns = [
    path("", views.home, name="home"),
    path("room/<str:room_name>/", views.board, name="room"),
    path("create", views.create, name="create"),
    path("boards", views.boards, name="boards"),
    path("rooms", views.rooms, name="rooms"),
    path("api/boards", views.get_all_rooms_fen),
    path("createRoom", views.create_room)
]
