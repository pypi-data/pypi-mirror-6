import sys
import pkgutil
import inspect
import importlib

from logging import debug

module_members = {}
modules = {}


def complete(word, words):
    if not words:
        return word
    if len(words) == 1:
        return words[0]
    n = len(word)
    if len(words[0]) == n:
        return word
    x = words[0][n]
    for w in words[1:]:
        if len(w) == n or w[n] != x:
            break
    else:
        return complete(word + x, words)
    return word

    
def complete_import_statement(doc):
    r, c = doc.view.pos
    line = doc.lines[r]
    words = line[:c].split()
    if len(words) < 2:
        return
    if len(words) >= 4 and words[0] == 'from' and words[2] == 'import':
        module_name = words[1]
        if module_name in module_members:
            allnames = module_members[module_name]
        else:
            try:
                module = importlib.import_module(module_name)
            except SyntaxError:
                return 'syntax error'
            allnames = [name for name, obj in inspect.getmembers(module)]
            module_members[module_name] = allnames
        name1 = words[-1]
        names = [name for name in allnames if name.startswith(name1)]
        debug((name1, names))
        name2 = complete(name1, names)
        if name2 != name1:
            doc.change(c, r, c, r, [name2[len(name1):]])
        return True
            
    if (words[0] == 'import' and len(words) > 1 or
        words[0] == 'from' and len(words) == 2):
        module_name = words[-1]
        if not modules:
            for name in sys.builtin_module_names:
                modules[name] = None
            for _, name, _ in pkgutil.iter_modules():
                modules[name] = None
        names = module_name.split('.')
        M1 = modules
        debug(names)
        for name in names[:-1]:
            if name not in M1:
                return False
            M2 = M1[name]
            if M2 is None:
                module = importlib.import_module(name)
                M2 = {m[1]: None 
                      for m in pkgutil.iter_modules(module.__path__)}
                debug((module, name, M2))
                M1[name] = M2
            M1 = M2
        name1 = names[-1]
        names = [name for name in M1 if name.startswith(name1)]
        debug((name1, names))
        name2 = complete(name1, names)
        if name2 != name1:
            doc.change(c, r, c, r, [name2[len(name1):]])
        return True
