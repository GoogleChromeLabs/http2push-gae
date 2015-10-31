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
import sys
import jinja2
import webapp2

import http2push as http2

JINJA_ENVIRONMENT = jinja2.Environment(
    loader=jinja2.FileSystemLoader(os.path.dirname(__file__))
    )


# TODO(ericbidelman): investigate + remove
# ATM, this is necessary to only add the vulcanized bundle URL when it's actually
# being requested by the browser. There appears to be a bug in GAE s.t. other
# files won't be pushed if one of the URLs is never requested by the browser.
# by the browser.
def fixup_for_vulcanize(vulcanize, urls):
  """Replaces element.html URL with a vulcanized version or
     elements.vulcanize.html with the unvulcanized version.

    Args:
        vulcanize: True if the URL should be replaced by the vulcanized version.
        urls: A dict of url: priority mappings.

    Returns:
        An update dict of URL mappings.
  """

  # TODO: don't hardcode adding the vulcanized import bundle.
  UNVULCANIZED_FILE = 'elements.html'
  VULCANIZED_FILE = 'elements.vulcanize.html'

  push_urls = {}

  for k,v in urls.iteritems():
    url = k

    if vulcanize is not None:
      if k.endswith(UNVULCANIZED_FILE):
        url = k.replace(UNVULCANIZED_FILE, VULCANIZED_FILE)
    else:
      if k.endswith(VULCANIZED_FILE):
        url = k.replace(VULCANIZED_FILE, UNVULCANIZED_FILE)

    push_urls[url] = v

  return push_urls


class MainHandler(http2.PushHandler):

  def get(self):
    vulcanize = self.request.get('vulcanize', None)

    # TODO: Remove (see above).
    push_urls = self.push_urls;
    noextras = self.request.get('noextras', None)
    if noextras is not None:
      push_urls = fixup_for_vulcanize(vulcanize, self.push_urls)

    # HTTP2 server push resources?
    if self.request.get('nopush', None) is None:

      # Send X-Associated-Content header.
      self.response.headers.add_header(
          'X-Associated-Content',
          self._generate_associate_content_header(push_urls))

      # Send Link: <URL>; rel="preload" header.
      headers = self._generate_link_preload_headers(push_urls)
      if type(headers) is list:
        for h in headers:
          self.response.headers.add_header('Link', h)
      else:
        self.response.headers.add_header('Link', headers)

    template = JINJA_ENVIRONMENT.get_template('static/index.html')

    return self.response.write(template.render({
      'vulcanize': vulcanize is not None
      }))

# # Example - decorators.
# class MainHandler(http2.PushHandler):

#   @http2.push('push_manifest.json')
#   def get(self):
#     vulcanize = self.request.get('vulcanize', None)

#     # TODO: Remove (see above).
#     fixup_for_vulcanize(vulcanize, self.push_urls)

#     path = os.path.join(os.path.dirname(__file__), 'static/index.html')

#     return self.response.write(template.render(path, {
#       'vulcanize': vulcanize is not None
#       }))


app = webapp2.WSGIApplication([
    ('/', MainHandler),
], debug=True)
