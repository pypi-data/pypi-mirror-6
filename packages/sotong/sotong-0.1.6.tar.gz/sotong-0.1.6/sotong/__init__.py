"""
============
Sotong
============

Sotong is a tiny automation tool like Jenkins, Buildbot, etc...

Based on

- `sched <http://docs.python.org/2/library/sched.html>`_
- `watchdog <https://github.com/gorakhargosh/watchdog>`_
- `fabric <https://github.com/fabric/fabric>`_

>>> from sotong.sotong import Sotong
>>> s = Sotong()
>>> @s.watch('/path/to/project')
... def project_file_modified(event):
...     with s.cd("/path/to/project/test"):
...         out = s.shell("python *.py")
...         if out.failed:
...             s.alert(out.stderr)
...             s.logger.info(out.stderr)
...         else:
...             s.logger.info(out.stdout)
...
>>> @s.interval(10)
... def interval():
...      import datetime
...      print datetime.datetime.now()
...
>>> @s.daily(7, 0, 0)
... def daily_task():
...     print "Good morning"
...
>>> s.run()
"""

__version__ = '0.1.6'
__author__ = 'wak'

