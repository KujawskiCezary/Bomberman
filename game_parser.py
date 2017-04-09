from game_objects import Player,Bomb


def parse(message):
    message = message.split('%')
    type_of_elem = message[0]
    elem = message[1].split(',')
    if type_of_elem == "<class 'game_objects.Player'>":
        return Player(x=int(elem[0][3:]), y=int(elem[1][4:]), id=int(elem[2][5:]))
    elif type_of_elem == "<class 'game_objects.Bomb'>":
        print(elem)
        return Bomb(x=int(elem[0][3:]), y=int(elem[1][4:]), range=int(elem[2][8:]), timer=float(elem[3][8:]))



