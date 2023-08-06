#!/usr/bin/python
#------------------------------------------------------------------------------
# Copyright 2013-2014 Numenta Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#------------------------------------------------------------------------------
""" Grok Custom Metrics sample data collector.  Run this periodically using
    a scheduler such as cron to report open file descriptors (the total number
    of files open by all processes).
"""
import datetime
import subprocess
import time

from grokcli.api import GrokSession
try:
  from sample_credentials import (GROK_API_KEY,
                                  GROK_SERVER,
                                  METRIC_NAME)
except (SyntaxError, ImportError):
  print ("\nERROR: You must update Grok credentials in sample_credentials.py "
         "before you can continue.\n")
  import sys
  sys.exit(1)

if __name__ == "__main__":
  # Grok client
  grok = GrokSession(server=GROK_SERVER, apikey=GROK_API_KEY)

  today = datetime.date.today()
  ts = datetime.datetime(today.year, today.month, today.day)

  # Add custom metric data
  with grok.connect(port=49153) as sock:
    for (x, delta) in enumerate(range(0, 24*60*60, 60)):
      msg = "%s %s %d\n" % ("foo.bar", x, time.mktime(ts.timetuple()))
      ts += datetime.timedelta(seconds=delta)
      sock.sendall(msg)

