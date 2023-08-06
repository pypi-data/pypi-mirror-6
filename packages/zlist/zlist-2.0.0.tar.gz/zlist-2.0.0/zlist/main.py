'''
This is the primary touchpaper module; the `main` function is called when you
run `zlist` on the command line.
'''

import argparse
import cssutils
import logging
import sys

from ._version import get_version


cssutils.log.setLevel(logging.CRITICAL)


'''
Main package routine

Parse CSS files for elements with a defined z-index and list them

Usage: $ python zlist.py <file.css> <file2.css> ..
'''
def main():
    ''' Argument parser init '''
    parser = argparse.ArgumentParser(description='Parse CSS files for elements '
                                                 'with a defined z-index and '
                                                 'list them')
    parser.add_argument('-v', '--version', dest='version', action='store_true',
                        help='show package version information and exit')
    parser.add_argument('files', nargs='*')
    args = parser.parse_args()

    if args.version:
        print "zlist v%s" % get_version()
        sys.exit(0)

    ''' Iterate files supplied as args and parse them '''
    for filename in args.files:
        sheet = cssutils.parseFile(filename)
        zlist = []
        for rule in sheet:
            if rule.type == rule.STYLE_RULE:
                z = None
                for prop in rule.style:
                    if prop.name == 'z-index':
                        z = prop.value
                if z:
                    zlist.append([z, rule.selectorList])
        if zlist:
            print "%s: %d z-index declaration(s) found\n" % (filename, len(zlist))
            print "index  |".rjust(13), " selector\n", "".rjust(30, '-')
            zlist.sort(key=lambda entry: int(entry[0]))
            for entry in zlist:
                print entry[0].rjust(10), "".rjust(3),
                for selector in entry[1]:
                    if selector != entry[1][0]:
                        print "".rjust(14),
                    print selector.selectorText
            print ""
        else:
            print "%s: No z-index declarations found" % filename


if __name__ == "__main__":
    main()
