import os
import signal

from .exceptions import StopSession
from .search import Search
from .keys import aliases, typos
from .help import HelpDocument
from .fromimp import complete_import_statement

from logging import debug


class Actions:
    def __init__(self, session):
        self.session = session

    def insert_character(self, doc, char):
        r, c = doc.view.pos
        for key in typos:
            if self.session.chars.endswith(key):
                doc.change(c - len(key) + 1, r, c, r, [typos[key]])
                self.session.chars = ''
                return
                
        doc.change(c, r, c, r, [char])

    def up(self, doc):
        doc.view.move(max(0, doc.view.r - 1), None)

    def down(self, doc):
        doc.view.move(doc.view.r + 1, None)

    def scroll_up(self, doc):
        y1 = doc.view.y1
        if y1 == 0:
            return
        r = doc.view.r
        if doc.view.y == y1 + doc.view.text.h - 1:
            r -= 1
            if r < 0:
                return
        doc.view.y1 -= 1
        doc.view.move(r, None)
        
    def scroll_down(self, doc):
        y1 = doc.view.y1
        if y1 == len(doc.view.lines) - 1:
            return
        r = doc.view.r
        if doc.view.y == y1:
            r += 1
        doc.view.y1 += 1
        doc.view.move(r, None)
        
    def left(self, doc):
        doc.view.move(*doc.view.prev())

    def right(self, doc):
        doc.view.move(*doc.view.next())

    def ctrl_up(self, doc, dir='up'):
        if doc.view.mark:
            mark = doc.view.mark
            pos = doc.view.pos
            if (mark > pos) ^ (dir in ['down', 'right']):
                getattr(self, dir)(doc)
            else:
                self.mark(doc)
                doc.view.move(*mark)
        else:
            self.mark(doc)
            getattr(self, dir)(doc)
        
    def ctrl_down(self, doc):
        self.ctrl_up(doc, 'down')
        
    def ctrl_left(self, doc):
        self.ctrl_up(doc, 'left')
        
    def ctrl_right(self, doc):
        self.ctrl_up(doc, 'right')
        
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
        doc.view.move(None, 0)

    def homehome(self, doc):
        doc.view.move(0, 0)

    def end(self, doc):
        doc.view.move(None, len(doc.lines[doc.view.r]))
    
    def endend(self, doc):
        doc.view.move(len(doc.lines) - 1, len(doc.lines[-1]))

    def page_up(self, doc):
        doc.view.move(max(0, doc.view.r - doc.view.text.h), None)
        
    def page_down(self, doc):
        doc.view.move(doc.view.r + doc.view.text.h, None)
        
    def bs(self, doc):
        r2, c2 = doc.view.pos
        if doc.lines[r2][:c2].isspace():
            c1 = (c2 - 1) // 4 * 4
            r1 = r2
        else:
            r1, c1 = doc.view.prev()
        doc.change(c1, r1, c2, r2, [''])
        
    def upper(self, doc, f=str.upper):
        if doc.view.mark:
            r1, c1, r2, c2 = doc.view.marked_regionange()
            doc.view.mark = None
        else:
            r1, c1 = doc.view.pos
            r2, c2 = doc.view.next()
        lines = doc.change(c1, r1, c2, r2, [''])
        doc.change(c1, r1, c1, r1, [f(line) for line in lines])
                
    def lower(self, doc):
        self.upper(doc, str.lower)

    def delete(self, doc):
        if doc.view.mark:
            r1, c1, r2, c2 = doc.view.marked_region()
            lines = doc.change(c1, r1, c2, r2, [''])
            self.session.memory = lines
            doc.view.mark = None
        else:
            r1, c1 = doc.view.pos
            r2, c2 = doc.view.next()
            doc.change(c1, r1, c2, r2, [''])

    def rectangle_delete(self, doc):
        r1, c1, r2, c2 = doc.view.marked_region()
        if c1 == c2:
            return
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
        r1, c1, r2, c2 = doc.view.marked_region()
        doc.color.stop()
        lines = doc.delete_range(c1, r1, c2, r2)
        doc.insert_lines(c1, r1, lines)
        self.session.memory = lines

    def indent(self, doc, direction=1):
        if doc.view.mark:
            r1, c1, r2, c2 = doc.view.marked_region()
            if c2 > 0:
                r2 += 1
        else:
            r1 = doc.view.r
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
            r, c = doc.view.mark
            doc.view.mark = r, min(c, len(doc.lines[r]))
            doc.view.move(*doc.view.pos)
            
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
            if dir:
                dir += '/'
        else:
            dir = ''
        self.session.docs.append(FileInputDocument(self.session, dir))
        self.session.docs[-1].view.update(self.session)

    def help(self, doc):
        doc = HelpDocument(actions=Actions(self.session))
        doc.view.set_screen(self.session.scr)
        doc.view.update(self.session)
        self.session.docs.append(doc)

    def paste(self, doc):
        r, c = doc.view.pos
        doc.change(c, r, c, r, self.session.memory)
        doc.view.mark = None

    def esc(self, doc):
        doc.view.mark = None
        doc.changes = 42
        
    def delete_to_end_of_line(self, doc, append=False):
        r, c = doc.view.pos
        if (r, c) == doc.view.next():
            return
        line = doc.lines[r]
        if c == 0 and line.strip() == '' and r < len(doc.lines) - 1:
            lines = doc.change(0, r, 0, r + 1, [''])
        elif c == len(line):
            lines = doc.change(c, r, 0, r + 1, [''])
        else:
            lines = doc.change(c, r, len(line), r, [''])
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
        doc.view.mark = doc.view.pos

    def enter(self, doc):
        r, c = doc.view.pos
        doc.change(c, r, c, r, ['', ''])
        doc.view.pos = (r + 1, 0)
        self.tab(doc)
        
    def tab(self, doc):
        r, c = doc.view.pos
        for key in aliases:
            if self.session.chars.endswith(key):
                doc.change(c - len(key), r, c, r, [aliases[key]])
                self.session.chars = ''
                return
                
        if complete_import_statement(doc):
            return
                
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
        doc.view.move(r, c)

    def quit(self, doc):
        for doc in self.session.docs:
            if doc.modified and doc.filename is not None:
                doc.write()
        raise StopSession

    def stop(self, doc):
        self.session.scr.stop()
        os.kill(os.getpid(), signal.SIGSTOP)
        import time
        time.sleep(2)
        self.session.scr.start()
        