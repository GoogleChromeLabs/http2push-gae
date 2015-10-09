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

import logging
import json
import webapp2


PUSH_MANIFEST = 'push_manifest.json'

manifest_cache = {} # filename -> list of push URL mapping.

def use_push_manifest(filename):
  global manifest_cache

  push_urls = {}

  # Read file only if it's not in memory.
  if filename in manifest_cache:
    push_urls = manifest_cache[filename]['push_urls']
  else:
    try:
      with open(filename) as f:
        push_urls = json.loads(f.read())

      manifest_cache[filename] = {'push_urls': push_urls} # cache it.
    except IOError as e:
      logging.error("Error reading %s: %s" % (filename, e.strerror))

  return push_urls


class PushHandler(webapp2.RequestHandler):
  """Base handler for constructing Link rel=preload header."""

  push_urls = use_push_manifest(PUSH_MANIFEST)

  # def __init__(self, request, response):
   # self.initialize(request, response)

  def _generate_associate_content_header(self, urls=None):
    """Constructs a value for the X-Associated-Content header.

    The format of the header value is a comma-separated list of double-quoted
    URLs, each of which may optionally be followed by a colon and a SPDY
    priority number (from 0 to 7 inclusive). URL needs to be a full absolute
    URL. Whitespace between tokens is optional, and is ignored if present.

    For example:

      X-Associated-Content: "https://www.example.com/styles/foo.css",
          "/scripts/bar.js?q=4":2, "https://www.example.com/images/baz.png": 5,
           "https://www.example.com/generate_image.php?w=32&h=24"

    App Engine supports this header for now. Link: rel=preload is the standard
    and you should use that to be compliant with the HTTP2 spec.

    Args:
        url: A dict of url: priority mappings to use in the header.

    Returns:
        Comma separated string for the X-Associated-Content header.
    """

    if urls is None:
      urls = self.push_urls

    host = self.request.host_url

    associate_content = []
    for url,v in urls.iteritems():
      url = '%s%s' % (host, str(url)) # Construct absolute URLs.

      if v is None:
        associate_content.append('"%s"' % url)
      else:
        associate_content.append('"%s":%s' % (url, str(v)))

    headers = list(set(associate_content)) # remove duplicates

    return ','.join(headers)

  def _generate_link_preload_headers(self, urls=None):
    """Constructs a value for the Link: rel=preload header.

    The format of the preload header is described in the spec
    http://w3c.github.io/preload/:

      Link: <https://example.com/font.woff>; rel=preload;

    Args:
        url: A list of urls to use in the header.

    Returns:
        A list of Link header values.
    """

    if urls is None:
      urls = self.push_urls

    host = self.request.host_url

    preload_links = []
    for url in urls:
      url = '%s%s' % (host, str(url))  # Construct absolute URLs.
      preload_links.append('<%s>; rel="preload"' % url)

    headers = list(set(preload_links)) # remove duplicates

    # TODO: check that implementations support a single Link header with
    # with commma separated values.
    return headers # ','.join(headers)

"""
Example:

 @http2push.push()
 def get(self):
   pass

 @http2push.push('push_manifest.json') # Use a custom manifest.
 def get(self):
   pass

?nopush on the URL prevents the header from being included.
"""
def push(manifest=PUSH_MANIFEST):
  def decorator(handler):
    push_urls = use_push_manifest(manifest)

    def wrapper(*args, **kwargs):
      instance = args[0]
      # nopush URL param prevents the Link header from being included.
      if instance.request.get('nopush', None) is None and len(push_urls):
        # Send X-Associated-Content header.
        instance.response.headers.add_header('X-Associated-Content',
              instance._generate_associate_content_header(push_urls))

        preload_headers = instance._generate_link_preload_headers(push_urls)
        if type(preload_headers) is list:
          for h in preload_headers:
            instance.response.headers.add_header('Link', h)
        else:
          instance.response.headers.add_header('Link', preload_headers)

      return handler(*args, **kwargs)

    return wrapper
  return decorator
