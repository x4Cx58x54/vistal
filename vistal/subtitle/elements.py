from typing import Any, List, Union, Optional

__all__ = ['DialogueText', 'Rectangle', 'Move', 'Position', 'Colour', 'Time']


class DialogueText:
    def __init__(self, name: Optional[str]=None, args: Optional[List] = None):
        self.name = name
        self.args = args
    def __str__(self):
        if self.name is not None:
            res = f'\\{self.name}'
            if self.args is not None:
                res += ','.join([str(x) for x in self.args])
            res = '{' + res + '}'
            return res
        else:
            raise NotImplementedError
    def __add__(self, other: Any):
        return str(self) + str(other)
    def __radd__(self, other: Any):
        return str(other) + str(self)


class Colour(DialogueText):
    def __init__(
        self, b: int = 255, g: int = 255, r: int = 255, alpha: int = 0,
        mode: Optional[str] = None
    ):
        '''
        It seems in the ASS subtitle specification, alpha channel is opposite
        to RGBA color model definition. Therefore alpha is in fact transparency:
        alpha = 255 for transparent and alpha = 0 for opaque.
        '''
        for i in (alpha, b, g, r):
            if i < 0 or i > 255:
                raise ValueError('Color channel value not between 0 and 255.')
        self.alpha = alpha
        self.b = b
        self.g = g
        self.r = r
        self.mode = mode
    def tag(self):
        return Colour(self.b, self.g, self.r, self.alpha, 'tag')
    def style(self):
        return Colour(self.b, self.g, self.r, self.alpha, 'style')
    def is_transparent(self):
        return self.alpha == 255
    def __str__(self):
        if self.mode == 'tag':
            return f'{{\\1a&H{self.alpha:02X}&\\c&H{self.b:02X}{self.g:02X}{self.r:02X}&}}'
        elif self.mode == 'style':
            return f'&H{self.alpha:02X}{self.b:02X}{self.g:02X}{self.r:02X}'
        else:
            raise ValueError('Cannot determine color string mode.')


class Time:
    def __init__(self, total_seconds: Union[int, float]):
        self.total_seconds = total_seconds

        self.seconds = int(total_seconds)
        self.centiseconds = round((total_seconds - self.seconds)*100)
        self.hours = self.seconds // 3600
        self.minutes = (self.seconds % 3600) // 60
        self.seconds = self.seconds % 60

        assert 0 <= self.hours < 10, \
               'ASS subtitle supports only hours between 0~9.'

    def __str__(self):
        return f'{self.hours:d}:{self.minutes:02d}:{self.seconds:02d}.{self.centiseconds:02d}'


class Point:
    def __init__(self, x: Union[int, float], y: Union[int, float]):
        self.x = x
        self.y = y
        self.type = int # one of the coord is float, point is float
        if isinstance(self.x, float):
            self.type = float
            self.x_str = f'{self.x:.2f}'
        else:
            self.x_str = str(self.x)
        if isinstance(self.y, float):
            self.type = float
            self.y_str = f'{self.y:.2f}'
        else:
            self.y_str = str(self.y)
    def __str__(self):
        return f'{self.x_str} {self.y_str}'
    def __mul__(self, other):
        return Point(self.x*other, self.y*other)
    def __rmul__(self, other):
        return Point(self.x*other, self.y*other)


class Rectangle(DialogueText):
    def __init__(self, x, y, w, h):
        super().__init__()
        self.x = x
        self.y = y
        self.w = w
        self.h = h
        self.top_left  = Point(self.x,        self.y)
        self.top_right = Point(self.x+self.w, self.y)
        self.bot_left  = Point(self.x,        self.y+self.h)
        self.bot_right = Point(self.x+self.w, self.y+self.h)
        self.type = int
        for i in (self.top_left, self.top_right, self.bot_left, self.bot_right):
            if i.type == float:
                self.type = float
                break
        self.draw_mode:int = 1 if self.type == int else 4 # ass \p tag number
        self.resolution_scale = 2**(self.draw_mode-1)
    def __str__(self):
        res = ''
        res += f'{{\\p{self.draw_mode}}}'
        res += f'm {self.top_left *self.resolution_scale} '
        res += f'l {self.top_right*self.resolution_scale} '
        res += f'l {self.bot_right*self.resolution_scale} '
        res += f'l {self.bot_left *self.resolution_scale} '
        res += f'l {self.top_left *self.resolution_scale} '
        res += f'{{\\p0}}'
        return res


class Move(DialogueText):
    def __init__(self, x1: int, y1: int, x2: int, y2: int):
        super().__init__()
        self.x1 = x1
        self.y1 = y1
        self.x2 = x2
        self.y2 = y2
    def __str__(self):
        return f'{{\\move({self.x1},{self.y1},{self.x2},{self.y2})}}'


class Position(DialogueText):
    def __init__(self, x: int, y: int):
        super().__init__()
        self.x = x
        self.y = y
    def __str__(self):
        return f'{{\\pos({self.x}, {self.y})}}'
