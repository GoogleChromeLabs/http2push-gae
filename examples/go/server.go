package app

import (
	"fmt"
	"net/http"

	"github.com/google/http2preload"
)

// gopher is the gopher image.
const gopher = "gopher.png"

//go:generate http2preload-manifest -o preload.json

// init registers HTTP handlers.
func init() {
	m, err := http2preload.ReadManifest("preload.json")
	if err != nil {
		panic(err)
	}
	http.Handle("/", m.Handler(handleRoot))
	http.HandleFunc("/img.png", handleImg)
	http.HandleFunc("/gopher", handleGopher)
}

// handleRoot serves the landing page.
func handleRoot(w http.ResponseWriter, r *http.Request) {
	http.ServeFile(w, r, "index.html")
}

// handleImg serve gopher image.
func handleImg(w http.ResponseWriter, r *http.Request) {
	http.ServeFile(w, r, gopher)
}

// handleGopher demonstrates how to push resources
// without a manifest file.
func handleGopher(w http.ResponseWriter, r *http.Request) {
	assets := map[string]http2preload.AssetOpt{
		gopher: {Type: http2preload.Image},
	}
	s := "http"
	if r.TLS != nil {
		s = "https"
	}
	// the next line will add the following header:
	// Link: <host/gopher.png>; rel=preload; as=image
	http2preload.AddHeader(w.Header(), s, r.Host, assets)
	// respond with minimal HTML5, omitting <html> and <body>
	fmt.Fprintf(w, `<img src="%s">`, gopher)
}
