from dataclasses import dataclass
from typing import List, Optional, Union

from distinctipy import get_colors

from .subtitle.elements import Rectangle, Move, Position, Time, Colour
from .subtitle.sections import EventItem

__all__ = [
    'get_fit_rectangle',
    'ColourScheme',
    'ColourSchemeLegend',
    'TimelinePosition',
    'TimelinePositionCalculator',
    'Timeline'
]


def get_fit_rectangle(font_size):
    return Rectangle(0, font_size/10, font_size/1.3, font_size/1.3)


class ColourScheme:
    transparent = Colour(0, 0, 0, 255)
    def __init__(self, *,
        n_colours: Optional[int] = None,
        random_seed: Optional[int]= 1,
        transparent_id: Optional[Union[List[int], int]] = None,
        alpha: int = 0,
        colours: Optional[List[Colour]] = None,
        **kwargs
    ):
        '''
        Generate a colour scheme randomly or by specification:

        Randomly (by distinctipy):

        ColourScheme(n_colours=10, random_seed=0, transparent_id=0, alpha=0)

        By specification:

        ColourScheme([Colour(1,2,3), Colour(2,3,4)])

        Index this class instance to get colours: colour_scheme[idx].

        Args:
            n_colours: number of colours to generate.

            random_seed: the random seed.

            transparent_id: colour of this id will be transparent.

            alpha: uint8 for alpha channel; note that alpha in ass subtitle is
            opposite to RGBA definition.

            kwargs: other parameters for distinctipy.get_colors.

            colours: list of Colours specifying the colour scheme.
            if specified, other params will be ignored.
        '''
        if colours is not None:
            self.colours = colours
        else:
            # assert isinstance(colour_num, int)
            # random.seed(random_seed)
            # def random_channel():
            #     b = random.randint(0, 0xFF)
            #     g = random.randint(0, 0xFF)
            #     r = random.randint(0, 0xFF)
            #     a = random.randint(0, 0xFF) if alpha is None else alpha
            #     return b, g, r, a
            # self.colours = [Colour(*random_channel()) for _ in range(colour_num)]
            self.colours = [
                Colour(
                    round(b*255),
                    round(g*255),
                    round(r*255),
                    alpha
                )
                for r, g, b in get_colors(n_colours, rng=random_seed, **kwargs)
            ]
            if isinstance(transparent_id, int):
                self.colours[transparent_id] = self.transparent
            elif isinstance(transparent_id, list):
                for i in transparent_id:
                    self.colours[i] = self.transparent
    def __len__(self):
        return len(self.colours)
    def __getitem__(self, idx):
        return self.colours[idx]


@dataclass
class TimelinePosition:
    timeline_x: int
    timeline_y: int
    text_x: int
    text_y: int


class TimelinePositionCalculator:
    def __init__(
        self,
        display_width, display_height,
        timeline_height, timeline_margin_bot,
        font_size, text_margin_top, text_margin_bot, text_margin_left,
        cursor_width
    ):
        self.display_width = display_width
        self.display_height = display_height
        self.timeline_height = timeline_height
        self.timeline_margin_bot = timeline_margin_bot
        self.font_size = font_size
        self.text_margin_top = text_margin_top
        self.text_margin_bot = text_margin_bot
        self.text_margin_left = text_margin_left
        self.cursor_width = cursor_width
    def __call__(self, idx):
        bar_total_height = (
            self.text_margin_top + self.text_margin_bot + self.font_size
          + self.timeline_margin_bot + self.timeline_height
        )
        bar_bot = self.display_height - bar_total_height * idx
        timeline_x = 0
        timeline_y = bar_bot - self.timeline_margin_bot - self.timeline_height
        text_x = self.text_margin_left
        text_y = timeline_y - self.text_margin_bot - self.font_size
        return TimelinePosition(timeline_x, timeline_y, text_x, text_y)


class EventItemContainer:
    def __init__(self):
        self.event_items = []
    def __iter__(self):
        return iter(self.event_items)


class Timeline(EventItemContainer):
    def __init__(
        self, name: str,
        tl_pos_cal: TimelinePositionCalculator, idx: int,
        temporal_list, video_duration, label_names,
        colour_scheme: ColourScheme
    ):
        super().__init__()
        self.name = name
        self.tl_pos_cal = tl_pos_cal

        self.event_items = []

        if isinstance(label_names, dict):
            max_label_len = len(str(max(label_names.keys())))
        elif isinstance(label_names, list):
            max_label_len = len(str(len(label_names)))
        else:
            raise ValueError('Unsupported label_names type.')

        tl_pos = tl_pos_cal(idx)
        for i in temporal_list:
            start, end, label_id = i

            # Text
            text = Position(tl_pos.text_x, tl_pos.text_y)
            label_id_str = str(label_id).rjust(max_label_len)
            text += f'{self.name}: {label_id_str} '
            text += colour_scheme[label_id].tag() # set colour for the square
            text += '{\\bord1\\shad0}' # no border and shadow for the square
            text += get_fit_rectangle(tl_pos_cal.font_size)
            text += '{\\r}' # reset style
            text += f' {label_names[label_id]}'
            self.event_items.append(
                EventItem(
                    name='Dialogue', Start=Time(start), End=Time(end),
                    Style='TimelineText', Text=text
                )
            )
            if colour_scheme[label_id].alpha != 255:
                rect_x = start / video_duration * tl_pos_cal.display_width
                rect_y = tl_pos.timeline_y
                rect_w = (end-start)/video_duration*tl_pos_cal.display_width
                rect_h = tl_pos_cal.timeline_height
                rect = Rectangle(rect_x, rect_y, rect_w, rect_h)
                rect = Position(0, 0) + colour_scheme[label_id].tag() + rect
                self.event_items.append(
                    EventItem(
                        'Dialogue', Start=Time(0), End=Time(video_duration),
                        Style='TimelineRect', Text=rect
                    )
                )
        rect_cursor = Colour().tag()
        rect_cursor += Move(0, tl_pos.timeline_y,
        tl_pos_cal.display_width, tl_pos.timeline_y)
        rect_cursor += Rectangle(0, 0, tl_pos_cal.cursor_width, tl_pos_cal.timeline_height)
        self.event_items.append(
            EventItem(
                name='Dialogue', Start=Time(0), End=Time(video_duration),
                Style='MovingCursor', Text=rect_cursor
            )
        )


class ColourSchemeLegend(EventItemContainer):
    def __init__(
        self, colour_scheme: ColourScheme, start, end,
        tl_pos_cal: TimelinePositionCalculator
    ):
        super().__init__()
        length = len(colour_scheme)
        digit_length = len(str(length-1))
        text = [
            '{\\bord1\\shad0}'
            + colour_scheme[i].tag()
            + get_fit_rectangle(tl_pos_cal.font_size)
            + f'{{\\bord0\\shad0\\fs{max(1, tl_pos_cal.font_size//4)}}}\\h'
            # a small hard space
            + '{\\r}' # reset style
            + str(i).rjust(digit_length)
            for i in range(length)
        ]
        text = (' '*3).join(text)
        pos =  Position(tl_pos_cal.text_margin_left, tl_pos_cal.text_margin_top)
        text = pos + text

        self.event_items = [EventItem(
            name='Dialogue', Start=Time(start), End=Time(end),
            Style='TimelineText', Text=text
        )]
