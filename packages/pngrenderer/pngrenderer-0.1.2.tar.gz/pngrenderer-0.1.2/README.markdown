# PNG Renderer

For constructing a zip file of png images. I created this package as I had many plots associated from the output of a plotting script and wanted to keep them together. Similar to `matplotlib.backends.PdfPages` I wanted to associate the images, but using the `png` format, so I chose to zip the collection of images. I wanted png images as they contained large amounts of data which created extremely large pdf files.

## Example usage

``` python
import matplotlib.pyplot as plt
from pngrenderer import PNGRenderer

fig = plt.figure()

plt.plot(...)

# Save the resulting image(s) to "out.zip"
renderer = PNGRenderer("out")

# Save the first png image
renderer.savefig("first.png")

# Alternatively call .save_page
# renderer.save_page("first.png")

# Render the zip file to disk
renderer.render()

# Alternatively use the context manager
from pngrenderer import png_render

with png_render("out") as renderer:
    renderer.savefig()

# The context manager calls the `render` method
```


## Requirements and installation

This package requires matplotlib, but no other packages

Installation: `pip install git+https://github.com/mindriot101/pngrenderer.git`

If this package ever makes it onto pypi then probably the installation will be `pip install matplotlib-pngrenderer`.

## Contributing

To contribute, clone the repository at [this github link](https://github.com/mindriot101/matplotlib-pngrenderer), and run the tests with `python setup.py test`
