from .keys import keynames, doubles
from .document import Document


x="""
 ----
|SPEL|
|LTIN|
|KLE |
 ----
pkgutil, sys.modules

open-current-session-in-new-window-and-stop-the-old-one()

irc+email+todo-list

only one file-list at the time

replace
no indent after return
line 1 bg color: pale yellow?
run tests
<ctrl>+<arrow-key>: mark?
replace marked area by abc and add line before with abc = <marked-area>

go to point befor jump
go to next problem marker

Fast and simple editor based on Python and pygments.

Put help for opening files on the filelist page

When selcting area with mouse use scrollbar to scroll up or down

session.py: result=actions.method(doc);isgenerator(result)? (for questions and other input)

Colors: in color array: search, syntax, match ()[]{}''"", errors
at update time: current line, marked region

remove tabs when reading (or replace with 4 tabs that display as spaces?)
* open terminal in current dir
smooth scrolling when jumping?
a home
b block: b:begin, r:rectangle, l:lines
c copy
d delete
e end
f replace,x:regex
g goto 123,()[]{},x:inner
h help,x:search in help
i-(tab) x:insert file or !shell
j- x:join
k kill,x:backwards
l delete line
m- x:makro
n
o open file or !shell
p paste
q quit,x:ask
r reverse find,x:word under cursor
s find
t
u undo,x:redo
v view: 0,1,2,v:open list
w write, x:saveas
x
y mark: wl()[]{},x:inner
z delete wl()[]{},x:inner
spc format

How about ^Z?

^#12 or ^1^2?

Jump to marked point? Put position on stack

format text

reST mode

crash: report to launchpad

Modes: normal, mark(block,line,rectangle), find
close single doc
<c-1><c-2>: repeat 12 times
spell check
move to other tab
scroll:up, down,center,top, bottom
upper/lower case
big movements
swap two chars
look at to vim plugins: svn,snippets,easymove
complete

scripting: abc<enter><up><end>

Modeline: row:1/234 col:1 (python) 0%

When moving: show movement in "popup": [moved 240 lines forward]

Use number columns to show stuff: last changed line(s)

aliases: imoprt=import

check state of file every two seconds when active?

write docs on errors and write debug info

python3 -m spelltinkle

spt --beginner --verbose --read-only --black-and-white

colors:
fg:pygments(normal,comment,keyword,number,string),error,lineno,status
bg:normal,mark(normal,rectangle,lines),search,currenst line,lineno,error,
notice,status,outside-doc

"""


class HelpDocument(Document):
    def __init__(self, actions):
        Document.__init__(self, actions=actions)
        self.name = '[help]'
        lines = []
        for c in sorted(keynames):
            k = keynames[c]
            if not isinstance(k, str):
                k = '+'.join(k)
            lines.append('  {}: {}'.format(c, k))
        for c1 in doubles:
            for c2, k in doubles[c1].items():
                if not isinstance(k, str):
                    k = '+'.join(k)
                lines.append('{}{:2}: {}'.format(c1, c2, k))
        lines += x.split('\n')
        self.change(0, 0, 0, 0, lines)
        self.view.move(0, 0)
