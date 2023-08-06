import fnmatch
import threading
import xmlrpclib

from supervisor.supervisorctl import ControllerPluginBase


class QuickControllerPlugin(ControllerPluginBase):
    name = "quick"

    def __init__(self, controller, **config):
        self.ctl = controller

    def _quick_do(self, arg, command):
        assert command in ("start", "stop", "restart")

        patterns = arg.strip().split()
        if not patterns:
            return self.ctl.output('No process matched given expression.')

        # compatible with group
        patterns = [p + '*' if p.endswith(':') else p for p in patterns]

        # if 'all' pattern exists, match all.
        if "all" in patterns or '*' in patterns:
            patterns = ['*']

        processes = set()
        for p in self.ctl.get_supervisor().getAllProcessInfo():
            p_name = "{}:{}".format(p["group"], p["name"])
            for pattern in patterns:
                if fnmatch.fnmatch(p_name, pattern):
                    processes.add(p_name)
                    break

        def _do(process):
            supervisor = self.ctl.get_supervisor()
            _command = getattr(supervisor, "{}Process".format(command))
            try:
                _command(process, False)
                self.ctl.output("{}: {}ed".format(process, command))
            except xmlrpclib.Fault as e:
                self.ctl.output("{} ERROR({})".format(
                    process, e.faultString.split(':')[0]))

        threads = []
        for p in processes:
            # set wait to False to do it quick
            t = threading.Thread(target=_do, args=(p,))
            t.start()
            threads.append(t)

        for t in threads:
            t.join()

    def do_quickstop(self, arg):
        self._quick_do(arg, command='stop')

    def do_quickstart(self, arg):
        self._quick_do(arg, command='start')

    def do_quickrestart(self, arg):
        pass


def make_quick_controllerplugin(controller, **config):
    return QuickControllerPlugin(controller, **config)
