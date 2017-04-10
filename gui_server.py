import sys
from PyQt5.QtGui import QPixmap
from PyQt5.QtCore import Qt, QBasicTimer, QRect
from PyQt5.QtWidgets import QLabel, QWidget, QApplication, QMainWindow, QPushButton
from PyQt5.QtWidgets import QVBoxLayout
import random
from game import Game
from game_objects import Player, Block, Bomb
from game_parser import parse
import socket
import threading
import jsonpickle
import time

class GUI(QMainWindow):
    def __init__(self):
            super().__init__()
            #self.welcomeUI()
            self.create_socket()
            self.initUI()


    def welcomeUI(self):
        self.setGeometry(50, 50, 600, 600)
        self.setWindowTitle('Bomberman')
        self.show()

    def initUI(self):
        self.setGeometry(50, 50, 600, 600)
        self.setWindowTitle('Bomberman')
        self.timer = QBasicTimer()
        self.timer.start(20, self)
        self.__player = next(filter(lambda player: player.id == 1, self.__game.players), None)
        self.bombs = []
        self.label_bombs = []
        self.labels_for_bombs = [QLabel(self) for i in range(200)]
        for label in self.labels_for_bombs:
            label.setPixmap(QPixmap('bomb1.jpg'))
            label.setGeometry(50, 50, 0, 0)
        self.label_players = [[QLabel(self), player] for player in self.__game.players]
        for label in self.label_players:
            label[0].setPixmap(QPixmap('player1.jpg'))
        self.label_blocks1 = [[QLabel(self), block] for block in self.__game.blocks if not block.destroyable]
        for label in self.label_blocks1:
            label[0].setPixmap(QPixmap('block1.jpg'))
            label[0].setGeometry(QRect(15 * label[1].x, 15 * label[1].y, 15, 15))
        self.label_blocks2 = [[QLabel(self), block] for block in self.__game.blocks if block.destroyable]
        for label in self.label_blocks2:
            label[0].setPixmap(QPixmap('block2.jpg'))
            label[0].setGeometry(QRect(15 * label[1].x, 15 * label[1].y, 15, 15))

        threading.Thread(target=self.ai, args=(3,)).start()
        threading.Thread(target=self.ai, args=(4,)).start()
        self.show()

    def timerEvent(self, event):
        if event.timerId() == self.timer.timerId():
            self.repaint()
        else:
            super.timerEvent(event)

    def paintEvent(self, *args, **kwargs):
        try:
            new_bombs = set(self.__game.bombs).difference(set(self.bombs))
            if len(new_bombs) > 0:
                self.bombs.extend(list(new_bombs))
                for bomb in new_bombs:
                    self.label_bombs.append([self.labels_for_bombs.pop(), bomb])

            for label in self.label_players + self.label_bombs:
                if label[1].alive:
                    label[0].setGeometry(QRect(15 * label[1].x, 15 * label[1].y, 15, 15))
                else:
                    label[0].hide()

            for label in self.label_blocks2:
                if not label[1].alive:
                    label[0].hide()
        except:
            pass

    def keyPressEvent(self, e):
        if self.__player.alive and  not e.isAutoRepeat():
            if e.key() == Qt.Key_Space:
                bomb = self.__player.place_bomb()
                self.__game.bomb_it(bomb)
                self.send(bomb)
                return
            if e.key() == Qt.Key_W:
                self.__player.move('Up', self.__game)
            if e.key() == Qt.Key_S:
                self.__player.move('Down', self.__game)
            if e.key() == Qt.Key_A:
                self.__player.move('Left', self.__game)
            if e.key() == Qt.Key_D:
                self.__player.move('Right', self.__game)
            self.send(self.__player)

        if e.key() == Qt.Key_Escape:
            self.close()
        if e.key() == Qt.Key_Q:
            print(self.__player, end = '')

    def recieve(self, socket):
        while True:
            resp = socket.recv(128).decode('utf-8')
            if resp != '':
                game_object = parse(resp)
                if isinstance(game_object, Player):
                    self.__game.players[int(game_object.id) - 1].x = (int(game_object.x))
                    self.__game.players[int(game_object.id) - 1].y = (int(game_object.y))
                    self.label_players[int(game_object.id) - 1][1] = game_object
                else:
                    self.__game.bomb_it(game_object)

    def send(self, game_object):
        self.clientsocket.send(str(game_object).encode('utf-8'))


    def create_socket(self):
        self.__game = Game()
        serversocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        serversocket.bind((socket.gethostname(), 8080))
        serversocket.listen(5)
        #while True:
        (self.clientsocket, address) = serversocket.accept()
        print("hi ", address)
        self.clientsocket.send(jsonpickle.encode(self.__game).encode('utf-8'))
        threading.Thread(target = self.recieve, args = (self.clientsocket,)).start()

    def connect_to_socket(self):
        clientsocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        clientsocket.connect(('Czarek', 8080))
        resp = clientsocket.recv(4048).decode('utf-8')
        game = jsonpickle.decode(resp)

    def ai(self, id):
        player = next(filter(lambda player: player.id == id, self.__game.players), None)
        while True and player.alive:
            time.sleep(0.1)
            moves_score = []
            moves_score.append(self.assign_move(player, 'Up'))
            moves_score.append(self.assign_move(player, 'Down'))
            moves_score.append(self.assign_move(player, 'Left'))
            moves_score.append(self.assign_move(player, 'Right'))
            moves_score.append(self.assign_move(player, 'Bomb'))
            moves_score.sort(key=lambda move:move[0])
            print(moves_score)
            if moves_score[0][1] == 'Bomb':
                bomb = player.place_bomb()
                self.__game.bomb_it(bomb)
                self.send(bomb)
            else:
                player.move(moves_score[0][1], self.__game)
                self.send(player)


    def assign_move(self, player, move):
        if move == 'Up':
            points = 100 * self.in_bomb_range(player.x, player.y - 1) + 400 * self.move_is_viable(player.x, player.y - 1)
        elif move == 'Down':
            points = 100 * self.in_bomb_range(player.x, player.y + 1) + 400 * self.move_is_viable(player.x, player.y + 1)
        elif move == 'Left':
            points = 100 * self.in_bomb_range(player.x - 1, player.y) + 400 * self.move_is_viable(player.x - 1, player.y)
        elif move == 'Right':
            points = 100 * self.in_bomb_range(player.x + 1, player.y) + 400 * self.move_is_viable(player.x + 1, player.y)
        else:
            points = 100 * self.in_bomb_range(player.x, player.y)
            return points + random.randint(1, 10) - 50*self.bomb_can_kill_anything(player), move
        return points + random.randint(1,10), move

    def in_bomb_range(self, x, y):
        for bomb in filter(lambda bomb:bomb.alive, self.__game.bombs):
            if bomb.x == x and bomb.y == y:
                return 2
            if (bomb.x - bomb.range < x < bomb.x + bomb.range and bomb.y == y) \
                    or (bomb.y - bomb.range < y < bomb.y + bomb.range and bomb.x == x):
                #print('bomba blisko')
                return 1
        return 0

    def bomb_can_kill_anything(self, player):
        for game_object in self.__game.players and self.__game.blocks:
            if game_object.alive and (not isinstance(game_object, Block) or game_object.destroyable) \
                and (player.x - 3 < game_object.x < player.x + 3 and player.y == game_object.y
                     or player.y - 3 < game_object.y < player.y + 3 and player.x == game_object.x):
                #print('obiekt blisko')
                return 1

        return -1

    def move_is_viable(self, x, y):
        if (0 <= x < 40 and Block(x, self.y) not in self.__game.blocks \
                and not next(filter(lambda bomb: bomb.x == x and bomb.y == y, self.__game.bombs),
                             Bomb(0, 0, 0, 0, False)).alive)\
                and (0 <= y < 40 and Block(self.x, y) not in self.__game.blocks \
                and not next(filter(lambda bomb: bomb.x == x and bomb.y == y, self.__game.bombs),
                         Bomb(0, 0, 0, 0, False)).alive):
            return 0
        return 1


if __name__ == '__main__':
    app = QApplication(sys.argv)
    gui = GUI()
    sys.exit(app.exec_())