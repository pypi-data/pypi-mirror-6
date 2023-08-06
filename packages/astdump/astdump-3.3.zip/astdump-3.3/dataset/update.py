#!/usr/bin/env python
# 
# This code is placed into public domain
# by anatoly techtonik <techtonik@gmail.com>
# and uses snippets from `locally` library,
# which is public domain also.

import os

# dataset root (this dir)
ROOT = os.path.abspath(os.path.dirname(__file__))

import ast
import sys

# make sure astdump.py from parent dir is preferred
sys.path.insert(0, os.path.dirname(ROOT))

import astdump

PY3K = sys.version_info >= (3, 0)

# --/end of setup


# --- main ---
# [x] iterate over files in dataset dir
#  [x] split each file contents by section
#  [x] if len(sections) < 3, expand
#   [x] make sure sections are delimited by at least
#       two blank lines
#  [x] update sections 2 (ast.dump) and 3 (astdump)
#  [x] write file back

# section starts with ---[, at least 3 sections:
#
#  1. comments and Python snippet to be dumped
#  2. output of ast.dump() from stdlib
#  3. current output of astdump.py


def secsplit(text, delimiter='---['):
  '''
  Return list of sections. Every middle section ends
  with at least two blank lines
  '''
  ss = [] # list of sections
  s = []  # temp list for section lines

  for line in text.splitlines():
    if line.startswith(delimiter): # new section
      # close previous section
      ss.append('\n'.join(s))
      s = []
    s.append(line)

  ss.append('\n'.join(s))
  return ss


if __name__ == '__main__':  # allow to use as a lib
  # two modes of operation
  if sys.argv[1:]:
    # if an argument is supplied, run ast.dump over it
    # [x] if arg is file - dump file
    # [ ] if arg is string - dump source
    # [ ] if arg is node_ file, ... ?
    print(ast.dump(ast.parse(open(sys.argv[1]).read())))

  else:
    for name in sorted(os.listdir(ROOT)):
      if name.startswith('node_') and name.endswith('.txt'):
        print('..processing %s' % name)
        text = ''
        with open(name, 'rb') as f:
          text = f.read()
          if PY3K:
            text = text.decode('utf-8')
        sections = secsplit(text)
        if len(sections) < 3:
          sections.extend(['\n']*(3-len(sections)))
        content = []
        for idx, section in enumerate(sections):
          if idx == 0:
            # check that first section contains at
            # least two blank lines at the end
            while not section.endswith('\n\n'):
              section += '\n'
          if idx == 1:
            # regenerate section from scratch
            section  = '---[ast.dump]--------------------\n\n'
            section += ast.dump(ast.parse(sections[0]))
            section += '\n\n'
          if idx == 2:
            # regenerate section from scratch
            section  = '---[astdump]---------------------\n\n'
            section += astdump.indented(sections[0], printres=False)
            section += '\n'
          content.append(section)

        with open(name, 'wb') as fw:
          for s in content:
            s += '\n'
            if PY3K:
              s = s.encode('utf-8')
            fw.write(s)
