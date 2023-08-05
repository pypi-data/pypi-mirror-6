""" Read-Only Tkinter Text Widget.  This is a variation of the Tkinter Text
widget in that the text itself is not editable (it is read-only), but it allows
selection for cut/paste to other apps.  Cut-paste may currently only work
under X11.

A vastly simpler way of doing this is to use a Tkinter.Text widget and set
it to DISABLED, but then you cannot select text.
$Id$
"""
from __future__ import division # confidence high

# System level modules
import Tkinter

ALLOWED_SYMS = ('Up','Down','Left','Right','Home','End','Prior','Next', \
                'Shift_L', 'Shift_R')

class ROText(Tkinter.Text):

    def __init__(self, master, **kw):
        """  defer most of __init__ to the base class """
        self._fbto = None
        if 'focusBackTo' in kw:
            self._fbto = kw['focusBackTo']
            del kw['focusBackTo']
        Tkinter.Text.__init__(self, master, **kw)
        # override some bindings to return a "break" string
        self.bind("<Key>", self.ignoreMostKeys)
        self.bind("<Button-2>", lambda e: "break")
        self.bind("<Button-3>", lambda e: "break")
        if self._fbto:
            self.bind("<Leave>", self.mouseLeft)
        self.config(insertwidth=0)

    # disallow common insert calls, but allow a backdoor when needed
    def insert(self, index, text, *tags, **kw):
        if 'force' in kw and kw['force']:
            Tkinter.Text.insert(self, index, text, *tags)

    # disallow common delete calls, but allow a backdoor when needed
    def delete(self, start, end=None, force=False):
        if force:
            Tkinter.Text.delete(self, start, end)

    # a way to disable text manip
    def ignoreMostKeys(self, event):
        if event.keysym not in ALLOWED_SYMS:
            return "break" # have to return this string to stop the event

    def mouseLeft(self, event):
        if self._fbto:
            self._fbto.focus_set()
        return "break" # have to return this string to stop the event


# Test the above class
if __name__ == '__main__':

    import sys, time

    rot = None

    def quit():
        sys.exit()

    def clicked():
        rot.insert(Tkinter.END, "\nClicked at "+time.asctime(), force=True)
        rot.see(Tkinter.END)

    # make our test window
    top = Tkinter.Tk()
    f = Tkinter.Frame(top)

    sc = Tkinter.Scrollbar(f)
    sc.pack(side=Tkinter.RIGHT, fill=Tkinter.Y)
    rot = ROText(f, wrap=Tkinter.WORD, height=10, yscrollcommand=sc.set,
                 focusBackTo=top)
    rot.pack(side=Tkinter.TOP, fill=Tkinter.X, expand=True)
    sc.config(command=rot.yview)
    f.pack(side=Tkinter.TOP, fill=Tkinter.X)

    b = Tkinter.Button(top, text='Click Me', command=clicked)
    b.pack(side=Tkinter.TOP, fill=Tkinter.X, expand=1)

    q = Tkinter.Button(top, text='Quit', command=quit)
    q.pack(side=Tkinter.TOP)

    # start
    top.mainloop()
