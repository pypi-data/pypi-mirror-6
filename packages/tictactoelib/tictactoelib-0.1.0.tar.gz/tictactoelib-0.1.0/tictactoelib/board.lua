local T = require("tictaclib")

local Board = {} -- 9x9 board
local SBoard = {} -- 3x3 board

SBoard.tostring = function(self)
    local ret = T.StringBuffer()
    for x = 1, 3 do
        for y = 1, 3 do
            ret = ret .. (self[x][y] == nil and "-" or self[x][y]) .. " "
        end
        ret = ret .. "\n"
    end
    return tostring(ret)
end

SBoard.new = function()
    local sboard = {
        {nil, nil, nil},
        {nil, nil, nil},
        {nil, nil, nil}
    }
    setmetatable(sboard, {__tostring=SBoard.tostring, __index=SBoard})
    return sboard
end


Board.tostring = function(self)
    local ret = T.StringBuffer()
    for y1 = 1, 3 do
        for y2 = 1, 3 do
            for x1 = 1, 3 do
                for x2 = 1, 3 do
                    local i = self[y1][x1][y2][x2]
                    ret = ret .. (i == nil and "-" or i) .. " "
                end
                ret = ret .. " "
            end
            ret = ret .. "\n"
        end
        ret = ret .. "\n"
    end
    return tostring(ret)
end

Board.new = function()
    local board = {
        {SBoard.new(), SBoard.new(), SBoard.new()},
        {SBoard.new(), SBoard.new(), SBoard.new()},
        {SBoard.new(), SBoard.new(), SBoard.new()}
    }
    setmetatable(board, {__tostring=Board.tostring, __index=Board})
    return board
end


Board.copy = function(self)
    local board = Board.new()
    for x1 = 1, 3 do
        for y1 = 1, 3 do
            for x2 = 1, 3 do
                for y2 = 1, 3 do
                    board[x1][y1][x2][y2] = self[x1][y1][x2][y2]
                end
            end
        end
    end
    return board
end

-- Check state of a 3x3 board. Possible return values:
-- "draw", "x", "o", nil (continue)
SBoard.state = function(self)
    local choices = { -- diagonals
        {self[1][1], self[2][2], self[3][3]}, -- \
        {self[1][3], self[2][2], self[3][1]}  -- /
    }
    for x = 1, 3 do
        table.insert(choices, {self[x][1], self[x][2], self[x][3]}) -- rows
        table.insert(choices, {self[1][x], self[2][x], self[3][x]}) -- cols
    end

    local draw = true
    for _, set in ipairs(choices) do
        local a, b, c = set[1], set[2], set[3]
        if a == b and b == c and b ~= nil then
            return b
        elseif a == nil or b == nil or c == nil then
            draw = false
        end
    end
    return draw and "draw" or nil
end

-- Check state of 9x9 board. Possible return values:
-- "draw", "x", "o", nil (continue)
Board.state = function(self)
    local sboard = SBoard.new()
    for x = 1, 3 do
        for y = 1, 3 do
            sboard[x][y] = SBoard.state(self[x][y])
        end
    end
    local state = SBoard.state(sboard)
    return state ~= nil and state or nil
end

return Board
