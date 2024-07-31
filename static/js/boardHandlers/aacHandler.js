// aacHandler.js


aac_starting_square = null
var aac_drawing_aoc = null
var aac_stockfish_white = null
var aac_stockfish_black = null

function handleAAC(data) {
  if (data.type == "aac.all")
  {
    chessboard.clearArrows()
    chessboard.clearCircles()

    data.data.aac.forEach(aoc => {
      if (aoc.end)
      {
        chessboard.addArrow({start: aoc.start, end:aoc.end, color:aoc.color})
      }
      else
      {
        chessboard.addCircle({square: aoc.start, color:aoc.color})
      }
    });
  }
}

function aacStockfishWhite(from, to)
{
  if (aac_stockfish_white)
  {
    chessboard.removeItem(aac_stockfish_white)
  }
  if (! doesStockfishEnabled()) 
    return
  aac_stockfish_white = chessboard.addArrow({
    start: from,
    end: to,
    color: 'white',
    size: 'small'
  })
}

function aacStockfishBlack(from, to)
{
  if (aac_stockfish_black)
  {
    chessboard.removeItem(aac_stockfish_black)
  }
  if (! doesStockfishEnabled()) 
    return
  aac_stockfish_black = chessboard.addArrow({
    start: from,
    end: to,
    color: 'black',
    size: 'small'
  })
}
function aacClear()
{
  aacReset()
  sockerAACdeleteAll()
}

function aacReset()
{
  aac_starting_square = null
  if (aac_drawing_aoc)
  {
    chessboard.removeItem(aac_drawing_aoc)
    aac_drawing_aoc = null
  }
}

aacReset()

function aocUpdateDrawing(sq)
{
  if (aac_drawing_aoc) {
    chessboard.removeItem(aac_drawing_aoc)
  }

  aac_drawing_aoc = chessboard.addArrow({start: aac_starting_square, end: sq, size: 'small'})
}

function aacStart(square)
{
  aac_starting_square = square
}

function aacUpdate(square)
{
  aocUpdateDrawing(square)
}

function aacEnd(square)
{
  aacAdd(square)
}

function chessboardHaveItem(start, end=undefined)
{
  items = chessboard.getItems()
  for (let i = 0; i < items.length; i++) {
    item = items[i]
    if (end)
    {
      if (item.start && (item.start == start && item.end == end))
      {
        return true
      }
    }
    else
    {
      if (item.square && item.square == start)
      {
        return true
      }
    }
  }
  return false
}

function aacAdd(end)
{
  let tmp = aac_starting_square
  if (end == tmp)
  {
    end = undefined
  }
  aacReset() 
  if (chessboardHaveItem(tmp, end))
  {
    socketAACremove(tmp, end)
  }
  else 
  {
    socketAACadd(tmp, "green", end)
  }
}
