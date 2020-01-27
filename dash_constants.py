# constants used in app.py

HEADER_2_SIZE = '30px'

PLOT_BACKGROUND_COLOR = '#f0f0f0'
BACKGROUND_COLOR_LIGHT = '#d7ded3'
BACKGROUND_COLOR_DARK = '#567D46'

BACKGROUND_ALPHA = 0.9

BACKGROUND_LIGHT_RGB = tuple(int(BACKGROUND_COLOR_LIGHT.lstrip('#')[i:i+2], 16) for i in (0, 2, 4))
BACKGROUND_DARK_RGB = tuple(int(BACKGROUND_COLOR_DARK.lstrip('#')[i:i+2], 16) for i in (0, 2, 4))

AXIS_TITLE_SIZE = 18
