import pyautogui as auto
import keyboard as key
from time import sleep 

key1 = 'e'
on = 'home'
off = 'end'
click = 0  
lag = 0
status=0
while True:
    if status==1:
        auto.typewrite('Lox you was banned by my bot')
        auto.press('enter')
        click+=1
        print(click)
        sleep(0)
        
    if key.is_pressed(off) and status!=0:
        status=0
        print('Выключено')
        sleep(1)
    if key.is_pressed(on) and status!=1:
        status=1
        print('Включено')
        sleep(1)
def other():
    print('')
