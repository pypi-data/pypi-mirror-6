import argparse
import os.path as osp
from xlsxdiff.compare import (diff, CellDifference,
                              MissingCell, MissingWorksheet, klass)
from itertools import groupby
import sys


def stats(list_of_errors):
    for error_type, errors in groupby(list_of_errors, klass):
        print (' ' * 5 + "%s: %d" % (error_type, len(list(errors))))


def run():
    parser = argparse.ArgumentParser()
    parser.add_argument("reference", help="the 'reference' workbook")
    parser.add_argument("other", help="the 'modified' workbook")
    parser.add_argument("-m", "--ignore-missing", action="store_true")
    parser.add_argument("-c", "--ignore-changed", action="store_true")
    parser.add_argument("-d", "--decimals", type=int,
                        help=("numbers of decimals to "
                              "consider in number comparison"))
    parser.add_argument("-s", "--stats", action="store_true")
    parser.add_argument("-t", "--ignore-types",
                        action="store_true",
                        help=("try to compare numerical values expressed "
                              "as text as actual numbers, to ignore "
                              "differences based on data type"))

    args = parser.parse_args()

    ignores = []
    if args.ignore_missing:
        ignores.extend([MissingCell, MissingWorksheet])
    if args.ignore_changed:
        ignores.append(CellDifference)

    ab = osp.abspath
    wb, sh = diff(ab(args.reference), ab(args.other),
                  ignores, args.decimals, args.ignore_types)

    print('comparing %s (reference) and %s (other)' % (ab(args.reference),
                                                       ab(args.other)))
    if args.decimals is not None:
        print('using %d digits decimal comparison precision' % args.decimals)
    print

    if wb:
        print(' Workbook-level differences: '.center(40, '-'))
        if args.stats:
            stats(wb)
        else:
            for d in wb:
                print(d)

    if sh:
        print(' Sheet-level differences: '.center(40, '-'))
        for worksheet, diffs in sh.items():
            print(' ' * 3 + ('--> in "%s": ' % worksheet))
            if args.stats:
                stats(diffs)
            else:
                for d in diffs:
                    print(' ' * 5 + repr(d))

    sys.exit(bool(wb or sh))
