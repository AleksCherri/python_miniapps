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
        auto.click(button = 'left')
        #auto.click(button = 'right')
    if key.is_pressed(off) and status!=0:
        status=0
        print('Выключено')
        sleep(1)
    if key.is_pressed(on) and status!=1:
        
        status=1
        print('Включено')
        sleep(1)
