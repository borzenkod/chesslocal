from django.http import HttpResponse
from . import models
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.core import serializers
import random
import chess.pgn
import io


# Create your views here.
def home(req):
    return render(req, "home.html")


def board(request, room_name):
    return render(request, "board.html", {"room_name": room_name})


def generateRandomId():
    return f'{"".join([random.choice("AaBbCcDdEeFfGgHhIiJjKkLlMmNnOoPpQqRrSsTtUuVvWwXxYyZz1234567890_"[:]) for _ in range(4)])}'


def getRandomIdThatNotInDataBase():
    result = False
    while not result:
        id = generateRandomId()
        if models.Room.objects.filter(room_uid=id).__len__() == 0:
            return id

@login_required
def get_all_rooms_fen(req):
    boards = models.Board.objects.all()
    return HttpResponse(serializers.serialize('json', boards), content_type="text/json-comment-filtered")


def create(request):
    if "roomId" in request.GET:
        return redirect("room", request.GET["roomId"])
    if not request.user.is_authenticated:
        return render(request, "create.html")
    if "m" in request.GET:
        # Create board
        id = getRandomRoomIdThatNotInDataBase()
        board = models.Board()
        board.room_name = id
        board.save()
        return redirect("room", id)
    elif "timeOptions" in request.GET:
        # Create game
        # time = request.GET["gameTime"]
        # add = request.GET["timePerMove"]
        id = getRandomRoomIdThatNotInDataBase()
        return redirect("room", id)
    elif "pgn" in request.GET:
        id = getRandomRoomIdThatNotInDataBase()

        # read pgn
        board = models.Board()
        board.room_name = id

        game = chess.pgn.read_game(io.StringIO(request.GET["pgn"]))
        chessboard = game.board()
        for move in game.mainline_moves():
            chessboard.push(move)
            board.add_child(chessboard.fen(), move.uci(), "white" if chessboard.turn == chess.WHITE else "black")

        board.save()
        return redirect("room", id)
    return render(request, "create.html")


def boards(req):
    boards = models.Board.objects.all()
    return render(req, "boards.html", {"boards": boards})

def rooms(req):
    rooms = models.Room.objects.all()
    return render(req, "rooms.html", {"rooms": rooms})

def create_room(req):
    room = models.Room()
    room.room_uid = getRandomIdThatNotInDataBase()
    room.save()
    return redirect("room", room.room_uid)
