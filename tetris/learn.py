from Tkinter import *

root = Tk()

def up(event):
    print "up", repr(event.char)

def down(event):
    print "down", repr(event.char)

def left(event):
    print "left", repr(event.char)

def right(event):
    print "right", repr(event.char)

def callback(event):
    frame.focus_set()
    print "clicked at", event.x, event.y

frame = Frame(root, width=100, height=100)
frame.bind("<Up>", up)
frame.bind("<Down>", down)
frame.bind("<Right>", right)
frame.bind("<Left>", left)
frame.bind("<Button-1>", callback)
frame.pack()

root.mainloop()