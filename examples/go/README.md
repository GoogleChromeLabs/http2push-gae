# http2preload demo

A sample app demonstrating the usage of http2preload package.

To run the sample, you'll need Go and App Engine SDK for Go installed.

1. Make sure you have the cli tool installed:
   `go get -u github.com/google/http2preload/cmd/http2preload-manifest`.
2. Generate `preload.json` manifest with `go generate`.
3. Upload the app to appspot with `$GAE_GO/goapp deploy -application <app-id> -version <app-ver>`.

Navigate to `<app-id>.appspot.com` and follow the instructions.
For more details check out [the explainer](https://github.com/GoogleChrome/http2push-gae/blob/master/EXPLAINER.md).

Note: you don't really have to use http2preload-manifest tool. Alternatives are:

- npm package [http2-push-manifest](https://www.npmjs.com/package/http2-push-manifest)
- manually create a preload.json manifest.

### License

(c) Google, 2015. Licensed under [Apache-2](../LICENSE) license.

The Go gopher image was designed by Renee French. (http://reneefrench.blogspot.com/)
The design is licensed under the Creative Commons 3.0 Attributions license.
Read this article for more details: https://blog.golang.org/gopher
