
local T = require("tictaclib")
local play = require("play")

local main = function(f1, f2)
    local p1, p2 = T.runfile(f1), T.runfile(f2)

    for xo, moveresult, log, board in play(p1, p2) do
        if moveresult[1] == "error" then
            print (xo .. " error: " .. moveresult[2])
        elseif moveresult[1] == "state_coords" then
            local places = table.concat(moveresult[2][2], "; ")
            local state = moveresult[2][1]
            print (xo .. " placed " .. "(" .. places .. ")")
            if state == "draw" then
                print ("draw")
            elseif state == "x" or state == "o" then
                print (state .. " won:")
                print (board)
            end
        end
    end
end

return main
