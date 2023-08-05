import os
_points = {'': 0,
          'a':1,
          'b':3,
          'c':3,
          'd':2,
          'e':1,
          'f':4,
          'g':2,
          'h':4,
          'i':1,
          'j':8,
          'k':5,
          'l':1,
          'm':3,
          'n':1,
          'o':1,
          'p':3,
          'q':10,
          'r':1,
          's':1,
          't':1,
          'u':1,
          'v':4,
          'w':4,
          'x':8,
          'y':4,
          'z':10,}

alphabet = ['e'] * 25 + \
           ['t', 'a', 'o', 'i'] * 20 + \
           ['n', 's', 'h', 'r'] * 15 + \
           ['d', 'l', 'c', 'u', 'm'] * 12 + \
           ['w', 'f', 'g', 'y', 'p', 'b'] * 10 + \
           ['v', 'k', 'j'] * 5 + \
           ['x', 'q', 'z'] * 2

class Alphabet(object):
    """
    class: Alphabet class, the objects of which are stored in the grid.
    """
    def __init__(self, letter):
        self.letter = letter
        '''image path wrt to practicewordament.py'''
        image_path = os.path.join(os.path.dirname(__file__), 'images/alphabet/')
        self.image = image_path + self.letter + '.png'
        self.points = _points[self.letter]

class Game:
    """
    class: Represents a game.
    """
    def __init__(self, grid, grid_words_list, sum_total_points, total_points):
        self.grid = [x[:] for x in grid]
        self.grid_words_list = grid_words_list
        self.sum_total_points = sum_total_points
        self.total_points = total_points
        self.user_words_list = []
        self.sum_user_points = 0
    
class GameQueue:
    """
    class: Data structure to hold the games created.
    """
    def __init__(self):
        self._list = []
        self._len = 0

    def push(self, obj, to_start=False):
        if to_start:
            self._list.insert(0, obj)
        else:
            self._list.append(obj)
        self._len += 1
    
    def empty(self):
        return self._len == 0

    @property
    def size(self):
        return self._len

    def pop(self):
        if self.empty(): return None
        obj = self._list.pop(0)
        self._len -= 1
        return obj