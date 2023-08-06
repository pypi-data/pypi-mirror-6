#!/usr/bin/env python
""""Generate build profile"""

from subprocess import Popen, PIPE
import argparse
import os
import time
import json
import traceback
import socket
import threading
import webbrowser
import SocketServer
import SimpleHTTPServer


class statsThread (threading.Thread):
    IN_HEADER = 0
    IN_PROCESSES = 1

    last_ccache_stats = None

    def __init__(self, opts):
        threading.Thread.__init__(self)
        self.opts = opts
        self.last_ccache_stats = None
        self.done = False

    def getCCacheStats(self, curSample, ccacheDir):
        stats = None
        for i in xrange(16):
            fn = os.path.join(ccacheDir, format(i, 'x'), "stats")
            if os.path.exists(fn):
                with open(fn, 'r') as f:
                    # Get all numbers from file
                    stats_by_lines = [l.split() for l in f.readlines()]
                    # Use sum() to flatten a list of lists.
                    _stats = [int(n) for n in sum(stats_by_lines, [])]
                    if stats is None:
                        stats = _stats
                    else:
                        stats = [x + y for x, y in zip(stats, _stats)]
        if self.last_ccache_stats is None:
            if stats is not None:
                curSample['ccache_stats'] = [0] * len(stats)
            else:
                curSample['ccache_stats'] = []
        else:
            curSample['ccache_stats'] = [x - y for x, y in zip(stats, self.last_ccache_stats)]
        self.last_ccache_stats = stats

    def run(self):
        opts = self.opts
        FILE_HEADER = ('<html><meta http-equiv="REFRESH" content="0;url=\'%(UI_URI)s\'"></HEAD>'
                       '<body><a href="\'%(UI_URI)s\'">redirect</a></body></html><!--\n'
                       % dict(UI_URI=opts.ui_url))
        self.getCCacheStats(dict(), opts.ccache_dir)
        time.sleep(.1)
        self.getCCacheStats(dict(), opts.ccache_dir)
        state = self.IN_HEADER
        cur_sample = dict(tasks=[])
        first_time = time.time()
        out = None
        for line in Popen("COLUMNS=300 LANG=C top -b -c -d %s" % (opts.interval,),
                          shell=True, bufsize=1, stdout=PIPE).stdout:
            if self.done:
                return
            try:
                toks = line.split()
                if len(toks) < 1:
                    continue
                if state == self.IN_HEADER:
                    if toks[0] == "Mem:":
                        cur_sample["mem"] = toks[3]
                    elif toks[0].startswith("Cpu"):
                        cur_sample["cpu_user"] = toks[1].split("%")[0]
                        cur_sample["cpu_sys"] = toks[2].split("%")[0]
                    elif toks[0] == "PID":
                        state = self.IN_PROCESSES
                elif state == self.IN_PROCESSES:
                    if toks[0] == "top":
                        state = self.IN_HEADER
                        # if we never opened the file,
                        # or the file was erased by another process
                        if out is None or not os.path.exists(opts.full_output_file):
                            if out is not None:
                                out.close()
                            dirname = os.path.dirname(opts.full_output_file)
                            if not os.path.exists(dirname):
                                try:
                                    os.makedirs(dirname)
                                except OSError:
                                    pass  # race condition with other processes on dir creation
                            out = open(opts.full_output_file, "w")
                            out.write(FILE_HEADER)
                            first_time = time.time()
                        else:
                            out.write(",\n")
                        self.getCCacheStats(cur_sample, opts.ccache_dir)
                        cur_sample['time'] = int((time.time()-first_time)*1000)
                        out.write(json.dumps(cur_sample))
                        out.flush()
                        cur_sample = dict(tasks=[])
                    else:
                        user = toks[1]
                        cpu = toks[8]
                        if user == opts.user:
                            cmd = " ".join(toks[11:])
                            mem = toks[5]
                            if mem.endswith("k"):
                                mem = float(mem[:-1]) * 1024
                            elif mem.endswith("m"):
                                mem = float(mem[:-1]) * 1024 * 1024
                            elif mem.endswith("g"):
                                mem = float(mem[:-1]) * 1024 * 1024 * 1024
                            else:
                                mem = float(mem)
                            cur_sample["tasks"].append(dict(cpu=cpu, mem=mem, cmd=cmd))
            except Exception:
                traceback.print_exc()
                print "still continue"


def sibpath(*elts):
    return os.path.join(os.path.dirname(__file__), *elts)


class Handler(SimpleHTTPServer.SimpleHTTPRequestHandler):
    def list_disrectory(self, path):
        return None

    def translate_path(self, origpath):
        path = SimpleHTTPServer.SimpleHTTPRequestHandler.translate_path(self, origpath)
        if origpath.startswith("/buildprof"):
            path = sibpath(path.replace(os.getcwd()+"/buildprof/", "static/"))
        print origpath, path
        return path


def startBrowser(opts):

    os.chdir(opts.output_dir)
    httpd = None
    while httpd is None:
        try:
            httpd = SocketServer.TCPServer(("", opts.http_port), Handler, False)
        except socket.error:
            opts.http_port += 1
            "trying port", opts.http_port
    httpd.allow_reuse_address = True
    httpd.server_bind()
    httpd.server_activate()
    webbrowser.open("http://localhost:%d/%s" % (opts.http_port, opts.output_file))
    httpd.serve_forever()


def main():
    def relative_path(s):
        if "/" in s:
            raise ValueError(s + " must be a filename, without directory")
        return s

    # Global command-line arguments
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--user', action='store', default="whoami",
                        help='Filter process by user')
    parser.add_argument('--output_dir', action='store', default=".",
                        help='output result to directory')
    parser.add_argument('--output_file', action='store', type=relative_path, default=socket.gethostname() + ".html",
                        help='output filename')
    parser.add_argument('--interval', '-d', action='store', default="4",
                        help='interval in between gathering of statistics')
    parser.add_argument('--ccache_dir', action='store', default=os.path.expanduser("~/.ccache/"),
                        help='ccache dir where to get stats')
    parser.add_argument('--ui_url', action='store', default="/buildprof/index.html",
                        help='uri where is stored the angular js UI')
    parser.add_argument('--http_port', action='store', type=int, default=8000,
                        help='http port to use')
    parser.add_argument('--no_openbrowser', action='store_true',
                        help='dont open a browser at the end of the run')
    parser.add_argument('--test', action='store_true',
                        help='dont actuall run the command')
    parser.add_argument('commands', action='store', nargs=argparse.REMAINDER,
                        help='shell command to run while profiling')

    opts = parser.parse_args()
    opts.full_output_file = os.path.join(opts.output_dir, opts.output_file)
    if opts.user == "whoami":
        opts.user = os.environ["USER"]
    if not opts.test:
        thread = statsThread(opts)
        thread.start()
        os.system(" ".join(opts.commands))
        thread.done = True
        thread.join()

    if not opts.no_openbrowser:
        startBrowser(opts)
