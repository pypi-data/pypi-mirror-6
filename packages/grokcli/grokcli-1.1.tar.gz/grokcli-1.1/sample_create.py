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
""" Grok Custom Metrics sample application.

    This script will instruct Grok to start monitoring a custom metric called
    "open.file.descriptors".  You must first (and separately) create the custom
    metric by scheduling sample_collect_data.py with something like cron to
    periodically collect a sample and save the result to the
    "open.file.descriptors" custom metric.

    Be sure to update the contents of sample_credentials.py to reflect your
    Grok configuration.  You can obtain your Grok API key from the Grok web
    interface or by running the `grok credentials` command.
"""

import sys
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

    # Check metric created
    for metric in grok.listMetrics("custom"):
      if metric["name"] == METRIC_NAME:
        uid = metric["uid"]
        print 'Metric "%s" has uid: %s' % (METRIC_NAME, uid)
        break
    else:
      print ('"%s" metric does not exist (yet).  You can create the metric by'
             ' sending data to Grok.  See "sample-collect-data.py" for a'
             " simple script that you can use to periodically sample open"
             " file  descriptors, and report the results to the Grok Custom"
             " Metrics endpoint" % METRIC_NAME)

    # Send model creation request to create a model connected to the metric
    models = grok.createModel({"uid": uid, "datasource": "custom"})

    model = models[0]
    assert model["uid"] == uid
    assert model["name"] == METRIC_NAME

    # Get model status
    for _ in xrange(30):
      modelResponse = grok.get(grok.server + "/_models/" + uid, auth=grok.auth)
      models = modelResponse.json()
      model = models[0]
      if model["status"] == 1:
        break
      time.sleep(10)
    else:
      raise Exception('Model did not transition to "ready" status in a '
                      "reasonable amount of time.")

    print ('Your model is ready and Grok is actively monitoring the "%s"'
           " custom metric.  You can monitor the progress in the Grok Android"
           " Client." % METRIC_NAME)
