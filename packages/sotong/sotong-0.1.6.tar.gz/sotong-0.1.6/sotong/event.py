"""

.. autosummary::

    Scheduler
    WatchObserver
    WatchEventHandler
"""
import time
from functools import wraps

import sched
import watchdog
import watchdog.observers

from . import log


class Scheduler(object):

    def __init__(self):
        self._scheduler = sched.scheduler(time.time, time.sleep)
        self.logger = log.get_logger()
        self.before_callbacks = []
        self.after_callbacks = []

    def run(self):
        self._scheduler.run()

    def _wrap(self, callback):
        @wraps(callback)
        def wrapped_callback():
            try:
                for before in self.before_callbacks:
                    before()
                callback()
                for after in self.after_callbacks:
                    after()
            except Exception as e:
                self.logger.error(e, exc_info=True)
        return wrapped_callback

    def enter(self, time, priority, callback, args):
        self._scheduler.enter(time, priority, self._wrap(callback), args)

    def enterabs(self, time, priority, callback, args):
        self._scheduler.enterabs(time, priority, self._wrap(callback), args)


class WatchObserver(watchdog.observers.Observer):

    def __init__(self, *args, **kwargs):
        super(WatchObserver, self).__init__(*args, **kwargs)
        self.logger = log.get_logger()
        self.before_callbacks = []
        self.after_callbacks = []

    def dispatch_events(self, event_queue, timeout):
        """ override :py:func:`watchdog.observers.Observer.dispatch_event` """
        event, watch = event_queue.get(block=True, timeout=timeout)
        try:
            for before in self.before_callbacks:
                before(event)
            self._dispatch_event(event, watch)
            for after in self.after_callbacks:
                after(event)
        except Exception as e:
            self.logger.error(e, exc_info=True)
        event_queue.task_done()


class WatchEventHandler(watchdog.events.FileSystemEventHandler):

    def __init__(self, callback, *args, **kwargs):
        super(WatchEventHandler, self).__init__(*args, **kwargs)
        self.callback = callback

    def on_any_event(self, event):
        self.callback(event)

