# afterimage

scan a folder of images into a local index, report near-duplicates.

    python3 afterimage.py scan <dir>
    python3 afterimage.py dupes <dir> 5

there's a read-only web view now:

    python3 web.py <dir>          # http://127.0.0.1:8777

`tools/make_samples.py` writes a synthetic corpus to `samples/` if you
don't have a folder of images handy. index + thumbnails live under
`<dir>/.afterimage/`.
