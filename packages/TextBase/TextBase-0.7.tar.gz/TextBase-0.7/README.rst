textbase - A Python library to manipulate Inmagic/DBText style data
files

What are textbase files?
------------------------

A simple format separating data records with a single character
delimiter, (all files we use have a $ character on a line. For each
record the fieldname is the first word on the line, usually in upper
case. Any text following the fieldname is that value for the field.
Repeating values in a list for the fieldname can be specified on
consecutive lines using a semicolon. If the text value for a field is
very long and needs to wrap, start the line with one (or more) spaces.

Why did you re-invent the wheel?
--------------------------------

We already have CSV files, or JSON files, or YAML, why did you make
this? Well, I didn't invent this. It is actually a format used by a
suite of software from InMagic:
http://www.inmagic.com/products/dbtext-library-suite/

We used the dbText software to create a boatload of data files since the
early eighties, which is a LONG time ago in Internet-land. Those exact
same data files are still used to drive a lot of software, and has
proven to be remarkably useful over the years. Think of it as Markdown
vs HTML, or as a simpler dataformat with über-simple Key:Value records
that are human readable.

Example File:
-------------

::

    FOO A Foo field
    BAR A Baz field with mulitple entries
    ; Another
    ; and yet even more
    $
    FOO This is the FOO field for the next record
    BAR Nothing

The main utitlity class is TextBase. It can be initialised with an open
file, or a string buffer, named sourcefile. Sourcefile is iterated over,
splitting the contents into chunks. Each chunk is parsed and added to an
internal buffer list. The internal buffer contains a dict for each
record. Each entry in the dict is keyed on the DBText record fieldname,
the entry itself is a list of the values.

The TextBase object can be used as a generator to iterate over the
contents, or the Textbase object can be index-addressed like a list.

Example Usage:
--------------

.. code:: python

    import textbase
    t = textbase.TextBase(somebuf)

    print len(t)

    for x in t[10:20]:
        print x.keys()

    print t[0]

If you do not want the records parsed into Python dictionaries and just
want to muck about with the records as text blobs, initialise like this:

.. code:: python

      t = textbase.TextBase(somebuf, parse=False)

Author: Etienne Posthumus Mail: ep@epoz.org
