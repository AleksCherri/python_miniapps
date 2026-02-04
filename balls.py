from turtle import *
from random import *
from math import *
from time import sleep, time

#G = 6.67*10**(-11)
G = 1
FPS = 60 # 0 = No limit

#Full screen -> 960x540
WIDTH = 960
HEIGHT = 540

SPAWN_MASS = [10, 1000]
SPAWN_VELOCITY = 1

LIMIT_WIDTH = 5000
LIMIT_HEIGHT = 5000
SPAWN_WIDTH = 2500
SPAWN_HEIGHT = 2500

BALLS_LIMIT = 1000
MASS_LIMIT = 5000
SPAWN_RATIO = 0.5


RADIATION_MASSPERCENT = 0.01
RADIATION_RATE = 0.01
RADIATION_POWER = 2.5

BLOW_PARTICLES = [3, 12]
BLOW_CHANCE = 0.1
BLOW_POWER = 0.5

DRAW_SPAWNAREA = True
DRAW_HUD = True
LIMIT_MASS = True
BLOW = True
LIMIT_RANGE = True

COLORS = ['#FF0000','#00FF00','#0000FF','#FFFF00','#00FFFF','#FF00FF']

title('Balls')
tracer(0)
penup()
hideturtle()

balls = []

spawn_mass = 1000
max_mass = 0
all_mass = 0
Sx = 0
Sy = 0
zoom = 1
focus = 0
tfps = 0

def increase_mass():
    global spawn_mass
    spawn_mass *= 1.1

def decrease_mass():
    global spawn_mass
    spawn_mass /= 1.1

def manual_spawn():
    add_ball([Sx,Sy], spawn_mass, 0, 0, choice(COLORS))

def follow(point):
    global Sx, Sy
    Sx = point[0][0]
    Sy = point[0][1]

def zoomin():
    global zoom
    zoom *= 1.1

def zoomout():
    global zoom
    zoom /= 1.1

def setcoords(x,y):
    global Sx, Sy, focus
    x1 = Sx + x/zoom
    y1 = Sy + y/zoom
    for point in balls:
        if dist(point, [[x1, y1]]) < radius(point):
            focus = point
            return None
        else:
            Sx = x1
            Sy = y1
            focus = 0

def radiating(point):
    r = radius(point)
    randangle = pi*2*random()
    x = cos(randangle)
    y = sin(randangle)
    add_ball([point[0][0] + x*r*1.5, point[0][1] + y*r*1.5], point[1]*RADIATION_MASSPERCENT, x*G**0.5*r**0.5*RADIATION_POWER + point[2], y*G**0.5*r**0.5*RADIATION_POWER + point[3], choice(COLORS))

def blowing(point):
    particles = randint(BLOW_PARTICLES[0], BLOW_PARTICLES[1])
    r = radius(point)
    ci = pi*2/particles
    randangle = pi*2*random()
    for i in range(particles):
        x = cos(ci*i+randangle)
        y = sin(ci*i+randangle)
        add_ball([point[0][0] + x*r, point[0][1] + y*r], point[1]/particles, x*G**0.5*r**0.5*BLOW_POWER*particles + point[2], y*G**0.5*r**0.5*BLOW_POWER*particles + point[3], point[4])

def merge(point1,point2):
    global balls, focus

    mass = point1[1]+point2[1]
    if LIMIT_MASS and mass > MASS_LIMIT and not BLOW:
        balls.remove(point1)
        balls.remove(point2)
        return None

    if point2[1] > point1[1]:
        point = point2
        balls.remove(point1)
    else:
        point = point1
        balls.remove(point2)

    r1 = point1[1]/mass
    r2 = point2[1]/mass

    x = point1[2]*r1 + point2[2]*r2
    y = point1[3]*r1 + point2[3]*r2

    r = hex(int(int(point1[4][1:3],16)*r1 + int(point2[4][1:3],16)*r2))[2:]
    g = hex(int(int(point1[4][3:5],16)*r1 + int(point2[4][3:5],16)*r2))[2:]
    b = hex(int(int(point1[4][5:7],16)*r1 + int(point2[4][5:7],16)*r2))[2:]

    if len(r) == 1:
        r = '0' + r
    if len(g) == 1:
        g = '0' + g
    if len(b) == 1:
        b = '0' + b
    color = '#'+r+g+b

    new_point = [[point[0][0],point[0][1]], mass, x, y, color]
    balls[balls.index(point)] = new_point
    if point == focus:
        focus = new_point

    if LIMIT_MASS and mass > MASS_LIMIT and BLOW and random() < BLOW_CHANCE:
        blowing(new_point)
        balls.remove(new_point)

def cicle():
    global tfps

    while True:
        time1 = time()

        onscreenclick(setcoords, btn = 1)
        onkeypress(zoomin, key = 'Up')
        onkeypress(zoomout, key = 'Down')
        onkeypress(decrease_mass, key = 'Left')
        onkeypress(increase_mass, key = 'Right')
        onkeypress(manual_spawn, key = 'space')
        listen()

        while attraction():
            attraction()

        while move():
            move()

        if random() < SPAWN_RATIO and len(balls) < BALLS_LIMIT:
            gen_ball()

        if focus != 0:
            follow(focus)

        draw()
        if FPS != 0:
            sleep(max(1/FPS - (time() - time1),0))
        tfps = 1/(time()-time1)

def move():
    global balls, max_mass, all_mass
    max_mass = 0
    all_mass = 0
    for i in range(len(balls)):
        if balls[i][4] == '#000000' and random() < RADIATION_RATE and len(balls) < BALLS_LIMIT:
            radiating(balls[i])
            balls[i][1] *= 1 - RADIATION_MASSPERCENT

        if (abs(balls[i][0][0]) > LIMIT_WIDTH or abs(balls[i][0][1]) > LIMIT_HEIGHT) and LIMIT_RANGE:
            balls.remove(balls[i])
            return True

        balls[i][0][0] += balls[i][2]
        balls[i][0][1] += balls[i][3]
        max_mass = max(balls[i][1], max_mass)
        all_mass += balls[i][1]

def radius(p):
    #return (p[1]/pi)**0.5
    return (p[1]/(4/3)/pi)**(1/3)

def angle(p1,p2):
    ang = atan((p2[0][1] - p1[0][1])/abs(p2[0][0] - p1[0][0]))
    return ang

def dist(p1,p2):
    return ((p1[0][0] - p2[0][0])**2 + (p1[0][1] - p2[0][1])**2)**0.5

def attraction():
    balls.sort()
    n = len(balls)
    for i in range(n-1):
        point1 = balls[i]
        for j in range(i+1,n):
            point2 = balls[j]
            ds = dist(point1,point2)
            F = G*point1[1]*point2[1]/(ds**2)
            ang = angle(point1,point2)
            balls[i][2] += F/point1[1] * cos(ang)
            balls[i][3] += F/point1[1] * sin(ang)
            balls[j][2] -= F/point2[1] * cos(ang)
            balls[j][3] -= F/point2[1] * sin(ang)
            if ds < radius(point1)+radius(point2):
                merge(point1,point2)
                return True

def add_ball(pos, size, x_speed, y_speed, color):
    balls.append([pos, size, x_speed, y_speed, color])

def gen_ball():
    pos = [(random()-0.5)*2*SPAWN_WIDTH, (random()-0.5)*2*SPAWN_HEIGHT]
    mass = SPAWN_MASS[0] + (SPAWN_MASS[1] - SPAWN_MASS[0])*random()
    x_velocity = (random()-0.5)*2*SPAWN_VELOCITY
    y_velocity = (random()-0.5)*2*SPAWN_VELOCITY
    color = choice(COLORS)
    add_ball(pos, mass, x_velocity, y_velocity, color)

def draw():
    clear()
    for point in balls:
        dot_radius = radius(point)*2*zoom
        x = point[0][0]- Sx
        y = point[0][1]- Sy
        if abs(x)-dot_radius < WIDTH/zoom and abs(y)-dot_radius < HEIGHT/zoom and dot_radius > 2:
            teleport(x*zoom , y*zoom)
            dot(dot_radius, point[4])

    if LIMIT_RANGE:
        teleport((-LIMIT_WIDTH-Sx)*zoom, (-LIMIT_HEIGHT-Sy)*zoom)
        pencolor('red')
        pendown()
        goto((LIMIT_WIDTH-Sx)*zoom, (-LIMIT_HEIGHT-Sy)*zoom)
        goto((LIMIT_WIDTH-Sx)*zoom, (LIMIT_HEIGHT-Sy)*zoom)
        goto((-LIMIT_WIDTH-Sx)*zoom, (LIMIT_HEIGHT-Sy)*zoom)
        goto((-LIMIT_WIDTH-Sx)*zoom, (-LIMIT_HEIGHT-Sy)*zoom)
        penup()

    if DRAW_SPAWNAREA:
        teleport((-SPAWN_WIDTH-Sx)*zoom, (-SPAWN_HEIGHT-Sy)*zoom)
        pencolor('green')
        pendown()
        goto((SPAWN_WIDTH-Sx)*zoom, (-SPAWN_HEIGHT-Sy)*zoom)
        goto((SPAWN_WIDTH-Sx)*zoom, (SPAWN_HEIGHT-Sy)*zoom)
        goto((-SPAWN_WIDTH-Sx)*zoom, (SPAWN_HEIGHT-Sy)*zoom)
        goto((-SPAWN_WIDTH-Sx)*zoom, (-SPAWN_HEIGHT-Sy)*zoom)
        penup()

    if DRAW_HUD:
        pencolor('black')

        teleport(-WIDTH+25, HEIGHT-100)
        write(f'Balls: {len(balls)}/{BALLS_LIMIT}', font=('Arial', 25, 'normal'))

        teleport(-WIDTH+25, HEIGHT-150)
        if all_mass < 1000:
            write(f'All mass: {round(all_mass,2)}kg', font=('Arial', 25, 'normal'))
        elif all_mass < 1000000:
            write(f'All mass: {round(all_mass/1000,2)}t', font=('Arial', 25, 'normal'))
        elif all_mass < 1000000000:
            write(f'All mass: {round(all_mass/1000000,2)}Kt', font=('Arial', 25, 'normal'))
        else:
            write(f'All mass: {round(all_mass/1000000000,2)}Mt', font=('Arial', 25, 'normal'))

        teleport(-WIDTH+25, -HEIGHT+50)
        write(f'{int(Sx)}X {int(Sy)}Y Zoom: x{round(1/zoom,2)} Spawning mass: {round(spawn_mass/1000,2)}t', font=('Arial', 20, 'normal'))

        teleport(-WIDTH+25, -HEIGHT+80)
        write(f'FPS: {round(tfps)}', font=('Arial', 20, 'normal'))

        teleport(-WIDTH+25, HEIGHT-200)
        if max_mass < 1000:
            write(f'Max mass: {round(max_mass,2)}kg', font=('Arial', 25, 'normal'))
        elif max_mass < 1000000:
            write(f'Max mass: {round(max_mass/1000,2)}t', font=('Arial', 25, 'normal'))
        elif max_mass < 1000000000:
            write(f'Max mass: {round(max_mass/1000000,2)}Kt', font=('Arial', 25, 'normal'))
        else:
            write(f'Max mass: {round(max_mass/1000000000,2)}Mt', font=('Arial', 25, 'normal'))

        if focus != 0:
            if all_mass != 0:
                mp = round(focus[1]/all_mass*100,2)
            else:
                mp = 100
            teleport(-WIDTH+25, HEIGHT-225)
            write(f'Mass: {round(focus[1]/1000,2)}t ({mp}%)', font=('Arial', 10, 'normal'))
            teleport(-WIDTH+25, HEIGHT-250)
            write(f'Diameter: {round(radius(focus)*2,2)}m', font=('Arial', 10, 'normal'))
            teleport(-WIDTH+25, HEIGHT-275)
            write(f'Speed: {round((focus[2]**2+focus[3]**2)**0.5,2)}', font=('Arial', 10, 'normal'))
            teleport(-WIDTH+25, HEIGHT-300)
            write(f'Color: {focus[4]}', font=('Arial', 10, 'normal'))

    update()

cicle()
