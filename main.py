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

__author__ = 'Eric Bidelman <ebidel@>'

import os
import webapp2

from google.appengine.ext.webapp import template

import http2push as http2

# # TODO(ericbidelman): investigate + remove
# # ATM, this is necessary to only add the vulcanized bundle URL when it's actually
# # being requested by the browser. There appears to be a bug in GAE s.t. other
# # files won't be pushed if one of the URLs is never requested by the browser.
# # by the browser.
# def fixup_for_vulcanize(vulcanize, urls):
#   """Replaces element.html URL with a vulcanized version or
#      elements.vulcanize.html with the unvulcanized version.

#     Args:
#         vulcanize: True if the URL should be replaced by the vulcanized version.
#         urls: A dict of url: priority mappings.

#     Returns:
#         An update dict of URL mappings.
#   """

#   # TODO: don't hardcode adding the vulcanized import bundle.
#   UNVULCANIZED_FILE = 'elements.html'
#   VULCANIZED_FILE = 'elements.vulcanize.html'

#   for url,priority in urls.iteritems():
#     if vulcanize is not None:
#       if url.endswith(UNVULCANIZED_FILE):
#         url = url.replace(UNVULCANIZED_FILE, VULCANIZED_FILE)
#     else:
#       if url.endswith(VULCANIZED_FILE):
#         url = url.replace(VULCANIZED_FILE, UNVULCANIZED_FILE)

#   return urls

# # Example - regular handler, explicitly setting headers.
# class RegularHandler(http2.PushHandler):

#   def get(self):
#     vulcanize = self.request.get('vulcanize', None)

#     # TODO: Remove (see above).
#     #fixup_for_vulcanize(vulcanize, self.push_urls)

#     # HTTP2 server push resources?
#     if self.request.get('nopush', None) is None:

#       # Send X-Associated-Content header.
#       self.response.headers.add_header(
#           'X-Associated-Content',
#           self._generate_associate_content_header())

#       # Send Link: <URL>; rel="preload" header.
#       headers = self._generate_link_preload_headers()
#       if type(headers) is list:
#         for h in headers:
#           self.response.headers.add_header('Link', h)
#       else:
#         self.response.headers.add_header('Link', headers)

#     path = os.path.join(os.path.dirname(__file__), 'static/index.html')

#     return self.response.out.write(template.render(path, {
#       'vulcanize': vulcanize is not None
#       }))

class DecoratedHandler(http2.PushHandler):

  @http2.push('push_manifest.json')
  def get(self):
    vulcanize = self.request.get('vulcanize', None)

    # TODO: Remove (see above).
    #fixup_for_vulcanize(vulcanize, self.push_urls)

    path = os.path.join(os.path.dirname(__file__), 'static/index.html')

    return self.response.out.write(template.render(path, {
      'vulcanize': vulcanize is not None
      }))


app = webapp2.WSGIApplication([
    ('/', DecoratedHandler),
], debug=True)
