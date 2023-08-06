import argparse
import re


def exportToHtml(infn, outfn, debug=False):
    # chicken and egg import
    from .cmdline import sibpath

    def escape_inline_js(s):
        # inlining js is tricky because we need to escape literals like:
        # alert("</script>")
        # this would be interpreted by the html parser to be the end of the script tag
        # so after trying several method, the easiest, is just to convert to base 64
        # and eval the result string
        import base64
        s = "\neval(atob('" + base64.b64encode(s) + "'))"
        return s

    index = open(sibpath("static/index.html")).read()
    # we read the original html file, and inline the css, and scripts
    # adding the data inside the script tag
    # doing string manipulation on such big strings is very slow
    # so we split the
    scripts = escape_inline_js(open(sibpath("static/scripts/scripts.min.js")).read())
    styles = open(sibpath("static/styles/styles.min.css")).read()
    styles = '<style>' + styles + '</style>'
    styles_re = re.compile(r'<link rel="stylesheet" href="styles/styles.min.css\?_\d+">')
    index_1, index_2 = styles_re.split(index)
    scripts_re = re.compile(r'<script src="scripts/scripts.min.js\?_\d+"></script>')
    index_2, index_3 = scripts_re.split(index_2)
    data = open(infn, "r").read()
    # remove the first line
    _, _, jsondata = data.partition("\n")
    json_script = "window.data = [" + jsondata + "];\n"
    o = open(outfn, "w")
    o.write(index_1)
    o.write(styles)
    o.write(index_2)
    o.write("<script>")
    o.write(escape_inline_js(json_script))
    if not debug:
        o.write(scripts)
    o.write("</script>")
    if debug:
        o.write("<script src='" + sibpath("static/scripts/scripts.min.js") + "''></script>")
    o.write(index_3)
    o.close()


def exportHtml():
    # Global command-line arguments
    parser = argparse.ArgumentParser()
    parser.add_argument('files', action='store', nargs=argparse.REMAINDER,
                        help='files to convert to a standalone html5 page, with embedded data, and webapp')
    parser.add_argument('--debug', action='store_true',
                        help='dont include the script inline')
    opts = parser.parse_args()
    for fn in opts.files:
        ofn = fn.replace(".html", ".exported.html")
        exportToHtml(fn, ofn, opts.debug)
