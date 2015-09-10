# HTTP 2.0 push on App Engine

This project contains a reference server implementation for doing HTTP2
push on Google App Engine. It also contains a script for generating a list of 
static resources on a site, which is useful for generating the necessary HTTP header
for push resources.

Demo: https://http20-experiment.appspot.com/

![Effects of HTTP2 push perforamnce](https://raw.githubusercontent.com/GoogleChrome/http2push-gae/master/static/images/pushstats.jpg)

### Perf results

Full [WebPageTest results](http://www.webpagetest.org/video/compare.php?tests=150827_DY_13KF-l%3Anopush%2C150826_KA_1928-l%3Avulcanize%2C150826_YH_16K7-l%3Apush%2C150826_GQ_190C-l%3Avulcanize+(push)&thumbSize=100&ival=100&end=visual)

TL;DR;

- HTTP2 push means we no longer need to concat all our JS/CSS together in one file! This reduces the amount of required tooling to make a great, fast web app.
- In my testing, the browser can handle smaller, indvidual files better than one large file. More testing needs to be done here, but the initial results are promising.
- For HTML Import resources, we no longer need to run `vulcanize` (crushes subimports into a single file). In testing, the latter is actually slower. Boom!
- In a world of web components, authors write components in a modular way using HTML Imports, a bit of CSS/JS, and markup. Push means we can ship our code _exactly_ as it was authored, minimizing the differences between dev and code shipped to production.

## Requirements & Setup

1. Download the [App Engine Python SDK](https://cloud.google.com/appengine/downloads?hl=en). You'll need the dev server.
2. Node. But you already have it right!?

### Setup

Install the dependencies:

    npm install

Note: this will also run `bower install` after npm finishes. If that doesn't happen,
be sure to run `bower install`

## How to use HTTP2 push on App Engine

App Engine support HTTP2 push with a special header, `X-Associated-Content`.
The format of the header value is a comma-separated list of double-quoted URLs,
each of which may optionally be followed by a colon and a SPDY priority number
(from 0 to 7 inclusive). The **URL needs to be full absolute URL**. Whitespace
between tokens is optional, and is ignored if present. For example:

    X-Associated-Content: "https://www.example.com/styles/foo.css",
        "/scripts/bar.js?q=4":2, "https://www.example.com/images/baz.png": 5,
        "https://www.example.com/generate_image.php?w=32&h=24"

**Note:** This header is not the spec'd standard `Link: <URL>; rel=preload` as
described in [http://w3c.github.io/preload/](http://w3c.github.io/preload/).
It's an older format used in SPDY.

Also note, the `X-Associated-Content` header will be stripped in production
App Engine. You won't see it on your requests. However, you'll be able to see it
locally when testing on the dev server.

### Verify resources are pushed

To verify resources are being pushed on production GAE: 

1. `chrome://net-internals` in Chrome.
2. Change the dropdown to `HTTP/2`
3. Reload your app URL
4. Go back to `chrome://net-internals` and drill into your app.

Pushed resoures will show a `HTTP2_STREAM_ADOPTED_PUSH_STREAM` in the report.

## Generating a push manifest

The `scripts` folder contains `generate_push_manifest.js`, a script for generating
a JSON file (manifest) listing all of your page's static resources. **This file is not required
by the HTTP2 protocol** but is useful for constructing the `X-Associated-Content` header
on your server.

Running `generate_push_manifest.js` will generate `push_manifest.json` in the top
level directoryL

    {
      "/css/app.css": 1,
      "/js/app.js": 1,
      "/bower_components/webcomponentsjs/webcomponents-lite.js": 1,
      "/bower_components/iron-selector/iron-selection.html": 1,
      ...
      "/elements.html": 1,
      "/elements.vulcanize.html": 1
    }

This file is used by the reference server to constructor the `X-Associated-Content` header.
The server reads this file, appends the URL origin (to make an absolute URL),
and servers the index.html page with with the constructed `X-Associated-Content` header.

### Build it!

Run the following script to vulcanize your app and generate `push_manifest.json`:

    ./scripts/build.sh

## Run the server

Start the App Engine dev server:

    dev_appserver.py --port 8080 .

Open `http://localhost:8080/`. 

## Deploy

To vulcanize imports and deploy to GAE, `deploy.sh` from the main directory:

    ./scripts/deploy.sh <VERSION>

Where `<VERSION>` is the app version you'd like to deploy as.
