"""
Core package

.. autosummary::

    Sotong
"""
import os
import datetime
from functools import wraps
import time
import tempfile
import threading
import logging
import webbrowser

from fabric.api import local, lcd, settings

from . import log, event

class Sotong(object):

    def __init__(self, tmp_dir=None, watch_interval=10, autoreload=False):
        if tmp_dir:
            self.tmp_dir = tmp_dir
        else:
            self.tmp_dir = tempfile.mkdtemp()
        self._watch_interval = watch_interval
        self._autoreload = autoreload
        self.logger = log.get_logger()
        self.scheduler = event.Scheduler()
        self.watch_observer = event.WatchObserver()

    def run(self):
        self.logger.addHandler(logging.StreamHandler())
        self.logger.addHandler(log.JSONLogHandler(os.path.join(self.tmp_dir,
                                                               "litebot.log")))
        print "##### START litebot tmp_dir=%s #####" % self.tmp_dir

        self.scheduler_thread = threading.Thread(target=self.scheduler.run, args=[])
        self.scheduler_thread.daemon = True
        self.scheduler_thread.start()
        self.watch_observer.start()
        try:
            while True:
                time.sleep(self._watch_interval)
        except KeyboardInterrupt:
            self.watch_observer.stop()
        self.watch_observer.join()
        print "##### STOP litebot tmp_dir=%s #####" % self.tmp_dir

    def watch(self, path, event_types=None):
        if not event_types:
            event_types = ("modified", )
        def decorator(f):
            @wraps(f)
            def decorated_function(event):
                if event.event_type in event_types:
                    f(event)
            event_handler = event.WatchEventHandler(decorated_function)
            self.watch_observer.schedule(event_handler, path=path, recursive=True)
            return decorated_function
        return decorator

    def interval(self, time):
        def decorator(f):
            @wraps(f)
            def decorated_function():
                self.scheduler.enter(time, 1, decorated_function, ())
                f()
            self.scheduler.enter(time, 1, decorated_function, ())
            return decorated_function
        return decorator

    def daily(self, hour, minutes, seconds):
        def decorator(f):
            @wraps(f)
            def decorated_function():
                f()
            datetime_time = datetime.time(hour, minutes, seconds)
            datetime_datetime = datetime.datetime.combine(datetime.datetime.now(),
                                                          datetime_time)
            daily_time = time.mktime(datetime_datetime.timetuple())
            if daily_time < time.time():
                return
            self.scheduler.enterabs(daily_time, 2, decorated_function, ())
            return decorated_function
        return decorator

    def alert(self, message):
        path = os.path.join(self.tmp_dir, "alert.html")
        with open(path, "w") as f:
            f.write("<pre>%s</pre>" % message)
        webbrowser.open("file://" + path, autoraise=True)

    def shell(self, command):
        with settings(warn_only=True):
            return local(command, capture=True)

    def cd(self, path):
        return lcd(path)
