// historyHandler.js

var currentHistoryIndex = []

function clearPGN()
{
    $("#history").empty()
}

function addPGNmove(index, txt, on)
{
    const newSpan = $(`<span class="fw-bold p-2">${index} ${txt}</span>`);

    if (on && typeof on === 'function') {
        newSpan.on('click', on);
    }

    $("#history").append(newSpan);
}

function addPGNcomment(txt, cld="secondary")
{
    var typ = cld === "secondary" ? "span" : "h3"
    const newSpan = $(`<${typ} class="text-${cld}">${txt}</${typ}>`);
    $("#history").append(newSpan);
}

function get_moveIndex(index)
{
    var tmp = 0;
    index.forEach(element => {
        tmp += 0.5
    });
    return tmp + tmp % 1
}

function get_moveTxt(index, orientation)
{
    if (index[index.length-2] != 0 && index[index.length-1] == 0)
    {
        return `${get_moveIndex(index)}... `
    }
    if (orientation == "black")
    {
        return ""
    }
    return `${get_moveIndex(index)}. `
}

function handleHistoryOnce(history, index)
{
  addPGNmove(get_moveTxt(index, history.orientation), history.txt, () => {
    socketReturn(index)
  })
  if (JSON.stringify(index) == JSON.stringify(currentHistoryIndex))
  {
    last_server_position = history.fen
    chessboard.position(history.fen)
  }
  if (history.main)
  {
    addPGNcomment(history.main.comment)
  }
  for (let i = 0; i < history.variants.length; i++) {
    addPGNcomment("(", "danger")
    handleHistoryOnce(history.variants[i], index.concat([i+1]))
    addPGNcomment(")", "danger")
  }
  if (history.main)
  {
    handleHistoryOnce(history.main, index.concat([0]))
  }
}

function handleHistory(data) {
    clearPGN()
    currentHistoryIndex = data.data.current_index;
    for (let i = 0; i < data.data.history.length; i++) {
        handleHistoryOnce(data.data.history[i], [i])
    }
}
