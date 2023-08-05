import os

from .exceptions import StopSession
from .search import Search
from .document import Document
from .keys import aliases, typos
#from .fromimp import complete_import_statement

from logging import debug


class Actions:
    def __init__(self, session):
        self.session = session

    def insert_character(self, doc, char):
        c, r = doc.view.cr()
        for key in typos:
            if self.session.chars.endswith(key):
                doc.change(c - len(key) + 1, r, c, r, [typos[key]])
                self.session.chars = ''
                return
                
        doc.change(c, r, c, r, [char])

    def up(self, doc):
        c, r = doc.view.cr()
        doc.view.move(None, max(0, r - 1))

    def down(self, doc):
        c, r = doc.view.cr()
        doc.view.move(None, r + 1)

    def scroll_up(self, doc):
        y1 = doc.view.y1
        if y1 == 0:
            return
        c, r = doc.view.pos
        if doc.view.y == y1 + doc.view.text.h - 1:
            r -= 1
            if r < 0:
                return
        doc.view.y1 -= 1
        doc.view.move(None, r)
        
    def scroll_down(self, doc):
        y1 = doc.view.y1
        if y1 == len(doc.view.lines) - 1:
            return
        c, r = doc.view.pos
        if doc.view.y == y1:
            r += 1
        doc.view.y1 += 1
        doc.view.move(None, r)
        
    def left(self, doc):
        doc.view.move(*doc.prev(*doc.view.pos))

    def right(self, doc):
        doc.view.move(*doc.next(*doc.view.pos))

    def mouse_clicked(self, doc):
        x, y = self.session.scr.position
        if y == 0:
            for i, c in enumerate(doc.view.tabcolumns):
                if c > x:
                    if i > 1:
                        docs = self.session.docs
                        docs.append(docs.pop(-i))
                        docs[-1].view.set_screen(self.session.scr)
                        docs[-1].changes = 42
                    break
        else:
            doc.view.mouse(x, y)
        
    def mouse_released(self, doc):
        x, y = self.session.scr.position
        if y > 0:
            self.mark(doc)
            doc.view.mouse(x, y)
        
    def home(self, doc):
        doc.view.move(0)

    def homehome(self, doc):
        doc.view.move(0, 0)

    def end(self, doc):
        doc.view.move(len(doc.lines[doc.view.r]))
    
    def endend(self, doc):
        doc.view.move(len(doc.lines[-1]), len(doc.lines) - 1)

    def page_up(self, doc):
        c, r = doc.view.cr()
        doc.view.move(None, max(0, r - doc.view.text.h))
        
    def page_down(self, doc):
        c, r = doc.view.cr()
        doc.view.move(None, r + doc.view.text.h)
        
    def bs(self, doc):
        c2, r2 = doc.view.cr()
        if c2 == 0 and r2 == 0:
            return
        if doc.lines[r2][:c2].isspace():
            c1 = (c2 - 1) // 4 * 4
            r1 = r2
        else:
            c1, r1 = doc.prev(c2, r2)
        doc.change(c1, r1, c2, r2, [''])

    def delete(self, doc):
        c1, r1 = doc.view.cr()
        if doc.view.mark:
            c2, r2 = doc.view.mark
            if (r1, c1) > (r2, c2):
                r1, c1, r2, c2 = r2, c2, r1, c1
            lines = doc.change(c1, r1, c2, r2, [''])
            self.session.memory = lines
            doc.view.mark = None
        else:
            c2, r2 = doc.next(c1, r1)
            if c1 != c2 or r1 != r2:
                doc.change(c1, r1, c2, r2, [''])

    def rectangle_delete(self, doc):
        c1, r1 = doc.view.cr()
        c2, r2 = doc.view.mark
        if c1 == c2:
            return
        if (r1, c1) > (r2, c2):
            r1, c1, r2, c2 = r2, c2, r1, c1
        if c2 < c1:
            c1, c2 = c2, c1
        lines = []
        for r in range(r1, r2 + 1):
            line = doc.lines[r]
            n = len(line)
            if c1 >= n:
                continue
            c3 = min(n, c2)
            line = doc.change(c1, r, c3, r, [''])[0]
            lines.append(line)
            
        self.session.memory = lines
        doc.view.mark = None
        doc.changed = 42
        
    def copy(self, doc):
        if not doc.view.mark:
            return
        c1, r1 = doc.view.cr()
        c2, r2 = doc.view.mark
        if (r1, c1) > (r2, c2):
            r1, c1, r2, c2 = r2, c2, r1, c1
        doc.color.stop()
        lines = doc.delete_range(c1, r1, c2, r2)
        doc.insert_lines(c1, r1, lines)
        self.session.memory = lines

    def indent(self, doc, direction=1):
        c1, r1 = doc.view.cr()
        if doc.view.mark:
            c2, r2 = doc.view.mark
            if (r1, c1) > (r2, c2):
                r1, c1, r2, c2 = r2, c2, r1, c1
            if c2 > 0:
                r2 += 1
        else:
            r2 = r1 + 1
        if direction == 1:
            for r in range(r1, r2):
                doc.change(0, r, 0, r, ['    '])
        else:
            for r in range(r1, r2):
                if doc.lines[r][:4] != '    ':
                    return
            for r in range(r1, r2):
                doc.change(0, r, 4, r, [''])
            doc.view.mark = max(0, c1 - 4), r1
            
    def dedent(self, doc):
        self.indent(doc, -1)
                
    def undo(self, doc):
        doc.history.undo(doc)

    def redo(self, doc):
        doc.history.redo(doc)

    def search_forward(self, doc):
        doc.actions = Search(self.session, doc)

    def search_backward(self, doc):
        doc.actions = Search(self.session, doc, -1)

    def view_files(self, doc):
        from .filelist import FileList
        self.session.docs.append(FileList(self.session))
        self.session.docs[-1].view.update(self.session)

    def write(self, doc):
        doc.write()

    def write_as(self, doc):
        from .fileinput import FileInputDocument
        filename = doc.filename or ''
        self.session.docs.append(FileInputDocument(self.session, filename,
                                                   action='write as'))
        self.session.docs[-1].view.update(self.session)

    def open(self, doc):
        from .fileinput import FileInputDocument
        if doc.filename:
            dir = os.path.split(doc.filename)[0]
        else:
            dir = ''
        self.session.docs.append(FileInputDocument(self.session, dir))
        self.session.docs[-1].view.update(self.session)
        
    def paste(self, doc):
        c, r = doc.view.cr()
        change = doc.change(c, r, c, r, self.session.memory)
        doc.view.mark = None

    def esc(self, doc):
        doc.view.mark = None
        
    def delete_to_end_of_line(self, doc, append=False):
        c, r = doc.view.cr()
        if (c, r) == doc.next(c, r):
            return
        if c == len(doc.lines[r]):
            lines = ['', '']    
            doc.change(c, r, 0, r + 1, [''])
        else:
            lines = [doc.lines[r][c:]]
            doc.change(c, r, len(doc.lines[r]), r, [''])
        if append:
            if self.session.memory[-1] == '':
                self.session.memory[-1:] = lines
            else:
                self.session.memory.append('')
        else:
            self.session.memory = lines

    def delete_to_end_of_line_again(self, doc):
        self.delete_to_end_of_line(doc, True)

    def mark(self, doc):
        doc.view.mark = doc.view.cr()

    def enter(self, doc):
        c, r = doc.view.cr()
        doc.change(c, r, c, r, ['', ''])
        doc.view.pos = (0, r + 1)
        self.tab(doc)
        
    def tab(self, doc):
        c, r = doc.view.cr()
        for key in aliases:
            if self.session.chars.endswith(key):
                doc.change(c - len(key), r, c, r, [aliases[key]])
                self.session.chars = ''
                return
                
        #complete_import_statement(doc)
                
        r0 = r - 1
        p = []
        pend = False
        indent = None
        while r0 >= 0:
            line = doc.lines[r0]
            if line and not line.isspace():
                n = len(line)
                for i in range(n - 1, -1, -1):
                    x = line[i]
                    j = '([{'.find(x)
                    if j != -1:
                        if not p:
                            if i < n - 1:
                                indent = i + 1
                                break
                            pend = True
                        elif p.pop() != ')]}'[j]:
                            indent = 0
                            # message
                            break
                    elif x in ')]}':
                        p.append(x)

                if indent is not None:
                    break
                
                if not p:
                    indent = len(line) - len(line.lstrip())
                    break

            r0 -= 1
        else:
            indent = 0
            line = '?'
                        
        if pend or line.rstrip()[-1] == ':':
            indent += 4

        line = doc.lines[r]
        i = len(line) - len(line.lstrip())
        if i < indent:
            doc.change(0, r, 0, r, [' ' * (indent - i)])
        elif i > indent:
            doc.change(0, r, i - indent, r, [''])
        c += indent - i
        if c < indent:
            c = indent
        doc.view.move(c, r)

    def quit(self, doc):
        for doc in self.session.docs:
            if doc.modified and doc.filename is not None:
                doc.write()
        raise StopSession
