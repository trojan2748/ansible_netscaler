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
from datetime import datetime
import argparse
import sys

startTime = datetime.now()
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
profiles = {}
servers = {}
servicegroups = {}
services = {}
ssl = {}
users = {}


def GetArgs():
    parser = argparse.ArgumentParser(
        description='Script to dump ns.conf to yaml format')
    parser.add_argument('-s', '--servicegroup', required=False, action='store',
        help='Dump specifc serviceGroup conf')
    parser.add_argument('-a', '--all', required=False, action='store_true',
        help='Dump all ns.conf to yaml, only if -s is not set')
    parser.add_argument('-f', '--files', required=False, action='store_true',
        help='Dump to files, else dump to stdout')
    parser.add_argument('-d', '--delete', required=False, action='store_true',
        help='Show netscaler CLI delete commands')
    parser.set_defaults(all=False)
    parser.set_defaults(files=False)
    parser.set_defaults(delete=False)
    args = parser.parse_args()

    if args.servicegroup == None:
      args.all = True

    return args
i = 0
readlineTime = datetime.now()
rm = []
for line in lines:
    if "add policy patset" in line:
        name = line.split()[3]
        patsets[name] = []

    elif "bind policy patset" in line:
        name = line.split()[3]
        patsets[name].append(line.split()[4])


    elif "add policy expression" in line:
        name = line.split()[3]
        policyexpressions[name] = {}
        policyexpressions[name]["name"] = name
        if "-comment" in line:
            policyexpressions[name]["value"] = line.split(name)[1].split(" -comment")[0].strip()
        else: 
            policyexpressions[name]["value"] = line.split(name)[1].strip()


    elif "add responder action" in line:
        s = line.split()
        s = [s.strip() for s in s]
        name = s[3]
        actions[name] = {}
        a = actions[name]
        a["name"] = name
        a["t"] = "responderaction"
        a["type"] = s[4]
        if "-bypassSafetyCheck" in line:
            a["bypasssafetycheck"] = 'YES'
            target = line.split(s[4])[1].split("-bypassSafetyCheck")[0]
        elif "-comment" in line and "-bypassSafetyCheck" not in line:
            target = line.split(s[4])[1].split("-comment")[0]
        else:
            target = " ".join(s[5:])
        target = target.replace("q{", "").replace("}","").strip()
        a["target"] = "'%s'" % target
        

    elif "add rewrite action" in line:
        s = line.split()
        s = [s.strip() for s in s]
        name = s[3]
        actions[name] = {}
        a = actions[name]
        a["name"] = name
        a["t"] = "rewriteaction"
        a["type"] = s[4]
        a["target"] = s[5]
        if "-bypassSafetyCheck" in line:
            a["bypasssafetycheck"] = 'YES'
            a["stringbuilderexpr"] = line.split(s[5])[1].split("-bypassSafetyCheck")[0].strip()
            a["stringbuilderexpr"] = line.split(s[5], 1)[1].strip().split("-bypassSafetyCheck", 1)[0]
        elif "-comment" in line and "-bypassSafetyCheck" not in line:
            a["stringbuilderexpr"] = line.split(s[5])[1].split("-comment")[0].strip()
        else: 
            a["stringbuilderexpr"] = " ".join(s[6:])


    elif "add db user" in line:
        s = line.split()
        username = s[3]
        if "dbuser" not in users:
            users["dbuser"] = {}

        users["dbuser"][username] = {}
        users["dbuser"][username]["password"] = s[5]
        users["dbuser"][username]["username"] = username


    elif "add responder policy" in line:
        s = [s.strip() for s in line.split()]
        name = s[3]
        policies[name] = {}
        pol = policies[name]
        pol["name"] = name
        pol["t"] = "responderpolicy"
        pol["action"] = s[-1]
        if "-comment" in line:
            pol["action"] = s[-3]
        pol["rule"] = line.split(name)[1].split(pol["action"])[0].strip()


    elif "add rewrite policy" in line:
        name = line.split()[3]
        policies[name] = {}
        p = policies[name]
        p["t"] = "rewritepolicy"
        p["name"] = name
        p["rule"] = line.split()[4]
        p["action"] = line.split()[5]
        if "NOREWRITE" in line:
            p["undefaction"] = "NOREWRITE"
        if "RESET" in line:
            p["undefaction"] = "RESET"
        if "DROP" in line:
            p["DROP"] = "NOREWRITE"


    elif "add cs policy" in line:
        name = line.split()[3].strip()
        policies[name] = {}
        policies[name]["name"] = name
        policies[name]["policyname"] = name
        policies[name]["t"] = "cspolicy"
        policies[name]["rule"] = line.split("-rule")[1].strip()


    elif "add transform profile" in line:
        s = [s.strip() for s in line.split()]
        name = s[3]
        profiles[name] = {}
    

    elif "add transform action" in line:
        s = line.split()
        name = s[3]
        actions[name] = {}
        a = actions[name]
        a["name"] = name
        a["profilename"] = s[4]
        a["priority"] = s[5]
        a["t"] = "transformaction"

    elif "add transform policy" in line:
        s = line.split()
        name = s[3]
        policies[name] = {}
        a = policies[name]
        a["name"] = name
        a["t"] = "transformpolicy"
        a["profilename"] = line.split()[-1]
        a["rule"] = "".join(line.split("policy %s" % name)[1].split(a["profilename"])[0])

    elif "set transform action" in line:
        s = line.split()
        name = s[3]
        a = actions[name]
        items = line.split("action %s" % name)[1].split(" -")
        for item in items:
            if item == "":
                continue

            key = item.strip().split()[0].strip()
            value = " ".join(item.split()[1:]).strip()
            a[key] = value


    elif "add server " in line:
        name = line.split()[2].strip()
        servers[name] = {}
        servers[name]["name"] = name
        servers[name]["ipaddress"] = line.split()[3].strip()


    elif "add lb monitor" in line:
        l = line.split(" ")
        name = l[3]
        lbmons[name] = {}
        lbmons[name]["name"] = name
        lbmons[name]["monitorname"] = name
        lbmons[name]["type"] = l[4].strip()
        rm.append("rm lb monitor %s %s" % (name, l[4].strip()))
        split = line.split(l[4].strip())[1].split(" -")
        for item in split:
            if item == "":
                continue
            key = item.split()[0].lower()
            value = " ".join(item.split()[1:])
            if value == "YES" or value == "NO":
                value = "'%s'" % value
            lbmons[name][key] = value


    elif "add cs vserver" in line:
        name = line.split()[3]
        csvservers[name] = {}
        csvservers[name]["name"] = name
        csvservers[name]["binds"] = []
        csvservers[name]["servicetype"] = line.split()[4]
        csvservers[name]["ipv46"]  = line.split()[5]
        csvservers[name]["port"] = line.split()[6]
        pair = "%s %s" % (line.split()[5], line.split()[6])
        items = line.split(pair, 1)[1].strip().split(" -")
        for item in items:
            key = item.split()[0].lower()
            if key[0] == "-":
                key = key.split("-")[1]
            value = " ".join(item.split()[1:]).strip()
            csvservers[name][key] =  value


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


    elif "bind lb vserver" in line:
        s = [s.strip() for s in line.split()]
        if "lbvserver_binding" not in bindings.keys():
            bindings["lbvserver_binding"] = {}

        if "-policyName" not in line:
            name = s[3]
            svg_n = s[4]
            b = {"name": name, "servicegroupname": svg_n}
            if "lbvserver_servicegroup_binding" not in bindings["lbvserver_binding"].keys():
                bindings["lbvserver_binding"]["lbvserver_servicegroup_binding"] = []
            bindings["lbvserver_binding"]["lbvserver_servicegroup_binding"].append(b)
        elif "-policyName" in line:
            if "lbvserver_binding" not in bindings["lbvserver_binding"].keys():
                bindings["lbvserver_binding"]["lbvserver_binding"] = {}
            b = {}
            b["name"] = s[3]
            args = " ".join(s[4:]).split(" -")
            for arg in args:
                key = arg.split()[0].strip().lower().replace("-","")
                if key == "type":
                    key = "bindpoint"
                value = arg.split()[1].strip()
                b[key] = value
            bindings["lbvserver_binding"]["lbvserver_binding"][s[3]] = b

    elif "add service " in line:
        s = [s.strip() for s in line.split()]
        name = s[2]
        services[name] = {}
        ss = services[name]
        ss["servicetype"] = s[4]
        ss["servername"] = s[3]
        ss["port"] = s[5]
        pair = "%s %s" % (s[4], s[5])
        args = [x for x in line.split(pair, 1)[1].split(" -") if x != ""]
        for arg in args:
            key = arg.split(" ", 1)[0].lower().strip()
            value = arg.split(" ", 1)[1].strip()
            if key == "cip" and "ENABLED" in value:
                ss[key] = "ENABLED"
                ss["cipheader"] = value.split()[-1]
                continue
            ss[key] = value

    elif "bind service " in line:
        s = [s.strip() for s in line.split()]
        name = s[2]
        if "service_lbmonitor_binding" not in bindings:
            bindings["service_lbmonitor_binding"] = {}
        if name not in bindings["service_lbmonitor_binding"]:
            bindings["service_lbmonitor_binding"][name] = {}
        
        b = bindings["service_lbmonitor_binding"][name]
        if "-monitorName" in line:
            if "monitorname" not in b:
                b["monitorname"] = []
            mon = line.split("-monitorName", 1)[1].strip()
            b["monitorname"].append(mon)


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


    elif "bind serviceGroup " in line:
        name = line.split()[2].strip()
        if "-monitorName" in line:
            l = {}
            l["monitor_name"] = line.split("-monitorName")[1].split()[0].strip()
            l["servicegroupname"] = name
            bindings["servicegroup_binding"]["servicegroup_lbmonitor_binding"][name].append(l)

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

    elif "add ssl certKey " in line:
        s = line.split()
        name = s[3]
        if "certkey" not in ssl:
            ssl["certkey"] = {}
        if name not in ssl["certkey"]:
            ssl["certkey"][name] = {}
        ssl["certkey"][name]["certkey"] = name
        ss = ssl["certkey"][name]

        for item in line.split(" -")[1:]:
            if item == "":
                continue
            key = item.split()[0].lower().strip()
            value = item.split(" ", 1)[1]
            ss[key] =  value

    elif "link ssl certKey " in line:
        s = line.split()
        name = s[3]
        if name not in ssl["certkey"]:
            ssl["certkey"][name] = {}
        ss = ssl["certkey"][name]
        ss["linkcertkeyname"] = s[-1]

    elif "set ssl vserver " in line:
        s = line.split()
        name = s[3]
        if "set" not in ssl:
            ssl["set"] = {}
        if name not in ssl["set"]:
            ssl["set"][name] = {}
        ss = ssl["set"][name]

        for item in line.split(" -")[1:]:
            if item == "":
                continue
            key = item.split()[0].lower().strip()
            value = item.split(" ", 1)[1]
            ss[key] =  value

#    elif "bind ssl vserver " in line:




def get_all_conf():
    rm = ["#"]
    print "---\n\n"
    print "servicegroups:"
    print "    servicegroup:"
    for group in sorted(servicegroups):
        print "        - servicegroupname: %s" % group
        rm.append("rm serviceGroup %s" % group)
        svg = servicegroups[group]
        for key in sorted(svg.keys()):
            if key != "name":
                if svg[key] == "yes" or svg[key] == "no" or svg[key] == "on":
                    print "          %s: \"%s\"" % (key, svg[key].upper())
                else:
                    print "          %s: %s" % (key, svg[key])

    print "    servicegroup_lbmonitor_binding:"
    for binding in sorted(bindings["servicegroup_binding"]["servicegroup_lbmonitor_binding"]):
        b = bindings["servicegroup_binding"]["servicegroup_lbmonitor_binding"][binding]
        for mon in b:
            print "        - servicegroupname: %s" % (mon["servicegroupname"])
            print "          monitor_name: %s" % (mon["monitor_name"])

    print "    servicegroup_servicegroupmember_binding:"
    for binding in sorted(bindings["servicegroup_binding"]["servicegroup_servicegroupmember_binding"]):
        b = bindings["servicegroup_binding"]["servicegroup_servicegroupmember_binding"][binding]
        for server in b:
            port = server["port"]
            if port == "*":
                port = "\"*\""
            print "        - servicegroupname: %s" % (binding)
            print "          servername: %s" % (server["servername"])
            print "          port: '%s'" % (server["port"])
            print "          state: %s" % (server["state"])
            if "customerserverid" in server:
                print "          customserverid: %s" % (server["customerserverid"])

    print "\n\n"
    print "services:"
    print "    service:"
    for service in sorted(services):
        print "        - name: %s" % service
        s = services[service]
        for key in sorted(s):
            if key != "name":
                print "          %s: '%s'" % (key, s[key])
    print "    service_lbmonitor_binding:"
    for bind in sorted(bindings["service_lbmonitor_binding"]):
        b = bindings["service_lbmonitor_binding"][bind]
        for item in b["monitorname"]:
            print "        - name: %s" % bind
            print "          monitor_name: %s" % item



    backup_lbs = []
    print "\n\n"
    print "lbvservers:"
    print "    lbvserver:"
    for lb in sorted(lbvservers):
        l = lbvservers[lb]
        print "        - name: %s" % lb
        for key in l:
            if key != "name" and key != "csvs":
                if key == "port":
                    print '          %s: "%s"' % (key, l[key])
                else:
                    print '          %s: %s' % (key, l[key])
            if key == "backupvserver":
                backup_lbs.append(l[key])
    print "    backuplbvserver:"
    for lb in sorted(set(backup_lbs)):
        l = lbvservers[lb]
        print "        - name: %s" % lb
        for key in l:
            if key != "name" and key != "csvs":
                print '          %s: %s' % (key, l[key])

    print "    lbvserver_binding:"
    print "        lbvserver_servicegroup_binding:"
    for binding in sorted(bindings["lbvserver_binding"]["lbvserver_servicegroup_binding"]):
        if "SVC-" in binding['servicegroupname']:
            print "            - name: %s" % (binding['name'])
            print "              servicename: %s" % (binding['servicegroupname'])
            continue
        print "            - name: %s" % (binding['name'])
        print "              servicegroupname: %s" % (binding['servicegroupname'])

    pols = [bindings["lbvserver_binding"]["lbvserver_binding"][x]["policyname"] for x in bindings["lbvserver_binding"]["lbvserver_binding"]]
    pol_types = set([policies[x]["t"] for x in pols])
    for pol in sorted(pol_types):
        print "        lbvserver_%s_binding:" % pol
        for lb in bindings["lbvserver_binding"]["lbvserver_binding"]:
            l = bindings["lbvserver_binding"]["lbvserver_binding"][lb]
            pol_name = l["policyname"]
            if policies[pol_name]['t'] == pol:
                print "            - name: %s" % lb
                for key in l:
                    if key != "name":
                        print "              %s: %s" % (key, l[key])

        

    print "\n\n"
    print "users:"
    print "    dbuser:"
    for user in users["dbuser"]:
        u = users["dbuser"][user]
        print "        - username: %s" % u["username"]
        print "          password: %s" % u["password"]

    print "\n\n"
    print "profiles:"
    print "    transformprofile:"
    for pro in profiles:
        print "        - name: %s" % pro

    print "\n\n"
    print "csvservers:"
    print "    csvserver:"
    backup_csvs = []
    for csv in sorted(csvservers.keys()):
      c = csvservers[csv]
      print "        - name: %s" % csv
      for key in c:
          if key != "binds" and key != "name":
              print "          %s: %s" % (key, c[key])
          if key == "backupvserver":
              backup_csvs.append(c[key])
    print "    csvserver_backup:"
    for csv in sorted(set(backup_csvs)):
      c = csvservers[csv]
      print "        - name: %s" % csv
      for key in c:
          if key != "binds" and key != "name":
              print "          %s: %s" % (key, c[key])
          if key == "backupvserver":
              backup_csvs.append(c[key])

    print "    csvserver_binding:"
    print "        csvserver_cspolicy_binding:"
    for binding in sorted(bindings["csvserver_binding"]["csvserver_cspolicy_binding"]):
        b = bindings["csvserver_binding"]["csvserver_cspolicy_binding"][binding]
        for pol in b:
            print "            - name: %s" % (pol['name'])
            for key in pol:
                if key != "name":
                    if key == "type":
                        print "              %s: %s" % ("bindpoint", pol[key])
                    else:
                        print "              %s: %s" % (key, pol[key])
    print "        csvserver_lbvserver_binding:"
    for csv in sorted(bindings["csvserver_binding"]["csvserver_lbvserver_binding"]):
        for b in bindings["csvserver_binding"]["csvserver_lbvserver_binding"][csv]:
            print "            - name: %s" % (b['name'])
            for key in b:
                if key != "name":
                    print "              %s: %s" % (key, b[key])

    print "\n\n"
    print "servers:"
    print "    server:"
    for server in sorted(servers):
        s = servers[server]
        print "        - name: %s" % server
        print "          ipaddress: %s" % s['ipaddress']

    print "\n\n"
    print "lbmonitors:"
    print "    lbmonitor:"
    for mon in sorted(lbmons):
        l = lbmons[mon]
        print "        - monitorname: %s" % l["name"]
        for key in l.keys():
            if key != "name" and key != "monitorname":
                if key == "downtime":
                    value = int(l[key].split()[0]) * 60
                    print "          %s: '%s'" % (key, value)
                else:
                    print '          %s: %s' % (key, l[key])

    print "\n\n"
    print "actions:"
    types = set([actions[x]['t'] for x in actions.keys()])
    for t in types:
        print "    %s:" % (t)
        acts = sorted([actions[x] for x in actions.keys() if actions[x]['t'] == t])
        for act in acts:
            if t == "transformaction":
                print "        - name: %s" % act['name']
                print "          profilename: %s" % act['profilename']
                print "          priority: %s" % act['priority']
                continue
            print "        - name: %s" % act['name']
            for key in act:
                if key != "name" and key != "t":
                    if key == "target":
                        print "          %s: %s" % (key, act[key].strip())
                    else:
                        print "          %s: '%s'" % (key, act[key])
    
    if "transformaction" in types:
        print "    transformactionset:" 
        acts = sorted([actions[x] for x in actions.keys() if actions[x]['t'] == "transformaction"])
        for act in acts:
            print "        - name: %s" % act['name']
            for key in act:
                if key != "t" and key != "name" and key != "profilename":
                    print "          %s: %s" % (key, act[key].strip())


    print "\n\n"
    print "policyexpressions:"
    print "    policyexpression:"
    for exp in sorted(policyexpressions):
        e = policyexpressions[exp]
        print "        - name: %s" % e['name']
        print "          value: %s" % e['value']
       
    
    print "\n\n"
    print "policies:"
    pol_types = set([policies[x]["t"] for x in policies.keys() if "t" in policies[x].keys()])
    notin = [x for x in policies if "t" not in policies[x].keys()]
#    print pol_types
#    print notin
#    sys.exit(1)
    for t in pol_types:
#        if t == "transform":
 #           continue
        if t == "cspolicy":
            print "    %s:" % t
        else:
            print "    %s:" % t
        pols = [x for x in policies if "t" in policies[x].keys() and policies[x]["t"] == t]
        for pol in sorted(pols):
            p = policies[pol]
            if t == "cspolicy":
                print "        - policyname: %s" % p['name']
            else:
                print "        - name: %s" % p['name']
            for key in p:
                if key not in ["t", "name", "policyname"]:
                    print "          %s: %s" % (key, p[key])

    print "\n\n"
    print "patsets:"
    print "    patset:"
    for pat in sorted(patsets):
        print "        %s:" % pat
    print "    policypatset_pattern_binding:"
    for pat in patsets:
        p = patsets[pat]
        for b in p:
            print "        - name: %s" % pat
            print "          String: %s" % b
            break


def get_group_conf(group, delete):
  rm = "# "
  global getconfTime 
  global getconfStop
  getconfTime = datetime.now()
  print "---\n\n"
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
  rm += "; rm serviceGroup %s " % group

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
  print "\n\n"
  print "lbvservers:"
  if len(group_lbs) > 0:
    print "    lbvserver:"
    for lb in group_lbs:
      print "        - name: %s" % lb
      rm += " ; rm lb vserver %s " % lb
      for key in sorted(lbvservers[lb]):
        if key != "name" and key != "csvs":
          if key == "backupvserver":
            backup_lbs.append(lbvservers[lb][key])
          print "          %s: %s" % (key, lbvservers[lb][key])
  if len(backup_lbs) > 0:
    print "    backuplbvserver:"
    for lb in backup_lbs:
      print "        - name: %s" % lb
      rm += " ; rm lb vserver %s " % lb
      for key in sorted(lbvservers[lb]):
        if key != "name" and key != "csvs":
          if key == "backupvserver":
            backup_lbs.append(lbvservers[lb][key])
          print "          %s: %s" % (key, lbvservers[lb][key])


  # l checkes to see if group has any lb bindings
  l = [x['servicegroupname'] for x in bindings["lbvserver_binding"]["lbvserver_servicegroup_binding"] if x['servicegroupname'] == group]
  csvs = []
  print "    lbvserver_binding:"
  if len(l) > 0:
    print "        lbvserver_servicegroup_binding:"
    for l in group_lbs:
       print "            - name: %s" % (l)
       print "              servicegroupname: %s" % group
       csvs.extend(lbvservers[l]['csvs'])

  print "\n\n"
  print "csvservers:"
  backup_csvs = []
  if len(csvs) > 0:
    print "    csvserver:"
    for csv in set(csvs):
      print "        - name: %s" % csv
      rm += " ; rm cs vserver %s " % csv
      for key in sorted(csvservers[csv]):
        if key != "binds" and key != "name":
          print "          %s: %s" % (key, csvservers[csv][key])
        if key == "backupvserver":
          backup_csvs.append(csvservers[csv][key])
  if len(backup_csvs) > 0:
    print "    csvserver_backup:"
    for csv in backup_csvs:
      print "        - name: %s" % csv
      for key in sorted(csvservers[csv]):
        if key != "binds" and key != "name":
          print "          %s: %s" % (key, csvservers[csv][key])



  pols = []
  pol_types = []
  print "    csvserver_binding:"
  print "        csvserver_cspolicy_binding:"
  if len(csvs) > 0:  
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
  print "\n\n"
  print "policies:"
  if len(pol_types) > 0:
    pol_exps = set([x for x in policyexpressions.keys()])
    for t in set(pol_types):
      if t =="cspolicy":
        print "    %s:" % (t)
      else:
        print "    %s%s:" % (t, "policy")
      for pol in set(pols):
        p = policies[pol]
        if p["t"] == t:
          if t == "cspolicy":
            print "        - policyname: %s" % pol
            rm += " ; rm cs policy %s " % (pol)
          else:
            print "        - name: %s" % pol
            rm += " ; rm %s policy % s " % (t, pol)
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

  print "\n\n"
  print "policyexpressions:"
  if len(exps) > 0:
    print "    policyexpression:"
    for exp in exps:
      e = policyexpressions[exp]
      print "        - name: %s" % e["name"]
      rm += " ; rm policy expression %s " % e["name"]
      for key in e.keys():
        if key != "name":
          print '          %s: %s' % (key, e[key])
        if key == "value":
          for pat in patsets.keys():
             if pat in e[key]:
               pats.append(pat)

  print "patsets:"
  if len(pats) > 0:
    print "\n\n"
    print "    patset:"
    for pat in set(pats):
       print "        %s: " % pat
       print "    policypatset_pattern_binding:"
       rm += " ; rm policy patset %s " % pat
       for b in patsets[pat]:
           print "            - name: %s" % pat
           print "              String: %s" % b


  print "\n\n"
  print "servers:"
  print "    server:"
  for s in ss:
    print "        - name: %s" % s
    print "          ipaddress: %s" % servers[s]["ipaddress"]
    rm += " ; rm server %s " % s


  print "\n\n"
  print "lbmonitors:"
  if len(group_mons) > 0:
    print "    lbmonitor:"
    for mon in group_mons:
      if mon == "ping":
        print "        - monitorname: ping"
        print "          type: ping"
        continue
      l = lbmons[mon]
      print "        - monitorname: %s" % l["name"]
      rm += " ; rm lb monitor %s HTTP" % l["name"]
      for key in l.keys():
        if key != "name" and key != "monitorname":
          print "          %s: %s" % (key, l[key])

  acts = [policies[x]["action"] for x in policies.keys() if "action" in policies[x].keys() and policies[x]["name"] in pols]
  print
  print "actions:"
  if len(acts) > 0:
    act_types = set([actions[x]["t"] for x in acts if x != "DROP"])
    for tt in act_types:
      print "    %s%s:" % (tt, "action")
      for act in acts:
        if act in actions.keys() and actions[act]["t"] == tt:
          a = actions[act]
          print "          - name: %s" % a["name"]
          rm += " ; rm %s action %s " % (tt, a["name"])
          for key in a.keys():
            if key != "t" and key != "name":
              if key == "target":
                print "            %s: %s" % (key, a[key].strip())
              else:
                print "            %s: '%s'" % (key, a[key])
  getconfStop = datetime.now()
  if delete == True:
      print rm
  
def main():
  args = GetArgs()
  if args.servicegroup:
    if args.servicegroup in servicegroups.keys():
      get_group_conf(args.servicegroup, args.delete)
    else:
      print "%s not found" % args.servicegroup
  else:
    get_all_conf()

  """
  print startTime 
  print readlineTime
  print getconfTime 
  print getconfStop

  print "---> :      %s" % (readlineTime - startTime)
  print "Readlins:   %s" % (getconfTime - readlineTime)
  print "Print conf: %s" % (getconfStop - getconfTime)
  print "Total:      %s" % (getconfStop - startTime)
  """


if __name__ == "__main__":
  main()
