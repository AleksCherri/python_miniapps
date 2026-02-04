from tkinter import *
import random
lvl=0
root=Tk()
root.title('Clicker V1')
a='#fe8144'
root['bg']=a
import time
cost=10
mo=1
col='black'
bak='white'
def addlvl():
    global mo, click, lvl, cost, b, lvlc, textl
    if click>cost:
        lvl+=1
        mo+=1
        click-=cost
        cost=cost*2
    lvlc=Button(text=(lvl,'+'), font=('Arial', 10), bg='grey', fg='black', command=addlvl)
    lvlc.place_forget()
    lvlc.place(x=30,y=170)
    b=Button(text=click, font=('Arial', 20), bg=bak, fg=col, command=cl)
    b.place_forget()
    b.place(x=75,y=75)
    textl=Label(text=('стоимость:', cost), fg='black', bg='grey')
    textl.place_forget()
    textl.place(x=75,y=175)
def cl(): 
    global click, bak, col, mo, a, b, lvlc
    root['bg']=('#fe8144')
    click+=mo
    print(click)
    b=Button(text=click, font=('Arial', 20), bg=bak, fg=col, command=cl)
    b.place_forget()
    b.place(x=75,y=75)
click=0
b=Button(text=click, font=('Arial', 20), bg=bak, fg=col, command=cl)
b.place(x=75,y=75)
lvlc=Button(text=(lvl,'+'), font=('Arial', 10), bg='grey', fg='black', command=addlvl)
lvlc.place(x=30,y=170)
textl=Label(text=('стоимость:', cost), fg='black', bg='grey')
textl.place(x=75,y=175)

root.mainloop()
