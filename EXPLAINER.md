## HTTP2 push improvest performance

HTTP2 allows servers to preemptively push resources at high priority to the
client by using a header:

    Link: <URL>; rel="preload"

The client can also ask for resource that it knows it will need by using:

    <link rel="preload" href="<URL>">

The performance benefits of doing this for critical resources is very promising.

![Effects of HTTP2 push performance](https://raw.githubusercontent.com/GoogleChrome/http2push-gae/master/static/images/pushstats.jpg)

Full [WebPageTest results](http://www.webpagetest.org/video/compare.php?tests=150827_DY_13KF-l%3Anopush%2C150826_KA_1928-l%3Avulcanize%2C150826_YH_16K7-l%3Apush%2C150826_GQ_190C-l%3Avulcanize+(push)&thumbSize=100&ival=100&end=visual)

TL;DR;

- HTTP2 push means we no longer need to concatenate all our JS/CSS together in one file! This reduces the amount of required tooling to make a great, fast web app.
- In my testing, the browser can handle smaller, individual files better than one large file. More testing needs to be done here, but the initial results are promising.
- For HTML Import resources, we no longer need to run `vulcanize` (crushes sub-imports into a single file). In testing, the latter is actually slower. Boom!
- In a world of web components, authors write components in a modular way using HTML Imports, a bit of CSS/JS, and markup. Push means we can ship our code _exactly_ as it was authored, minimizing the differences between dev and code shipped to production.

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

<a href="https://raw.githubusercontent.com/GoogleChrome/http2push-gae/master/site/static/img/netinternals.png" target="_blak"><img src="https://raw.githubusercontent.com/GoogleChrome/http2push-gae/master/site/static/img/netinternals.png" alt="chrome://net-internals"></a>
