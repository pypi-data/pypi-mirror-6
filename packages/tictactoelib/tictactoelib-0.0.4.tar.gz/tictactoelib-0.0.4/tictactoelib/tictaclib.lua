local T = {}

local shallow_copy = function(tbl)
    local new_tbl = {}
    for k, v in pairs(tbl) do
        new_tbl[k] = v
    end
    return new_tbl
end

local env = {
    print=print, -- disable on prod

    tostring=tostring, unpack=unpack, next=next, assert=assert,
    tonumber=tonumber, pairs=pairs, pcall=pcall, type=type, select=select,
    ipairs=ipairs, _VERSION=_VERSION, error=error,

    math=shallow_copy(math), table=shallow_copy(table)
}

local get_user_function_file = function(filename)
    if _VERSION:find("5.1$") then
        local user_function = assert(loadfile(filename))
        setfenv(user_function, env)
        return user_function
    elseif _VERSION:find("5.2$") then
        return assert(loadfile(filename, nil, 't', env))
    else
        error("Lua 5.1 or 5.2 required")
    end
end

local get_user_function_string = function(string)
    if _VERSION:find("5.1$") then
        local user_function = assert(loadstring(string))
        setfenv(user_function, env)
        return user_function
    elseif _VERSION:find("5.2$") then
        return assert(load(string, nil, 't', env))
    else
        error("Lua 5.1 or 5.2 required")
    end
end

local function run(user_function)
    local err, fun = assert(pcall(user_function))
    assert(err and type(fun) == "function", "bad function")
    return fun
end

T.runfile = function(filename) return run(get_user_function_file(filename)) end
T.runstring = function(string) return run(get_user_function_string(string)) end

T.StringBuffer = function()
    local ret = {}
    local bfr_mt = {
        __concat = function(self, x) table.insert(self, x); return self end,
        __tostring = function(self) return table.concat(self, "") end
    }
    setmetatable(ret, bfr_mt)
    return ret
end

return T
