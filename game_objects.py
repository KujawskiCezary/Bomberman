import random
import time


class GameObject:
    def __init__(self, x, y, alive=True):
        self.__x = x
        self.__y = y
        self.__alive = alive

    @property
    def x(self):
        return self.__x

    @property
    def y(self):
        return self.__y

    @property
    def alive(self):
        return self.__alive

    @alive.setter
    def alive(self, value):
        self.__alive = value


class Playing_board(GameObject):
    pass


class Player(GameObject):
    def __init__(self, x, y, id, alive=True):
        super().__init__(x, y, alive)
        self.__id = id

    def move(self, direction, game):
        self.__game = game
        if direction == 'Up':
            self.set_y(self.y - 1)
        if direction == 'Down':
            self.set_y(self.y + 1)
        if direction == 'Left':
            self.set_x(self.x - 1)
        if direction == 'Right':
            self.set_x(self.x + 1)

    def place_bomb(self):
        return Bomb(self.x, self.y, random.randint(1, 5), time.time() + 3)

    @property
    def x(self):
        return self._GameObject__x

    @x.setter
    def x(self, value):
        self._GameObject__x = value

    @property
    def y(self):
        return self._GameObject__y

    @y.setter
    def y(self, value):
        self._GameObject__y = value

    def set_x(self, value):
        if 0 <= value < 40 and Block(value, self.y) not in self.__game.blocks \
                and not next(filter(lambda bomb: bomb.x == value and bomb.y == self.y, self.__game.bombs),
                         Bomb(0, 0, 0, 0, False)).alive:
            self._GameObject__x = value

    def set_y(self, value):
        if 0 <= value < 40 and Block(self.x, value) not in self.__game.blocks \
                and not next(filter(lambda bomb: bomb.x == self.x and bomb.y == value, self.__game.bombs),
                         Bomb(0, 0, 0, 0, False)).alive:
            self._GameObject__y = value

    @property
    def id(self):
        return self.__id

    def __repr__(self):
        return '{0}%x: {1}, y: {2}, id: {3}, alive: {4}'.format(type(self), self.x, self.y, self.id, self.alive)


class Bomb(GameObject):
    def __init__(self, x, y, range, timer, alive=True):
        super().__init__(x, y, alive)
        self.__range = range
        self.__timer = timer

    def __repr__(self):
        return '{0}%x: {1}, y: {2}, range: {3}, timer: {4}, alive: {5}' \
            .format(type(self), self.x, self.y, self.__range, self.__timer, self.alive)

    def make_boom(self, blocks, players):
        self.check_if_dead(blocks)
        self.check_if_dead(players)

    def check_if_dead(self, game_objects):
        for game_object in game_objects:
            if (self.x - self.range < game_object.x < self.x + self.range and self.y == game_object.y) \
                    or (self.y - self.range < game_object.y < self.y + self.range and self.x == game_object.x) \
                            and (not isinstance(game_object, Block) or game_object.destroyable):
                print(game_object)
                game_object.alive = False
                print(game_object)
    @property
    def range(self):
        return self.__range

    @property
    def timer(self):
        return self.__timer

    @timer.setter
    def timer(self, value):
        self.__timer = value

    def __hash__(self):
        return hash((self.x, self.y, self.range, self.timer))

    def __eq__(self, other):
        return self.x == other.x and self.y == other.y and self.timer == other.timer and self.range == other.range


class Block(GameObject):
    def __init__(self, x, y, destroyable=False, alive=True):
        super().__init__(x, y, alive)
        self.__destroyable = destroyable

    @property
    def destroyable(self):
        return self.__destroyable

    def __hash__(self):
        return hash((self.x, self.y, self.alive))

    def __eq__(self, other):
        return self.x == other.x and self.y == other.y and self.alive == other.alive

    def __repr__(self):
        return ('x: {0}, y: {1}, destroyable: {2}, alive: {3}'.format(self.x, self.y, self.destroyable, self.alive))