import json
from pprint import pprint
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
import chess.pgn
import io
import traceback

import random
from .models import Room, Board
from web import models

def generateRandomRoomId():
    return f'{"".join([random.choice("AaBbCcDdEeFfGgHhIiJjKkLlMmNnOoPpQqRrSsTtUuVvWwXxYyZz1234567890_"[:]) for _ in range(8)])}'

@database_sync_to_async
def getRandomRoomIdThatNotInDataBase():
    result = False
    while not result:
        id = generateRandomRoomId()
        if models.Board.objects.filter(board_name=id).__len__() == 0:
            return id


class RoomConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.room_uid = self.scope['url_route']['kwargs']['room_uid']
        self.room_group_name = f"chess_room_{self.room_uid}"

        # Check if the room exists
        room_exists = await self.check_room_exists()

        if not room_exists:
            await self.close()
        else: 
            await self.channel_layer.group_add(
                self.room_group_name,
                self.channel_name
            )

            # Check if room have board (in case if it just created)
            _, blen = await self.get_room_boards()
            if blen == 0:
                await self.handle_board_creation({"data": {}}) # Creates empty board
            await self.accept()

            # Send initial data separately
            await self._send_board()
            await self._send_history()
            await self._send_arrows_and_circles()

    @database_sync_to_async
    def check_room_exists(self):
        return Room.objects.filter(room_uid=self.room_uid).exists()
    
    @database_sync_to_async
    def get_current_board(self):
        return (room := Room.objects.get(room_uid=self.room_uid)).boards.all()[room.current_board]

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

    async def _send_board(self):
        room: Room = await self.get_room_data()
        boards, _ = await self.get_room_boards()
        await self.send(json.dumps({
            'type': 'board.update',
            'data': {
                'current_id': room.current_board,
                'boards': [{"name": board.title} for board in list(boards)],
            }
        }))

    async def _send_history(self):
        current_board: Board = await self.get_current_board()
        await self.send(json.dumps({
            'type': 'history.update',
            'data': {
                'history': await current_board.get_json(),
                'current_index': current_board.current_index
            }
        }))

    async def _send_arrows_and_circles(self):
        current_board = await self.get_current_board()
        await self.send(json.dumps({
            'type': 'aac.all',
            'data': { 
                'aac': current_board.arrows_and_circles
            }
        }))

    @database_sync_to_async
    def get_room_data(self) -> Room:
        return Room.objects.get(room_uid=self.room_uid)
    
    @database_sync_to_async
    def get_room_boards(self):
        return (boards := Room.objects.get(room_uid=self.room_uid).boards.all()), len(boards)
    
    @database_sync_to_async
    def change_current_board_idx(self, idx):
        room = Room.objects.get(room_uid=self.room_uid)
        if idx == -1:
            idx = len(room.boards.all())-1 # Last
        room.current_board = idx
        room.save()

    @database_sync_to_async
    def add_board(self, board):
        room = Room.objects.get(room_uid=self.room_uid)
        room.boards.add(board)
        room.save()

    async def receive(self, text_data):
        data = json.loads(text_data)

        if "type" not in data:
            return 
        if "data" not in data:
            return

        if data["type"] == "board.change":
            # Some client change current board index
            await self.handle_board_change(data)
        if data["type"] == "board.create":
            await self.handle_board_creation(data)
        if data["type"] == "board.delete":
            await self.handle_board_deletion(data)

        if data["type"] == "position.change":
            await self.handle_position_changing(data)

        if data["type"] == "history.return":
            await self.handle_history_return(data)

        if data["type"] == "aac.add":                                          # Add specific
            await self.handle_aac_add(data)
        if data["type"] == "aac.remove":                                       # Remove specific
            await self.handle_aac_remove(data)
        if data["type"] == "aac.delete":                                       # Delete all
            await self.handle_aac_delete(data)

    async def handle_aac_delete(self, data):
        # Update aac
        board: Board = await self.get_current_board()        
        board.arrows_and_circles = []
        await board.asave()

        # Tell everyone
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                "type": "aac.update",
            }
        ) 

    async def handle_aac_remove(self, data):
        if "start" not in data["data"]:
            await self.send(json.dumps({
                "type": "error",
                "status": 2302,
                "message": "Start is not in request"
            }))
            return
        # Update aac
        board: Board = await self.get_current_board()        
        if "end" in data["data"]:
            await board.remove_aac(data["data"]["start"], data["data"]["end"])
        else:
            await board.remove_aac(data["data"]["start"])

        # Tell everyone
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                "type": "aac.update",
            }
        )

    async def handle_aac_add(self, data):
        if "color" not in data["data"]:
            await self.send(json.dumps({
                "type": "error",
                "status": 2300,
                "message": "Color is not in request"
            }))
            return
        if "start" not in data["data"]:
            await self.send(json.dumps({
                "type": "error",
                "status": 2301,
                "message": "Start is not in request"
            }))
            return


        # Update aac 
        board: Board = await self.get_current_board()        
        if "end" in data["data"]:
            await board.add_aac(data["data"]["color"], data["data"]["start"], data["data"]["end"])
        else:
            await board.add_aac(data["data"]["color"], data["data"]["start"])

        # Tell everyone
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                "type": "aac.update",
            }
        )

    async def handle_history_return(self, data):
        if "index" not in data["data"]:
            await self.send(json.dumps({
                "type": "error",
                "status": 2200,
                "message": "Index is not in request"
            }))
            return
        
        # Update history
        board: Board = await self.get_current_board()
        board.current_index = data["data"]["index"]
        await board.asave()
        # Tell everyone that history have been changed
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                "type": "history.update",
            }
        )

    async def handle_position_changing(self, data):
        # Check
        if "fen" not in data["data"]:
            await self.send(json.dumps({
                "type": "error",
                "status": 2100,
                "message": "Fen is not in request"
            }))
            return
        if "txt" not in data["data"]:
            await self.send(json.dumps({
                "type": "error",
                "status": 2101,
                "message": "txt is not in request"
            }))
            return
        if "orientation" not in data["data"]:
            await self.send(json.dumps({
                "type": "error",
                "status": 2102,
                "message": "orientation is not in request"
            }))
            return
        if data["data"]["orientation"] != "white" and data["data"]["orientation"] != "black":
            await self.send(json.dumps({
                "type": "error",
                "status": 2103,
                "message": "orientation is not valid"
            }))
            return

        # Change current board fen
        board: Board = await self.get_current_board()
        await board.add_variant(data["data"]["fen"], data["data"]["txt"], data["data"]["orientation"], "")
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                "type": "history.update",
            }
        )

    async def handle_board_deletion(self, data):
        room: Room = await self.get_room_data()
        board: Board = await  self.get_current_board()
        # Remove board from room
        await room.boards.aremove(board)
        # Delete board
        await board.adelete()
        # Save room
        await room.asave()
        # Check if we have another board
        _, blen = await self.get_room_boards()
        if blen != 0:
            # If yes:
            # Move everyone to new board
            await self.change_current_board_idx(-1)
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    "type": "board.update",
                }
            )
        else:
            # If no:
            # Create empty board
            await self.handle_board_creation({"type": "board.create", "data": {}})

    async def handle_board_creation(self, data):
        # Create board
        board = None
        board = models.Board()
        if "fen" in data["data"]:
            board.board_name = await getRandomRoomIdThatNotInDataBase()
            board.title = f"Board #{board.board_name}"
            board.add_variant(data["data"]["fen"], "from fen", "white", "")
            pass # Make fen board
        elif "pgn" in data["data"]:
            tree__ = ""
            lvl = 0
            async def add_move(board: Board, chessboard: chess.Board, node: chess.pgn.ChildNode, tree__, lvl):
                tree__ += f"{' '*lvl}|\n"
                chessboard.push(node.move)
                await board.add_variant(
                    chessboard.fen().split(" ")[0],
                    node.san(),
                    "white" if chessboard.turn == chess.BLACK else "black",
                    node.comment
                )
                tmp = board.current_index
                if len(node.variations) > 0:
                    lvl += 1
                    await add_move(board, chessboard, node[0], tree__, lvl)
                    lvl -= 1
                if len(node.variations) > 1:
                    for v in node.variations[1:]:
                        lvl += 1
                        await add_move(board, chessboard, v, tree__, lvl)
                        lvl -= 1
                board.pop()
                chessboard.pop()


            async def parse(board: Board, chessboard: chess.Board, game: chess.pgn.Game, tree__, lvl):
                await self.send("Starting parsing")
                nodes = game.mainline()
                await add_move(board, chessboard, nodes.start.variations[0], tree__, lvl)


            try:
                board.board_name = await getRandomRoomIdThatNotInDataBase()
                board.title = f"Board #{board.board_name}"
            
                game = chess.pgn.read_game(io.StringIO(data["data"]["pgn"]))
                chessboard = game.board()
                await board.init()
                await parse(board, chessboard, game, tree__, lvl)
                await self.send(tree__)
            except Exception as e:
                traceback.print_exc()
                await self.send(str(e))

            pass # Make board from fen
        else:
            board.board_name = await getRandomRoomIdThatNotInDataBase()
            board.title = f"Board #{board.board_name}"
            await board.init()
            pass # Make board with start position

        if "title" in data["data"] and len(data["data"]["title"]) > 2:
            board.title = data["data"]["title"]
        else:
            board.title = f"#{board.board_name}"
        # Add board to room
        await board.asave() 
        await self.add_board(board)

        # Move everyone to new board
        await self.change_current_board_idx(-1)
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                "type": "board.update",
            }
        )
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                "type": "history.update"   
            }
        )

    async def handle_board_change(self, data):
        # Perform checks
        if "data" not in data:
            await self.send(json.dumps({
                "type": "error",
                "stautus": 2000,
                "data": {
                    "message": "data is not presented"
                }
            }))
            return
        if "new_id" not in data['data']:
            await self.send(json.dumps({
                "type": "error",
                "stautus": 2001,
                "data": {
                    "message": "new_id is not presented"
                }
            }))
            return
        _, blen = await self.get_room_boards()
        if data['data']["new_id"] < 0 or data['data']["new_id"] > blen:
            await self.send(json.dumps({
                "type": "error",
                "stautus": 2002,
                "data": {
                    "message": "new_id is out of scope"
                }
            }))
            return
        
        idx = 0
        if isinstance(data['data']["new_id"], str):
            idx = int(data['data']["new_id"])
        else:
            idx = data['data']["new_id"]

        await self.change_current_board_idx(idx)
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                "type": "board.update",
            }
        )
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                "type": "history.update",
            }
        )
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                "type": "aac.update",
            }
        )

    async def board_update(self, event):
        await self._send_board()

    async def history_update(self, event):
        await self._send_history()

    async def aac_update(self, event):
        await self._send_arrows_and_circles()
