--[[
Example player implementation with syntax errror (add string and int).
--]]

local function move(xo, board, row, col)
    return 1 + "badarg"
end

return move
