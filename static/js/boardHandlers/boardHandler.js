// boardHandler.js

var currentBoard = 0;

function handleBoard(data) {
    currentBoard = data.data.current_id

    $("#boardTabs").empty()
    for (let index = 0; index < data.data.boards.length; index++) {
        const board = data.data.boards[index];

        var color = "btn-primary"
        if (index == currentBoard)
        {
            color = "btn-danger"
        }

        $("#boardTabs").append(`<button id=bt${index} type="button" class="btn ${color}">${board.name}</button>`)
        $(`#bt${index}`).on('click', () => {
            boardSocket.send(JSON.stringify({
                type: "board.change",
                data: {
                    new_id: index
                }
            }))
        })
    }
}
