import os
import sys
import argparse
import cStringIO
import puppet

def fmt(path, options):
    tokens = puppet.tokenize(path)
    token = tokens[0]
    token = puppet.remove_whitespace(token)
    resources, _ = puppet.parse(token)
    for r in resources:
        if options.verbose:
            sys.stderr.write("Rewriting {}[{}]...".format(r.name.capitalize(), r.title))
        r.rewrite()
        if options.verbose:
            sys.stderr.write(" ok.\n")

    buf = cStringIO.StringIO()
    for token in puppet.until_end(token, False):
        buf.write(token.to_manifest())
    if options.write:
        open(path, 'wb').write(buf.getvalue())
    else:
        sys.stdout.write(buf.getvalue())

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('files', action="store", nargs='*', help="files to format")
    parser.add_argument('-w', '--write', action="store_true", default=False, help="write result to (source) file instead of stdout")
    parser.add_argument('--verbose', action="store_true", default=False, help="show additional logging information")
    options = parser.parse_args()
    if not options.files:
        parser.print_help()
    for f in options.files:
        fmt(f, options)
