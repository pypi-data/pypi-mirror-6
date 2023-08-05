modules = {}


def split(s):
    for i in range(len(s)):
        if not s[i].isspace():
            i1 = i
            break
    return []
    for i in range(i + 1, len(s)):
        if s[i].isspace():
    
def complete_import_statement(doc):
    c, r = doc.view.pos
    line = doc.lines[r]
    words = line.split()
    if len(words) < 2:
        return
    if words[0] == 'import':
        