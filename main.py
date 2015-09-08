#!/usr/bin/env python
#
# Copyright 2015 Google Inc.
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
#

import json
import os
import logging
import re
import time
import webapp2

from google.appengine.ext.webapp import template


class SlowHandler(webapp2.RequestHandler):

  def get(self, f):
    time.sleep(1) # simluate slow response.
    self.response.headers['Cache-Control'] = 'private, max-age=100'
    self.response.headers['Content-Type'] = 'text/css'
    self.response.out.write('''
body {
  font-style: italic;
}
''')

class MainHandler(webapp2.RequestHandler):

  def __generate_associate_content_header(self, urls):
    # https://code.google.com/p/mod-spdy/wiki/OptimizingForSpdy
    # The format of the header value is a comma-separated list of
    # double-quoted URLs, each of which may optionally be followed by a
    # colon and a SPDY priority number (from 0 to 7 inclusive). URL needs to be
    # a full absolute URL. Whitespace between tokens
    # is optional, and is ignored if present. For example:
    #
    #   X-Associated-Content: "https://www.example.com/styles/foo.css",
    #       "/scripts/bar.js?q=4":2, "https://www.example.com/images/baz.png": 5,
    #        "https://www.example.com/generate_image.php?w=32&h=24"

    # Proposed header:
    # http://blog.kazuhooku.com/2015/02/ann-h2o-version-092-released-incl.html

    host = self.request.host_url
    vulcanize = self.request.get('vulcanize', None)

    associate_content = []
    for url,v in urls.iteritems():
      url = str(url)

      # TODO: only add vulcanized bundle if being requested by the browser.
      # This appears to be a bug in Chrome or GAE that stops app.css from
      # being pushed if you have a file in the header that's never requested
      # by the browser.

      # TODO: don't hardcode adding the vulcanized import bundle.
      if vulcanize is not None:
        if url.endswith('elements.html'):
          url = url.replace('elements.html', 'elements.vulcanize.html')
      else:
        if url.endswith('elements.vulcanize.html'):
          url = url.replace('elements.vulcanize.html', 'elements.html')

      if v is not None:
        associate_content.append('"%s%s":%s' % (host, url, str(v)))
      else:
        associate_content.append('"%s%s"' % (host, url))

    associate_content = list(set(associate_content)) # remove duplicates

    return ','.join(associate_content)

  def get(self):
    vulcanize = self.request.get('vulcanize', None)

    # HTTP2 server push resources?
    if self.request.get('nopush', None) is None:
      with open('push_manifest.json') as f:
        urls = json.loads(f.read())
      associate_content_header = self.__generate_associate_content_header(urls)
      self.response.headers.add_header('X-Associated-Content', associate_content_header)

    path = os.path.join(os.path.dirname(__file__), 'static/index.html')

    self.response.out.write(template.render(path, {
      'vulcanize': vulcanize is not None
      }))


app = webapp2.WSGIApplication([
    ('/', MainHandler),
    ('/css/(.*)', SlowHandler)
], debug=True)
