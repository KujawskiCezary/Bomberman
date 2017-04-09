from game_objects  import Playing_board, Block, Player
import jsonpickle
import random
import time
import threading
class Game:
    def __init__(self):
        self.__playing_board = Playing_board(40, 40)
        self.__blocks = {
            Block(8, i) for i in list(range(5)) + list(range(35, 40))
        }.union(
            Block(i, 8) for i in list(range(5)) + list(range(35, 40))
        ).union(
            Block(31, i) for i in list(range(5)) + list(range(35, 40))
        ).union(
            Block(i, 31) for i in list(range(5)) + list(range(35, 40))
        ).union(
            Block(random.randint(10, 30), random.randint(10, 30)) for i in range(100)
        ).union(
            Block(random.randint(5, 35), random.randint(5, 35), True) for i in range(400)
        )
        self.__players = [
            Player(random.randint(0, 4), random.randint(0, 4), 1), Player(random.randint(35, 39), random.randint(0, 4), 2),
            Player(random.randint(0, 4), random.randint(35, 39), 3), Player(random.randint(35, 39), random.randint(35, 39), 4)
        ]
        self.__bombs = []


    @property
    def playing_board(self):
        return self.__playing_board

    @property
    def blocks(self):
        return self.__blocks

    @property
    def players(self):
        return self.__players

    @property
    def bombs(self):
        return self.__bombs

    def bomb_thread(self, bomb):

        while(True):
            if time.time() > float(bomb.timer):
                bomb.make_boom(self.blocks, self.players)
                bomb.alive = False
                print("boom")
                break

    def bomb_it(self, bomb):
        self.__bombs.append(bomb)
        threading.Thread(target=self.bomb_thread, args=(bomb,)).start()

    def toJSON(self):
        return jsonpickle.encode({'players': self.players, 'blocks': self.blocks, 'bombs': self.bombs})

