
var last_server_position = ""

function createBoardSocket(roomName) {
    const socket = new WebSocket(
        (location.protocol == 'http:' ? 'ws://' : 'wss://') +
        window.location.host +
        '/ws/room/' +
        roomName +
        '/'
    );

    socket.onopen = function () {
        console.log('WebSocket connection opened');
    };

    socket.onclose = function (event) {
        console.error('WebSocket connection closed:', event);
    };

    socket.onerror = function (error) {
        console.error('WebSocket error:', error);
    };

    return socket;
}

function socketPositionChanged(fen, txt, orientation)
{
    if (last_server_position == fen)
        return

    boardSocket.send(JSON.stringify({
        "type": "position.change",
        "data": {
            "fen": fen,
            "txt": txt,
            "orientation": orientation
        }
    }))
}

function socketCreateBoard(title, pgn=undefined)
{
    boardSocket.send(JSON.stringify({
        type: "board.create",
        data: {
            title,
            pgn
        }
    }))
}

function socketReturn(index)
{
    boardSocket.send(JSON.stringify({
        type: "history.return",
        data: {
            index
        }
    }))
}

function socketSendDelete()
{
    boardSocket.send(JSON.stringify({
        type: "board.delete",
        data: {
        }
    }))
}

function socketAACadd(start, color, end=undefined)
{
  boardSocket.send(JSON.stringify({
    type: "aac.add",
    data: {
      start, color, end
    }
  }))
}

function socketAACremove(start, end=undefined)
{
  boardSocket.send(JSON.stringify({
    type: "aac.remove",
    data: {
      start, end
    }
  }))
}

function socketAACdeleteAll()
{
  boardSocket.send(JSON.stringify({
    type: "aac.delete",
    data: {}
  }))
}
