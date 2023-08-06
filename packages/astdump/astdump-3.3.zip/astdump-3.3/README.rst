Get information from Python module without executing it. 

This is a tool and a library to work with Abstract Syntax Tree
(AST) of source code in Python. It can be used to explore AST,
inspect nodes and process them.

When used from command line, ``astdump.py`` can generate
``setup.py`` for your module or print its structure.


What is AST
-----------

There is a good talk `What would you do with an AST?
<http://desmaj.bitbucket.org/talks/>`_ by Matthew J Desmarais
with information that you will find useful.

`astdump` package provides dataset_ with generated examples of
AST representation for various Python snippets. Feel free to
clone repository and experiment with the code - it is safe and
version controlled.

For the curious, structure of Python abstract tree is defined in
http://hg.python.org/cpython/file/v2.7.6/Parser/Python.asdl


Command line usage
------------------

::

  $ ./astdump.py 
  Usage: astdump.py [options] <filename.py>

  AST dump tool to inspect Python source code without importing it. Can
  extract values of top level vars, automatically generate setup.py and
  dump structure of an Abstract Syntax Tree in readable format.

  Options:
    -h, --help  show this help message and exit
    --topvars   get top level variables
    --generate  generate setup.py for a given filename


Read top level variables from Python module without importing::

  $ ./astdump.py --topvars astdump.py
  __author__ = 'anatoly techtonik <techtonik@gmail.com>'
  __description__ = 'Extract information from Python module without importing it.'
  __license__ = 'Public Domain'
  __version__ = '3.0'

Automatically generate `setup.py`::

  $ ./astdump.py --generate astdump.py
  #!/usr/bin/env python
  from distutils.core import setup

  setup(
      name = 'astdump',
      version = '3.0',
      author = 'anatoly techtonik',
      author_email = 'techtonik@gmail.com',
      description = 'Extract information from Python module without importing it.',
      license = 'Public Domain',

      py_modules=['astdump'],
  )

'prettyprint' AST tree::

  $ ./astdump.py setup.py
  Module
    ImportFrom
      alias
    Expr
      Call
        Name
          Load
        keyword
          Str
        keyword
          Str
        ...
        keyword
          Str
        keyword
          List
            Str
            Load


Library Usage
-------------
``top_level_vars(filename)``
 Return name/value pairs for top level variables for the script specified as
 `filename`.
 Only string and int values are supported.

::

  >>> import astdump
  >>> astdump.top_level_vars("astdump.py")
  {'__version__': '3.0', '__description__': 'Extract information from Python
  module without importing it.', '__license__': 'Public Domain', '__author__
  ': 'anatoly techtonik <techtonik@gmail.com>'}


``indented(text, printres=True)``
 Print indented AST for the Python code specified in `text` variable. The goal
 is to print AST as pretty as possible, so the output is likely to change. If
 `printres` is false, return string instead.

::

  >>> import astdump
  >>> astdump.indented('2+3')
  Module
    Expr
      BinOp
        Num
        Add
        Num

``dumpattrs(node, indent=0, oneline=False, output=sys.stdout)``
 Dump attributes of given node to `output` (sys.stdout by default).
 If `oneline` is set, format output as one line. Otherwise dump one
 attribute per line with the given `indent`.

::

  >>> from astdump import dumpattrs as dat
  >>> import ast
  >>> root = ast.parse('2+3')
  >>> root
  <_ast.Module at 0x35f8790>
  >>> dat(root)
  body: [<_ast.Expr object at 0x035F8730>]
  >>> dat(root.body[0])
  value: <_ast.BinOp object at 0x035F8850>


Links
-----

.. # Tools that use Python AST

- `pss <https://bitbucket.org/eliben/pss>`_ - filetype aware grep for sources, with colors, public domain
- `redhawk <http://pypi.python.org/pypi/redhawk/>`_ - AST aware grep, BSD license

- `PythonJS <https://github.com/PythonJS/PythonJS>`_ - Python to JavaScript translator using AST, license BSD-3

- `astviewer <https://github.com/titusjan/astviewer>`_ - MIT licensed ASTree viewer in Qt (PySide)

.. # Discussions

- `python-ideas <https://groups.google.com/d/msg/python-ideas/d-LNcweOQDU/IskneIaEutwJ>`_ -
  original mail about static module/package inspection that started it all
- `python-static-type-checking <https://groups.google.com/forum/?fromgroups#!forum/python-static-type-checking/>`_ -
  Group about static analysis of Python programs
- `issue19557 <http://bugs.python.org/issue19557>`_ on Python bug tracker
  about incomplete official AST documentation 


Changes
-------
3.3 (2014-03-21)
 * setup.py generator is rewritten to look up missing
   attributes on PyPI, add classifiers and README read()
   for long description

3.2 (2013-11-27)
 * API change:

   * ``dumpattrs(node)`` helper to print node attributes

3.1 (2013-11-20)
 * fix missing dataset/ dir from source distribution

3.0 (2013-11-19)
 * added dataset/ dir with snippets, output examples and
   update.py that regenerates them. See dataset/README.txt
 * API changes:

   * added ``indented(text)`` to dump indented AST, only
     shows nodes for now
   * ``indented(text, printres=False)`` returns string
     instead of printing
   * made TreeDumper() silent by default. It just walks.

 * fixed pip install, added MANIFEST.in, added trove
   categories, thanks to Jonathan Eunice (pull request #1)

2.0 (2013-11-10)
 * API change:

   * remove --dump option, AST is dumped by default
   * add --topvars option for previous behaviour

1.2 (2013-11-10)
 * fix default output for Python 2 (broken in 1.1)

1.1 (2013-09-16)
 * support Python 3

1.0 (2012-03-29)
 * API change:
  
   * ``get_top_vars(node)`` is replaced with ``top_level_vars(filename)``


Release checklist
-----------------
| [ ] update version in astdump.py  
| [ ] run dataset/update.py for Python 2 and 3
| [ ] update README.rst
| [ ] python astdump.py --generate astdump.py >setup.py
| [ ] check that setup.py contains unix linefeeds
| [ ] setup.py sdist register upload
| [ ] hg tag


.. _dataset: https://bitbucket.org/techtonik/astdump/src/tip/dataset/
