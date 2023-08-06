This directory contains dataset of AST dumps for
various Python snippets. The goal is to provide
100% coverage of node parameters that can appear
as arguments of your generic visitor.


Files in this dir:

 - README.txt  - this one, contains description
                 and check list with status of
                 coverage
 - node_*.txt  - semi-automatically updated AST
                 dump files
 - update.py   - script that automatically
                 updates node_*.txt files


---[node_*.txt format and update.py automation]--

Let's start with example:

  node_Assign_01.txt
  ^                -- prefix to filter dataset
       ^           -- node name
             ^     -- optional suffix to allow
                      many snippets for one node

All lines in this file are either:

  # comments
  ---[section delimiters]---
  everything else

All files consist of three sections:

  1. comments and Python snippet to be dumped
  2. output of ast.dump() from stdlib
  3. current output of astdump.py

You need to write onlt the first section and run
update.py - it will fill or update other sections
automatically.

Mercurial is used to revert changes back, so feel
free to experiment with astdump.py and update.py,
try different Python versions on this dataset and
compare results.


---[dataset checklist]---------------------------

Checklist of dataset coverage for building AST
visitors is below. It is ASDL definition from
Python source code:

http://hg.python.org/cpython/file/v2.7.6/Parser/Python.asdl

Every important line that AST visitor should care
about is prepended with a checkbox. To expand,
add new file with your snippet and run update.py


---[checklist]-----------------------------------

Legend:
 [ ]  - not implemented
 [x]  - done
 [?]  - unknown


    -- ASDL's five builtin types are identifier, int, string, object, bool

    module Python version "$Revision$"
    {
[?]     mod = Module(stmt* body)
[?]         | Interactive(stmt* body)
[?]         | Expression(expr body)

[?]         -- not really an actual node but useful in Jython's typesystem.
[?]         | Suite(stmt* body)

[?]     stmt = FunctionDef(identifier name, arguments args, 
[?]                             stmt* body, expr* decorator_list)
[?]           | ClassDef(identifier name, expr* bases, stmt* body, expr* decorator_list)
[?]           | Return(expr? value)

[?]           | Delete(expr* targets)
[ ]           | Assign(expr* targets, expr value)
[?]           | AugAssign(expr target, operator op, expr value)

[?]           -- not sure if bool is allowed, can always use int
[?]           | Print(expr? dest, expr* values, bool nl)

[?]           -- use 'orelse' because else is a keyword in target languages
[?]           | For(expr target, expr iter, stmt* body, stmt* orelse)
[?]           | While(expr test, stmt* body, stmt* orelse)
[?]           | If(expr test, stmt* body, stmt* orelse)
[?]           | With(expr context_expr, expr? optional_vars, stmt* body)

[?]           -- 'type' is a bad name
[?]           | Raise(expr? type, expr? inst, expr? tback)
[?]           | TryExcept(stmt* body, excepthandler* handlers, stmt* orelse)
[?]           | TryFinally(stmt* body, stmt* finalbody)
[x]           | Assert(expr test, expr? msg)

[?]           | Import(alias* names)
[?]           | ImportFrom(identifier? module, alias* names, int? level)

[?]           -- Doesn't capture requirement that locals must be
[?]           -- defined if globals is
[?]           -- still supports use as a function!
[?]           | Exec(expr body, expr? globals, expr? locals)

[?]           | Global(identifier* names)
[?]           | Expr(expr value)
[?]           | Pass | Break | Continue

[?]           -- XXX Jython will be different
[?]           -- col_offset is the byte offset in the utf8 string the parser uses
[?]           attributes (int lineno, int col_offset)

[?]           -- BoolOp() can use left & right?
[?]     expr = BoolOp(boolop op, expr* values)
[?]          | BinOp(expr left, operator op, expr right)
[?]          | UnaryOp(unaryop op, expr operand)
[?]          | Lambda(arguments args, expr body)
[?]          | IfExp(expr test, expr body, expr orelse)
[?]          | Dict(expr* keys, expr* values)
[?]          | Set(expr* elts)
[?]          | ListComp(expr elt, comprehension* generators)
[?]          | SetComp(expr elt, comprehension* generators)
[?]          | DictComp(expr key, expr value, comprehension* generators)
[?]          | GeneratorExp(expr elt, comprehension* generators)
[?]          -- the grammar constrains where yield expressions can occur
[?]          | Yield(expr? value)
[?]          -- need sequences for compare to distinguish between
[?]          -- x < 4 < 3 and (x < 4) < 3
[?]          | Compare(expr left, cmpop* ops, expr* comparators)
[?]          | Call(expr func, expr* args, keyword* keywords,
[?]              expr? starargs, expr? kwargs)
[?]          | Repr(expr value)
[?]          | Num(object n) -- a number as a PyObject.
[?]          | Str(string s) -- need to specify raw, unicode, etc?
[?]          -- other literals? bools?

             -- the following expression can appear in assignment context
[x]          | Attribute(expr value, identifier attr, expr_context ctx)
[x]          | Subscript(expr value, slice slice, expr_context ctx)
[x]          | Name(identifier id, expr_context ctx)
[x]          | List(expr* elts, expr_context ctx) 
[x]          | Tuple(expr* elts, expr_context ctx)

[?]           -- col_offset is the byte offset in the utf8 string the parser uses
[?]           attributes (int lineno, int col_offset)

[?]     expr_context = Load | Store | Del | AugLoad | AugStore | Param

[?]     slice = Ellipsis | Slice(expr? lower, expr? upper, expr? step) 
[?]           | ExtSlice(slice* dims) 
[?]           | Index(expr value) 

[?]     boolop = And | Or 

[?]     operator = Add | Sub | Mult | Div | Mod | Pow | LShift 
[?]              | RShift | BitOr | BitXor | BitAnd | FloorDiv

[?]     unaryop = Invert | Not | UAdd | USub

[?]     cmpop = Eq | NotEq | Lt | LtE | Gt | GtE | Is | IsNot | In | NotIn

[?]     comprehension = (expr target, expr iter, expr* ifs)

[?]     -- not sure what to call the first argument for raise and except
[?]     excepthandler = ExceptHandler(expr? type, expr? name, stmt* body)
[?]                     attributes (int lineno, int col_offset)

[?]     arguments = (expr* args, identifier? vararg, 
[?]                  identifier? kwarg, expr* defaults)

[?]     -- keyword arguments supplied to call
[?]     keyword = (identifier arg, expr value)

[?]     -- import name with optional 'as' alias.
[?]     alias = (identifier name, identifier? asname)
    }
