## HTTP2 push on App Engine

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

Pushed resources will show a `HTTP2_STREAM_ADOPTED_PUSH_STREAM` in the report.
