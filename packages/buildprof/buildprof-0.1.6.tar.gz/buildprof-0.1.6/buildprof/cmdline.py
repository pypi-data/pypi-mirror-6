#!/usr/bin/env python
""""Generate build profile"""

import SimpleHTTPServer
import SocketServer
import argparse
import json
import os
import socket
import threading
import time
import traceback
import webbrowser

from subprocess import PIPE
from subprocess import Popen


class statsThread(threading.Thread):
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
        CCACHE_NUM_SUB_DIRS = 16
        for i in xrange(CCACHE_NUM_SUB_DIRS):
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

    def initStateMachine(self):
        self.FILE_HEADER = ('<html><meta http-equiv="REFRESH" content="0;url=\'%(UI_URI)s\'"></HEAD>'
                            '<body><a href="\'%(UI_URI)s\'">redirect</a></body></html><!--\n'
                            % dict(UI_URI=self.opts.ui_url))
        self.getCCacheStats(dict(), self.opts.ccache_dir)
        self.state = self.IN_HEADER
        self.curSample = dict(tasks=[])
        self.firstTime = time.time()
        self.out = None

    def run(self):
        self.initStateMachine()
        for line in Popen("COLUMNS=300 LANG=C top -b -c -d %s" % (self.opts.interval,),
                          shell=True, bufsize=1, stdout=PIPE).stdout:
            if self.done:
                return
            try:
                self.parseOneLine(line)
            except Exception:
                traceback.print_exc()
                print "still continue"

    def parseOneLine(self, line):
        toks = line.split()
        if not toks:
            return
        if self.state == self.IN_HEADER:
            self.parseHeader(toks)
        elif self.state == self.IN_PROCESSES:
            self.parseProcesses(toks)

    def parseHeader(self, toks):
        if toks[0] == "Mem:":
            self.curSample["mem"] = toks[3]
        elif toks[0].startswith("Cpu"):
            self.curSample["cpu_user"] = toks[1].split("%")[0]
            self.curSample["cpu_sys"] = toks[2].split("%")[0]
        elif toks[0] == "PID":
            self.state = self.IN_PROCESSES

    def parseMem(self, mem):
        if mem.endswith("k"):
            mem = float(mem[:-1]) * 1024
        elif mem.endswith("m"):
            mem = float(mem[:-1]) * 1024 * 1024
        elif mem.endswith("g"):
            mem = float(mem[:-1]) * 1024 * 1024 * 1024
        else:
            mem = float(mem)
        return mem

    def parseProcesses(self, toks):
        if toks[0] == "top":
            self.state = self.IN_HEADER
            self.writeSample(self.curSample)
            self.curSample = dict(tasks=[])
        else:
            user = toks[1]
            cpu = toks[8]
            if user == self.opts.user:
                cmd = " ".join(toks[11:])
                mem = self.parseMem(toks[5])
                self.curSample["tasks"].append(dict(cpu=cpu, mem=mem, cmd=cmd))

    def writeSample(self, curSample):
        # if we never opened the file,
        # or the file was erased by another process
        if self.out is None or not os.path.exists(self.opts.full_output_file):
            if self.out is not None:
                self.out.close()
            dirname = os.path.dirname(self.opts.full_output_file)
            if not os.path.exists(dirname):
                try:
                    os.makedirs(dirname)
                except OSError:
                    pass  # race condition with other processes on dir creation
            self.out = open(self.opts.full_output_file, "w")
            self.out.write(self.FILE_HEADER)
            self.firstTime = time.time()
        else:
            self.out.write(",\n")
        self.getCCacheStats(curSample, self.opts.ccache_dir)
        curSample['time'] = int((time.time() - self.firstTime) * 1000)
        self.out.write(json.dumps(curSample))
        self.out.flush()


def sibpath(*elts):
    return os.path.join(os.path.dirname(__file__), *elts)


class Handler(SimpleHTTPServer.SimpleHTTPRequestHandler):
    # those function are overrides from python stdlib

    def list_directory(self, path):
        return None

    def translate_path(self, origpath):
        path = SimpleHTTPServer.SimpleHTTPRequestHandler.translate_path(self, origpath)
        if origpath.startswith("/buildprof"):
            path = sibpath(path.replace(os.getcwd() + "/buildprof/", "static/"))
        print origpath, path
        return path


def startBrowser(opts):
    if opts.output_dir:
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
    def fileNameWithoutPath(s):
        if os.sep in s:
            raise ValueError("%s must be a filename, without '%s'" % (s, os.sep))
        return s

    # Global command-line arguments
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--user', action='store', default="whoami",
                        help='Filter process by user')
    parser.add_argument('--output_dir', action='store', default=".",
                        help='output result to directory')
    parser.add_argument('--output_file', action='store', type=fileNameWithoutPath,
                        default=socket.gethostname() + ".html",
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
    parser.add_argument('commands', action='store', nargs=argparse.REMAINDER,
                        help='shell command to run while profiling, or html file to view')

    opts = parser.parse_args()
    opts.full_output_file = os.path.join(opts.output_dir, opts.output_file)
    if opts.user == "whoami":
        opts.user = os.environ["USER"]

    # shortcut to be able to run "buildprof /path/to/output.html", and just view the html results
    maybeHtmlFile = opts.commands[0]
    if os.path.exists(maybeHtmlFile) and maybeHtmlFile.endswith(".html"):
        opts.output_dir = os.path.dirname(maybeHtmlFile)
        opts.output_file = os.path.basename(maybeHtmlFile)
    else:
        thread = statsThread(opts)
        thread.start()
        os.system(" ".join(opts.commands))
        thread.done = True
        thread.join()

    if not opts.no_openbrowser:
        startBrowser(opts)
