from random import randint

PACK_PATH = 'pack.txt'
OUTPUT_FOLDER = 'outputs/'

pack_file = open(PACK_PATH, encoding='utf-8')
player_list = pack_file.readline().split('<')
player_list.pop(-1)

pack = dict()
for line in pack_file:
    line = line.split('^')
    props = line[1].split('<')
    props.pop(-1) if props[-1] in ('\n','') else None
    pack[line[0]] = props

for player in player_list:
    player_card = f'Имя: {player}\nВозраст: {randint(0,130)}\n'
    for prop in pack:
        player_card += f'{prop}: {pack[prop].pop(randint(-1, len(pack[prop])-1))}\n'

    with open(f'{OUTPUT_FOLDER}{player}_card.txt', 'w') as file:
        file.write(player_card)

print(f'Player cards generated at {OUTPUT_FOLDER}.')
