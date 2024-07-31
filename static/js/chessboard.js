// chessboard.js

var chessboard;

function createChessboard() {
    var board;
    var txt = "";
    var orientation = ""
    var stopDrag = false
    var placing_piece = null

    function updateBoardView() {
        function swapOs()
        {
            var topCnt = $("#boardTop").html()
            var bottomCnt = $("#boardBottom").html()
            $("#boardTop").html(bottomCnt)
            $("#boardBottom").html(topCnt)

            $("#ooW").click(() => {
                var pos = board.getPosition('object')
                if (pos.e1 == "wK" && !pos.f1 && !pos.g1 && pos.h1 == "wR")
                {
                    delete pos.e1
                    delete pos.h1
                    pos.g1 = "wK"
                    pos.f1 = "wR"
                    txt = "0-0"
                    orientation = "white"
                    board.position(pos)
                }
            })
            $("#oooW").click(() => {
                var pos = board.getPosition('object')
                if (pos.e1 == "wK" && !pos.d1 && !pos.c1 && !pos.b1 && pos.a1 == "wR")
                {
                    delete pos.e1
                    delete pos.a1
                    pos.c1 = "wK"
                    pos.d1 = "wR"
                    txt = "0-0-0"
                    orientation = "white"
                    board.position(pos)
                }
            })
            $("#ooB").click(() => {
                var pos = board.getPosition('object')
                if (pos.e8 == "bK" && !pos.f8 && !pos.g8 && pos.h8 == "bR")
                {
                    delete pos.e8
                    delete pos.h8
                    pos.g8 = "bK"
                    pos.f8 = "bR"
                    txt = "0-0"
                    orientation = "black"
                    board.position(pos)
                }
            })
            $("#oooB").click(() => {
                var pos = board.getPosition('object')
                if (pos.e8 == "bK" && !pos.d8 && !pos.c8 && !pos.b8 && pos.a8 == "bR")
                {
                    delete pos.e8
                    delete pos.a8
                    pos.c8 = "bK"
                    pos.d8 = "bR"
                    txt = "0-0-0"
                    orientation = "black"
                    board.position(pos)
                }
            })
        }

        const boardOrientation = board.orientation();
        if (boardOrientation == "white")
        {
            if($("#boardTop").attr('black') === undefined && $("boardBottom").attr('white') === undefined)
            {
                swapOs()
                $("#boardTop").removeAttr('white').attr('black', '')
                $("#boardBottom").removeAttr('black').attr('white', '')
            }
        }
        if (boardOrientation == "black")
        {
            if($("#boardTop").attr('white') === undefined && $("boardBottom").attr('black') === undefined)
            {
                swapOs()
                $("#boardTop").removeAttr('black').attr('white', '')
                $("#boardBottom").removeAttr('white').attr('black', '')
            }
        }

        $('#board').children().on("contextmenu",function(){
            return false;   
        });
        $('[data-square-coord="a1"]').empty().append(`<p>a</p>`)
        $('[data-square-coord="b1"]').empty().append(`<p>b</p>`)
        $('[data-square-coord="c1"]').empty().append(`<p>c</p>`)
        $('[data-square-coord="d1"]').empty().append(`<p>d</p>`)
        $('[data-square-coord="e1"]').empty().append(`<p>e</p>`)
        $('[data-square-coord="f1"]').empty().append(`<p>f</p>`)
        $('[data-square-coord="g1"]').empty().append(`<p>g</p>`)
        $('[data-square-coord="h1"]').empty().append(`<div class="position-relative top-0 start-0"><p class="position-absolute">h</p><p class="position-absolute top-0 end-0">1</p></div>`)
        $('[data-square-coord="h2"]').empty().append(`<p>2</p>`)
        $('[data-square-coord="h3"]').empty().append(`<p>3</p>`)
        $('[data-square-coord="h4"]').empty().append(`<p>4</p>`)
        $('[data-square-coord="h5"]').empty().append(`<p>5</p>`)
        $('[data-square-coord="h6"]').empty().append(`<p>6</p>`)
        $('[data-square-coord="h7"]').empty().append(`<p>7</p>`)
        $('[data-square-coord="h8"]').empty().append(`<p>8</p>`)
    }

    function onChange(oldPosition, newPosition) {
        socketPositionChanged(board.fen(), txt, orientation)

        updateBoardView();
        updateStockfish()
    }

    function logMouseenterSquare(evt, domEvt) {
        if (domEvt.buttons == 2)
          aacUpdate(evt.square)
    }

    function updateIng (piece) {
      placing_piece = piece
    }

    function setFen(fen)
    {
      txt = "fen"
      if (orientation == "") 
        orientation = "white"
      else
        orientation = orientation == "white" ? "black" : "white"
      board.position(fen)
    }

    function logMousedownSquare(evt, domEvt)
    {
      if (domEvt.button == 2)
      { 
        stopDrag = true
        aacStart(evt.square)
        aacUpdate(evt.square)
      }
      else {
        if (placing_piece)
        {
          let position = board.getPosition()
          position[evt.square] = placing_piece;
          txt = `${placing_piece} add`
          orientation = /w+/.test(placing_piece) ? "white" : "black";
          board.position(position)
          placing_piece = null
        }
      }
    }

    function logMouseupSquare(evt, domEvt) 
    {
      if (domEvt.button == 2) 
      {
        aacEnd(evt.square)
        stopDrag = false
      }
    }


    function onDrop(source) {
      console.log(source)
      txt = `${source.source}${source.target}`
      orientation = /w/.test(source.piece) ? "white" : "black"
    }

    function onDragStart(evt) {
      return ! stopDrag      
    }

    function flipBoard() {
        board.flip();
        updateBoardView();
    }

    function startBoard() {
      txt = "start"
      if (orientation == "") 
        orientation = "white"
      else
        orientation = orientation == "white" ? "black" : "white"
      board.start();
    }

    function clearBoard() {
      txt = "clear"
      if (orientation == "") 
        orientation = "white"
      else
        orientation = orientation == "white" ? "black" : "white"
      board.clear();
    }

    function clearArrows() {
        board.clearArrows();
    }

    function clearCircles() {
        board.clearCircles();
    }

    board = Chessboard2('board', {
        draggable: true,
        pieceTheme: 'https://chessboardjs.com/img/chesspieces/alpha/{piece}.png',
        position: 'start',
        dropOffBoard: 'remove',
        onMouseupSquare: logMouseupSquare,
        onMousedownSquare: logMousedownSquare,
        onChange: onChange,
        onMouseenterSquare: logMouseenterSquare,
        onDragStart, onDrop
    });

    updateBoardView()

    chessboard = board

    return {
      board,
      flipBoard,
      startBoard,
      clearBoard,
      clearArrows,
      clearCircles,
      setFen,
      updateIng
    };
}
