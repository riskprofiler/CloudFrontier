local coroutine = require "coroutine"
local datetime = require "datetime"
local formulas = require "formulas"
local math = require "math"
local nmap = require "nmap"
local outlib = require "outlib"
local stdnse = require "stdnse"
local table = require "table"

-- These scripts contribute clock skews, so we need them to run first.
-- portrule scripts do not always run before hostrule scripts, and certainly
-- not before the hostrule is evaluated.
dependencies = {
  "bitcoin-info",
  "http-date",
  "http-ntlm-info",
  "imap-ntlm-info",
  "memcached-info",
  "ms-sql-ntlm-info",
  "nntp-ntlm-info",
  "ntp-info",
  "openwebnet-discovery",
  "pop3-ntlm-info",
  "rfc868-time",
  "smb-os-discovery",
  "smb-security-mode",
  "smb2-time",
  "smb2-vuln-uptime",
  "smtp-ntlm-info",
  "ssl-date",
  "telnet-ntlm-info",
}

description = [[
Analyzes the clock skew between the scanner and various services that report timestamps.

At the end of the scan, it will show groups of systems that have similar median
clock skew among their services. This can be used to identify targets with
similar configurations, such as those that share a common time server.

You must run at least 1 of the following scripts to collect clock data:
* ]] .. table.concat(dependencies, "\n* ") .. "\n"

---
-- @output
-- Host script results:
-- |_clock-skew: mean: -13s, deviation: 12s, median: -6s
--
-- Post-scan script results:
-- | clock-skew:
-- |  -6s: Majority of systems scanned
-- |  3s:
-- |    192.0.2.5
-- |_   192.0.2.7 (example.com)
--
-- @xmloutput
-- <elem key="stddev">12.124355652982</elem>
-- <elem key="mean">-13.0204495</elem>
-- <elem key="median">-6.0204495</elem>

author = "Daniel Miller"

license = "Same as Nmap--See https://nmap.org/book/man-legal.html"

categories = {"default", "safe"}

hostrule = function(host)
  return host.registry.datetime_skew and #host.registry.datetime_skew > 0
end

postrule = function()
  return nmap.registry.clock_skews and #nmap.registry.clock_skews > 0
end

local function format_host (host)
  local name = stdnse.get_hostname(host)
  if name == host.ip then
    return name
  else
    return ("%s (%s)"):format(host.ip, name)
  end
end

local function record_stats(host, mean, stddev, median)
  local reg = nmap.registry.clock_skews or {}
  reg[#reg+1] = {
    ip = format_host(host),
    mean = mean,
    stddev = stddev,
    median = median,
    -- Allowable variance to regard this a match.
    variance = host.times.rttvar * 2
  }
  nmap.registry.clock_skews = reg
end

hostaction = function(host)
  local skews = host.registry.datetime_skew
  if not skews or #skews < 1 then
    return nil
  end
  local mean, stddev = formulas.mean_stddev(skews)
  local median = formulas.median(skews)
  -- truncate to integers; we don't care about fractional seconds)
  mean = math.modf(mean)
  stddev = math.modf(stddev)
  median = math.modf(median)
  record_stats(host, mean, stddev, median)
  if mean ~= 0 or stddev ~= 0 or nmap.verbosity() > 1 then
    local out = {count = #skews, mean = mean, stddev = stddev, median = median}
    return out, (#skews == 1 and datetime.format_time(mean)
      or ("mean: %s, deviation: %s, median: %s"):format(
        datetime.format_time(mean),
        datetime.format_time(stddev),
        datetime.format_time(median)
        )
      )
  end
end

local function sorted_keys(t)
  local ret = {}
  for k, _ in pairs(t) do
    ret[#ret+1] = k
  end
  table.sort(ret)
  return ret
end

postaction = function()
  local skews = nmap.registry.clock_skews

  local host_count = #skews
  local groups = {}
  for i=1, host_count do
    local current = skews[i]
    -- skip if we already grouped this one
    if not current.grouped then
      current.grouped = true
      local group = {current.ip}
      groups[current.mean] = group
      for j=i+1, #skews do
        local check = skews[j]
        if not check.grouped then
          -- Consider it a match if it's within a the average variance of the 2 targets.
          -- Use the median to rule out influence of outliers, since these ought to be discrete.
          if math.abs(check.median - current.median) < (check.variance + current.variance) / 2 then
            check.grouped = true
            group[#group+1] = check.ip
          end
        end
      end
    end
  end

  local out = {}
  for mean, group in pairs(groups) do
    -- Collapse the biggest group
    if #groups > 1 and #group > host_count // 2 then
      out[datetime.format_time(mean)] = "Majority of systems scanned"
    elseif #group > 1 then
      -- Only record groups of more than one system together
      out[datetime.format_time(mean)] = group
    end
  end

  if next(out) then
    return outlib.sorted_by_key(out)
  end
end

local ActionsTable = {
  -- hostrule: Get the average clock skew and put it in the registry
  hostrule = hostaction,
  -- postrule: compare clock skews and report similar ones
  postrule = postaction
}

-- execute the action function corresponding to the current rule
action = function(...) return ActionsTable[SCRIPT_TYPE](...) end
