import sys
from PyQt5.QtGui import QPixmap
from PyQt5.QtCore import Qt, QBasicTimer, QRect
from PyQt5.QtWidgets import QLabel, QWidget, QApplication, QMainWindow, QPushButton
from PyQt5.QtWidgets import QVBoxLayout

from game import Game
from game_objects import Player
from game_parser import parse
import socket
import threading
import jsonpickle

class GUI(QMainWindow):
    def __init__(self):
            super().__init__()
            #self.welcomeUI()
            self.connect_to_socket()
            self.initUI()


    def initUI(self):
        self.setGeometry(50, 50, 600, 600)
        self.setWindowTitle('Bomberman')
        self.timer = QBasicTimer()
        self.timer.start(20, self)
        self.__player = next(filter(lambda player: player.id == 2, self.__game.players), None)
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

            for label in self.label_players  + self.label_bombs:
                #if isinstance(label[1], Player): print(label[1])
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
            print(self.__player)

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
        # while True:
        (self.clientsocket, address) = serversocket.accept()
        print("hi ", address)
        self.clientsocket.send(jsonpickle.encode(self.__game).encode('utf-8'))
        threading.Thread(target=self.recieve, args=(self.clientsocket,)).start()

    def connect_to_socket(self):
        self.clientsocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.clientsocket.connect(('Czarek', 8080))
        resp = self.clientsocket.recv(60720).decode('utf-8')
        game = jsonpickle.decode(resp)
        self.__game = game
        threading.Thread(target=self.recieve, args=(self.clientsocket,)).start()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    gui = GUI()
    sys.exit(app.exec_())