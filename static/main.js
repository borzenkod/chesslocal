// main.js
const wasmSupported = typeof WebAssembly === 'object' && WebAssembly.validate(Uint8Array.of(0x0, 0x61, 0x73, 0x6d, 0x01, 0x00, 0x00, 0x00));
const stockfish = createStockfish(wasmSupported);
const roomName = JSON.parse(document.getElementById('room-name').textContent);
const boardSocket = createBoardSocket(roomName);
const { _, flipBoard, startBoard, clearBoard, clearArrows, clearCircles, setFen, updateIng } = createChessboard();

// Your other client-side logic goes here

boardSocket.onmessage = function (e) {

    const data = JSON.parse(e.data);
    console.log(data)


    switch (data.type.split('.')[0]) {
        case 'board':
            handleBoard(data);
            break;
        case 'history':
            handleHistory(data);
            break;
        case 'aac':
            handleAAC(data);
            break;
        default:
            // Handle unknown type
    }
};

boardSocket.onclose = function (e) {
    console.error('Socket closed unexpectedly', e);
};

$("#createNewStart").on("click", () => {
    socketCreateBoard($("#newBoardName").val())
})

$("#newFen").on("click", () => {
    socketCreateBoard($("#newBoardName").val(), $("#newPgn").val())
    
})

$("#sendRemove").on("click", () => {
    socketSendDelete()
})

$("#startPos").on("click", () => {
  startBoard()  
})

$("#clearBoard").on("click", () => {
  clearBoard()
})

$("#clearArrows").on("click", () => {
  aacClear()
})

$("#setFEN").on("click", () => {
  setFen($("#fen").val())
})


$("#addP").click(() => {
  updateIng('wP');
})
$("#addR").click(() => {
  updateIng('wR');
})
$("#addN").click(() => {
  updateIng('wN');
})
$("#addB").click(() => {
  updateIng('wB');
})
$("#addQ").click(() => {
  updateIng('wQ');
})
$("#addK").click(() => {
  updateIng('wK');
})


$("#addPb").click(() => {
  updateIng('bP');
})
$("#addRb").click(() => {
  updateIng('bR');
})
$("#addNb").click(() => {
  updateIng('bN');
})
$("#addBb").click(() => {
  updateIng('bB');
})
$("#addQb").click(() => {
  updateIng('bQ');
})
$("#addKb").click(() => {
  updateIng('bK');
})

$("#flipBoard").on('click', () => {
  flipBoard()
})
