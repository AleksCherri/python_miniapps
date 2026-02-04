from random import *
width = 16
height = 16
maps = []
genome = []
sprouts = []
func = ['u','r','d','l','leaf','seed', 'move']
food_d = 100
food = 100
muta = 0.5
time = 0
score = 0
ge = 0

btime = [0,[],[]]
bsize = [0,[],[]]
bgen = [0,[],[]]

l_gen = 5
x_gen = 3
seed_gen = -3
spr_gen = -5

stops = False
show = True
itera = 10000

def gen_maps():
    global maps
    maps = ['.'] * (width * height)
    

def gen_genome():
    genome.clear()
    for i in range(randint(1,10)):
        genome.append([
            func[randint(0,3)],
            func[randint(4, len(func) - 1)]
        ]) 

def gen_sprouts(pos, gens, seed):
    if muta > random():
        a = randint(0,2)
        if a == 0:
            gens.append([func[randint(0,3)],func[randint(4,len(func)-1)]])
        if a == 1 and len(gens) > 1:
            gens.pop(randint(0,len(gens)-1))
        if a == 2:
            gens[randint(0,len(gens)-1)] = [func[randint(0,3)],func[randint(4,len(func)-1)]]
    sprouts.append([pos, gens, seed]) #[клетка][позиция, геном[ген][сторона, тип клетки]]
    if seed:
        maps[pos] = 'S'
    else:
        maps[pos] = 'O'
    if show:
        print('generated',pos,'sprouts =',len(sprouts))

def count_leaf():
    for i in range(len(maps)):
        if maps[i] == 'L':
            pass

def draw():
    for y in range(height):
        a = ''
        for x in range(width):
            a += maps[(y*width) + x] + ' '
        print(a)

def grow():
    global maps, food, time, score
    a = []
    
    if sprouts == []:
        print('It is dead:',score,'Generations:',ge)
        score = 0
        if stops or itera <= ge:
            input()
        else:
            start()
        return False

    for i in sprouts:
        a.append(len(i[1]))

    for i in range(max(a)):
        for h in sprouts:
            if len(h[1]) > i and not h[2]:
                p = ''
                if h[1][i][0] == 'u' and h[0]//width > 0:
                    if maps[h[0]-width] == '.':
                        p = h[0]-width
                if h[1][i][0] == 'd' and h[0]//width+2 <= height:
                    if maps[h[0]+width] == '.':
                        p = h[0]+width
                if h[1][i][0] == 'l' and h[0]%width-1 >= 0:
                    if maps[h[0]-1] == '.':
                        p = h[0]-1
                if h[1][i][0] == 'r' and h[0]%width+1 < width:
                    if maps[h[0]+1] == '.':
                        p = h[0]+1
                if p != '':
                    if h[1][i][1] == 'leaf':
                        maps[p] = 'L'
                    if h[1][i][1] == 'seed':
                        gen_sprouts(p, h[1][:], True)
                    if h[1][i][1] == 'move':
                        maps[p] = 'O'
                        maps[h[0]] = 'X'
                        h[0] = p

        food += maps.count('L') + maps.count('X')*x_gen + maps.count('S')*seed_gen + maps.count('O')*spr_gen - time
        time += 1
        if food <= 0:
            death()
            break
        if show:
            print(food, time)
            draw()
            input()
    return True

def record():
    global btime, bsize, bgen
    if time > btime[0]:
        btime[0] = time
        btime[1] = maps[:]
        btime[2] = sprouts[:]
    size = width * height - maps.count('.')
    if size > bsize[0]:
        bsize[0] = size
        bsize[1] = maps[:]
        bsize[2] = sprouts[:]
    if score > bgen[0]:
        bgen[0] = score
        bgen[1] = maps[:]
        bgen[2] = sprouts[:]

def death():
    global maps, food, sprouts, score, time, ge

    record()

    for i in range(len(maps)):
        if maps[i] == 'X' or maps[i] == 'L' or maps[i] == 'O':
            maps[i] = '.'
        if maps[i] == 'S':
            maps[i] = 'O'

    buffer = []
    for i in sprouts:
        if i[2]:
            buffer.append(i)
    sprouts = buffer[:]
    
    for i in sprouts:
        i[2] = False

    food = food_d
    time = 0
    score += 1
    ge += 1
    if show:
        print('Death happened.')
        print('sprouts =',len(sprouts))

def cicle():
    if show:
        print(genome)
    while grow():
        pass

def start():
    gen_maps()
    gen_genome()
    gen_sprouts(height//2*width + width//2, genome[:], False)
    cicle()

def load(a):
    global maps, sprouts

    if a == 't':
        maps = btime[1][:]
        sprouts = btime[2][:]
        print(btime[0],'iterations.')
    if a == 's':
        maps = bsize[1][:]
        sprouts = btime[2][:]
        print(bsize[0],'cells.')
    if a == 'g':
        maps = bgen[1][:]
        sprouts = bgen[2][:]
        print(bgen[0], 'generations.')
    
    draw()
    print('Loaded best generation.')

def rang(n):
    i = 0
    while i < n:
        yield i
        i += 1

start()
