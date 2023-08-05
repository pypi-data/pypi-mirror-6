When reading HTML, named entities are often neater and easier to comprehend than
numeric entities, Unicode (or other charset) characters, or a mixture of all of
the above. Because they fall within the ASCII range, entities are also much
safer to use in multiple contexts than Unicode and its various encodings (UTF-8
and such).

This module helps convert from numerical HTML entities and Unicode characters
that fall outside the normal ASCII range into named entities. Or, if you prefer,
it will help you go the other way, mapping all entities into Unicode. And if you
decide you want entities of the counting type, it will even help you go numeric.
Decimal or hexadecimal.

Usage
=====

Python 2::

    from namedentities import *

    u = u'both em\u2014and&#x2013;dashes&hellip;'

    print "named:  ", repr(named_entities(u))
    print "numeric:", repr(numeric_entities(u))
    print "hex:"   ", repr(hex_entities(u))
    print "unicode:", repr(unicode_entities(u))

yields::

    named:   'both em&mdash;and&ndash;dashes&hellip;'
    numeric: 'both em&#8212;and&#8211;dashes&#8230;'
    hex:     'both em&#x2014;and&#x2013;dashes&#x2026;'
    unicode: u'both em\u2014and\u2013dashes\u2026'

You can do just about the same thing in Python 3, but you have to use a
``print`` function rather than a ``print`` statement, and prior to 3.3, you have
to skip the ``u`` prefix that in Python 2 marks string literals as being Unicode
literals. In Python 3.3 and following, however, you can start using the ``u``
marker again, if you like. It's an optional feature that doesn't do anything
terribly specific, because all Python 3 strings are Unicode--but it sure helps
with cross-version code compatibility. (You can use the ``six`` cross-version
compatibility library, as the tests do.)

One good use for ``unicode_entities`` is to create cross-platform,
cross-Python-version strings that conceptually contain
Unicode characters, but spelled out as named (or numeric) HTML entities. For
example::

    unicode_entities('This &rsquo;thing&rdquo; is great!')

This has the advantage of using only ASCII characters and common
string encoding mechanisms, yet rendering full Unicode strings upon
reconstitution.  You can use the other functions, say ``named_entities()``,
to go from Unicode characters to named entities.

Alternate API
=============

A new function ``entities(text, kind)`` takes text and the kind of entities
you'd like returned. ``kind`` can be ``named`` (the default), ``numeric``,
``hex``, ``unicode``, or ``none``.

Recent Changes
==============

 * As of 1.6, ``entities()`` API added. A slighly different import mechanism is used.

 * The ``numeric_entities(text)`` and ``hex_entities(text)`` APIs have been
   added, shifting the module's mission from "named entities" to "general
   purpose entity transformation." Live and learn!

 * The ``unescape(text)`` API changes all entities into Unicode characters.
   While long present, is now available for easy external consumption. It has an
   alias, ``unicode_entities(text)`` for parallelism with the other APIs.

 * Repackaged first as a Python package, rather than independent modules. Then,
   given my growing confidence in managing cross-version packages, previously
   separate backend implementations for Python 2 and Python 3 have been merged
   into a single backend.

 * Now successfully packaged for, and tests against, against Python
   2.6, 2.7, and 3.3, as well as PyPy 2.0.2 (based on 2.7.3).
   Automated multi-version testing managed with the wonderful `pytest
   <http://pypi.python.org/pypi/pytest>`_ and `tox
   <http://pypi.python.org/pypi/tox>`_.

 * Should also work under Python 2.5, 3.2, and 3.4 releases, and PyPy 1.9, but those
   are not "officially support" because they are aren't supported
   in my testing environment.

Notes
=====

 * Doesn't attempt to encode ``&lt;``, ``&gt;``, or
   ``&amp;`` (or their numerical equivalents) to avoid interfering
   with HTML escaping.

 * This module started as basically a packaging of `Ian Beck's work
   <http://beckism.com/2009/03/named_entities_python/>`_. While it's
   moved slighly forward since then, it's still mostly Ian under the
   covers. Thank you, Ian!

Installation
============

::

    pip install -U namedentities

To ``easy_install`` under a specific Python version (3.3 in this example)::

    python3.3 -m easy_install --upgrade namedentities

(You may need to prefix these with "sudo " to authorize installation.)
