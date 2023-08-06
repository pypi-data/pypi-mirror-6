3. Using pyRXP
==============

3.1. Simple use without validation
----------------------------------

3.1.1 The Parse method and callable instances of the parser
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Firstly you have to import the pyRXP module (using Python's import
statement). While we are here, pyRXP has a couple of attributes that are
worth knowing about: ``version`` gives you a string with the version number
of the pyRXP module itself, and ``RXPVersion`` gives you string with the
version information for the rxp library embedded in the module.

::

    >>> import pyRXP
    >>> pyRXP.version
    '1.16'
    >>> pyRXP.RXPVersion
    'RXP 1.5.0 Copyright Richard Tobin, LTG, HCRC, University of Edinburgh'

Once you have imported pyRXP, you can instantiate a parser instance
using the Parser class.

::

    >>>rxp=pyRXP.Parser()


To parse some XML, you use the ``parse`` method, passing a string as the first argument and
receiving the parsed Tuple Tree as a result:

::

    >>> rxp=pyRXP.Parser()
    >>> rxp.parse('<a>some text</a>')
    ('a', None, ['some text'], None)


As a shortcut, you can call the instance directly:

::

    >>> rxp=pyRXP.Parser()
    >>> rxp('<a>some text</a>')
    ('a', None, ['some text'], None)


__Note__:
Throughout this documentation, we'll use the explicit call syntax for clarity.

3.1.2 Basic usage
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

We'll start with some very simple examples and leave validation for
later.

::

    >>> rxp.parse('<tag>content</tag>')
    ('tag', None, ['content'], None)


Each element ("tag") in the XML is represented as a tuple of 4 elements:

-  'tag': the tag name (aka element name).
-  None: a dictionary of the tag's attributes (None here since it
   doesn't have any).
-  ['content']: a list of the children elements of the tag.
-  None: the fourth element is unused by default.

This tree structure is equivalent to the input XML, at least in
information content. It is theoretically possible to recreate the
original XML from this tree since no information has been lost.

A tuple tree for more complex XML snippets will contain more of these
tuples, but they will all use the same structure as this one.

::

    >>> rxp.parse('<tag1><tag2>content</tag2></tag1>')
    ('tag1', None, [('tag2', None, ['content'], None)], None)

This may be easier to understand if we lay it out differently:

::

    >>> rxp.parse('<tag1><tag2>content</tag2></tag1>')
    ('tag1',
     None,
         [('tag2',
           None,
           ['content'],
           None)
         ],
    None)

Tag1 is the name of the outer tag, which has no attributes. Its contents
is a list. This contents contains Tag2, which has its own attribute
dictionary (which is also empty since it has no attributes) and its
content, which is the string 'content'. It has the closing null element,
then the list for Tag2 is closed, Tag1 has its own final null element
and it too is closed.

The XML that is passed to the parser must be balanced. Any opening and
closing tags must match. They wouldn't be valid XML otherwise.

3.1.3 Empty tags and the ExpandEmpty flag
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Look at the following three examples. The first one is a fairly ordinary
tag with contents. The second and third can both be considered as empty
tags - one is a tag with no content between its opening and closing tag,
and the other is the singleton form which by definition has no content.

::

    >>> rxp.parse('<tag>my contents</tag>')
    ('tag', None, ['my contents'], None)

    >>> rxp.parse('<tag></tag>')
    ('tag', None, [], None)

    >>> rxp.parse('<tag/>')
    ('tag', None, None, None)

Notice how the contents list is handled differently for the last two
examples. This is how we can tell the difference between an empty tag
and its singleton version. If the content list is empty then the tag
doesn't have any content, but if the list is None, then it can't have
any content since it's the singleton form which can't have any by
definition.

Another example:

::

    >>>rxp.parse('<outerTag><innerTag>bb</innerTag>aaa<singleTag/></outerTag>')
    ('outerTag', None, [('innerTag', None, ['bb'], None), 'aaa', ('singleTag',
    None, None, None)], None)

Again, this is more understandable if we show it like this:

::

    ('outerTag',
     None,
         [('innerTag',
           None,
           ['bb'],
           None),
              'aaa',
                  ('singleTag',
                   None,
                   None,
                   None)
          ],
     None)

In this example, the tuple contains the outerTag (with no attribute
dictionary), whose list of contents are the innerTag, which contains the
string 'bb' as its contents, and the singleton singleTag whose contents
list is replaced by a null.

The way that these empty tags are handled can be changed using the
``ExpandEmpty`` flag. If ``ExpandEmpty`` is set to 0, these singleton forms come
out as None, as we have seen in the examples above. However, if you set
it to 1, the empty tags are returned as standard tags of their sort.

This may be useful if you will need to alter the tuple tree at some
future point in your processing. Lists and dictionaries are mutable, but
None isn't and therefore can't be changed.

Some examples. This is what happens if we accept the default behaviour:

::

    >>> rxp.parse('<a>some text</a>')
    ('a', None, ['some text'], None)

Explicitly setting ExpandEmpty to 1 gives us these:

::

    >>> rxp.parse('<a>some text</a>', ExpandEmpty=1)
    ('a', {}, ['some text'], None)

Notice how the None from the first example is being returned as an empty
dictionary in the second version. ``ExpandEmpty`` makes the sure that the
attribute list is always a dictionary. It also makes sure that a
self-closed tag returns an empty list.

A very simple example of the singleton or 'self-closing' version of a
tag.

::

    >>> rxp.parse('<b/>', ExpandEmpty=0)
    ('b', None, None, None)

::

    >>> rxp.parse('<b/>', ExpandEmpty=1)
    ('b', {}, [], None)

Again, notice how the Nones have been expanded.

Some more examples show how these work with slightly more complex XML
which uses nested tags:

::

    >>> rxp.parse('<a>some text<b>Hello</b></a>', ExpandEmpty=0)
    ('a', None, ['some text', ('b', None, ['Hello'], None)], None)

    >>> rxp.parse('<a>some text<b>Hello</b></a>', ExpandEmpty=1)
    ('a', {}, ['some text', ('b', {}, ['Hello'], None)], None)

::

    >>> rxp.parse('<a>some text<b></b></a>', ExpandEmpty=0)
    ('a', None, ['some text', ('b', None, [], None)], None)

    >>> rxp.parse('<a>some text<b></b></a>', ExpandEmpty=1)
    ('a', {}, ['some text', ('b', {}, [], None)], None)

::

    >>> rxp.parse('<a>some text<b/></a>', ExpandEmpty=0)
    ('a', None, ['some text', ('b', None, None, None)], None)

    >>> rxp.parse('<a>some text<b/></a>', ExpandEmpty=1)
    ('a', {}, ['some text', ('b', {}, [], None)], None)

3.1.4 Processing instructions
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Both the comment and processing instruction tag names are special - you
can check for them relatively easily. This section processing
instruction and the next one covers handling comments.

A processing instruction allows developers to place information specific
to an outside application within the document. You can handle it using
the ``ReturnProcessingInstruction`` attribute.

::

    >>> rxp.parse(<a><?works document="hello.doc"?></a>')
    ('a', None, [], None)
    >>> #vanishes - like a comment
    >>> rxp.parse('<a><?works document="hello.doc"?></a>', ReturnProcessingInstructions=1)
    ('a', None, [('<?', {'name': 'works'}, ['document="hello.doc"'], None)], None)
    >>>


pyRXP uses a module pseudo-constant called ``piTagName`` (it's not an instance
attribute) to check for processing instructions:

::

    >>> pyRXP.piTagName
    '<?'

You can test against ``piTagName`` - but don't try and change it. See the
section on trying to change ``commentTagName`` for an example of what would
happen.

::

    >>> rxp.parse('<a><?works document="hello.doc"?></a>',
    ... ReturnProcessingInstructions=1)[2][0][0] is pyRXP.piTagName
    True

This is a simple test and doesn't even have to process the characters.
It allows you to process these lists looking for processing instructions
(or comments if you are testing against ``commentTagName`` as shown in the
next section)

3.1.5 Handling comments and the srcName attribute
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

**NB** The way ``ReturnComments`` works has changed between versions.

By default, PyRXP ignores comments and their contents are lost (this
behaviour can be changed - see the section of Flags later for details).

::

    >>> rxp.parse('<tag><!-- this is a comment about the tag --></tag>')
    ('tag', None, [], None)

    >>> rxp.parse('<!-- this is a comment -->')
    Traceback (most recent call last):
      File "<stdin>", line 1, in <module>
    pyRXP.error: Error: Document ends too soon
     in unnamed entity at line 1 char 27 of [unknown]
    Document ends too soon
    Parse Failed!

This causes an error, since the parser sees an empty string which isn't
valid XML.

It is possible to set pyRXP to not swallow comments using the
``ReturnComments`` attribute.

::


    >>> rxp.parse('<tag><!-- this is a comment about the tag --></tag>', ReturnComments=1)
    ('tag', None, [('<!--', None, [' this is a comment about the tag '], None)], None)

Using ``ReturnComments``, the comment are returned in the same way as an
ordinary tag, except that the tag has a special name. This special name
is defined in the module pseudo-constant ``commentTagName`` (again, not an instance attribute):

::

    >>> rxp.commentTagName
    Traceback (most recent call last):
      File "<stdin>", line 1, in <module>
    AttributeError: commentTagName

    >>> pyRXP.commentTagName
    '<!--'

Please note that changing ``commentTagName`` won't work: what would be changed is simply the
Python representation, while the underlying C object would remain untouched:

::

    >>> import pyRXP
    >>> p=pyRXP.Parser()
    >>> pyRXP.commentTagName = "##" # THIS WON'T WORK!
    >>> pyRXP.commentTagName
    '##'
    >>> #LOOKS LIKE IT WORKS - BUT SEE BELOW FOR WHY IT DOESN'T
    >>> rxp.parse('<a><!-- this is another comment comment --></a>', ReturnComments = 1)
    >>> # DOESN'T WORK!
    >>> ('a', None, [('<!--', None, [' this is another comment comment '], None)], None)
    >>> #SEE?

What it is useful for is to check against to see if you have been
returned a comment:

::

    >>> rxp.parse('<a><!-- comment --></a>', ReturnComments=1)
    ('a', None, [('<!--', None, [' comment '], None)], None)
    >>> rxp.parse('<a><!-- comment --></a>', ReturnComments=1)[2][0][0]
    '<!--'
    >>> #this returns the comment name tag from the tuple tree...
    >>> rxp.parse('<a><!-- comment --></a>', ReturnComments=1)[2][0][0] is pyRXP.commentTagName
    1
    >>> #they're identical
    >>> #it's easy to check if it's a special name

Using ``ReturnComments`` is useful, but there are circumstances where it
fails. Comments which are outside the root tag (in the following
snippet, that means which are outside the tag '<tag/>', ie the last
element in the line) will still be lost:

::


    >>> rxp.parse('<tag/><!-- this is a comment about the tag -->', ReturnComments=1)
    ('tag', None, None, None)

To get around this, you need to use the ``ReturnList`` attribute:

::

    >>> rxp.parse('<tag/><!-- this is a comment about the tag -->', ReturnComments=1, ReturnList=1)
    [('tag', None, None, None), ('<!--', None, [' this is a comment about the tag '], None)]
    >>>

Since we've seen a number of errors in the preceding paragraphs, it
might be a good time to mention the ``srcName`` attribute. The Parser has an
attribute called ``srcName`` which is useful when debugging. This is the
name by which pyRXP refers to your code in tracebacks. This can be
useful - for example, if you have read the XML in from a file, you can
use the ``srcName`` attribute to show the filename to the user. It doesn't
get used for anything other than pyRXP Errors - SyntaxErrors and
IOErrors still won't refer to your XML by name.

::

    >>> rxp.srcName = 'mycode'
    >>> rxp.parse('<a>aaa</a')
    Traceback (most recent call last):
      File "<stdin>", line 1, in <module>
    pyRXP.error: Error: Expected > after name in end tag, but got <EOE>
     in unnamed entity at line 1 char 10 of mycode
    Expected > after name in end tag, but got <EOE>
    Parse Failed!

The XML that is passed to the parser must be balanced. Not only must the
opening and closing tags match (they wouldn't be valid XML otherwise),
but there must also be one tag that encloses all the others. If there
are valid fragments that aren't enclosed by another valid tag, they are
considered 'multiple elements' and a pyRXP Error is raised.

::

    >>> rxp.parse('<a></a><b></b>')
    Traceback (most recent call last):
      File "<stdin>", line 1, in <module>
    pyRXP.error: Error: Document contains multiple elements
     in unnamed entity at line 1 char 9 of mycode
    Document contains multiple elements
    Parse Failed!

    >>> rxp.parse('<outer><a></a><b></b></outer>')
    ('outer', None, [('a', None, [], None), ('b', None, [], None)], None)

3.1.6 A brief note on pyRXPU
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

PyRXPU is the 16-bit Unicode aware version of pyRXP.

In most cases, the only difference in behaviour between pyRXP and pyRXPU
is that pyRXPU returns Unicode strings. This may be inconveneient for
some applications as Python doesn't yet handle unicode filenames etc
terribly well. A work around is to get pyRXPU to return **utf8** using
the *ReturnUTF8* boolean argument in the parser creation or call. Then
all values are returned as utf8 encoded strings.

pyRXPU is built to try and do the right thing with both unicode and
non-unicode strings.

::

    >>> import pyRXPU
    >>> pyRXPU.Parser()('<a><?works document="hello.doc"?></a>', ReturnProcessingInstructions=1)
    (u'a', None, [(u'<?', {'name': u'works'}, [u'document="hello.doc"'], None)], None)

In most cases, the only way to tell the difference (*other* than sending
in Unicode) is by the module name.

::

    >>> import pyRXPU
    >>> pyRXPU.__name__
    'pyRXPU'
    >>> import pyRXP
    >>> pyRXP.__name__
    'pyRXP'

3.2. Validating against a DTD
-------------------------------------------------------------------------

This section describes the default behaviours when validating against a
DTD. Most of these can be changed - see the section on flags later in
this document for details on how to do that.

For the following examples, we're going to assume that you have a single
directory with the DTD and any test files in it.

::

    >>> dtd = open('tinydtd.dtd', 'r').read()

    >>> print dtd
    <!-- A tiny sample DTD for use with the PyRXP documentation -->
    <!-- $Header $-->

    <!ELEMENT a (b)>
    <!ELEMENT b (#PCDATA)*>

This is just to show you how trivial the DTD is for this example. It's
about as simple as you can get - two tags, both mandatory. Both a and b
must appear in an xml file for it to conform to this DTD, but you can
have as many b's as you want, and they can contain any content.

::

    >>> fn=open('sample1.xml', 'r').read()

    >>> print fn
    <?xml version="1.0" encoding="iso-8859-1" standalone="no" ?>
    <!DOCTYPE a SYSTEM "tinydtd.dtd">

    <a>
    <b>This is the contents</b>
    </a>

This is the simple example file. The first line is the XML declaration,
and the *standalone="no"* part says that there should be an external
DTD. The second line says where the DTD is, and gives the name of the
root element - *a* in this case. If you put this in your XML document,
pyRXP will attempt to validate it.

::


    >> rxp.parse(fn)
    ('a',
     None,
     ['\n', ('b', None, ['This tag is the contents'], None), '\n'],
     None)
    >>>

This is a successful parse, and returns a tuple tree in the same way as
we have seen where the input was a string.

If you have a reference to a non-existant DTD file in a file (or one
that can't be found over a network), then any attempt to parse it will
raise a pyRXP error.

::


    >>> fn=open('sample2.xml', 'r').read()

    >>> print fn
    <?xml version="1.0" encoding="iso-8859-1" standalone="no" ?>
    <!DOCTYPE a SYSTEM "nonexistent.dtd">

    <a>
    <b>This is the contents</b>
    </a>

    >>> rxp.parse(fn)
    C:\tmp\pyRXP_tests\nonexistent.dtd: No such file or directory
    Traceback (most recent call last):
      File "<stdin>", line 1, in <module>
    pyRXP.Error: Error: Couldn't open dtd entity file:///C:/tmp/pyRXP_tests/nonexistent.dtd
     in unnamed entity at line 2 char 38 of [unknown]

This is a different kind of error to one where no DTD is specified:

::


    >>> fn=open('sample4.xml', 'r').read()

    >>> print fn
    <?xml version="1.0" encoding="iso-8859-1" standalone="no" ?>
    <a>
    <b>This is the contents</b>
    </a>

    >>> rxp.parse(fn,NoNoDTDWarning=0)
    Traceback (most recent call last):
      File "<stdin>", line 1, in <module>
    pyRXP.error: Error: Document has no DTD, validating abandoned
     in unnamed entity at line 3 char 2 of [unknown]
    Document has no DTD, validating abandoned
    Parse Failed!

If you have errors in your XML and it does not validate against the DTD,
you will get a different kind of pyRXPError.

::

    >>> fn=open('sample3.xml', 'r').read()

    >>> print fn
    <?xml version="1.0" encoding="iso-8859-1" standalone="no" ?>
    <!DOCTYPE a SYSTEM "tinydtd.dtd">

    <x>
    <b>This is the contents</b>
    </x>

    >>> rxp.parse(fn)
    Traceback (most recent call last):
      File "<stdin>", line 1, in <module>
    pyRXP.Error: Error: Start tag for undeclared element x
     in unnamed entity at line 4 char 3 of [unknown]
    >>>

Whether PyRXP validates against a DTD, together with a number of other
behaviours is decided by how the various flags are set.

By default, ``ErrorOnValidityErrors`` is set to 1, as is ``NoNoDTDWarning``.
If you want the XML you are parsing to actually validate against your DTD,
you should have both of these set to 1 (which is the default value),
otherwise instead of raising a pyRXP error saying the XML that doesn't
conform to the DTD (which may or may not exist) this will be silently
ignored. You should also have ``Validate`` set to 1, otherwise validation
won't even be attempted.

Note that the first examples in this chapter - the ones without a DTD -
only worked because we had carefully chosen what seem like the sensible
defaults. It is set to validate, but not to complain if the DTD is
missing. So when you feed it something without a DTD declaration, it
notices the DTD is missing but continues in non-validating mode. There
are numerous flags set out below which affect the behaviour.

3.3 Interface Summary
-------------------------------------------------------------------------

The python module exports the following:

``error``

a python exception

``version``

the string version of the module

``RXPVersion``

the version string of the rxp library embedded in the module

``parser_flags``

a dictionary of parser flags - the values are the defaults for parsers

``Parser(**kwargs)``

Create a parser

``piTagName``

special tagname used for processing instructions

``commentTagName``

special tagname used for comments

``recordLocation``

a special do nothing constant that can be used as the 'fourth' argument
and causes location information to be recorded in the fourth position of
each node.

3.4 Parser Object Attributes and Methods
-------------------------------------------------------------------------

``parse(src, **kwargs)``

We have already seen that this is the main interface to the parser. It
returns ReportLab's standard tuple tree representation of the xml
source. The string *src* contains the xml.

The keyword arguments can modify the instance attributes for this call
only. For example, we can do

::

    >>> rxp.parse('<a>some text</a>', ReturnList=1, ReturnComments=1)

instead of

::

    >>> rxp.ReturnList=1
    >>> rxp.ReturnComments=1
    >>> rxp.parse('<a>some text</a>')

Any other parses using rxp will be unaffacted by the values of ``ReturnList``
and ``ReturnComments`` in the first example, whereas all parses using p will
have ``ReturnList`` and ``ReturnComments`` set to 1 after the second.

``srcName``

A name used to refer to the source text in error and warning messages.
It is initially set as '<unknown>'. If you know that the data came from
"spam.xml" and you want error messages to say so, you can set this to
the filename.

``warnCB``

Warning callback. Should either be None, 0, or a callable object (e.g. a
function) with a single argument which will receive warning messages. If
None is used then warnings are thrown away. If the default 0 value is
used then warnings are written to the internal error message buffer and
will only be seen if an error occurs.

``eoCB``

Entity-opening callback. The argument should be None or a callable
method with a single argument. This method will be called when external
entities are opened. The method should return a (possibly modified) URI.
So, you could intercept a declaration referring to
*http://some.slow.box/somefile.dtd* and point at at the local copy you
know you have handy, or implement a DTD-caching scheme.

``fourth``

This argument should be None (default) or a callable method with no
arguments. If callable, will be called to get or generate the 4th item
of every 4-item tuple or list in the returned tree. May also be the
special value ``pyRXP.recordLocation`` to cause the 4th item to be set to a
location information tuple
((startname,startline,startchar),(endname,endline,endchar)).

3.5 List of Flags
-------------------------------------------------------------------------

Flag attributes corresponding to the rxp flags; the values are the
module standard defaults. ``pyRXP.parser_flags`` returns these as a
dictionary if you need to refer to these inline.

+----------------------------------+-----------+
| Flag (1=on, 0=off)               | Default   |
+----------------------------------+-----------+
| AllowMultipleElements            | 0         |
+----------------------------------+-----------+
| AllowUndeclaredNSAttributes      | 0         |
+----------------------------------+-----------+
| CaseInsensitive                  | 0         |
+----------------------------------+-----------+
| ErrorOnBadCharacterEntities      | 1         |
+----------------------------------+-----------+
| ErrorOnUndefinedAttributes       | 0         |
+----------------------------------+-----------+
| ErrorOnUndefinedElements         | 0         |
+----------------------------------+-----------+
| ErrorOnUndefinedEntities         | 1         |
+----------------------------------+-----------+
| ErrorOnUnquotedAttributeValues   | 1         |
+----------------------------------+-----------+
| ErrorOnValidityErrors            | 1         |
+----------------------------------+-----------+
| ExpandCharacterEntities          | 1         |
+----------------------------------+-----------+
| ExpandEmpty                      | 0         |
+----------------------------------+-----------+
| ExpandGeneralEntities            | 1         |
+----------------------------------+-----------+
| IgnoreEntities                   | 0         |
+----------------------------------+-----------+
| IgnorePlacementErrors            | 0         |
+----------------------------------+-----------+
| MaintainElementStack             | 1         |
+----------------------------------+-----------+
| MakeMutableTree                  | 0         |
+----------------------------------+-----------+
| MergePCData                      | 1         |
+----------------------------------+-----------+
| NoNoDTDWarning                   | 1         |
+----------------------------------+-----------+
| NormaliseAttributeValues         | 1         |
+----------------------------------+-----------+
| ProcessDTD                       | 0         |
+----------------------------------+-----------+
| RelaxedAny                       | 0         |
+----------------------------------+-----------+
| ReturnComments                   | 0         |
+----------------------------------+-----------+
| ReturnProcessingInstructions     | 0         |
+----------------------------------+-----------+
| ReturnDefaultedAttributes        | 1         |
+----------------------------------+-----------+
| ReturnList                       | 0         |
+----------------------------------+-----------+
| ReturnNamespaceAttributes        | 0         |
+----------------------------------+-----------+
| ReturnUTF8 (pyRXPU)              | 0         |
+----------------------------------+-----------+
| SimpleErrorFormat                | 0         |
+----------------------------------+-----------+
| TrustSDD                         | 1         |
+----------------------------------+-----------+
| Validate                         | 1         |
+----------------------------------+-----------+
| WarnOnRedefinitions              | 0         |
+----------------------------------+-----------+
| XMLExternalIDs                   | 1         |
+----------------------------------+-----------+
| XMLLessThan                      | 0         |
+----------------------------------+-----------+
| XMLMiscWFErrors                  | 1         |
+----------------------------------+-----------+
| XMLNamespaces                    | 0         |
+----------------------------------+-----------+
| XMLPredefinedEntities            | 1         |
+----------------------------------+-----------+
| XMLSpace                         | 0         |
+----------------------------------+-----------+
| XMLStrictWFErrors                | 1         |
+----------------------------------+-----------+
| XMLSyntax                        | 1         |
+----------------------------------+-----------+

3.6 Flag explanations and examples
-------------------------------------------------------------------------

With so many flags, there is a lot of scope for interaction between
them. These interactions are not documented yet, but you should be aware
that they exist.

.. _AllowMultipleElements:

AllowMultipleElements
^^^^^^^^^^^^^^^^^^^^^

Default: 0

Description:

A piece of XML that does not have a single root-tag enclosing all the
other tags is described as having multiple elements. By default, this
will raise a pyRXP error. Turning this flag on will ignore this and not
raise those errors.

Example:

::

    >>> rxp.AllowMultipleElements = 0
    >>> rxp.parse('<a></a><b></b>')
    Traceback (most recent call last):
      File "<stdin>", line 1, in <module>
    pyRXP.error: Error: Document contains multiple elements
     in unnamed entity at line 1 char 9 of [unknown]
    Document contains multiple elements

    >>> rxp.AllowMultipleElements = 1
    >>> rxp.parse('<a></a><b></b>')
    ('a', None, [], None)

.. _AllowUndeclaredNSAttributes:

AllowUndeclaredNSAttributes
^^^^^^^^^^^^^^^^^^^^^^^^^^^

Default: 0

Description:

*[to be added]*

Example:

*[to be added]*

.. _CaseInsensitive:

CaseInsensitive
^^^^^^^^^^^^^^^

Default: 0

Description:

This flag controls whether the parse is case sensitive or not.

Example:

::

    >>> rxp.CaseInsensitive=1
    >>> rxp.parse('<a></A>')
    ('A', None, [], None)

    >>> rxp.CaseInsensitive=0
    >>> rxp.parse('<a></A>')
    Traceback (most recent call last):
      File "<stdin>", line 1, in <module>
    pyRXP.error: Error: Mismatched end tag: expected </a>, got </A>
     in unnamed entity at line 1 char 7 of [unknown]
    Mismatched end tag: expected </a>, got </A>

.. _ErrorOnBadCharacterEntities:

ErrorOnBadCharacterEntities
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Default: 1

Description:

If this is set, character entities which expand to illegal values are an
error, otherwise they are ignored with a warning.

Example:

::

    >>> rxp.ErrorOnBadCharacterEntities=0
    >>> rxp.parse('<a>&#999;</a>')
    ('a', None, [''], None)

    >>> rxp.ErrorOnBadCharacterEntities=1
    >>> rxp.parse('<a>&#999;</a>')
    Traceback (most recent call last):
      File "<stdin>", line 1, in <module>
    pyRXP.error: Error: 0x3e7 is not a valid 8-bit XML character
     in unnamed entity at line 1 char 10 of [unknown]
    0x3e7 is not a valid 8-bit XML character

.. _ErrorOnUndefinedAttributes:

ErrorOnUndefinedAttributes
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Default: 0

Description:

If this is set and there is a DTD, references to undeclared attributes
are an error.

See also: :ref:`ErrorOnUndefinedElements`

.. _ErrorOnUndefinedElements:

ErrorOnUndefinedElements
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Default: 0

Description:

If this is set and there is a DTD, references to undeclared elements are
an error.

See also: :ref:`ErrorOnUndefinedAttributes`

.. _ErrorOnUndefinedEntities:

ErrorOnUndefinedEntities
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Default: 1

Description:

If this is set, undefined general entity references are an error,
otherwise a warning is given and a fake entity constructed whose value
looks the same as the entity reference.

Example:

::

    >>> rxp.ErrorOnUndefinedEntities=0
    >>> rxp.parse('<a>&dud;</a>')
    ('a', None, ['&dud;'], None)

    >>> rxp.ErrorOnUndefinedEntities=1
    >>> rxp.parse('<a>&dud;</a>')
    Traceback (most recent call last):
      File "<stdin>", line 1, in <module>
    pyRXP.error: Error: Undefined entity dud
     in unnamed entity at line 1 char 9 of [unknown]
    Undefined entity dud

.. _ErrorOnUnquotedAttributeValues:

ErrorOnUnquotedAttributeValues
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Default: 1

Description:

*[to be added]*

.. _ErrorOnValidityErrors:

ErrorOnValidityErrors
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Default: 1

Description:

If this is on, validity errors will be reported as errors rather than
warnings. This is useful if your program wants to rely on the validity
of its input.

.. _ExpandEmpty:

ExpandEmpty
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Default: 0

Description:

If false, empty attribute dicts and empty lists of children are changed
into the value None in every 4-item tuple or list in the returned tree.

.. _ExpandCharacterEntities:

ExpandCharacterEntities
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Default: 1

Description:

If this is set, entity references are expanded. If not, the references
are treated as text, in which case any text returned that starts with an
ampersand must be an entity reference (and provided ``MergePCData`` is off,
all entity references will be returned as separate pieces).

See also: :ref:`ExpandGeneralEntities`, :ref:`ErrorOnBadCharacterEntities`

Example:

::

    >>> rxp.ExpandCharacterEntities=1
    >>> rxp.parse('<a>&#109;</a>')
    ('a', None, ['m'], None)

    >>> rxp.ExpandCharacterEntities=0
    >>> rxp.parse('<a>&#109;</a>')
    ('a', None, ['&#109;'], None)



.. _ExpandGeneralEntities:

ExpandGeneralEntities
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Default: 1

Description:

If this is set, entity references are expanded. If not, the references
are treated as text, in which case any text returned that starts with an
ampersand must be an entity reference (and provided ``MergePCData`` is off,
all entity references will be returned as separate pieces).

See also: :ref:`ExpandCharacterEntities`

Example:

::

    >>> rxp.ExpandGeneralEntities=0
    >>> rxp.parse('<a>&amp;</a>')
    ('a', None, ['&amp;'], None)

    >>> rxp.ExpandGeneralEntities=1
    >>> rxp.parse('<a>&amp;</a>')
    ('a', None, ['&#38;'], None)

.. _IgnoreEntities:

IgnoreEntities
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Default: 0

Description:

If this flag is on, normal entity substitution takes place. If it is
off, entities are passed through unaltered.

Example:

::

    >>> rxp.IgnoreEntities=0
    >>> rxp.parse('<a>&amp;</a>')
    ('a', None, ['&#38;'], None)

    >>> rxp.IgnoreEntities=1
    >>> rxp.parse('<a>&amp;</a>')
    ('a', None, ['&amp;'], None)

.. _IgnorePlacementErrors:

IgnorePlacementErrors
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Default: 0

Description:

*[to be added]*

.. _MaintainElementStack:

MaintainElementStack
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Default: 1

Description:

*[to be added]*

.. _MakeMutableTree:

MakeMutableTree
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Default: 0

Description:

If false, nodes in the returned tree are 4-item tuples; if true, 4-item
lists.

.. _MergePCData:

MergePCData
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Default: 1

Description:

If this is set, text data will be merged across comments and entity
references.

.. _NoNoDTDWarning:

NoNoDTDWarning
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Default: 1

Description:

Usually, if ``Validate`` is set, the parser will produce a warning if the
document has no DTD. This flag suppresses the warning (useful if you
want to validate if possible, but not complain if not).

.. _NormaliseAttributeValues:

NormaliseAttributeValues
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Default: 1

Description:

If this is set, attributes are normalised according to the standard. You
might want to not normalise if you are writing something like an editor.

.. _ProcessDTD:

ProcessDTD
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Default: 0

Description:

If ``TrustSDD`` is set and a DOCTYPE declaration is present, the internal
part is processed and if the document was not declared standalone or if
``Validate`` is set the external part is processed. Otherwise, whether the
DOCTYPE is automatically processed depends on ``ProcessDTD``; if ``ProcessDTD``
is not set the DOCTYPE is not processed.

See also: :ref:`TrustSDD`

.. _RelaxedAny:

RelaxedAny
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Default: 0

Description:

*[to be added]*

.. _ReturnComments:

ReturnComments
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Default: 0

Description:

If this is set, comments are returned as nodes with tag name
``pyRXP.commentTagName``, otherwise they are ignored.

Example:

::

    >>> rxp.ReturnComments = 1
    >>> rxp.parse('<a><!-- this is a comment --></a>')
    ('a', None, [('<!--', None, [' this is a comment '], None)], None)
    >>> rxp.ReturnComments = 0
    >>> rxp.parse('<a><!-- this is a comment --></a>')
    ('a', None, [], None)

See also: :ref:`ReturnList`

.. _ReturnDefaultedAttributes:

ReturnDefaultedAttributes
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Default: 1

Description:

If this is set, the returned attributes will include ones defaulted as a
result of ATTLIST declarations, otherwise missing attributes will not be
returned.

.. _ReturnList:

ReturnList
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Default: 0

Description:

If both ``ReturnComments`` and ``ReturnList`` are set to 1, the whole list
(including any comments) is returned from a parse. If ``ReturnList`` is set
to 0, only the first tuple in the list is returned (ie the actual XML
content rather than any comments before it).

Example:

::

    >>> rxp.ReturnComments=1
    >>> rxp.ReturnList=1
    >>> rxp.parse('<!-- comment --><a>Some Text</a><!-- another comment -->')
    [('<!--', None, [' comment '], None), ('a', None, ['Some Text'], None), ('<!--',
     None, [' another comment '], None)]
    >>> rxp.ReturnList=0
    >>> rxp.parse('<!-- comment --><a>Some Text</a><!-- another comment -->')
    ('a', None, ['Some Text'], None)
    >>>

See also: :ref:`ReturnComments`

.. _ReturnNamespaceAttributes:

ReturnNamespaceAttributes
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Default: 0

Description:

*[to be added]*

.. _ReturnProcessingInstructions:

ReturnProcessingInstructions
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Default: 0

Description:

If this is set, processing instructions are returned as nodes with
tagname ``pyRXP.piTagname``, otherwise they are ignored.

.. _SimpleErrorFormat:

SimpleErrorFormat
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Default: 0

Description:

This causes the output on errors to get shorter and more compact.

Example:

::

    >>> rxp.SimpleErrorFormat=0
    >>> rxp.parse('<a>causes an error</b>')
    Traceback (most recent call last):
      File "<stdin>", line 1, in <module>
    pyRXP.error: Error: Mismatched end tag: expected </a>, got </b>
     in unnamed entity at line 1 char 22 of [unknown]
    Mismatched end tag: expected </a>, got </b>

    >>> rxp.SimpleErrorFormat=1
    >>> rxp.parse('<a>causes an error</b>')
    Traceback (most recent call last):
      File "<stdin>", line 1, in <module>
    pyRXP.error: [unknown]:1:22: Mismatched end tag: expected </a>, got </b>
    Mismatched end tag: expected </a>, got </b>

.. _TrustSDD:

TrustSDD
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Default: 1

Description:

If ``TrustSDD`` is set and a DOCTYPE declaration is present, the internal
part is processed and if the document was not declared standalone or if
``Validate`` is set the external part is processed.

See also: :ref:`ProcessDTD`

.. _Validate:

Validate
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Default: 1

Description:

If this is on, the parser will validate the document. If it's off, it
won't. It is not usually a good idea to set this to 0.

.. _WarnOnRedefinitions:

WarnOnRedefinitions
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Default: 0

Description:

If this is on, a warning is given for redeclared elements, attributes,
entities and notations.

.. _XMLExternalIDs:

XMLExternalIDs
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Default: 1

Description:

*[to be added]*

.. _XMLLessThan:

XMLLessThan
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Default: 0

Description:

*[to be added]*

.. _XMLMiscWFErrors:

XMLMiscWFErrors
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Default: 1

Description:

To do with well-formedness errors.

See also: :ref:`XMLStrictWFErrors`

.. _XMLNamespaces:

XMLNamespaces
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Default: 0

Description:

If this is on, the parser processes namespace declarations (see below).
Namespace declarations are *not* returned as part of the list of
attributes on an element. The namespace value will be prepended to names
in the manner suggested by James Clark ie if *xmlns:foo='foovalue'* is
active then *foo:name-->{fovalue}name*.

See also: :ref:`XMLSpace`

.. _XMLPredefinedEntities:

XMLPredefinedEntities
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Default: 1

Description:

If this is on, pyRXP recognises the standard preset XML entities &amp;
&lt; &gt; &quot; and &apos;) . If this is off, all entities including
the standard ones must be declared in the DTD or an error will be
raised.

Example:

::

    >>> rxp.XMLPredefinedEntities=1
    >>> rxp.parse('<a>&amp;</a>')
    ('a', None, ['&'], None)

    >>> rxp.XMLPredefinedEntities=0
    >>> rxp.parse('<a>&amp;</a>')
    Traceback (most recent call last):
      File "<stdin>", line 1, in <module>
    pyRXP.error: [unknown]:1:9: Undefined entity amp
    Undefined entity amp


.. _XMLSpace:

XMLSpace
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Default: 0

Description:

If this is on, the parser will keep track of xml:space attributes

See also: :ref:`XMLNamespaces`

.. _XMLStrictWFErrors:

XMLStrictWFErrors
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Default: 1

Description:

If this is set, various well-formedness errors will be reported as
errors rather than warnings.

.. _XMLSyntax:

XMLSyntax
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Default: 1

Description:

*[to be added]*
