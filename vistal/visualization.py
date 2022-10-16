from typing import Dict, List, Tuple, Union, Optional

from vistal.subtitle.elements import Colour

from .subtitle.sections import (
    ScriptInfo,
    V4PlusStyleItem,
    V4plusStyles,
    Events,
    AssSubtitle
)
from .timeline import (
    ColourScheme,
    ColourSchemeLegend,
    TimelinePositionCalculator,
    Timeline
)

__all__ = ['vistal']

def vistal(
    temporal_list_dict: Dict[str, List[Tuple]],
    label_names: Union[Dict[int, str], List[str]],
    colour_scheme: ColourScheme,
    video_duration: Union[int, float],
    display_width: int = 3840, display_height: int = 2160,
    timeline_height: Optional[int] = None,
    timeline_margin_top: Optional[int] = None,
    timeline_margin_bot: Optional[int] = None,
    font_size: Optional[int] = None, font_name='Ubuntu Mono',
    text_colour : Optional[Colour] = None,
    text_margin_top: Optional[int] = None,
    text_margin_bot: Optional[int] = None,
    text_margin_left: Optional[int] = None,
    text_outline: Optional[int] = None,
    text_shadow: Optional[int] = None,
    cursor_width: Optional[int] = None,
    show_legend = False,
    n_fold: int = 1,
    background_colour: Colour = Colour(alpha=255),
):
    '''
    Construct the main visualization elements.
    This is the core function of vistal library.

    For all the optional arguments, this function will choose resonable values
    for them automatically.

    Args:

        temporal_list_dict: dict of {name:temporal_list}, where temporal_list is
        a list of tuple(start, end, label_id), specifying the starting second,
        ending second and an integer label_id for a period of action.

        label_names: dict mapping from integer label_ids to string label names,
        or list containing the label_ids.

        video_duration: duration of video in seconds.

        display_width, display_height: to be brief, match the aspect ratio and
        set the display_height to a few thousand and it works just fine.

        They are width and height of the canvas in pixels (PlayResX and PlayResY
        in ASS subtitles). Therefore it is not a must for these args to equal the
        video frame size. The following geometric args are in the same pixel
        unit (heights, widths, sizes, margins).

        timeline_height: optional int of coloured timeline height in pixels.

        timeline_margin_top, timeline_margin_bot: optional int of timeline
        margins in pixels.

        font_size: optional int of font size in pixels.

        font_name: optional str of font name, monospace fonts are strongly
        recommended. For example: 'Ubuntu Mono', 'Cascadia Mono', 'Roboto Mono',
        'Monaco', 'Consolas'.

        text_colour: optional Colour instance, white in default.

        text_margin_top, text_margin_bot, text_margin_left: optional int of text
        margins in pixels.

        text_outline: optional int of text outline width in pixels.

        text_shadow: optional int of text shadow distance in pixels.

        cursor_width: optional int of cursor width in pixels.

        show_legend: bool for whether show colour legend.

        n_fold: fold each timeline into equal parts for clearer illustration for
        relatively short actions.

        background_colour: optional Colour for background colour of the coloured
        timelines.

    Returns:

        An AssSubtitle object, containing the visualization elements for temporal
        action localization.
    '''

    if timeline_height is None:
        timeline_height = max(display_height // 20, 1) # default 108
    if timeline_margin_top is None:
        timeline_margin_top = max(display_height // 240, 1) # default 9
    if timeline_margin_bot is None:
        timeline_margin_bot = 0
    if font_size is None:
        font_size = max(display_height // 24, 10) # default 90
    if text_colour is None:
        text_colour = Colour() # white
    if text_margin_top is None:
        text_margin_top = max(display_height // 360, 1) # default 6
    if text_margin_bot is None:
        text_margin_bot = max(display_height // 200, 1) # default 10
    if text_margin_left is None:
        text_margin_left = max(display_height // 100, 1) # default 21
    if text_outline is None:
        text_outline = max(display_height // 400, 1) # default 5
    if text_shadow is None:
        text_shadow = 1
    if cursor_width is None:
        cursor_width = max(display_height // 500, 1) # default 4


    si = ScriptInfo(
        Title='VISTAL visualization subtitle',
        PlayResX=display_width, PlayResY=display_height
    )
    si.prepend_comments([
        'Created by vistal.',
        'https://github.com/x4Cx58x54/vistal',
    ])
    vs = V4plusStyles()
    vs.append_item(V4PlusStyleItem('Style', Name='Default'))
    vs.append_item(V4PlusStyleItem(
        'Style', Name='TimelineRect',
        BorderStyle=0, Outline=0, Shadow=0,
        Alignment=7, MarginL=0, MarginR=0, MarginV=0
    ))
    vs.append_item(V4PlusStyleItem(
        'Style', Name='MovingCursor',
        BorderStyle=0, Outline=1, Shadow=1,
        Alignment=8, MarginL=0, MarginR=0, MarginV=0
    ))
    vs.append_item(V4PlusStyleItem(
        'Style', Name='TimelineText',
        Fontname=font_name, Fontsize=font_size,
        PrimaryColour=text_colour.style(),
        BorderStyle=0, Outline=text_outline, Shadow=text_shadow,
        Alignment=7, MarginL=0, MarginR=10, MarginV=10
    ))
    vs.append_item(V4PlusStyleItem(
        'Style', Name='LegendText',
        Fontname=font_name, Fontsize=font_size,
        PrimaryColour=text_colour.style(),
        BorderStyle=0, Outline=text_outline, Shadow=text_shadow,
        Alignment=7, MarginL=0, MarginR=10, MarginV=10
    ))
    es = Events()

    tl_pos_cal = TimelinePositionCalculator(
        display_width, display_height,
        timeline_height, timeline_margin_top, timeline_margin_bot,
        font_size, text_margin_top, text_margin_bot, text_margin_left,
        cursor_width, n_fold
    )

    for i, (name, temporal_list) in enumerate(temporal_list_dict.items()):
        timeline = Timeline(
            name, tl_pos_cal, i, temporal_list, video_duration, label_names,
            colour_scheme, n_fold, background_colour
        )
        for item in timeline:
            es.append_item(item)

    if show_legend:
        csl = ColourSchemeLegend(colour_scheme, 0, video_duration, tl_pos_cal)
        for item in csl:
            es.append_item(item)

    return AssSubtitle(si, vs, es)
