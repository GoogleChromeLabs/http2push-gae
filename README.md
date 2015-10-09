# HTTP 2.0 push on App Engine

This project contains a drop-in library for doing HTTP2 push on Google App Engine.

Demo test site: https://http20-experiment.appspot.com/

## TL;DR quickstart

1. Run `node ./scripts/generate_push_manifest.js static index.html`. This generates `push_manifest.json`, a list of static resources to push when index.html is requested.
- Prune `push_manifest.json` as necessary. Also re-run `generate_push_manifest.js` when your list of resources changes. 
- Annotate your page handlers with the `@http2push.push()` decorator. This will read + cache `push_manifest.json` and automatically construct the correct `Link: rel=preload` headers.

That's it!

The example server is written in Python. If you'd like to see other App Engine
runtimes feel free to submit a pull request or visit the [EXPLAINER](EXPLAINER.md)
to read up on how to construct the `Link rel=preload` header yourself.

<!--It also contains a script for generating a list of  static resources on a site, which is useful for generating the necessary HTTP header for push resources. -->

## Requirements & Setup

1. Download the [App Engine Python SDK](https://cloud.google.com/appengine/downloads?hl=en). You'll need the dev server.
- Node. But you already have it right!?

### Installation in your project

Get the code:

    git clone https://github.com/GoogleChrome/http2push-gae http2push

Install the dependencies:

    npm install

Note: this will also run `bower install` after npm finishes. If that doesn't happen,
be sure to run `bower install`

## Generating a push manifest

The `scripts` folder contains `generate_push_manifest.js`, a script for generating
a JSON file (manifest) listing all of your app's static resources. **This file is not required
by the HTTP2 protocol** but is useful for constructing the `Link: rel=preload` header
on your server.

**Example** - list all the static resources of `static/index.html`, including sub-HTML Imports:

    node ./scripts/generate_push_manifest.js static index.html

**Example** - list all the resources in `static/elements/elements.html`:

    node ./scripts/generate_push_manifest.js static/elements elements.html

The script generates `push_manifest.json` in the top level directory with a
mapping of `<URL>: <PUSH_PRIORITY>`. Feel free to add/remove URLs as necessary
or change the priority level.

    {
      "/css/app.css": 1,
      "/js/app.js": 1,
      "/bower_components/webcomponentsjs/webcomponents-lite.js": 1,
      "/bower_components/iron-selector/iron-selection.html": 1,
      ...
      "/elements.html": 1,
      "/elements.vulcanize.html": 1
    }

This file can be loaded by your server to constructor the `Link` header. When you
use the provided `http2push` module, that's exact what it does!

## http2push drop-in server module

The `http2push` module provides a base handler and decorator to use in your
own server. The decorator is the simplest to integrate. Handlers which are annotated
with the `@http2push.push()` decorator will server-push the resources in
`push_manifest.json`.

**Example** - using the `push` decorator:

    import os
    import webapp2

    from google.appengine.ext.webapp import template
    import http2push as http2

    class Handler(http2.PushHandler):

      @http2.push() # push_manifest.json is used by default.
      def get(self):
        # Resources in push_manifest.json will be server-pushed with index.html.
        path = os.path.join(os.path.dirname(__file__), 'static/index.html')
        return self.response.out.write()

    app = webapp2.WSGIApplication([('/', Handler)])

To use a custom manifest file name, use `@http2push.push('FILENAME')`.

**Example** - using a custom manifest file:

    import http2push

    class Handler(http2push.PushHandler):

      @http2push.push('custom_manifest.json')
      def get(self):
        ...

For more control, you can also set the headers yourself.

**Example** - Explicitly set `Link: rel=preload` (no decorators):

    import http2push

    class Handler(http2push.PushHandler):

      def get(self):
        # Optional: use custom manifest file.
        # self.push_urls = http2push.use_push_manifest('custom_manifest.json')

        headers = self._generate_link_preload_headers()
        for h in headers:
          self.response.headers.add_header('Link', h)

        path = os.path.join(os.path.dirname(__file__), 'static/index.html')
        return self.response.out.write(template.render(path))

## Run the server

Start the App Engine dev server to see if everything went alright:

    dev_appserver.py --port 8080 .

Open `http://localhost:8080/`.

## Deployment (test site)

*Note: this section is only for maintainers of this project.*

### Build it

There's a one-stop convenience script to vulcanize the app and generate `push_manifest.json`:

    ./scripts/build.sh

### Deploy it

Run `deploy.sh` to deploy the demo site. Note: `build.sh` is ran as part of this process.

    ./scripts/deploy.sh <VERSION>

Where `<VERSION>` is the app version you'd like to deploy as.
