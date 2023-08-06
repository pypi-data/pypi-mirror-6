#!/usr/bin/env lua
extra_path = (arg[0]:sub(0, arg[0]:len() - string.len("run.lua")))
package.path = package.path .. ";" .. extra_path .. "?.lua"

local main_server = function(...)
    require("ui_server")(...)
end

local main_interactive = function(...)
    require("ui_interactive")(...)
end

if arg and arg[0]:find("run.lua$") then
    if arg[1] == "--server" then
        main_server()
    elseif #arg ~= 2 then
        io.stderr:write("Usage: " .. arg[0] .. " player1.lua player2.lua\n")
        io.stderr:write("       " .. arg[0] .. " --server\n")
        os.exit(1)
    else
        main_interactive(arg[1], arg[2])
    end
else
    return {main_server, main_interactive}
end
