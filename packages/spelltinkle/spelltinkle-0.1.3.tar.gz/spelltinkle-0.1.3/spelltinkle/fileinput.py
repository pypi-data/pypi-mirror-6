import os.path

from .actions import Actions
from .document import Document


class FileInputDocument(Document):
    def __init__(self, session, path, action='open'):
        Document.__init__(self, actions=FileInputActions(session))
        self.action = action
        self.name = '[{}]'.format(action)
        self.view.set_screen(session.scr)
        self.actions.update(self, path)

        
class FileInputActions:
    def __init__(self, session):
        self.session = session
        self.c = None
        self.dir = None
        self.name = None
        self.allfiles =  None
        self.path = None
        
    def insert_character(self, doc, chr):
        c = self.c
        p = self.path[:c] + chr + self.path[c:]
        self.c += 1
        self.update(doc, p)
        
    def enter(self, doc):
        self.session.docs.pop()
        if doc.action == 'open':
            doc = Document(actions=Actions(self.session))
            doc.view.set_screen(self.session.scr)
            doc.read(self.path)
            self.session.docs.append(doc)
        else:
            self.session.docs[-1].set_filename(self.path)
            self.session.docs[-1].write()

    def esc(self, doc):
        self.session.docs.pop()
    
    def bs(self, doc):
        c = self.c
        p = self.path[:c - 1] + self.path[c:]
        self.c -= 1
        self.update(doc, p)
        
    def delete(self, doc):
        c = self.c
        p = self.path[:c] + self.path[c + 1:]
        self.update(doc, p)
        
    def tab(self, doc):
        names = doc.lines[:-1]
        if not names:
            return
            
        i0 = i = len(self.name)
        while True:
            name0 = names[0][:i + 1]
            if len(name0) == i:
                break
            for f in names[1:]:
                if not f.startswith(name0):
                    break
            else:
                i += 1
                continue
            break
             
        self.c += i - i0
        self.name = name0[:i]
        self.path += name0[i0:i]
        doc.view.message = self.path + ' ', self.c
        
    def update(self, doc, path):
        self.path = path
            
        if self.c is None:
            self.c = len(path)
            
        doc.view.message = path + ' ', self.c

        if path == '..':
            dir = '..'
            self.name = ''
        else:
            dir, self.name = os.path.split(path)
        
        if dir != self.dir:
            self.allfiles = os.listdir(dir or '.')[:1000]
            self.dir = dir
        
        names = []
        for f in self.allfiles:
            if f.startswith(self.name):
                names.append(f)

        doc.change(0, 0, 0, len(doc.lines) - 1, names + [''])
        doc.view.move(0, 0)
