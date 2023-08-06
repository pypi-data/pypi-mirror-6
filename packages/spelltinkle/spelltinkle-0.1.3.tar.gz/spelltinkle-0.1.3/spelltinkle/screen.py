import os
import signal
import locale
import termios
import threading
import tty
import sys
from time import time

from logging import debug


class Screen:
    def __init__(self, size=None, corner=(0, 0)):
        if size is None:
            locale.setlocale(locale.LC_ALL, '')
            if sys.stdin.mode == 'r':
                sys.stdin = sys.stdin.detach()
            print('\x1b[?1047h\x1b[?1000h', end='')
            fd = sys.stdin.fileno()
            self.old_termios_settings = termios.tcgetattr(fd)
            tty.setraw(fd)
            signal.signal(signal.SIGWINCH, self.resize_handler)
            size = os.get_terminal_size()
        
        self.size = size
        self.w, self.h = size
        self.corner = corner

        self.colors = []
        for bg in ['\x1b[48;5;255m', '\x1b[48;5;253m', '\x1b[48;5;120m',
                   '\x1b[48;5;204m', '\x1b[48;5;228m']:
            for fg in ['\x1b[38;5;16m',
                       '\x1b[38;5;20m',
                       '\x1b[38;5;28m',
                       '\x1b[38;5;52m',
                       '\x1b[38;5;58m',
                       '\x1b[38;5;53m']:
                self.colors.append(fg + bg)
            self.colors.extend([None] * 4)
        self.colors.extend(['\x1b[38;5;94m\x1b[48;5;228m',
                            '\x1b[38;5;94m\x1b[48;5;226m',
                            '\x1b[38;5;255m\x1b[48;5;243m',
                            '\x1b[38;5;28m\x1b[48;5;251m',
                            '\x1b[38;5;52m\x1b[48;5;251m'])

        self.color = None

        self.keys = []
        self.children = []
        self.thread = None
        self.escthread = None
        self.character = None
        self.clicktime = 1e20
    
    def start(self):
        if sys.stdin.mode == 'r':
            sys.stdin = sys.stdin.detach()
        print('\x1b[?1047h\x1b[?1000h', end='')
        fd = sys.stdin.fileno()
        self.old_termios_settings = termios.tcgetattr(fd)
        tty.setraw(fd)

    def resize_handler(self, signalnum, frame):
        self.queue.put('resize')

    def resize(self, size=None):
        if size is None:
            size = os.get_terminal_size()
            self.w, self.h = self.size = size
            for child in self.children:
                child.resize(size)
        else:
            if self.h == 1:
                self.w = size.columns
                self.size = os.terminal_size((self.w, 1))
                if self.corner[1] > 0:
                    self.corner = (0, size.lines - 1)
            else:
                self.w, self.h = self.size = os.terminal_size((size.columns,
                                                               size.lines - 2))
            
    def write(self, text=' ', colors=0):
        if isinstance(colors, int):
            colors = [colors] * len(text)
        c0 = None
        for x, color in zip(text, colors):
            if color != c0:
                print(self.colors[color], end='')
                c0 = color
            print(x, end='')

    def get_keys(self, queue):
        def run():
            while 1:
                c = self.input()
                queue.put(c)
                if c == '^q':
                    break
                
        self.thread = threading.Thread(target=run)
        self.thread.start()
        self.queue = queue
        
    def input(self):
        if self.escthread:
            self.escthread.join()
            self.escthread = None
            c = self.character
        else:
            c = sys.stdin.read(1)
            
        if b'\x00' < c < b'\x1b':
            return '^' + chr(96 + ord(c))
        if c == b'\x7f':
            return 'bs'
        if c != b'\x1b':
            if 0 < ord(c) < 128:
                return c.decode()
            else:
                return self.input()
                
        thread = threading.Thread(target=self.check_escape)
        thread.start()
        thread.join(0.02)
        if thread.is_alive():
            self.escthread = thread
            return 'esc'

        c = self.character
        
        if c == b'O':
            c = sys.stdin.read(1)
            key = {b'H': 'home',
                   b'F': 'end'}.get(c)
            if key is None:
                return self.input()
            return key
        assert c == b'[', c
        key = b''
        while True:
            c = sys.stdin.read(1)
            key += c
            if ord(c) >= 65:
                break
        
        if c == b'M':
            c, x, y = sys.stdin.read(3)
            self.position = (x - 33, y - 33)
            c = chr(c)
            if c == ' ':
                self.clicktime = time()
                return 'mouse_clicked'
            if c == '#' and time() > self.clicktime + 0.3:
                return 'mouse_released'
            if c == '`':
                return ['scroll_up'] * 3
            elif c == 'a':
                return ['scroll_down'] * 3
                
        key = {b'A': 'up',
               b'B': 'down',
               b'C': 'right',
               b'D': 'left',
               b'1;5A': 'ctrl_up',
               b'1;5B': 'ctrl_down',
               b'1;5C': 'ctrl_right',
               b'1;5D': 'ctrl_left',
               b'3~': 'delete',
               b'5~': 'page_up',
               b'6~': 'page_down'}.get(key)
        if key is None:
            return self.input()
        return key

    def check_escape(self):
        self.character = sys.stdin.read(1)
        
    def erase(self):
        return
        for r in range(self.size.lines):
            print('\x1b[{};1H\x1b[2K'.format(r + self.corner[1] + 1))

    def refresh(self):
        sys.stdout.flush()

    def move(self, y, x):
        print('\x1b[{};{}H'.format(y + 1 + self.corner[1], x + 1), end='')
        self.c = x

    def stop(self):
        if self.thread is not None:
            self.thread.join()
        fd = sys.stdin.fileno()
        termios.tcsetattr(fd, termios.TCSADRAIN, self.old_termios_settings)
        print('\x1b[?1047l\x1b[?1000l', end='')

    def subwin(self, h, w, ch, cw):
        scr = Screen(os.terminal_size((w, h)), (cw, ch))
        self.children.append(scr)
        return scr


if __name__ == '__main__':
    print('\x1b[?1047h', end='')
    print('\x1b[?1000h', end='')
    sys.stdin = sys.stdin.detach()
    fd = sys.stdin.fileno()
    old_termios_settings = termios.tcgetattr(fd)
    tty.setraw(fd)
    for i in range(256):
        print('\x1b[48;5;%dm %3d ' % (i, i), end='')
    print('\x1b[38;5;13m', end='', flush=True)
    try:
        while 1:
            c = sys.stdin.read(1)
            print(c, ord(c), end=' ', flush=True)
            if c == b'q':
                break
    finally:
        fd = sys.stdin.fileno()
        termios.tcsetattr(fd, termios.TCSADRAIN, old_termios_settings)
        print('\x1b[?1000l', end='')
        print('\x1b[?1047l', end='', flush=True)
