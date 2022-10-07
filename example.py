from pathlib import Path

from vistal import vistal, ColourScheme, Colour


# duration of video
seconds = 30
# number of actions
n = 10

t_labels = [
    (i*seconds/n, (i+1)*seconds/n, i) for i in range(n)
]
label_names = {
    i: f'Action {i}' for i in range(n)
}

# generate a colour scheme randomly,
# and set the last action to be transparent on the timeline
colour_scheme = ColourScheme(n_colours=n, transparent_id=n-1)

sub = vistal(
    # two identical temporal lists, gt and pred, therefore same timelines
    # extra spaces in the keys are for text alignment
    temporal_list_dict={
        'gt  ': t_labels,
        'pred': t_labels
    },
    label_names=label_names,
    colour_scheme=colour_scheme,
    video_duration=seconds,
    display_width=1280,
    display_height=720,
    timeline_height=72, # each timeline takes 60/720 of video height, very large
    font_size=72,       # large font, too, for illustration
    font_name='Ubuntu Mono',
    show_legend=True
)
sub.save(Path('example.ass'))
