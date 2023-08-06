====================
header-detail-footer
====================

Overview
========

The header_detail_footer module provides a way to parse input
iterables (usually text files) that contain header rows, an unknown
number of data rows (called the details), and footer rows. The number
of header and footer rows must be specified when parsing begins. There
can be zero or more header rows, and independently zero or more footer
rows. The detail rows are all of the rows between the header and
footer. If a file consists of just headers and footers, there will be
zero detail rows.

The module API consists of a single function, parse(), and several
exceptions.

Note that the contents of each input "row" are never inspected: they
are just iterated over and returned by the parser. They are often
strings, but they could be any object.

Typical usage
=============

This code shows a simple usage of the `parse()` function::

    >>> from header_detail_footer import parse
    >>> header, details, footer = parse(['header', 'row 1', 'row 2', 'footer'])
    >>> header
    'header'
    >>> list(details)
    ['row 1', 'row 2']
    >>> footer()
    'footer'

The parse() function
====================

The parse() function takes 1 required parameter, the input
iterable. There are two optional parameters, header_rows and
footer_rows. Both default to 1. They represent the number of header
and footer rows present in the input, respectively.

parse() returns a 3-tuple: (header, details, footer). header is the
header row(s), if any; details is an iterator returning each detail
row; and footer is a callable returning the footer row(s), if any.

For header and footer(), they return a single row from the input if
header_rows or footer_rows is 1, respectively. Otherwise, including
the case of 0 rows, they contain a list::

    >>> header, details, footer = parse(['row 1', 'row 2', 'footer 1', 'footer 2'],
    ...                                 header_rows=0, footer_rows=2)
    >>> header
    []
    >>> list(details)
    ['row 1', 'row 2']
    >>> footer()
    ['footer 1', 'footer 2']

The returned footer callable need never be called. If footer is ever
called, details must have been exhausted, otherwise a RuntimeError is
raised::

    >>> header, detail, footer = parse('abc')
    >>> footer()
    Traceback (most recent call last):
        ...
    RuntimeError: called footer() before details were exhausted

Exceptions
==========

Two exceptions are defined at the module level: `HeaderError` and
`FooterError`. Note that these exceptions are raised in the `parser()`
method. They are never raised when iterating over the header, details,
or footer.

HeaderError
-----------

Raised by `parser()` if the input does not contain enough rows for the header::

    >>> header, details, footer = parse(['row 1'], header_rows=3) #doctest: +IGNORE_EXCEPTION_DETAIL
    Traceback (most recent call last):
        ...
    HeaderError: too few rows for header

FooterError
-----------

Raised by `parser()` if the input does contain enough rows for the
header, but not enough rows for the footer::

    >>> header, details, footer = parse(['row 1', 'row 2', 'row 3'],
    ...                                 header_rows=2, footer_rows=2) #doctest: +IGNORE_EXCEPTION_DETAIL
    Traceback (most recent call last):
        ...
    FooterError: too few rows for footer

Usage with CSV files
====================

If you have a CSV file with a header row containing column names, and
also with a footer row, it's easiest if you tell header_detail_footer
that there is no header row. That way, the details iterator can be
passed to csv.DictReader, which will pick up the header row as usual::

    >>> import csv

    # here, the footer row contains a row count
    >>> _, details, footer = parse(['FRUIT,COLOR',
    ...                             'apple,red',
    ...                             'orange,orange',
    ...                             'rowcount:2'],
    ...                            header_rows=0)  # specify 0 header rows

    # pass the details to csv.DictReader. this includes what is now
    # the csv header row
    >>> reader = csv.DictReader(details)

    # print out each row
    >>> for count, row in enumerate(reader, 1):
    ...      (count, [(key, value) for key, value in sorted(row.items())])
    ...
    (1, [('COLOR', 'red'), ('FRUIT', 'apple')])
    (2, [('COLOR', 'orange'), ('FRUIT', 'orange')])

    # verify the footer count
    >>> _, _, footer_count = footer().partition(':')
    >>> int(footer_count) == count
    True
