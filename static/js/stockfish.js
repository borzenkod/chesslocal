// stockfish.js

var stockfishWhite = null
var stockfishBlack = null

function createStockfish(wasmSupported) {
  stockfishWhite = new Worker(wasmSupported ? '/static/stockfish.wasm.js' : "/static/stockfish.js");
  stockfishBlack = new Worker(wasmSupported ? '/static/stockfish.wasm.js' : "/static/stockfish.js");
  
  
  stockfishWhite.addEventListener('message', function (e) {
    let data = e.data.split(" ")
    if (data[0] == "info")
    {
      var pvi = data.findIndex((e) => e == "pv")
      aacStockfishWhite(data[pvi+1].substring(0, 2), data[pvi+1].substring(2, 4))

      var scorei = data.findIndex((e) => e == "score")
      if (data[scorei + 1] == "cp")
        $("#scoreWhite").text(data[scorei + 2]/100)
      if (data[scorei + 1] == "mate")
        $("#scoreWhite").text("#" + data[scorei + 2])
      if (data[scorei + 1] == "lowerbound")
        $("#scoreWhite").text("-Inf")
      if (data[scorei + 1] == "upperbound")
        $("#scoreWhite").text("+Inf")
    }
  });

  stockfishWhite.postMessage('uci');
  stockfishWhite.postMessage('ucinewgame');


  stockfishBlack.addEventListener('message', function (e) {
    let data = e.data.split(" ")
    if (data[0] == "info")
    {
      var pvi = data.findIndex((e) => e == "pv")
      aacStockfishBlack(data[pvi+1].substring(0, 2), data[pvi+1].substring(2, 4))

      var scorei = data.findIndex((e) => e == "score")
      if (data[scorei + 1] == "cp")
        $("#scoreBlack").text(data[scorei + 2]/100)
      if (data[scorei + 1] == "mate")
        $("#scoreBlack").text("#" + data[scorei + 2])
      if (data[scorei + 1] == "lowerbound")
        $("#scoreBlack").text("-Inf")
      if (data[scorei + 1] == "upperbound")
      $("#scoreBlack").text("+Inf")
    }
  });

  stockfishBlack.postMessage('uci');
  stockfishBlack.postMessage('ucinewgame');
}

function updateStockfishWhite()
{
  stockfishWhite.postMessage(`stop`)
  stockfishWhite.postMessage(`position fen ${chessboard.fen()} w`)
  stockfishWhite.postMessage(`go depth 20`)
}

function updateStockfishBlack()
{
  stockfishBlack.postMessage(`stop`)
  stockfishBlack.postMessage(`position fen ${chessboard.fen()} b`)
  stockfishBlack.postMessage(`go depth 20`)
}

function updateStockfish()
{
  if (!doesStockfishEnabled()) {
    aacStockfishWhite()
    aacStockfishBlack()
    return
  }
  updateStockfishWhite()
  updateStockfishBlack()
}

function doesStockfishEnabled()
{
  try {
    return $("#engine").parent().attr('class').split(" ").length != 4
  } catch {
    return false
  }
}

$('#engine').change(function() {
  updateStockfish()
})
