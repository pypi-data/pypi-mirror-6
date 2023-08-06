import time
import keyword
import builtins
import tokenize
import threading
import subprocess
from logging import debug

import pygments.lexers
import pygments.token
import pygments.util

keywords = frozenset(keyword.kwlist + list(builtins.__dict__.keys()))


class NoColor:
    def __init__(self):
        self.colors = [bytearray()]

    def stop(self):
        pass

    def update(self, c1, r1, c2, r2, lines):
        pass

    def run(self):
        pass


class Color(NoColor):
    def __init__(self, doc):
        NoColor.__init__(self)
        self.doc = doc
        self.r = None
        self._stop = None
        self.thread = None
        self.pep8time = time.time() - 1
        self.lexer = None
        self.token2color = {}
        
    def stop(self):
        self._stop = True
        if self.thread:
            self.thread.join()

    def update(self, c1, r1, c2, r2, lines):
        if c1 != c2 or r1 != r2:
            start = self.colors[r1][:c1]
            end = self.colors[r2][c2:]
            if r1 == r2:
                self.colors[r1] = start + end
            else:
                self.colors[r1] = start
                del self.colors[r1 + 1:r2 + 1]
                self.colors[r1].extend(end)
        if lines != ['']:
            start = self.colors[r1][:c1]
            end = self.colors[r1][c1:]
            self.colors[r1] = start + bytearray(len(lines[0]))
            self.colors[r1 + 1:r1 + 1] = [bytearray(len(line))
                                          for line in lines[1:]]
            self.colors[r1 + len(lines) - 1].extend(end)

    def run(self, queue):
        if self.lexer is None:
            try:
                self.lexer = pygments.lexers.get_lexer_for_filename(
                    self.doc.name, stripnl=False)
            except pygments.util.ClassNotFound:
                self.lexer = False
            else:
                name = self.lexer.name
                self.doc.mode = name
                if name == 'reStructuredText':
                    self.tokens = [pygments.token.Operator,
                                   pygments.token.Generic,
                                   pygments.token.Name,
                                   pygments.token.Comment,
                                   pygments.token.Punctuation]
                else:
                    self.tokens = [pygments.token.Keyword,
                                   pygments.token.Number,
                                   pygments.token.String,
                                   pygments.token.Comment]

        if not self.lexer:
            return
        self._stop = False
        self.thread = threading.Thread(target=self.target, args=[queue])
        self.thread.start()

    def target(self, queue):
        try:
            self.paint()
        except (tokenize.TokenError, IndentationError):
            pass
        
        queue.put('draw colors')
        
        if time.time() > self.pep8time + 2:
            self.pep8()
            self.pyflakes()
            self.pep8time = time.time()
            queue.put('draw colors')

    def paint(self):
        text = '\n'.join(self.doc.lines)
        r = 0
        c = 0
        for token, s in pygments.lex(text, self.lexer):
            if self._stop:
                break
            color = self.token2color.get(token)
            if color is None:
                for color, t in enumerate(self.tokens):
                    if token in t:
                        color += 1
                        break
                else:
                    color = 0
                self.token2color[token] = color
                
            lines = s.split('\n')
            for i, line in enumerate(lines):
                n = len(line)
                for m in range(n):
                    self.colors[r][c + m] = color
                if i == len(lines) - 1:
                    break
                r += 1
                c = 0
            c += n

    def pep8(self):
        name = self.doc.filename
        if name is None or not name.endswith('.py'):
            return
            
        p = subprocess.Popen(['pep8', '--ignore=W293', '-'],
                             stdin=subprocess.PIPE,
                             stdout=subprocess.PIPE,
                             universal_newlines=True)
        for line in self.doc.lines:
            print(line, file=p.stdin)
        output = p.communicate()[0]
        if p.returncode == 0:
            return
        
        for line in output.split('\n'):
            try:
                r, c = (int(n) - 1
                        for n in line.split(' ', 1)[0].split(':')[1:3])
                self.colors[r][c] += 30
            except (IndexError, ValueError):
                return

    def pyflakes(self):
        name = self.doc.filename
        if name is None or not name.endswith('.py'):
            return

        p = subprocess.Popen(['pyflakes'],
                             stdin=subprocess.PIPE,
                             stdout=subprocess.PIPE,
                             stderr=subprocess.PIPE,
                             universal_newlines=True)
        for line in self.doc.lines:
            print(line, file=p.stdin)
        output = ''.join(o for o in p.communicate() if o is not None)
        debug(output)
        debug(str(p.returncode))
        if p.returncode == 0:
            return
        
        for line in output.split('\n'):
            if line.startswith('<stdin>'):
                try:
                    r = int(line.split(':', 2)[1]) - 1
                    self.colors[r][0] += 30
                except (IndexError, ValueError):
                    break
