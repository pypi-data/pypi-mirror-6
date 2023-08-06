local T = {}

local shallow_copy = function(tbl)
    local new_tbl = {}
    for k, v in pairs(tbl) do
        new_tbl[k] = v
    end
    return new_tbl
end

local env = {
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

local function saferun(loader, loader_arg)
    -- returns lambda, user's function caller.
    --
    -- first call returns a lambda, the user's function.
    -- result intended to be called with pcall.
    local user_fun = nil
    local maybe_load_fun_and_call = function(...)
        if user_fun == nil then
            user_fun = loader(loader_arg)
        end
        return user_fun()(...)
    end
    return maybe_load_fun_and_call
end

T.runfile = function(filename)
    return saferun(get_user_function_file, filename)
end

T.runstring = function(string)
    return saferun(get_user_function_string, string)
end

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
