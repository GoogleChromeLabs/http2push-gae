## HTTP2 push improvest performance

HTTP2 allows servers to preemptively push resources at high priority to the
client by using a header:

    Link: <URL>; rel=preload; as=<TYPE>

The client can also ask for resource that it knows it will need by using:

    <link rel="preload" href="<URL>" as="<type>">

The performance benefits of doing this for critical resources is very promising.

![Effects of HTTP2 push performance](https://raw.githubusercontent.com/GoogleChrome/http2push-gae/master/static/images/pushstats.jpg)

Full [WebPageTest results](http://www.webpagetest.org/video/compare.php?tests=150827_DY_13KF-l%3Anopush%2C150826_KA_1928-l%3Avulcanize%2C150826_YH_16K7-l%3Apush%2C150826_GQ_190C-l%3Avulcanize+(push)&thumbSize=100&ival=100&end=visual)

TL;DR;

- HTTP2 push means we no longer need to concatenate all our JS/CSS together in one file! This reduces the amount of required tooling to make a great, fast web app.
- In my testing, the browser can handle smaller, individual files better than one large file. More testing needs to be done here, but the initial results are promising.
- For HTML Import resources, we no longer need to run `vulcanize` (crushes sub-imports into a single file). In testing, the latter is actually slower. Boom!
- In a world of web components, authors write components in a modular way using HTML Imports, a bit of CSS/JS, and markup. Push means we can ship our code _exactly_ as it was authored, minimizing the differences between dev and code shipped to production.

## HTTP2 push on App Engine

GAE supports the standard preload header! 

### Verify resources are pushed

To verify resources are being pushed on production GAE: 

1. `chrome://net-internals` in Chrome.
2. Change the dropdown to `HTTP/2`
3. Reload your app URL
4. Go back to `chrome://net-internals` and drill into your app.

Pushed resources will show a `HTTP2_STREAM_ADOPTED_PUSH_STREAM` in the report.

<a href="https://raw.githubusercontent.com/GoogleChrome/http2push-gae/master/site/static/img/netinternals.png" target="_blak"><img src="https://raw.githubusercontent.com/GoogleChrome/http2push-gae/master/site/static/img/netinternals.png" alt="chrome://net-internals"></a>
