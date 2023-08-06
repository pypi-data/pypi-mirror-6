--[[
-- msgpack-based non-interactive user interface
--
-- Input via stdin: <NN> [x code, o code]
-- Outputs via stdout: [ <NN> [ xo; moveresult; log ] ]
-- Where NN is two bytes of message size, most significant byte first.
-- xo, moveresult and log are explained in lib/play.lua
--
--]]

local T = require("tictaclib")
local mp = require("MessagePack")
local play = require("play")

local read_payload = function()
    local len_s = io.stdin:read(2)
    local len = len_s:byte(1) * 256 + len_s:byte(2)
    return io.stdin:read(len)
end

local write_payload = function(payload)
    local len = payload:len()
    local len_s = string.char(math.floor(len / 256), len % 256)
    io.stdout:write(len_s, payload)
    io.stdout:flush()
end

main = function()
    local code = mp.unpack(read_payload())
    local p1, p2 = T.runstring(code[1]), T.runstring(code[2])

    for xo, moveresult, log, board in play(p1, p2) do
        ret = mp.pack({xo, moveresult, log})
        write_payload(ret)
    end
end

return main
