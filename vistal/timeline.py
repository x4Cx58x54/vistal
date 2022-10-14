from dataclasses import dataclass
from typing import List, Optional, Union

from distinctipy import get_colors

from .subtitle.elements import Rectangle, Move, Position, Time, Colour
from .subtitle.sections import EventItem

__all__ = [
    'get_inline_rectangle',
    'ColourScheme',
    'ColourSchemeLegend',
    'TimelinePosition',
    'TimelinePositionCalculator',
    'Timeline'
]


def get_inline_rectangle(font_size):
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
    timeline_ys: List[int]
    text_x: int
    text_y: int


class TimelinePositionCalculator:
    def __init__(
        self,
        display_width, display_height,
        timeline_height, timeline_margin_top, timeline_margin_bot,
        font_size, text_margin_top, text_margin_bot, text_margin_left,
        cursor_width, n_fold
    ):
        self.display_width = display_width
        self.display_height = display_height
        self.timeline_height = timeline_height
        self.timeline_margin_top = timeline_margin_top
        self.timeline_margin_bot = timeline_margin_bot
        self.font_size = font_size
        self.text_margin_top = text_margin_top
        self.text_margin_bot = text_margin_bot
        self.text_margin_left = text_margin_left
        self.cursor_width = cursor_width
        self.n_fold = n_fold
    def __call__(self, idx) -> TimelinePosition:
        bar_per_height = self.timeline_margin_top + self.timeline_height
        bar_total_height = (
            self.text_margin_top + self.text_margin_bot + self.font_size
          + bar_per_height*self.n_fold + self.timeline_margin_bot
        )
        bar_bot = self.display_height - bar_total_height * idx
        text_x = self.text_margin_left
        text_y = (
            bar_bot
          - self.timeline_margin_bot - bar_per_height*self.n_fold
          - self.text_margin_bot - self.font_size
        )
        timeline_x = 0
        timeline_ys = []
        for i in range(self.n_fold):
            timeline_ys.append(
                bar_bot
              - self.timeline_margin_bot
              - bar_per_height*(self.n_fold-i)
              + self.timeline_margin_top
            )
        return TimelinePosition(timeline_x, timeline_ys, text_x, text_y)


class EventItemContainer:
    def __init__(self):
        self.event_items = []
    def __iter__(self):
        return iter(self.event_items)


import numpy as np

def temporal_repartition(temporal_list, n_fold, video_duration):
    '''
    Handles overlaps between sections. Repartition the time dimension into
    disjoint parts, each associated with a list of label IDs and then devide
    into equal n_fold parts with equal durations. For example:
    temporal_repartition([
        (1, 3, 0),
        (2, 4, 1),
    ])
    =>
    [[
        (1, 2, [0]),
        (2, 3, [0, 1]),
        (3, 4, [1]),
    ]]
    '''
    new_temporal_list = []
    div_points = [video_duration * i / n_fold for i in range(1, n_fold)]
    timestamps = [i for i in div_points] # a deep copy
    for start, end, label_id in temporal_list:
        timestamps.append(start)
        timestamps.append(end)
    timestamps = np.unique(timestamps)
    for start, end in zip(timestamps[:-1], timestamps[1:]):
        middle = (start+end)/2
        middle_label_ids = []
        for start_0, end_0, label_id_0 in temporal_list:
            if start_0 <= middle < end_0:
                middle_label_ids.append(label_id_0)
        new_temporal_list.append((start,end,np.unique(middle_label_ids)))

    div_parts_start = [0] + div_points
    cur_i_div = 0
    new_temporal_list_folded = [[] for _ in range(n_fold)]
    for i in new_temporal_list:
        start, end, label_ids = i
        if cur_i_div < n_fold-1 and (start+end)/2 >= div_parts_start[cur_i_div+1]:
            cur_i_div += 1
        new_temporal_list_folded[cur_i_div].append(i)
    return new_temporal_list_folded


class Timeline(EventItemContainer):
    def __init__(
        self, name: str,
        tl_pos_cal: TimelinePositionCalculator, idx: int,
        temporal_list, video_duration, label_names,
        colour_scheme: ColourScheme,
        n_fold: int
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

        t_list_rep = temporal_repartition(temporal_list, n_fold, video_duration)

        tl_pos = tl_pos_cal(idx)

        name_text = Position(tl_pos.text_x, tl_pos.text_y)
        name_text += f'{self.name}:  '
        self.event_items.append(
            EventItem(
                name='Dialogue', Start=Time(0), End=Time(video_duration),
                Style='TimelineText', Text=name_text
            )
        )

        for i_fold in range(n_fold):
            # Label texts
            for start, end, label_ids in t_list_rep[i_fold]:
                label_texts = []
                for label_i, label_id in enumerate(label_ids):
                    label_text = str(label_id).rjust(max_label_len)
                    label_text += colour_scheme[label_id].tag() # set colour for the square
                    label_text += ' {\\bord1\\shad0}' # no border and shadow for the square
                    label_text += get_inline_rectangle(tl_pos_cal.font_size)
                    label_text += '{\\r}' # reset style
                    label_text += f' {label_names[label_id]}'
                    label_texts.append(label_text)
                self.event_items.append(
                    EventItem(
                        name='Dialogue', Start=Time(start), End=Time(end),
                        Style='TimelineText', Text=name_text+', '.join(label_texts)
                    )
                )

            # Colour rectangles
            for start, end, label_ids in t_list_rep[i_fold]:
                if len(label_ids) == 0:
                    continue
                rect_x = start / video_duration * tl_pos_cal.display_width * n_fold
                rect_y = tl_pos.timeline_ys[i_fold]
                rect_w = (end-start) / video_duration * tl_pos_cal.display_width * n_fold
                rect_h = tl_pos_cal.timeline_height
                rect_l_h = rect_h / len(label_ids)

                for label_i, label_id in enumerate(label_ids):
                    if colour_scheme[label_id].alpha == 255:
                        continue
                    rect = Rectangle(
                        rect_x - tl_pos_cal.display_width*i_fold,
                        rect_y + label_i*rect_l_h,
                        rect_w,
                        rect_l_h
                    )
                    rect = colour_scheme[label_id].tag() + rect
                    self.event_items.append(
                        EventItem(
                            'Dialogue', Start=Time(0), End=Time(video_duration),
                            Style='TimelineRect', Text=Position(0, 0)+rect
                        )
                    )

            # Moving cursor
            rect_cursor = Colour().tag()
            rect_cursor += Move(
                0, tl_pos.timeline_ys[i_fold],
                tl_pos_cal.display_width, tl_pos.timeline_ys[i_fold]
            )
            rect_cursor += Rectangle(
                0, 0,
                tl_pos_cal.cursor_width, tl_pos_cal.timeline_height
            )
            start = i_fold / n_fold * video_duration
            end = (i_fold+1) / n_fold * video_duration
            self.event_items.append(
                EventItem(
                    name='Dialogue', Start=Time(start), End=Time(end),
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
            + get_inline_rectangle(tl_pos_cal.font_size)
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
