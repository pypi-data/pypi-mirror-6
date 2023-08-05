## -*- coding: utf-8 -*-
##
## settings.py
##
## Author:   Toke Høiland-Jørgensen (toke@toke.dk)
## Date:     25 november 2012
## Copyright (c) 2012, Toke Høiland-Jørgensen
##
## This program is free software: you can redistribute it and/or modify
## it under the terms of the GNU General Public License as published by
## the Free Software Foundation, either version 3 of the License, or
## (at your option) any later version.
##
## This program is distributed in the hope that it will be useful,
## but WITHOUT ANY WARRANTY; without even the implied warranty of
## MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
## GNU General Public License for more details.
##
## You should have received a copy of the GNU General Public License
## along with this program.  If not, see <http://www.gnu.org/licenses/>.

import sys, os, optparse, socket, subprocess

from datetime import datetime

from fnmatch import fnmatch

try:
    from collections import OrderedDict
except ImportError:
    from netperf_wrapper.ordereddict import OrderedDict
from netperf_wrapper.resultset import ResultSet
from netperf_wrapper.build_info import DATA_DIR, VERSION
from netperf_wrapper import util

DEFAULT_SETTINGS = {
    'NAME': None,
    'HOST': None,
    'HOSTS': [],
    'LOCAL_HOST': socket.gethostname(),
    'STEP_SIZE': 0.2,
    'LENGTH': 60,
    'OUTPUT': '-',
    'FORMAT': 'default',
    'TITLE': '',
    'NOTE': '',
    'LOG_FILE': None,
    'INPUT': [],
    'DESCRIPTION': 'No description',
    'PLOTS': {},
    'IP_VERSION': None,
    'DELAY': 5,
    'TIME': datetime.now(),
    'SCALE_DATA': [],
    'SCALE_MODE': False,
    'ANNOTATE': True,
    'PRINT_TITLE': True,
    'PRINT_LEGEND': True,
    'ZERO_Y': False,
    'LOG_SCALE': True,
    }

TEST_PATH = os.path.join(DATA_DIR, 'tests')
DICT_SETTINGS = ('DATA_SETS', 'PLOTS')

def version(*args):
    print("Netperf-wrapper v%s.\nRunning on Python %s." %(VERSION, sys.version.replace("\n", " ")))
    try:
        import matplotlib
        print("Using matplotlib version %s on numpy %s." % (matplotlib.__version__, matplotlib.__version__numpy__))
    except ImportError:
        print("No matplotlib found. Plots won't be available.")
    sys.exit(0)


class Glob(object):
    """Object for storing glob patterns in matches"""

    def __init__(self, pattern, exclude=None):
        if exclude is None:
            self.exclude = []
        else:
            self.exclude = exclude
        self.pattern = pattern

    def filter(self, values, exclude):
        exclude += self.exclude
        return [x for x in values if fnmatch(x, self.pattern) and x not in exclude]

    def __iter__(self):
        return iter((self,)) # allow list(g) to return [g]

    @classmethod
    def filter_dict(cls, d):
        # Expand glob patterns in parameters. Go through all items in the
        # dictionary looking for subkeys that is a Glob instance or a list
        # that has a Glob instance in it.
        for k,v in list(d.items()):
            for g_k in list(v.keys()):
                try:
                    v[g_k] = cls.expand_list(v[g_k], list(d.keys()), [k])
                except TypeError:
                    continue
        return d

    @classmethod
    def expand_list(cls, l, values, exclude=None):
        l = list(l) # copy list, turns lone Glob objects into [obj]
        if exclude is None:
            exclude = []
        # Expand glob patterns in list. Go through all items in the
        # list  looking for Glob instances and expanding them.
        for i in range(len(l)):
            pattern = l[i]
            if isinstance(pattern, cls):
                l[i:i+1] = pattern.filter(values, exclude)
        return l

class TestEnvironment(object):

    def __init__(self, env={}, informational=False):
        self.env = dict(env)
        self.env.update({
            'glob': Glob,
            'o': OrderedDict,
            'include': self.include_test,
            'min_host_count': self.require_host_count,
            'find_ping': self.find_ping,
            })
        self.informational = informational

    def execute(self, filename):
        try:
            exec(compile(open(filename).read(), filename, 'exec'), self.env)
            return self.env
        except (IOError, SyntaxError):
            raise RuntimeError("Unable to read test config file: '%s'" % filename)

    def include_test(self, name, env=None):
        self.execute(os.path.join(TEST_PATH, name))

    def find_ping(self, ip_version, interval, length, host):
        """Find a suitable ping executable, looking first for a compatible
        `fping`, then falling back to the `ping` binary. Binaries are checked
        for the required capabilities."""
        if ip_version == 6:
            suffix = "6"
        else:
            suffix = ""

        fping = util.which('fping'+suffix)
        ping = util.which('ping'+suffix)

        if fping is not None:
            proc = subprocess.Popen([fping, '-h'],
                                    stdout=subprocess.PIPE,
                                    stderr=subprocess.PIPE)
            out,err = proc.communicate()
            if "print timestamp before each output line" in str(out):
                # fping has timestamp option, use it
                # there's no timeout parameter for fping, calculate a total number
                # of pings to send
                count = length // interval + 1
                interval = int(interval * 1000)

                return "%s -D -p %d -c %d %s" % (fping, interval, count, host)

        if ping is not None:
            # No checks atm; should check for presence of -D parameter
            return "%s -D -i %.2f -w %d %s" % (ping, max(0.2, interval), length, host)

        raise RuntimeError("No suitable ping tool found.")


    def require_host_count(self, count):
        if len(self.env['HOSTS']) < count:
            if self.informational:
                self.env['HOSTS'] = ['dummy']*count
            elif 'DEFAULTS' in self.env and 'HOSTS' in self.env['DEFAULTS'] and self.env['DEFAULTS']['HOSTS']:
                # If a default HOSTS list is set, populate the HOSTS list with
                # values from this list, repeating as necessary up to count
                def_hosts = self.env['DEFAULTS']['HOSTS']
                host_c = len(self.env['HOSTS'])
                missing_c = count-host_c
                self.env['HOSTS'].extend((def_hosts * (missing_c//len(def_hosts)+1))[:missing_c])
                if not self.env['HOST']:
                    self.env['HOST'] = self.env['HOSTS'][0]
            else:
                raise RuntimeError("Need %d hosts, only %d specified" % (count, len(self.env['HOSTS'])))

parser = optparse.OptionParser(description='Wrapper to run concurrent netperf-style tests.',
                               usage="Usage: %prog [options] <host|test|input file ...> ")

parser.add_option("-o", "--output", action="store", type="string", dest="OUTPUT",
                  help="File to write processed output to (default standard out). The JSON "
                  "data file is written to the same directory as this file, if provided. "
                  "Otherwise, the data file is written to the current directory.")
parser.add_option("-i", "--input", action="append", type="string", dest="INPUT",
                  help="File to read input from (instead of running tests). Input files "
                  "can also be specified as unqualified arguments without using the -i switch.")
parser.add_option("-f", "--format", action="store", type="string", dest="FORMAT",
                  help="Select output format (plot, csv, org_table, stats). Default is no "
                  "processed output (just writes the JSON data file).")
parser.add_option("-p", "--plot", action="store", type="string", dest="PLOT",
                  help="Select which plot to output for the given test (implies -f plot). "
                  "Use the --list-plots option to see available plots.")
parser.add_option("-t", "--title-extra", action="store", type="string", dest="TITLE",
                  help="Text to add to plot title and data file name.")
parser.add_option("-n", "--note", action="store", type="string", dest="NOTE",
                  help="Add arbitrary text as a note to be stored in the JSON data file "
                  "(under the NOTE key in the metadata object).")


test_group = optparse.OptionGroup(parser, "Test configuration",
                                  "These options affect the behaviour of the test being run "
                                  "and have no effect when parsing input files.")
test_group.add_option("-H", "--host", action="append", type="string", dest="HOSTS", metavar='HOST',
                  help="Host to connect to for tests. For tests that support it, multiple hosts "
                  "can be specified by supplying this option multiple times. Hosts can also be "
                  "specified as unqualified arguments; this parameter guarantees that the "
                  "argument be interpreted as a host name (rather than being subject to "
                  "auto-detection between input files, hostnames and test names).")
test_group.add_option("-l", "--length", action="store", type="int", dest="LENGTH",
                  help="Base test length (some tests may add some time to this).")
test_group.add_option("-s", "--step-size", action="store", type="float", dest="STEP_SIZE",
                  help="Measurement data point step size.")
test_group.add_option("-d", "--delay", action="store", type="int", dest="DELAY",
                  help="Number of seconds to delay parts of test (such as bandwidth "
                  "loaders).")
test_group.add_option("-4", "--ipv4", action="store_const", const=4, dest="IP_VERSION",
                  help="Use IPv4 for tests (some tests may ignore this).")
test_group.add_option("-6", "--ipv6", action="store_const", const=6, dest="IP_VERSION",
                  help="Use IPv6 for tests (some tests may ignore this).")
parser.add_option_group(test_group)

plot_group = optparse.OptionGroup(parser, "Plot configuration",
                                  "These options are used to configure the appearance of "
                                  "plot output and only make sense combined with -f plot.")

plot_group.add_option("-z", "--zero-y", action="store_true", dest="ZERO_Y",
                  help="Always start y axis of plot at zero, instead of auto-scaling the "
                  "axis (also disables log scales). Auto-scaling is still enabled for the "
                  "upper bound.")
plot_group.add_option("--disable-log", action="store_false", dest="LOG_SCALE",
                  help="Disable log scales on plots.")
plot_group.add_option("--scale-data", action="append", type="string", dest="SCALE_DATA",
                  help="Additional data files to consider when scaling the plot axes "
                  "(for plotting several plots with identical axes). "
                  "Can be supplied multiple times; see also --scale-mode.")
plot_group.add_option("-S", "--scale-mode", action="store_true", dest="SCALE_MODE",
                  help="Treat file names (except for the first one) passed as unqualified "
                  "arguments as if passed as --scale-data (default as if passed as --input).")
plot_group.add_option("--no-annotation", action="store_false", dest="ANNOTATE",
                  help="Exclude annotation with hostnames, time and test length from plots.")
plot_group.add_option("--no-legend", action="store_false", dest="PRINT_LEGEND",
                  help="Exclude legend from plots.")
plot_group.add_option("--no-title", action="store_false", dest="PRINT_TITLE",
                  help="Exclude title from plots.")
parser.add_option_group(plot_group)


misc_group = optparse.OptionGroup(parser, "Misc and debugging options")
misc_group.add_option("-L", "--log-file", action="store", type="string", dest="LOG_FILE",
                  help="Write debug log (test program output) to log file.")
misc_group.add_option('--list-tests', action='store_true', dest="LIST_TESTS",
                  help="List available tests and exit.")
misc_group.add_option('--list-plots', action='store_true', dest="LIST_PLOTS",
                  help="List available plots for selected test and exit.")
misc_group.add_option("-V", "--version", action="callback", callback=version,
                  help="Show netperf-wrapper version information and exit.")
parser.add_option_group(misc_group)

class Settings(optparse.Values, object):

    def check_testname(self, test_name):
        filename = os.path.join(TEST_PATH, test_name + ".conf")

        if not os.path.exists(filename):
            # Test not found, assume it's a hostname
            self.HOSTS.append(test_name)
        elif self.NAME is not None and self.NAME != test_name:
            raise RuntimeError("Multiple test names specified.")
        else:
            self.NAME = test_name


    def load_test(self, test_name=None, informational=False):
        if test_name is not None:
            self.NAME=test_name
        if self.NAME is None:
            raise RuntimeError("Missing test name.")
        if self.HOSTS:
            self.HOST = self.HOSTS[0]

        self.lookup_hosts()

        test_env = TestEnvironment(self.__dict__, informational)
        filename = os.path.join(TEST_PATH, self.NAME + ".conf")
        s = test_env.execute(filename)

        for k,v in list(s.items()):
            if k == k.upper():
                setattr(self, k, v)

        if 'DEFAULTS' in s:
            for k,v in list(s['DEFAULTS'].items()):
                if not hasattr(self, k):
                    setattr(self, k, v)

        if not 'TOTAL_LENGTH' in s:
            self.TOTAL_LENGTH = self.LENGTH

    def lookup_hosts(self):
        """If no explicit IP version is set, do a hostname lookup and try to"""
        version = 4
        for h in self.HOSTS:
            try:
                hostnames = socket.getaddrinfo(h, None, socket.AF_UNSPEC,
                                               socket.SOCK_STREAM)
                if not hostnames:
                    raise RuntimeError("Found no hostnames on lookup of %s" % h)
                hostname = hostnames[0]
                if hostname[0] == socket.AF_INET6:
                    version = 6
            except socket.gaierror as e:
                raise RuntimeError("Hostname lookup failed for host %s: %s" % (h,e))

        if self.IP_VERSION is None:
            self.IP_VERSION = version

    def __setattr__(self, k, v):
        if k in DICT_SETTINGS and isinstance(v, list):
            v = OrderedDict(v)

        object.__setattr__(self, k, v)

    def update(self, values):
        for k,v in list(values.items()):
            setattr(self, k, v)

settings = Settings(DEFAULT_SETTINGS)


def load():
    (dummy,args) = parser.parse_args(values=settings)

    if hasattr(settings, 'LIST_TESTS') and settings.LIST_TESTS:
        list_tests()

    if hasattr(settings, 'PLOT'):
        settings.FORMAT = 'plot'

    for a in args:
        if os.path.exists(a):
            if settings.SCALE_MODE and settings.INPUT:
                settings.SCALE_DATA.append(a)
            else:
                settings.INPUT.append(a)
        else:
            settings.check_testname(a)

    if settings.INPUT:
        results = []
        test_name = None
        for filename in settings.INPUT:
            r = ResultSet.load_file(filename)
            if test_name is not None and test_name != r.meta("NAME"):
                raise RuntimeError("Result sets must be from same test (found %s/%s)" % (test_name, r.meta("NAME")))
            test_name = r.meta("NAME")
            results.append(r)


        settings.update(results[0].meta())
        settings.load_test()
    else:
        settings.load_test()
        results = [ResultSet(NAME=settings.NAME,
                            HOST=settings.HOST,
                            HOSTS=settings.HOSTS,
                            TIME=settings.TIME,
                            LOCAL_HOST=settings.LOCAL_HOST,
                            TITLE=settings.TITLE,
                            NOTE=settings.NOTE,
                            LENGTH=settings.LENGTH,
                            TOTAL_LENGTH=settings.TOTAL_LENGTH,
                            STEP_SIZE=settings.STEP_SIZE,)]

    if settings.SCALE_DATA:
        scale_data = []
        for filename in settings.SCALE_DATA:
            if filename == settings.INPUT:
                # Do not load input file twice - makes it easier to select a set
                # of files for plot scaling and supply each one to -i without
                # having to change the other command line options each time.
                continue
            r = ResultSet.load_file(filename)
            if r.meta("NAME") != settings.NAME:
                raise RuntimeError("Setting name mismatch between test "
                                   "data and scale file %s" % filename)
            scale_data.append(r)
        settings.SCALE_DATA = scale_data


    if hasattr(settings, 'LIST_PLOTS') and settings.LIST_PLOTS:
        list_plots()

    if not settings.HOSTS and not results:
        raise RuntimeError("Must specify host (-H option).")

    return settings, results

def list_tests():
    tests = sorted([os.path.splitext(i)[0] for i in os.listdir(TEST_PATH) if i.endswith('.conf')])
    sys.stderr.write('Available tests:\n')
    max_len = max([len(t) for t in tests])
    for t in tests:
        settings.update(DEFAULT_SETTINGS)
        settings.load_test(t, informational=True)
        desc = settings.DESCRIPTION.replace("\n", "\n"+" "*(max_len+6))
        sys.stderr.write(("  %-"+str(max_len)+"s :  %s\n") % (t, desc))
    sys.exit(0)

def list_plots():
    plots = list(settings.PLOTS.keys())
    if not plots:
        sys.stderr.write("No plots available for test '%s'.\n" % settings.NAME)
        sys.exit(0)

    sys.stderr.write("Available plots for test '%s':\n" % settings.NAME)
    max_len = str(max([len(p) for p in plots]))
    for p in plots:
        sys.stderr.write(("  %-"+max_len+"s :  %s\n") % (p, settings.PLOTS[p]['description']))
    sys.exit(0)
