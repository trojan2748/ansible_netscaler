#!/usr/bin/env python
"""
Author: adamlandas@g m.@.l.c0m
Version: .1

Descripton: 
  * Script will take ns.conf (in script directory) and dump config

Changelog:
  % 12/20/2017 - Initial commit

"""
import yaml
import argparse

with open("ns.conf") as f:
  lines = f.readlines()
lines = [line.strip() for line in lines]

actions = {}
bindings = {}
csvservers = {}
lbmons = {}
lbvservers = {}
patsets = {}
policies = {}
policyexpressions = {}
servers = {}
servicegroups = {}

def GetArgs():
    parser = argparse.ArgumentParser(
        description='Script to dump ns.conf to yaml format')
    parser.add_argument('-s', '--servicegroup', required=False, action='store',
        help='Dump specifc serviceGroup conf')
    parser.add_argument('-a', '--all', required=False, action='store_true',
        help='Dump all ns.conf to yaml, only if -s is not set')
    parser.add_argument('-f', '--files', required=False, action='store_true',
        help='Dump to files, else dump to stdout')
    parser.set_defaults(all=False)
    parser.set_defaults(files=False)
    args = parser.parse_args()

    if args.servicegroup == None:
      args.all = True

    return args


for line in lines:
  if "add policy patset" in line:
    name = line.split()[3]
    patsets[name] = []
    continue
  elif "bind policy patset" in line:
    name = line.split()[3]
    patsets[name].append(line.split()[4])
    continue


  elif "add policy expression" in line:
    name = line.split()[3]
    policyexpressions[name] = {}
    policyexpressions[name]["name"] = name
    if "-comment" in line:
      policyexpressions[name]["value"] = line.split(name)[1].split(" -comment")[0].strip()
    else: 
      policyexpressions[name]["value"] = line.split(name)[1].strip()
    continue


  elif "add responder action" in line or "add rewrite action" in line:
    name = line.split()[3].strip()
    t = line.split()[1].strip() + "action"
    actions[name] = {}
    actions[name]["name"] = name
    actions[name]["t"] = t
    actions[name]["type"] = line.split()[4].strip()
    actions[name]["bypasssafetycheck"] = 'NO'
    if "-bypassSafetyCheck" in line:
      actions[name]["bypasssafetycheck"] = 'YES'
      s = line.split(actions[name]["type"])[1].split("-bypassSafetyCheck")[0].strip().split()
      if t == "rewriteaction":
        actions[name]["stringbuilderexpr"] = "".join(s[1:])
        actions[name]["target"] = s[0]
      else:
        actions[name]["target"] = "".join(s).replace("q{", "").replace("}","")
    elif "-comment" in line:
      target = line.split(actions[name]["type"])[1].split("-comment")[0]
      target =  target.replace("q{", "")
      target =  target.replace("}", "")
     
      actions[name]["target"] = line.split(actions[name]["type"])[1].split("-comment")[0].replace("q{", "").replace("}","")
    else: 
      if t == "rewriteaction":
        s = line.split(actions[name]["type"])[1]
        actions[name]["stringbuilderexpr"] = line.split(actions[name]["type"])[1].split()[1]
        actions[name]["target"] = line.split(actions[name]["type"])[1].split()[0]
      else:
        actions[name]["target"] = line.split(actions[name]["type"])[1].strip().replace("q{", "").replace("}","")
    continue


  elif "add responder policy" in line:
    name = line.split()[3].strip()
    t = line.split()[1].strip() + "policy"
    pol = {}
    pol["name"] = name
    pol["t"] = t
    pol["action"] = line.split()[-1].strip()
    if "-comment" in line:
      pol["action"] = line.split("-comment")[0].split()[-1].strip()
    pol["rule"] = line.split(name)[1].split(pol["action"])[0].strip()

    policies[name] = pol
    continue


  elif "add rewrite policy" in line:
    name = line.split()[3]
    policies[name] = {}
    p = policies[name]
    p["t"] = "rewritepolicy"
    p["name"] = name
    p["rule"] = line.split()[4]
    p["action"] = line.split()[5]
    continue


  elif "add cs policy" in line:
    name = line.split()[3].strip()
    policies[name] = {}
    policies[name]["name"] = name
    policies[name]["policyname"] = name
    policies[name]["t"] = "cspolicy"
    policies[name]["rule"] = line.split("-rule")[1].strip()
    continue

  elif "add transform " in line:
    name = line.split()[3]
    t = line.split()[2]
    tty = line.split()[1]
    if t == "action":
      a = {}
      a["name"] = name
      a["t"] = t
      a["type"] = tty
      a["profile"] = line.split()[4]
      a["proiority"] = line.split()[-1]
      actions[name] = a
      continue
    elif t == "policy":
      a = {}
      a["name"] = name
      a["t"] = t
      a["type"] = tty
      a["profile"] = line.split()[-1]
      a["rule"] = "".join(line.split("policy %s" % name)[1].split(a["profile"])[0])
      policies[name] = a
      continue

  elif "set transform action" in line:
    name = line.split()[3]
    t = "set"
    s = {}
    s["name"] = name
    s["type"] = "set"
    items = line.split("action %s" % name)[1].split(" -")
    for item in items:
      if item == "":
        continue
      key = item.strip().split()[0].strip()
      value = " ".join(item.split()[1:]).strip()
      s[key] = value
    policies[name] = s
    continue



  elif "add server " in line:
    name = line.split()[2].strip()
    servers[name] = {}
    servers[name]["name"] = name
    servers[name]["ipaddress"] = line.split()[3].strip()
    continue


  elif "add lb monitor" in line:
    l = line.split(" ")
    name = l[3]
    lbmons[name] = {}
    lbmons[name]["name"] = name
    lbmons[name]["monitorname"] = name
    lbmons[name]["type"] = l[4].strip()
    if "respCode" in line:
      lbmons[name]["respcode"] = [x for x in line.split("respCode")[1].split("-")[0].strip().split()]
    if "httpRequest" in line:
      lbmons[name]["httprequest"] = line.split("-httpRequest")[1].split("\"")[1].strip()
    if "LRTM" in line:
      lbmons[name]["lrtm"] = line.split("-LRTM")[1].split("-")[0].strip()
    if "interval" in line:
      lbmons[name]["interval"] = line.split("-interval")[1].split("-")[0].strip()
    if "resptimeout" in line:
      lbmons[name]["resptimeout"] = line.split("-resptimeout")[1].split("-")[0].strip()
    if "destPort" in line:
      lbmons[name]["destport"] = line.split("-destPort")[1].split("-")[0].strip()
    if "-send" in line:
      lbmons[name]["send"] = line.split("-send")[1].split("-")[0].strip()
    continue


  elif "add cs vserver" in line:
    name = line.split()[3]
    csvservers[name] = {}
    csvservers[name]["name"] = name
    csvservers[name]["binds"] = []
    csvservers[name]["servicetype"] = line.split()[4]
    csvservers[name]["ipv46"]  = line.split()[5]
    csvservers[name]["port"] = line.split()[6]
    items = line.split(csvservers[name]["port"], 1)[1].strip().split(" -")
    for item in items:
      key = item.split()[0].lower()
      if key[0] == "-":
        key = key.split("-")[1]
      value = " ".join(item.split()[1:]).strip()
      csvservers[name][key] =  value
    continue


  elif "bind cs vserver" in line:
    name = line.split()[3].strip()
    b = {}
    b["name"] = name

    if "csvserver_binding" not in bindings.keys():
      bindings["csvserver_binding"] = {}
 
    if "-lbvserver" in line:
      lb = line.split()[-1].strip()
      b["lbvserver"] = lb

      if "csvserver_lbvserver_binding" not in bindings["csvserver_binding"].keys():
        bindings["csvserver_binding"]["csvserver_lbvserver_binding"] = {}
      if name not in bindings["csvserver_binding"]["csvserver_lbvserver_binding"].keys():
        bindings["csvserver_binding"]["csvserver_lbvserver_binding"][name] = []

      bindings["csvserver_binding"]["csvserver_lbvserver_binding"][name].append(b)
      lbvservers[lb]["csvs"].append(name)
      continue
     
    elif "-targetLBVserver" in line:
      lb = line.split("-targetLBVserver")[1].split()[0].strip()
      b["targetlbvserver"] = lb
      lbvservers[lb]["csvs"].append(name)

    if "csvserver_cspolicy_binding" not in bindings["csvserver_binding"].keys():
      bindings["csvserver_binding"]["csvserver_cspolicy_binding"] = {}
 
    if name not in bindings["csvserver_binding"]["csvserver_cspolicy_binding"].keys():
      bindings["csvserver_binding"]["csvserver_cspolicy_binding"][name] = []

    items = line.split(name, 1)[1].strip().split(" -")
    for item in items:
      key = item.split()[0].lower()
      if key[0] == "-":
        key = key.split("-")[1]
      value = " ".join(item.split()[1:]).strip()
      b[key] = value

    bindings["csvserver_binding"]["csvserver_cspolicy_binding"][name].append(b)   
    csvservers[name]["binds"].append(b)
    continue


  elif "add lb vserver" in line:
    name = line.split()[3]
    lbvservers[name] = {}
    lbvservers[name]["csvs"] = []
    lbvservers[name]["name"] = name
    lbvservers[name]["servicetype"] = line.split()[4]
    lbvservers[name]["ipv46"] = line.split()[5]
    lbvservers[name]["port"] = line.split()[6]
    socket = "%s %s" % (lbvservers[name]["ipv46"], lbvservers[name]["port"])
    items = line.split(socket, 1)[1].strip().split(" -")
    for item in items:
      key = item.split()[0].lower()
      if key[0] == "-":
        key = key.split("-")[1]
      value = " ".join(item.split()[1:]).strip()
      lbvservers[name][key] = value
    continue


  elif "bind lb vserver" in line:
    if "-policyName" not in line:
      name = line.split()[3]
      svg_n = line.split()[4]

      b = {"name": name, "servicegroupname": svg_n}

      if "lbvserver_binding" not in bindings.keys():
        bindings["lbvserver_binding"] = {}
      if "lbvserver_servicegroup_binding" not in bindings["lbvserver_binding"].keys():
        bindings["lbvserver_binding"]["lbvserver_servicegroup_binding"] = []
      bindings["lbvserver_binding"]["lbvserver_servicegroup_binding"].append(b)
      continue
    

  elif "add serviceGroup " in line:
    name = line.split()[2]
    s = {}
    s["name"] = name
    s["servicetype"] = line.split()[3]
    pair = "%s %s" % (s["name"], s["servicetype"])
    items = line.split(pair, 1)[1].strip().split(" -")
    for item in items:
      key = item.split()[0].lower()
      value = " ".join(item.split()[1:]).strip()
      if key[0] == "-":
        key = key.split("-")[1]
      if key == "cip" and "ENABLED" in value:
        s["cip"] = "enabled"
        s["cipheader"] = value.split()[1]
      else:
        s[key] = value.lower()
    servicegroups[name] = s
    if "servicegroup_binding" not in bindings.keys():
      bindings["servicegroup_binding"] = {}
      bindings["servicegroup_binding"]["servicegroup_lbmonitor_binding"] = {}
      bindings["servicegroup_binding"]["servicegroup_servicegroupmember_binding"] = {}
    bindings["servicegroup_binding"]["servicegroup_lbmonitor_binding"][name] = []
    bindings["servicegroup_binding"]["servicegroup_servicegroupmember_binding"][name] = []
    continue


  elif "bind serviceGroup " in line:
    name = line.split()[2].strip()
    if "-monitorName" in line:
      l = {}
      l["monitor_name"] = line.split("-monitorName")[1].split()[0].strip()
      l["servicegroupname"] = name
      bindings["servicegroup_binding"]["servicegroup_lbmonitor_binding"][name].append(l)
      continue

    else:
      s = {}
      s["servername"] = line.split()[3].strip()
      s["port"] = line.split()[4].strip()
      s["state"] = "enabled"
      if "-state" in line:
        s["state"] = "disabled"
      if "-CustomServerID" in line:
        s["customerserverid"] = line.split("-CustomServerID")[1].split()[0].strip()
      bindings["servicegroup_binding"]["servicegroup_servicegroupmember_binding"][name].append(s)
      continue


def get_all_conf():
   pass


def get_group_conf(group):
  print "---\n\n"
  print "ns_ip: 10.1.3.205"
  print "ns_user: nsroot"
  print "ns_pass: nsroot"
  print
  svg = servicegroups[group]
  group_lbs = [x['name'] for x in bindings["lbvserver_binding"]["lbvserver_servicegroup_binding"] if x['servicegroupname'] == group]
  group_mons = [x['monitor_name'] for x in bindings["servicegroup_binding"]["servicegroup_lbmonitor_binding"][group] if x['servicegroupname'] == group]

  print "servicegroups:"
  print "    servicegroup:"
  print "        - servicegroupname: %s" % group
  for key in sorted(svg.keys()):
    if key != "name":
      if svg[key] == "yes" or svg[key] == "no" or svg[key] == "on":
        print "          %s: \"%s\"" % (key, svg[key].upper())
      else:
        print "          %s: %s" % (key, svg[key])

  if len(group_mons) > 0:
    print "    servicegroup_lbmonitor_binding:"
    try:
      for mon in bindings["servicegroup_binding"]["servicegroup_lbmonitor_binding"][group]:
        print "        - servicegroupname: %s" % (mon["servicegroupname"])
        print "          monitor_name: %s" % (mon["monitor_name"])
    except:
      pass

  ss = []
  if len(bindings["servicegroup_binding"]["servicegroup_servicegroupmember_binding"][group]) > 0:
    print "    servicegroup_servicegroupmember_binding:"
    try:
      for server in bindings["servicegroup_binding"]["servicegroup_servicegroupmember_binding"][group]:
        print "        - servicegroupname: %s" % (group)
        print "          servername: %s" % (server["servername"])
        print "          port: %s" % (server["port"])
        print "          state: %s" % (server["state"])
        ss.append(server["servername"])
    except:
      pass

  backup_lbs = []
  if len(group_lbs) > 0:
    print "\n\n"
    print "lbvservers:"
    print "    lbvserver:"
    for lb in group_lbs:
      print "        - name: %s" % lb
      for key in sorted(lbvservers[lb]):
        if key != "name" and key != "csvs":
          if key == "backupvserver":
            backup_lbs.append(lbvservers[lb][key])
          print "          %s: %s" % (key, lbvservers[lb][key])
  if len(backup_lbs) > 0:
    print "    backuplbvserver:"
    for lb in backup_lbs:
      print "        - name: %s" % lb
      for key in sorted(lbvservers[lb]):
        if key != "name" and key != "csvs":
          if key == "backupvserver":
            backup_lbs.append(lbvservers[lb][key])
          print "          %s: %s" % (key, lbvservers[lb][key])


  # l checkes to see if group has any lb bindings
  l = [x['servicegroupname'] for x in bindings["lbvserver_binding"]["lbvserver_servicegroup_binding"] if x['servicegroupname'] == group]
  csvs = []
  if len(l) > 0:
    print "    lbvserver_binding:"
    print "        lbvserver_servicegroup_binding:"
    for l in group_lbs:
       print "            - name: %s" % (l)
       print "              servicegroupname: %s" % group
       csvs.extend(lbvservers[l]['csvs'])

  if len(csvs) > 0:
    print "\n\n"
    print "csvservers:"
    print "    csvserver:"
    for csv in set(csvs):
      print "        - name: %s" % csv
      for key in sorted(csvservers[csv]):
        if key != "binds" and key != "name":
          print "          %s: %s" % (key, csvservers[csv][key])


  pols = []
  pol_types = []
  if len(csvs) > 0:  
    print "    csvserver_binding:"
    print "        csvserver_cspolicy_binding:"
    for csv in set(csvs):
      if csv in bindings["csvserver_binding"]["csvserver_cspolicy_binding"]:
        for bind in bindings["csvserver_binding"]["csvserver_cspolicy_binding"][csv]:
          if "targetlbvserver" in bind.keys() and bind["targetlbvserver"] not in group_lbs:
            continue
          pol_name = bind["policyname"]
          pols.append(pol_name)
          pol_types.append(policies[pol_name]["t"])
          print "            - name: %s" % (bind['name'])
          for key in bind:
            if key != "name":
              if key == "type":
                print "              %s: %s" % ("bindpoint", bind[key])
              else:
                print "              %s: %s" % (key, bind[key])

  flag = 0
  for csv in set(csvs):
    if csv in bindings["csvserver_binding"]["csvserver_lbvserver_binding"]:
      for bind in bindings["csvserver_binding"]["csvserver_lbvserver_binding"][csv]:
        if bind["lbvserver"] in group_lbs:
          if flag == 0:
            print "        csvserver_lbvserver_binding:"
            flag = 1
          print "            - name: %s" % (bind['name'])
          for key in bind:
            if key != "name":
              print "              %s: %s" % (key, bind[key])

  exps = []
  pats = []
  if len(pol_types) > 0:
    print "\n\n"
    print "policies:"
    pol_exps = set([x for x in policyexpressions.keys()])
    for t in set(pol_types):
      print "    %s:" % t
      for pol in set(pols):
        p = policies[pol]
        if p["t"] == t:
          if t == "cspolicy":
            print "        - policyname: %s" % pol
          else:
            print "        - name: %s" % pol
          for key in p.keys():
            if key != "t" and key != "name" and key != "policyname":
              print '          %s: %s' % (key, p[key])
              for exp in pol_exps:
                if exp in p[key]:
                  exps.append(exp)
            if key == "rule":
               for pat in patsets.keys():
                   if pat in p[key]:
                      pats.append(pat)

  if len(exps) > 0:
    print "\n\n"
    print "policyexpressions:"
    print "    policyexpression:"
    for exp in exps:
      e = policyexpressions[exp]
      print "        - name: %s" % e["name"]
      for key in e.keys():
        if key != "name":
          print '          %s: %s' % (key, e[key])
        if key == "value":
          for pat in patsets.keys():
             if pat in e[key]:
               pats.append(pat)

  if len(pats) > 0:
    print "\n\n"
    print "patsets:"
    print "    patset:"
    for pat in set(pats):
       print "        %s: " % pat
       for b in patsets[pat]:
           print "            - name: %s" % pat
           print "              String: %s" % b


  print "\n\n"
  print "servers:"
  print "    server:"
  for s in ss:
    print "        - name: %s" % s
    print "          ipaddress: %s" % servers[s]["ipaddress"]


  if len(group_mons) > 0:
    print "\n\n"
    print "lbmonitors:"
    print "    lbmonitor:"
    for mon in group_mons:
      if mon == "ping":
        continue
      l = lbmons[mon]
      print "        - monitorname: %s" % l["name"]
      for key in l.keys():
        if key != "name" and key != "monitorname":
          print "          %s: %s" % (key, l[key])

  acts = [policies[x]["action"] for x in policies.keys() if "action" in policies[x].keys() and policies[x]["name"] in pols]
  if len(acts) > 0:
    print
    print "actions:"
    act_types = set([actions[x]["t"] for x in acts if x != "DROP"])
    for tt in act_types:
      print "    %s:" % tt
      for act in acts:
        if act in actions.keys() and actions[act]["t"] == tt:
          a = actions[act]
          print "          - name: %s" % a["name"]
          for key in a.keys():
            if key != "t" and key != "name":
              if key == "target":
                print "            %s: '%s'" % (key, a[key].strip())
              else:
                print "            %s: '%s'" % (key, a[key])
  
def main():
  args = GetArgs()
  if args.servicegroup:
    if args.servicegroup in servicegroups.keys():
      get_group_conf(args.servicegroup)
    else:
      print "%s not found" % args.servicegroup
  else:
    get_all_conf()


if __name__ == "__main__":
  main()
