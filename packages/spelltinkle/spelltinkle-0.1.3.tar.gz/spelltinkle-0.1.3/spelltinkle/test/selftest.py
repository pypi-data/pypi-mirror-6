import os
import pstats
import shutil
import cProfile

from ..keys import keynames
from ..run import run
from .tests import all_tests
import spelltinkle.test.tests as tests

from logging import debug


class Input:
    session = None

    def __init__(self, test):
        self.stream = self.characters(test)
        self.queue = []
        
    def get(self):
        if self.queue:
            return self.queue.pop(0)
        c = next(self.stream)
        return c
    
    def put(self, c):
        self.queue.append(c)
        
    def characters(self, test):
        for s in test(self.session):
            while s:
                s0 = s
                if s[:2] == '^^':
                    yield '^'
                    s = s[2:]
                if s[0] == '^':
                    yield s[:2]
                    s = s[2:]
                elif s[:2] == '<<':
                    yield '<'
                    s = s[2:]
                elif s[0] == '<':
                    key, s = s[1:].split('>', 1)
                    yield key.replace('-', '_')
                elif s[0] == '\n':
                    s = s[1:]
                else:
                    yield s[0]
                    s = s[1:]
                debug(s0[:len(s0) - len(s)])
                

def test(names):
    if os.path.isdir('spelltinkle-self-test'):
        shutil.rmtree('spelltinkle-self-test')
    os.mkdir('spelltinkle-self-test')
    os.chdir('spelltinkle-self-test')
    prof = cProfile.Profile()
    prof.enable()
    if not names:
        names = all_tests
    for name in names:
        debug(name)
        t = getattr(tests, name)
        input = Input(t)
        run(getattr(t, 'args', []), input)
    prof.disable()
    prof.dump_stats('test.profile')
