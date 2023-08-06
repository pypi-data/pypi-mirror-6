import os
from glob import glob
from collections import namedtuple

incToken      = "include"
new_line      = '\n';
block_start   = '{';
block_end     = '}';
comment_start = '#';
comment_end   = new_line;
string_v1     = '\'';
string_v2     = '"';

class Node:
  def __init__(self, uri = "", node_row = 0, node_col = 0, key = "", values = []):
    self.uri     = uri
    self.row     = node_row
    self.col     = node_col
    self.key     = key
    self.values  = values
    self.comment = ""
    self.childs  = []

  def __repr__(self):
    return 'Node({0}, {1})'.format(self.key, self.values)

class Parser:
  _Code  = namedtuple('Code', '''
    NoError,
    ErrorOpenFile,
    ErrorEmptyData,
    ErrorUnfinishedLiteral,
    ErrorNoOpenBlock,
    ErrorUnfinishedBlock,
    ErrorIncludeSyntax''')

  _State = namedtuple('State', '''
    Default,
    Comment,
    String1,
    String2''')

  Code  = _Code(0, 1, 2, 3, 4, 5, 6)
  State = _State(0, 1, 2, 3)

  def __init__(self):
    self._root = Node()
    self._code = Parser.Code.NoError
    self._uri  = ""
    self._row  = 0
    self._col  = 0
    self.save_comments = True

  @property
  def root(self):
    return self._root

  @property
  def uri(self):
    return self._uri

  @property
  def row(self):
    return self._row

  @property
  def col(self):
    return self._col

  def parse(self, uri):
    _code = Parser.Code.NoError
    return self.__parse(uri, self._root)

  def __error(self, uri, row, col, code):
    self._uri  = uri
    self._row  = row
    self._col  = col
    self._code = code

  def __files(self, parent, mask):
    files = glob(os.path.join(os.path.dirname(parent), mask))
    files.sort()
    return files

  def __parse(self, uri, parent):
    files = self.__files
    error = self.__error
    cur  = ''
    pre  = ''
    row  = 0
    col  = -1
    node_row = 0
    node_col = 0
    parents  = {}
    data     = ""
    comment  = ""
    state    = Parser.State.Default
    node     = parent
    values   = []
    try:
      file   = open(uri, 'rt')
    except IOError:
      error(uri, row, col, Parser.Code.ErrorOpenFile);
      return self._code;
    left     = os.stat(uri).st_size
    def nodes_add():
      nonlocal node, values, node_row, node_col, comment
      tmp = Node(uri, node_row, node_col, values[0], values[1:])
      parents[tmp] = node

      if self.save_comments:
        tmp.comment = comment.strip()

      node.childs.append(tmp)

      comment = ""
      values  = []
      return node.childs[-1]


    while left and self._code == Parser.Code.NoError:
      buffer = file.read(4096)
      for tmp in buffer:
        pre, cur = cur, tmp
        col  += 1
        left -= len(cur.encode('utf-8'))
        end   = (left == 0)
        if pre == '\n':
          row += 1
          col  = 0

        if self._code != Parser.Code.NoError:
          break

        if state == Parser.State.Comment:
          if cur == comment_end:
            state = Parser.State.Default
          elif self.save_comments:
            comment += cur;
          continue;
        elif state == Parser.State.String1:
          if cur != string_v1:
            data += cur
          else:
            if pre == '\\':
              data = data[:-1] + cur
            else:
              state = Parser.State.Default
              if end:
                nodes_add()
          continue
        elif state == Parser.State.String2:
          if cur != string_v2:
            data += cur
          else:
            if pre == '\\':
              data = data[:-1] + cur
            else:
              state = Parser.State.Default
              if end:
                nodes_add()
          continue
        if cur == comment_start:
          state = Parser.State.Comment;
          continue;
        elif cur == string_v1:
          if len(data):
            values.append(data)
          data  = ""
          state = Parser.State.String1;
          continue;
        elif cur == string_v2:
          if len(data):
            values.append(data)
          data  = ""
          state = Parser.State.String2;
          continue;
        elif cur in (' ','\r', '\t', '\v'):
          cur = ' ';
          continue;
        elif cur == block_start:
          if len(data):
            values.append(data)
          data  = ""
          if not len(values):
            error(uri, node_row, node_col, Parser.Code.ErrorEmptyData);
            continue;
          if values[0] == incToken:
            error(uri, node_row, node_col, Parser.Code.ErrorIncludeSyntax);
            continue;
          node = nodes_add()
          continue;
        elif cur == block_end:
          if node == self._root:
            error(uri, row, col, Parser.Code.ErrorNoOpenBlock);
            continue;
          node = parents[node];
          continue;
        elif cur == new_line:
          if pre == '\\' and len(data):
            cur  = ' '
            data = data[:-1]
            continue;
          if len(data):
            values.append(data)
          data  = ""
          if len(values):
            if values[0] == incToken:
              if len(values) != 2:
                error(uri, node_row, node_col, Parser.Code.ErrorIncludeSyntax);
                continue
              for f in files(uri, values[1]):
                if not self.__parse(f, node):
                    break;
              print(node)
              data   = ""
              values = []
            else:
              nodes_add()
          continue
        else:
          if pre == ' ' and len(data):
            values.append(data)
            data  = ""
          if not len(values) and not len(data):
            node_row = row;
            node_col = col;
          data += cur;

    if self._code == Parser.Code.NoError:
      if state != Parser.State.Default:
        error(uri, node.row, node.col, Parser.Code.ErrorUnfinishedLiteral);
      elif node != parent:
        error(uri, node.row, node.col, Parser.Code.ErrorUnfinishedBlock);
    return self._code;

