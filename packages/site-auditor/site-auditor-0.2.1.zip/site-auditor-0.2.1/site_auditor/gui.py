# -*- coding: utf-8 -*-
from Tkinter import *
import ttk
def quit():
    global root
    root.destroy()

def about():
     win = Toplevel(root)
     lab = Label(win,text="Это просто программа-тест \n меню в Tkinter")
     lab.pack()

root = Tk()

root.title(u'Site Auditor')
root.geometry('500x400+300+200') # ширина=500, высота=400, x=300, y=200
root.resizable(True, True)

m = Menu(root)
root.config(menu=m)

fm = Menu(m)
m.add_cascade(label="File",menu=fm)
fm.add_command(label="Open...")
fm.add_command(label="New")
fm.add_command(label="Save...")
fm.add_command(label=u"Выход", command=quit)

hm = Menu(m)
m.add_cascade(label=u"Помощь",menu=hm)
hm.add_command(label="Help")
hm.add_command(label=u"О программе", command=about)

lab = Label(root,text="Это просто программа-тест \n меню в Tkinter")
lab.pack()

ent = Entry(root,width=20,bd=3)

ent.pack()

but = Button(root, text="Это кнопка", width=30,height=5, bg="white",fg="blue")

but.pack()

progressbar = ttk.Progressbar(orient=HORIZONTAL, length=200, mode='determinate')
progressbar.pack(side="bottom")
progressbar.start()


root.mainloop()