===========
WS Recorder
===========

Last changes
============

0.0.1:
* added function: string-join

Description
===========

Set of Xpath2 functions which you can register in lxml. User register all or chosen functions
and use them in own xpaths. Xpaths are accessible under default namespace:
kjw.pt/xpath2-functions or empty namespace if needed.


Usage
=====

Example::

    from lxml import etree
    import xpath2_functions

    # registering all available functions in default namespace
    xpath2_functions.register_functions(etree)

    # registering chosen functions in the empty namespace
    xpath2_functions.register_functions(etree, ns=None, functions=['string-join'])


Functions
=========

- string-join(arg1 as `xs:string`, arg2 as `xs:string`) - returns a arg1 created by concatenating the members of the
    $arg1 sequence using $arg2 as a separator. If the value of $arg2 is the zero-length string, then the members
    of $arg1 are concatenated without a separator.

