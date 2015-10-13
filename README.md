# HTTP 2.0 push on App Engine

This project contains a drop-in library for doing HTTP2 push on Google App Engine.

Demo test site: https://http2-push.appspot.com/

## TL;DR quickstart

1. Generate a `push_manifest.json` using a node script, [http2-push-manifest](https://www.npmjs.com/package/http2-push-manifest). See below.
- Annotate your request handlers with the `@http2push.push()` decorator.

<a href="https://raw.githubusercontent.com/GoogleChrome/http2push-gae/master/site/static/img/pushgaehowto.jpg" target="_blak"><img src="https://raw.githubusercontent.com/GoogleChrome/http2push-gae/master/site/static/img/pushgaehowto.jpg" alt="How this works"></a>

That's it!

## Requirements & Setup

1. [App Engine Python SDK](https://cloud.google.com/appengine/downloads?hl=en). You'll want the dev server for testing.
- Node

The example server is written in Python. If you'd like to see other App Engine
runtimes feel free to submit a pull request or visit the [EXPLAINER](EXPLAINER.md)
to read up on how to construct the `Link rel=preload` header yourself.

### Run the example server

**Important** the dev server does not support http2 push. An app needs to be
deployed to production App Engine.

`example/` contains a fully working example of an App Engine Python server that
uses http2push.py. You'll also see an example `push_manifest.json` in that folder.

To try the test server, start the App Engine dev server in the `example` folder:

    cd example
    dev_appserver.py --port 8080 .

Open `http://localhost:8080/`. 

## Installing in your project

1. Get the drop-in library: `git clone https://github.com/GoogleChrome/http2push-gae`
- Move `http2push-gae/http2push.py` into your project folder.
- Install [http2-push-manifest](https://www.npmjs.com/package/http2-push-manifest) script: `npm install http2-push-manifest --save-dev`

## Using

### Generating a push manifest

This project uses [http2-push-manifest](https://www.npmjs.com/package/http2-push-manifest)
to generate the list of files to push. The JSON file is loaded by `http2push.py`
to constructor the `Link` header.

Re-run the script whenever your list of resources changes. An easy way to do that
is by adding a script to your project's `package.json`.

For example, assuming `app/index.html` is your main page, you could add:

    "scripts": {
      "push": "http2-push-manifest app index.html"
    }

An run `npm run push` to re-generate the file.

Read[http2-push-manifest](https://www.npmjs.com/package/http2-push-manifest)'s
full documentation for more information on generating the manifest.

### Drop in the http2push server module

The `http2push.py` module provides a base handler and decorator to use in your
own server. The decorator is the simplest to integrate. Handlers which are annotated
with the `@http2push.push()` decorator will server-push the resources in
`push_manifest.json`.

> **Tip** - when testing your pages, the `?nopush` URL parameter disables push.
Use this parameter to test the effectiveness of server push on your own resources
or to run performance tests at webpagetest.org.

**Example** - using the decorator:

app.yaml:

```yaml
runtime: python27
api_version: 1
threadsafe: yes

libraries:
- name: webapp2
  version: "latest"

handlers:

- url: /css
  static_dir: static/css
  secure: always

- url: /js
  static_dir: static/js
  secure: always

- url: .*
  script: main.app
  secure: always
```

main.py:

```python
import os
import webapp2

from google.appengine.ext.webapp import template
import http2push as http2

class Handler(http2.PushHandler):

  @http2.push() # push_manifest.json is used by default.
  def get(self):
    # Resources in push_manifest.json will be server-pushed with index.html.
    path = os.path.join(os.path.dirname(__file__), 'static/index.html')
    return self.response.out.write(template.render(path, {}))

app = webapp2.WSGIApplication([('/', Handler)])
```

To use a custom manifest file name, use `@http2push.push('FILENAME')`.

**Example** - using a custom manifest file:

```python
import http2push

class Handler(http2push.PushHandler):

  @http2push.push('custom_manifest.json')
  def get(self):
    ...
```

For more control, you can also set the headers yourself.

**Example** - Explicitly set `Link: rel=preload` (no decorators):

```python
import http2push

class Handler(http2push.PushHandler):

  def get(self):
    # Optional: use custom manifest file.
    # self.push_urls = http2push.use_push_manifest('custom_manifest.json')

    headers = self._generate_link_preload_headers()
    for h in headers:
      self.response.headers.add_header('Link', h)

    path = os.path.join(os.path.dirname(__file__), 'static/index.html')
    return self.response.out.write(template.render(path, {}))
```

## Pushing content from a static handler

If you don't have a dynamic script handler, you can still push resources from
App Engine page by setting the `http_headers` on your static page handler in app.yaml.

app.yaml:

```yaml
...

handlers:

- url: /css
  static_dir: static/css
  secure: always

- url: /js
  static_dir: static/js
  secure: always

- url: /$
  static_files: path/to/index.html
  upload: path/to/index.html
  http_headers:
    X-Associated-Content: '"/js/app.js": 1, "/css/app.css": 1' # Need both headers for now.
    Link: '</js/app.js>; rel="preload", </css/app.css>; rel="preload"'
```

## Deployment (test site)

*Note: this section is only for maintainers of this project.*

### Build it

There's a one-stop convenience script to vulcanize the app and generate `push_manifest.json`:

    cd site
    ./scripts/build.sh

### Deploy it

Run `deploy.sh` to deploy the demo site. Note: `build.sh` is ran as part of this process.

    ./scripts/deploy.sh <VERSION>

Where `<VERSION>` is the app version you'd like to deploy as.
