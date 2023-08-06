import re                                                        
from logging import debug



class Search:
    def __init__(self, session, doc, direction=1):
        self.session = session
        self.direction = direction
        
        self.string = None
        self.match = None
        self.positions = None
        
        self.reset(doc)
        
    def reset(self, doc):
        self.string = ''
        self.match = ''
        self.update_info_line(doc.view)
        self.positions = [doc.view.pos + ('',)]

    def search_forward(self, doc, direction=1):
        if self.direction != direction:
            self.direction *= -1
            self.reset(doc)
        if self.string == '':
            for c in self.session.lastsearchstring:
                self.insert_character(doc, c)
            return
        self.find(doc, True)

    def search_backward(self, doc):
        self.search_forward(doc, direction=-1)

    def insert_character(self, doc, c):
        self.string += c
        self.find(doc)

    def bs(self, doc):
        if len(self.string) > len(self.match):
            self.string = self.string[:-1]
            r, c = doc.view.pos
        elif len(self.positions) == 1:
            return
        else:
            self.positions.pop()
            r, c, self.string = self.positions[-1]
            self.match = self.string
        self.update_info_line(doc.view)
        doc.view.move(r, c)

    def unknown(self, doc, name):
        doc.view.message = None
        doc.view.update_info_line()
        self.session.lastsearchstring = self.string
        from .actions import Actions
        doc.actions = Actions(self.session)
        doc.view.update(self.session)
        getattr(doc.actions, name)(doc)
            
    def find(self, doc, next=False):
        if self.string.islower():
            flags = re.IGNORECASE
        else:
            flags = 0
        d = self.direction
        reo = re.compile(re.escape(self.string[::d]), flags)
        r, c = doc.view.pos

        if d == 1:
            if next:
                c += len(self.match)

            for dr, line in enumerate(doc.lines[r:]):
                if dr == 0:
                    m = reo.search(line, c)
                else:
                    m = reo.search(line)
                if m:
                    c = m.start()
                    r += dr
                    self.match = self.string
                    self.update_info_line(doc.view)
                    self.positions.append((r, c, self.string))
                    doc.view.move(r, c)
                    return
        else:
            if next:
                c -= len(self.match)

            for dr, line in enumerate(doc.lines[r::-1]):
                N = len(line)
                if dr == 0:
                    m = reo.search(line[::-1], N - c)
                else:
                    m = reo.search(line[::-1])
                if m:
                    c = N - m.start() + 1
                    r -= dr
                    self.match = self.string
                    self.update_info_line(doc.view)
                    self.positions.append((r, c, self.string))
                    doc.view.move(r, c)
                    return
                    
        self.update_info_line(doc.view)
        doc.view.update(self.session)
                
    def update_info_line(self, view):
        view.message = 'Search: {}({})'.format(self.match,
                                               self.string[len(self.match):])
        view.update_info_line()
