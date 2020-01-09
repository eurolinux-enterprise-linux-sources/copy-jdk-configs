#!/usr/bin/lua
-- rpm call
-- lua -- copy_jdk_configs.lua   --currentjvm "%{uniquesuffix %{nil}}" --jvmdir "%{_jvmdir %{nil}}" --origname "%{name}" --origjavaver "%{javaver}" --arch "%{_arch}" --debug true
--test call
--lua -- copy_jdk_configs.lua   --currentjvm "java-1.8.0-openjdk-1.8.0.65-3.b17.fc22.x86_64" --jvmdir "/usr/lib/jvm" --origname "java-1.8.0-openjdk" --origjavaver "1.8.0" --arch "x86_64" --debug true  --jvmDestdir /home/jvanek/Desktop

-- yum install lua-posix
local posix = require "posix"

-- the one we are installing
local currentjvm = nil
local jvmdir = nil
local jvmDestdir = nil
local origname = nil
local origjavaver = nil
local arch = nil
local debug = false;

for i=1,#arg,2 do 
  if (arg[i] == "--help" or arg[i] == "-h") then 
    print("all but jvmDestdir and debug are mandatory")
    print("  --currentjvm")
    print("    NVRA of currently installed java")
    print("  --jvmdir") 
    print("    Directory where to find this kind of virtual machine. Generally /usr/lib/jvm")
    print("  --origname")
    print("    convinient switch to determine jdk. Generally java-1.X.0-vendor")
    print("  --origjavaver")
    print("    convinient switch to determine jdk's version. Generally 1.X.0")
    print("  --arch")
    print("    convinient switch to determine jdk's arch")
    print("  --jvmDestdir")
    print("    Migration/testing switch. Target Mostly same as jvmdir, but you may wont to copy ouside it.")
    print("  --debug")
    print("    Enables printing out whats going on. true/false")
    os.exit(0)
  end
  if (arg[i] == "--currentjvm") then 
    currentjvm=arg[i+1]
  end
  if (arg[i] == "--jvmdir") then 
    jvmdir=arg[i+1]
  end
  if (arg[i] == "--origname") then 
    origname=arg[i+1]
  end
  if (arg[i] == "--origjavaver") then 
    origjavaver=arg[i+1]
  end
  if (arg[i] == "--arch") then 
    arch=arg[i+1]
  end
  if (arg[i] == "--jvmDestdir") then 
    jvmDestdir=arg[i+1]
  end
  if (arg[i] == "--debug") then 
--no string, boolean, workaround
    if (arg[i+1] == "true") then
     debug = true
    end
  end
end

if (jvmDestdir == nill) then
jvmDestdir = jvmdir
end


if (debug) then
  print("--currentjvm:");
  print(currentjvm);
  print("--jvmdir:");
  print(jvmdir);
  print("--jvmDestdir:");
  print(jvmDestdir);
  print("--origname:");
  print(origname);
  print("--origjavaver:");
  print(origjavaver);
  print("--arch:");
  print(arch);
  print("--debug:");
  print(debug);
end


--trasnform substitute names to lua patterns
local name = string.gsub(string.gsub(origname, "%-", "%%-"), "%.", "%%.")
local javaver = string.gsub(origjavaver, "%.", "%%.")

local jvms = { }

local caredFiles = {"jre/lib/calendars.properties",
              "jre/lib/content-types.properties",
              "jre/lib/flavormap.properties",
              "jre/lib/logging.properties",
              "jre/lib/net.properties",
              "jre/lib/psfontj2d.properties",
              "jre/lib/sound.properties",
              "jre/lib/deployment.properties",
              "jre/lib/deployment.config",
              "jre/lib/security/US_export_policy.jar",
              "jre/lib/security/java.policy",
              "jre/lib/security/java.security",
              "jre/lib/security/local_policy.jar",
              "jre/lib/security/nss.cfg",
              "jre/lib/security/cacerts",
              "jre/lib/ext"}

function splitToTable(source, pattern)
  local i1 = string.gmatch(source, pattern) 
  local l1 = {}
  for i in i1 do
    table.insert(l1, i)
  end
  return l1
end

if (debug) then
  print("started")
end;

foundJvms = posix.dir(jvmdir);
if (foundJvms == nil) then
  if (debug) then
    print("no, or nothing in "..jvmdir.." exit")
  end;
  return
end

if (debug) then
  print("found "..#foundJvms.."jvms")
end;

for i,p in pairs(foundJvms) do
-- regex similar to %{_jvmdir}/%{name}-%{javaver}*%{_arch} bash command
  if (string.find(p, name.."%-"..javaver..".*"..arch) ~= nil ) then
    if (debug) then
      print("matched:  "..p)
    end;
    if (currentjvm ==  p) then
      if (debug) then
        print("this jdk is already installed. exiting lua script")
      end;
      return
    end ;
    table.insert(jvms, p)
  else
    if (debug) then
      print("NOT matched:  "..p)
    end;
  end
end

if (#jvms <=0) then 
  if (debug) then
    print("no matching jdk in "..jvmdir.." exit")
  end;
  return
end;

if (debug) then
  print("matched "..#jvms.." jdk in "..jvmdir)
end;

--full names are like java-1.7.0-openjdk-1.7.0.60-2.4.5.1.fc20.x86_64
table.sort(jvms , function(a,b) 
-- version-sort
-- split on non word: . - 
  local l1 = splitToTable(a, "[^%.-]+") 
  local l2 = splitToTable(b, "[^%.-]+") 
  for x = 1, math.min(#l1, #l2) do
    local l1x = tonumber(l1[x])
    local l2x = tonumber(l2[x])
    if (l1x ~= nil and l2x ~= nil)then
--if hunks are numbers, go with them 
      if (l1x < l2x) then return true; end
      if (l1x > l2x) then return false; end
    else
      if (l1[x] < l2[x]) then return true; end
      if (l1[x] > l2[x]) then return false; end
    end
-- if hunks are equals then move to another pair of hunks
  end
return a<b

end)

if (debug) then
  print("sorted lsit of jvms")
  for i,file in pairs(jvms) do
    print(file)
  end
end

latestjvm = jvms[#jvms]


for i,file in pairs(caredFiles) do
  local SOURCE=jvmdir.."/"..latestjvm.."/"..file
  local DEST=jvmDestdir.."/"..currentjvm.."/"..file
  if (debug) then
    print("going to copy "..SOURCE)
    print("to  "..DEST)
  end;
  local stat1 = posix.stat(SOURCE, "type");
  if (stat1 ~= nil) then
  if (debug) then
    print(SOURCE.." exists")
  end;
  local s = ""
  local dirs = splitToTable(DEST, "[^/]+") 
  for i,d in pairs(dirs) do
    if (i == #dirs) then
      break
    end
    s = s.."/"..d
    local stat2 = posix.stat(s, "type");
    if (stat2 == nil) then
      if (debug) then
        print(s.." does not exists, creating")
      end;
      posix.mkdir(s)
    else
      if (debug) then
        print(s.." exists,not creating")
      end;
    end
  end
-- Copy with -a to keep everything intact
    local exe = "cp".." -ar "..SOURCE.." "..DEST
    if (debug) then
      print("executing "..exe)
    end;    
    os.execute(exe)
  else
    if (debug) then
      print(SOURCE.." does not exists")
    end;
  end
end
