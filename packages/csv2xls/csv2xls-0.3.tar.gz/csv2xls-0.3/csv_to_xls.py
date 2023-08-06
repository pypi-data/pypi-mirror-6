#!/usr/bin/env python

"""
Put together some CSV files into a single Excel file, in different sheets.
"""

from __future__ import with_statement

import os, sys
import os.path as op
from datetime import datetime
from collections import defaultdict
import csv

import xlwt

DEF_DATE_FORMAT = "%Y-%m-%d"

# Sheet names limitations
FORBIDDEN = set([':', '/', '?'])
MAX_SIZE = 28

# Rows are limited in Excel
MAX_ROWS = 65535


def sanitize(name):
    """xlwt does not allow long sheet names.
    """
    for c in FORBIDDEN:
        # For '/', we do not print
        if c in name and c != '/':
            print("! Sheet names cannot contain '{0}', replacing in {1}".format(c, name))
        name = name.replace(c, '_')

    if len(name) > MAX_SIZE:
        print("! Sheet name too long. Trimming {0} to {1}".format(name, name[:MAX_SIZE]))
    return name[:MAX_SIZE]


def build_sheet_names(files, keep_prefix):
    """Build nice sheet names from file names.

    We trim the common prefix, remove the extension.
    """
    if not files:
        raise ValueError("No files provided.")

    if keep_prefix:
        prefix = ''
    else:
        prefix = op.commonprefix(files)

        if prefix == files[0]:
            # Can happen if only one repeated sheet
            prefix = ''

    # Helper lambdas
    trim_prefix = lambda s: s[len(prefix):]
    trim_extens = lambda s: op.splitext(s)[0]

    # Remove prefix, extension
    sheet_names = []
    for f in files:
        sheet_names.append((f, sanitize(trim_extens(trim_prefix(f)))))

    # Handling duplicates
    count_sheet_names = defaultdict(int)
    for f, sheet_name in sheet_names:
        count_sheet_names[sheet_name] += 1

    for sheet_name, nb in count_sheet_names.items():
        if nb == 1:
            # No duplicates here
            continue

        k = 1
        for j, (f, s) in enumerate(sheet_names):
            if sheet_name == s:
                new_s = '{0}_{1}'.format(s, k)
                sheet_names[j] = (f, new_s)
                k += 1
                print("! To avoid duplicated sheet names, renaming {0} to {1}".format(s, new_s))

    return sheet_names


def is_int(s):
    """Type inference when writing in Excel.
    """
    try:
        int(s)
    except ValueError:
        return False
    else:
        return True


def is_float(s):
    """Type inference when writing in Excel.
    """
    try:
        float(s)
    except ValueError:
        return False
    else:
        return True


def is_date(s, date_format):
    """Type inference when writing in Excel.
    """
    try:
        datetime.strptime(s, date_format)
    except ValueError:
        return False
    else:
        return True


# XFS style for date format
DATE_FORMAT_STYLE = xlwt.XFStyle()
DATE_FORMAT_STYLE.num_format_str = 'M/D/YY'

def infer_and_write(sheet, row_nb, col_nb, v, date_format):
    """Custom sheet writer with type inference.
    """
    if is_int(v):
        sheet.write(row_nb, col_nb, int(v))

    elif is_float(v):
        sheet.write(row_nb, col_nb, float(v))

    elif is_date(v, date_format):
        sheet.write(row_nb, col_nb,
                    datetime.strptime(v, date_format),
                    DATE_FORMAT_STYLE)
    else:
        sheet.write(row_nb, col_nb, v)


def add_to_sheet(sheet, fl, date_format, inference):
    """Add filelike content to sheet.
    """
    if inference:
        write = infer_and_write
    else:
        write = lambda s, r, c, v, _: s.write(r, c, v)

    broke = False

    for row_nb, row in enumerate(csv.reader(fl, delimiter=',', quotechar='"')):

        if row_nb > MAX_ROWS:
            broke = True
            break

        for col_nb, v in enumerate(row):
            # Type inference hidden here
            write(sheet, row_nb, col_nb, v, date_format)

    if broke:
        # We add one because we lost 1 when breaking
        nb_dropped = 1 + len(list(fl))
        print("! Exceeding max rows {0}, dropping remaining {1} rows...".format(MAX_ROWS, nb_dropped))


def create_xls_file(files, output, date_format=DEF_DATE_FORMAT, inference=True, keep_prefix=False, clean=False):
    """Main function creating the xls file.
    """
    if not output.endswith(".xls") and not output.endswith(".xlsx"):
        print("! Output name should end with .xls[x] extension, got:")
        print("{0:^40}".format(output))
        return

    if op.exists(output):
        print("! Output {0} already exists, removing.".format(output))
        os.unlink(output)

    # THE Excel book ;)
    book = xlwt.Workbook()

    for f, sheet_name in sorted(build_sheet_names(files, keep_prefix),
                                key=lambda t: t[1].lower()):

        print("Processing {0:>30} -> {1}/{2}".format(f, output, sheet_name))

        with open(f) as fl:
            sheet = book.add_sheet(sheet_name)
            add_to_sheet(sheet, fl, date_format, inference)

    book.save(output)

    # Hopefully no exception raised so far
    if clean:
        for f in sorted(files):
            print("Removing {0}.".format(f))
            os.unlink(f)


def main():
    """Main.
    """
    import argparse

    parser = argparse.ArgumentParser(description="""
    Put together some CSV files into a single Excel file.
    Basic types are inferred automatically.
    """)

    parser.add_argument("files", nargs='+')

    parser.add_argument("-o", "--output",
        help="""
        Define name for output Excel file.
        Default is %(default)s.""",
        default="output.xls")

    parser.add_argument("-k", "--keep-prefix",
        help="""
        Keep common prefix when building sheet names.
        Default is to remove the common prefix of input file names.
        """,
        action='store_true')

    parser.add_argument("-c", "--clean",
        help="""
        Delete input files afterwards, if successful.
        """,
        action='store_true')

    parser.add_argument("-no", "--no-type-inference",
        help="""
        Do not try to infer int/float/date when writing.
        This mode is faster and preserves input data.
        """,
        action='store_true')

    parser.add_argument("-d", "--date-format",
        help="""
        Change date format used during date type
        inference. Default is %(default)s.
        """,
        default=DEF_DATE_FORMAT,
        metavar="FORMAT")

    parser.epilog = """
    Example: {0} examples/sheet_alpha.csv examples/sheet_beta.csv
    """.format(op.basename(sys.argv[0]))

    args = parser.parse_args()

    create_xls_file(**{
        'files'       : args.files,
        'output'      : args.output,
        'date_format' : args.date_format,
        'inference'   : not args.no_type_inference,
        'keep_prefix' : args.keep_prefix,
        'clean'       : args.clean,
    })


if __name__ == "__main__":

    main()

