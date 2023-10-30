# docs

This repo contains the source code for [Keukeiland Docs](http://docs.keukeiland.nl/).
Regenerates _references_ and _documentation_ for the repo's every time when started, other files in _docs_ will be kept and served statically.

Build using `docker build -t docs .`

Run using `docker run -p 80:80 docs`