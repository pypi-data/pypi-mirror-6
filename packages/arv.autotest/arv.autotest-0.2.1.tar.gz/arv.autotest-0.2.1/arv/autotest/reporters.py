# -*- coding: utf-8 -*-

# $Id: reporters.py 904 2014-04-25 19:56:50Z alex $

"""A *reporter* is a class intended to consume the output produced by
a *runner*. Usually a reporter will produce output for human
consumption but it may as well act as a filter for other reporters.

A reporter must define three methods:

:start(): called at the beggining.

:feed(data): process a chunk of data produced by the runner.

:stop(return_code): the runner has finished with ``return_code``.

"""

from __future__ import print_function
from datetime import datetime
import sys
import time

from blessings import Terminal


class LineAssemblerReporter(object):
    """Assembles data into lines.

    The purpose of this reporter is assembling chunks of data into
    lines and then feeding them to a wrapped reporter one line at a
    time.

    """

    def __init__(self, wrapped):
        self._wrapped = wrapped
        self._data = []

    def start(self):
        self._wrapped.start()

    def feed(self, data):
        while "\n" in data:
            left, data = data.split("\n", 1)
            self._data.append(left)
            self._data.append("\n")
            self._feed_wrapped()
        if data:
            self._data.append(data)

    def stop(self, code):
        if self._data:
            self._feed_wrapped()
        self._wrapped.stop(code)

    def _feed_wrapped(self):
        self._wrapped.feed("".join(self._data))
        self._data = []


class TerminalReporter(object):
    """Displays data to a terminal.

    This reporter displays the received data into a terminal. On stop
    displays a highlighted message: green indicates success and red
    error.

    """

    def __init__(self, stdout=sys.stdout):
        self.stdout = stdout
        self.term = Terminal(stream=stdout)
        self.counter = 0
        self.width = self.term.width if self.term.is_a_tty else 80 # when testing t.width is None

    def start(self):
        self.counter += 1

    def feed(self, line):
        print(line, file=self.stdout, end="")

    def stop(self, code):
        if code:
            formatter = self.term.bold_white_on_red
            message = "ERROR"
        else:
            formatter = self.term.bold_white_on_green
            message = "OK"
        stamp = "%3i " % self.counter + datetime.now().strftime("%H:%M:%S %d/%m/%Y")
        message = message.center(self.width - 1 - len(stamp), " ")

        print("", file=self.stdout)
        print(formatter(stamp + message), file=self.stdout)


class NullReporter(object):
    """Discards the input it receives.

    This reporter displays a message on start and stop, ignoring the
    input which is feed with. Useful for debuging.

    """
    def __init__(self):
        self.term = Terminal()

    def start(self):
        print(self.term.white_on_blue("Starting null reporter."))

    def feed(self, data):
        pass

    def stop(self, code):
        print(self.term.white_on_blue("Stoping null reporter. Return code: %i" % code))


class DynamicThrottling(object):
    """Dynamically adjust throttling.

    This reporter measures the time required to run the program and
    adjust the throttling rate.

    """
    def __init__(self, throttler, timer=time.time):
        self._start = 0
        self._throttler = throttler
        self._timer = timer

    def start(self):
        self._start = self._timer()

    def feed(self, data):
        pass

    def stop(self, code):
        delta = self._timer() - self._start
        if delta > 0:
            self._throttler.adjust_delta(delta)


class Repeater(object):
    """Chains reporters.
    """
    def __init__(self, *reporters):
        self._reporters = reporters

    def start(self):
        for reporter in self._reporters:
            reporter.start()

    def feed(self, data):
        for reporter in self._reporters:
            reporter.feed(data)

    def stop(self, code):
        for reporter in self._reporters:
            reporter.stop(code)

