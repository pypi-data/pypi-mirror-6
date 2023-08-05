import glob
import itertools

from .actions import Actions
from .document import Document


class FileInputDocument(Document):
    def __init__(self, session, path, action='open'):
        Document.__init__(self, actions=FileInputActions(session, path))
        self.action = action
        self.name = '[{}]'.format(action)
        self.view.set_screen(session.scr)
        self.actions.tab(self)
        #self.change(0, 0, 0, 0, [filename])
        #self.view.move(len(filename), 0)
        

class FileInputActions:
    def __init__(self, session, path):
        self.session = session
        self.set_path(session.docs[-1], path)
        
    def set_path(self, doc, path):
        self.path = path
        doc.view.message = path

    def insert_character(self, doc, c):
        self.set_path(doc, self.path + c)
        
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
        self.set_path(doc, self.path[:-1])
        
    def tab(self, doc):
        filename = self.path

        names = []
        for name in glob.iglob(filename + '*'):
            if name.endswith('.pyc'):
               continue
            names.append(name)
            if len(names) == 1001:
                break

        doc.change(0, 0, 0, len(doc.lines), ['.', '..'] + names + [''])
        
        if not names:
            return
            
        i = len(filename)
        while True:
            name0 = names[0][:i + 1]
            if len(name0) == i:
                return
            for name in names[1:]:
                if not name.startswith(name0):
                    return
            self.set_path(doc, filename + name0[i])
            filename = self.path
            i += 1
