from pathlib import Path
from typing import Any, List, Dict, Union

from .elements import DialogueText, Colour, Time

__all__ = [
    'Item', 'Section', 'ScriptInfo', 'V4PlusStyleItem', 'V4plusStyles',
    'EventItem', 'Events', 'AssSubtitle'
]


class Item:
    def __init__(self, name: str, value: Any):
        self.name = name
        self.value = value
        if isinstance(self.value, list):
            self.value = ','.join([str(x) for x in self.value])
    def __str__(self):
        return f'{str(self.name)}: {str(self.value)}'


class Section:
    name = 'Unnamed Section'
    def __init__(self):
        super().__init__()
        self.items: List[Union[Item, str]] = list()
    def __str__(self):
        lines_list: List[str] = list()
        lines_list.append(f'[{self.name}]')
        lines_list.extend(
            str(item) for item in self.items
        )
        lines: str = '\n'.join(lines_list) + '\n'
        return lines
    def append_item(self, *args):
        if len(args) == 1:
            self.items.append(args[0])
        elif len(args) == 2:
            self.items.append(Item(args[0], args[1]))
        else:
            raise ValueError(f'append_item takes 1 (Item,) or 2 (name, value) arguments, but {len(args)} was/were given.')
    def append_kwargs_to_items(self, kwargs: Dict):
        self.items.extend(Item(k, v) for k, v in kwargs.items())


class ScriptInfo(Section):
    name = 'Script Info'
    def __init__(
        self, *, Title: str, ScriptType: str = 'v4.00+',
        ScaledBorderAndShadow: str = 'yes',
        PlayResX: int, PlayResY: int,
        **kwargs
    ):
        super().__init__()
        self.append_item('Title', Title)
        self.append_item('ScriptType', ScriptType)
        self.append_item('ScaledBorderAndShadow', ScaledBorderAndShadow)
        self.append_item('PlayResX', PlayResX)
        self.append_item('PlayResY', PlayResY)
        self.append_kwargs_to_items(kwargs)
    def prepend_comments(self, comments: List[str]):
        self.items = ['; '+c for c in comments] + self.items


class V4PlusStyleItem(Item):
    def __init__(
        self,
        name: str = 'Style', # Literal['Format', 'Style']
        Name = 'Default',
        Fontname = 'Arial',
        Fontsize = 20,
        PrimaryColour: Union[Colour, str] = Colour(255, 255, 255).style(),
        SecondaryColour: Union[Colour, str] = Colour(0, 0, 255).style(),
        OutlineColour: Union[Colour, str] = Colour(0, 0, 0).style(),
        BackColour: Union[Colour, str] = Colour(0, 0, 0).style(),
        Bold = 0, Italic = 0, Underline = 0, StrikeOut = 0,
        ScaleX = 100, ScaleY = 100, Spacing = 0, Angle = 0,
        BorderStyle = 1, Outline = 2, Shadow = 1,
        Alignment = 2, MarginL = 10, MarginR = 10, MarginV = 10,
        Encoding = 1,
    ):
        if name == 'Format':
            value = f'Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding'
        else:
            value = [Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding]
        super().__init__(name, value)


class V4plusStyles(Section):
    name = 'V4+ Styles'
    def __init__(self):
        super().__init__()
        self.append_item(V4PlusStyleItem('Format'))


class EventItem(Item):
    def __init__(
        self,
        name: str = 'Dialogue', # Literal['Format', 'Dialogue']
        Layer = 1,
        Start: Union[Time, str] = Time(0),
        End: Union[Time, str] = Time(0),
        Style = 'Default',
        Name = '',
        MarginL = 0, MarginR = 0, MarginV = 0, Effect = '',
        Text: Union[str, DialogueText] = '',
    ):
        if name == 'Format':
            value = f'Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text'
        else:
            value = [Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text]
        super().__init__(name, value)


class Events(Section):
    name = 'Events'
    def __init__(self):
        super().__init__()
        self.append_item(EventItem('Format'))


class AssSubtitle:
    '''
    Contains an ASS subtitle. Apply str function to get the content in string
    form. Apply save method to save to a file.
    '''
    def __init__(self, *args: Section):
        self.args = args
    def __str__(self):
        return '\n'.join([str(x) for x in self.args])
    def save(self, path: Union[Path, str], *, confirm_overwrite=True):
        '''
        Save the subtitle to an .ass file.

        Args:

            path: pathlib.Path or str, the path of the file to save.

            confirm_overwrite: optional bool, whether confirmation is needed
            before overwriting existing file.
        '''
        path = Path(path)
        if path.exists() and confirm_overwrite:
            confirm = input(f'\'{str(path)}\' exists, overwrite? [y/n]: ')
            if confirm != 'y':
                print('Quit saving.')
                return
        with open(path, 'w') as f:
            f.write(str(self))
            print(f'Subtitle saved to {str(path)}.')
