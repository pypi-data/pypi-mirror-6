1. Introduction
===============

1.1 Who is this document aimed at?
----------------------------------

This document is aimed at anyone who wants to know how to use the pyRXP
parser extension from Python. It's assumed that you know how to use the
Python programming language and understand its terminology. We make no
attempt to teach XML in this document, so you should already know the
basics (what a DTD is, some of the syntax etc.)

1.2 What is PyRXP?
------------------

PyRXP is a Python language wrapper around the excellent RXP parser. RXP
is a validating namespace-aware XML parser written in C.  It was released
by ReportLab in 2003, at a time when the available XML parsing tools in
Python were, frankly, a mess.  At the time it was the fastest XML-parsing 
framework available to Python programmers, with the benefit of validation.
Please bear in mind that much of the documentation was written at that time.

RXP was written by Richard Tobin at the Language Technology Group, Human
Communication Research Centre, University of Edinburgh. PyRXP was
written by Robin Becker at ReportLab.

ReportLab uses pyRXP to parse its own Report Markup Language formatting product,
and for all inbound XML within our document generation solutions.  Having a
validating XML parser is a huge benefit, because it stops a large proportion
of bad input from other systems early on, and forces producers to get things
right, rather than leaning on us to write ad-hoc cleanups for other peoples'
poor data.

The code is extremely mature and stable.  

In recent years, libxml2 and lxml have become popular and offer much of the 
same functionality, under less restrictive licenses; these may also be a
valid choice for your project.

This documentation describes pyRXP-1.16 being used with RXP 1.4.0, as
well as ReportLab's emerging XML toolkit which uses it.

1.3 License terms
-----------------

Edinburgh University have released RXP under the GPL. This is generally
fine for in-house or open-source use. But if you want to use it in a
closed-source commercial product, you may need to negotiate a separate
license with them. By contrast, most Python software uses a less
restrictive license; Python has its own license, and ReportLab uses the
FreeBSD license for our PDF Toolkit, which means you CAN use it in
commercial products.

We licensed RXP for our commercial products, but are releasing pyRXP
under the GPL. (We did try to persuade Edinburgh to release under a
Python style license, but they declined; otherwise pyRXP might have
become the Python standard.)

If you want to use pyRXP for a commercial product, you
need to purchase a license. We are authorised resellers for RXP and can
sell you a commercial license to use it in your own products. PyRXP is
ideal for embedded use being lightweight, fast and pythonic. 


1.4 Why another XML toolkit?
----------------------------

This grew out of real world needs which others in the Python community
may share. ReportLab make tools which read in some kind of data and make
PDF reports. One common input format these days is XML. It's very
convenient to express the interface to a system as an XML file. Some
other system might send us some XML with tags like <invoice> and
<customer>, and we turn these into nice looking invoices.

Also, we have a commercial product called Report Markup Language - we
sell a converter to turn RML files into PDF. This has to parse XML, and
do it fast and accurately.

Typically we want to get this XML into memory as fast as possible. And,
if the performance penalties are not too great, we'd like the option to
validate it as well. Validation is useful because we can stop bad data
at the point of input; if someone else sends our system an XML 'invoice
packet' which is not valid according to the agreed DTD, and gets a
validation error, they will know what's going on. This is a lot more
helpful than getting a strange and unrelated-sounding error during the
formatting stage.

We tried to use all the parsers we could find. We found that almost all
of them were constructing large object models in Python code, which took
a long time and a lot of memory. Even the fastest C-based parser, expat
(which was not yet a standard part of Python at the time) calls back
into Python code on every start and end tag, which defeats most of the
benefit. Aaron Watters of ReportLab sat down for a couple of days in
2000 and produced his own parser, rparsexml, which uses string.find and
got pretty much the same speed as pyexpat. We evolved our own
representation of a tree in memory; which became the cornerstone of our
approach; and when we found RXP we found it easy to make a wrapper
around it to produce the "tuple tree".

We have now reached the point in our internal bag-of-tools where XML
parsing is a standard component, running entirely at C-like speeds, and
we don't even think much about it any more. Which means we must be doing
something right and it's time to share it :-)

1.5 Design Goals
----------------

This is part of an XML framework which we will polish up and release
over time as we find the time to document it. The general components
are:

-  A standard in-memory representation of an XML document (the *tuple
   tree* below)
-  Various parsers which can produce this - principally pyRXP, but expat
   wrapping is possible
-  A 'lazy wrapper' around this which gives a very friendly Pythonic
   interface for navigating the tree
-  A lightweight transformation tool which does a lot of what XSLT can
   do, but again with Pythonic syntax

In general we want to get the whole structure of an XML document into
memory as soon as possible. Having done so, we're going to traverse
through it and move the data into our own object model anyway; so we
don't really care what kind of "node objects" we're dealing with and
whether they are DOM-compliant. Our goals for the whole framework are:

-  Fast - XML parsing should not be an overhead for a program
-  Validate when needed, with little or no performance penalty
-  Construct a complete tree in memory which is easy and natural to
   access
-  An easy lightweight wrapping system with some of the abilities of
   XSLT without the complexity

Note that pyRXP is just the main parsing component and not the framework
itself.

1.6 Design non-goals
--------------------

It's often much more helpful to spell out what a system or component
will NOT do. Most of all we are NOT trying to produce a
standards-compliant parser.

-  Not a SAX parser
-  Not a DOM parser
-  Does not capture full XML structure

Why not? Aren't standards good?

It's great that Python has support for SAX and DOM, but these are
basically Java (or at least cross-platform) APIs. If you're doing
Python, it's possible to make things simpler, and we've tried. Let's
imagine you have some XML containing an *invoice* tag, that this in turn
contains *lineItems* tags, and each of these has some text content and
an *amount* attribute. Wouldn't it be nice if you could write some
Python code this simple?

::

    invoice = pyRXP.Parser().parse(myInvoiceText)
    for lineItem in invoice:
        print invoice.amount

Likewise, if a node is known to contain text, it would be really handy
to just treat it as a string. We have a preprocessor we use to insert
data into HTML and RML files which lets us put Python expressions in
curly braces, and we often do things like

::

    <html><head><title>My web page</title></head>
    <body>
    <h1>Statement for {{xml.customer.DisplayName}}</h1>
    <!-- etc etc -->
    </body>
    </html>
    <h1></h1>

Try to write the equivalent in Java and you'll have loads of method
calls to getFirstElement(), getNextElement() and so on. Python has
beautifully compact and readable syntax, and we'd rather use it. So
we're not bothering with SAX and DOM support ourselves. (Although if
other people want to contribute full DOM and SAX wrappers for pyRXP,
we'll accept the patches).

1.7 How fast is it?
-------------------

The examples file includes a crude benchmarking script. It measures
speed and memory allocation of a number of different parsers and
frameworks. This is documented later on. Suffice to say that we can
parse hamlet in 0.15 seconds with full validation on a P500 laptop.
Doing the same with the *minidom* in the Python distribution takes 33
times as long and allocates 8 times as much memory, and does not
validate. It also appears to have a significant edge on Microsoft's XML
parser and on FourThought's cDomlette. Using pyRXP means that XML
parsing will typically take a tiny amount of time compared to whatever
your Python program will do with the data later.

1.8 The Tuple Tree structure
----------------------------

Most 'tree parsers' such as DOM create 'node objects' of some sort. The
DOM gives one consensus of what such an object should look like. The
problem is that "objects" means "class instances in Python", and the
moment you start to use such beasts, you move away from fast C code to
slower interpreted code. Furthermore, the nodes tend to have magic
attribute names like "parent" or "children", which one day will collide
with structural names.

So, we defined the simplest structure we could which captured the
structure of an XML document. Each tag is represented as a tuple of

::

    (tagName, dict_of_attributes, list_of_children, spare)

The dict_of_attributes can be None (meaning no attributes) or a
dictionary mapping attribute names to values. The list_of_children may
either be None (meaning a singleton tag) or a list with elements that
are 4-tuples or plain strings.

A great advantage of this representation - which only uses built-in
types in Python - is that you can marshal it (and then zip or encrypt
the results) with one line of Python code. Another is that one can write
fast C code to do things with the structure. And it does not require any
classes installed on the client machine, which is very useful when
moving xml-derived data around a network.

This does not capture the full structure of XML. We make decisions
before parsing about whether to expand entities and CDATA nodes, and the
parser deals with it; after parsing we have most of the XML file's
content, but we can't get back to the original in 100% of cases. For
example following two representations will both (with default settings)
return the string "Smith & Jones", and you can't tell from the tuple
tree which one was in the file:

::

    <provider>Smith &amp; Jones<provider>

Alternatively one can use

::

    <provider><[CDATA[Smith & Jones]]>]<![CDATA[]><provider>

So if you want a tool to edit and rewrite XML files with perfect
fidelity, our model is not rich enough. However, note that RXP itself
DOES provide all the hooks and could be the basis for such a parser.

1.9 Can I get involved?
-----------------------

Sure! Join us on the Reportlab-users mailing list
(*http://two.pairlist.net/mailman/listinfo/reportlab-users*), and feel free to contribute
patches. The final section of this manual has a brief "wish list".

Because the Reportlab Toolkit is used in many mission critical
applications and because tiny changes in parsers can have unintended
consequences, we will keep checkin rights on sourceforge to a trusted
few developers; but we will do our best to consider and process patches.