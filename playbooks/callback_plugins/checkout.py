from ansible.constants import mk_boolean
from ansible import constants as C
from ansible.module_utils.urls import open_url
from ansible.errors import AnsibleError
from ansible.plugins.callback import CallbackBase

from datetime import datetime

try:
    import prettytable
    HAS_PRETTYTABLE = True
except ImportError:
    HAS_PRETTYTABLE = False

class CallbackModule(CallbackBase):
    """
    This callback module tells you how long your plays ran for.
    """
    CALLBACK_VERSION = 2.0
    CALLBACK_TYPE = 'stdout'
    CALLBACK_NAME = 'checkout'
    CALLBACK_NEEDS_WHITELIST = False

    def __init__(self):
        self.super_ref = super(CallbackModule, self)
        self.super_ref.__init__()
        self.invs = {}
        self.statuscodes = {}
        self.StartTime = datetime.now()
        self.Tasks = {}


    def parse(self, result, task_name):
        res = []
        if "results" in result:
            res = result["results"]
        for r in res:
            try:
                status = r["status"]
            except:
                status = "UNKNOWN"
            if status not in self.statuscodes.keys():
                self.statuscodes[status] = 0
            self.statuscodes[status] += 1

            jmsg = "OK"
            j = ""
            if "json" in r:
                j = r["json"]
                jmsg = j["message"]

            if "invocation" in r:
                invocation = r["invocation"]
                inv_body = invocation["module_args"]["body"]
                inv = " ".join(inv_body.keys())
                if inv not in self.invs:
                    self.invs[inv] = {}
                if status not in self.invs[inv]:
                    self.invs[inv][status] = 0
                self.invs[inv][status] += 1

            if task_name not in self.Tasks:
                self.Tasks[task_name] = {}
                self.Tasks[task_name]["count"] = 0
            self.Tasks[task_name]["count"] += 1

            msg = []
            """
            for key in inv_body[inv]:
                print key
                print
                print inv_body[inv]
                if "name" in key:
                    msg.append(inv_body[inv][key])
            """
            if status == 200:
                color = C.COLOR_CHANGED
            elif status == 201:
                color = C.COLOR_CHANGED
            elif status == 404 or status == 400:
                print inv_body
                color = C.COLOR_ERROR
            elif "Invalid" in jmsg:
                color = C.COLOR_ERROR
                
            else:
                color = C.COLOR_OK
            m = "   %s [%s]: %s" % (jmsg, status, ": ".join(msg))
            if status != 200 and status != 201:
                self._display.display(m, color=color)


    def v2_runner_on_ok(self, result, **kwargs):
        res = result._result
        failed = result._result.get("failed")
        task_name = result._task.name
        self.parse(res, task_name)
        self.Tasks[task_name]["EndTime"] = datetime.now()
        Time = (self.Tasks[task_name]["EndTime"] - self.Tasks[task_name]["StartTime"])
        self._display.display("   %s items completed" % self.Tasks[task_name]["count"], color = C.COLOR_OK)


    v2_runner_on_failed = v2_runner_on_ok
    v2_runner_on_unreachable = v2_runner_on_ok
    v2_runner_on_skipped = v2_runner_on_ok

    def v2_playbook_on_task_start(self, task, is_conditional):
        self.St = datetime.now()
        print
        print "%s:" % task.name
        task_name = task.name
        if task_name not in self.Tasks:
            self.Tasks[task_name] = {}
        self.Tasks[task_name]["count"] = 0
        self.Tasks[task_name]["StartTime"] = datetime.now()

    def playbook_on_stats(self, stats):
        EndTime = datetime.now()
        ok = 0
        not_changed = 0
        errors = 0
        for inv in self.invs:
            for stat in self.invs[inv]:
                if stat == 201:
                    ok += self.invs[inv][stat]
                elif stat == 200:
                    ok += self.invs[inv][stat]
                elif stat == 409:
                    not_changed += self.invs[inv][stat]
                elif stat in [599, 400, 404]:
                    errors += self.invs[inv][stat]
                else:
                    print "UNKNOWN STAT: ", stat


        max_len = len(max(self.Tasks, key=len)) + 2
        tl = len(str(EndTime - self.StartTime))
        title = "{0:<{1}} | {2:<{3}} | {4:<{5}} |".format("Task", max_len, "Items", len("Items") + 2, "Task Time", tl)
        l = len("{0:<{1}} | {2:<{3}} | {4:<{5}} |".format("Task", max_len, "Items", len("Items") + 2, (EndTime - self.StartTime), tl))
        print "-" * l
        print title
        print "-" * l
        
        for task in sorted(self.Tasks):
            tt = (self.Tasks[task]["EndTime"] - self.Tasks[task]["StartTime"])
            print "{0:<{1}} | {2:<{3}} | {4:<{5}} |".format(task, max_len, self.Tasks[task]["count"], len("Items") + 2, tt, tl)
        print "-" * l
        print
        summary = "New: %s   Unchanged: %s   Errors: %s   Time: %s" %(ok, not_changed, errors, (EndTime - self.StartTime))
        print summary
        for k, v in self.statuscodes.iteritems():
            print "  %s: %s" % (k, v)
