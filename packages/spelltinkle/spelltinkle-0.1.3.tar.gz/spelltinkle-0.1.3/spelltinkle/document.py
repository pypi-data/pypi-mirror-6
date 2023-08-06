import os
import time
from logging import debug

from .view import View
from .history import History
from .color import Color


def untabify(line):
    if '\t' not in line:
        return line
    N = len(line)
    n = 0
    while n < N:
        if line[n] == '\t':
            m = 8 - n % 8
            line = line[:n] + ' ' * m + line[n + 1:]
            n += m
            N += m - 1
        else:
            n += 1
    return line
    

class Document:
    def __init__(self, view=None, actions=None):
        self.lines = ['']
        self.modified = False
        self.changes = None
        self.view = view or View(self)
        self.views = [self.view]
        self.actions = actions
        self.history = History()
        self.filename = None
        self.name = '[no name]'
        self.mode = 'Unknown'
        self.timestamp = 1e99
        self.color = Color(self)
        
    def set_filename(self, name):
        self.filename = name
        self.name = os.path.basename(name)
        
    def change(self, c1, r1, c2, r2, lines, remember=True):
        self.color.stop()
        c3 = c1
        r3 = r1
        if c1 != c2 or r1 != r2:
            oldlines = self.delete_range(c1, r1, c2, r2)
        else:
            oldlines = ['']
        if lines != ['']:
            self.insert_lines(c1, r1, lines)
            r3 = r1 + len(lines) - 1
            if r3 == r1:
                c3 = c1 + len(lines[0])
            else:
                c3 = len(lines[-1])

        self.modified = True
        if remember:
            change = (c1, r1, c2, r2, c3, r3, lines, oldlines)
            self.history.append(change)
        self.color.update(c1, r1, c2, r2, lines)
        self.changes = (r1, r2, r3)
        self.view.move(r3, c3)
        return oldlines
        
    def insert_lines(self, c, r, lines):
        start = self.lines[r][:c]
        end = self.lines[r][c:]
        self.lines[r] = start + lines[0]
        self.lines[r + 1:r + 1] = lines[1:]
        self.lines[r + len(lines) - 1] += end

    def delete_range(self, c1, r1, c2, r2):
        start1 = self.lines[r1][:c1]
        end1 = self.lines[r1][c1:]
        start2 = self.lines[r2][:c2]
        end2 = self.lines[r2][c2:]
        if r1 == r2:
            oldlines = [start2[c1:]]
            self.lines[r1] = start1 + end2
        else:
            oldlines = [end1]
            oldlines.extend(self.lines[r1 + 1:r2])
            oldlines.append(start2)
            self.lines[r1] = start1
            del self.lines[r1 + 1:r2 + 1]
            self.lines[r1] += end2
        return oldlines

    def write(self):
        #try:
        #    t = os.stat(self.filename).st_mtime
        #except FileNotFoundError:
        #    pass
        #else:
        #    if t > self.timestamp:
        #        self.set_filename(self.filename + '.new')
                
        with open(self.filename, 'w') as f:
            for line in self.lines[:-1]:
                print(line, file=f)
            if self.lines[-1]:
                print(self.lines[-1], file=f, end='')
        self.modified = False
        self.timestamp = time.time()
        self.changes = 42

    def read(self, filename):
        self.set_filename(filename)
        try:
            with open(filename, encoding='UTF-8') as f:
                lines = []
                line = '\n'
                for n, line in enumerate(f):
                    line = untabify(line)
                    for c in line[:-1]:
                        assert ord(c) > 31, (line, n)
                    lines.append(line[:-1])
                if line[-1] == '\n':
                    lines.append('')
                else:
                    lines[-1] = line
            self.change(0, 0, 0, 0, lines, remember=False)
            self.modified = False
            self.timestamp = time.time()
        except FileNotFoundError:
            pass
