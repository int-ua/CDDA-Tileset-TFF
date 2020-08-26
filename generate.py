#!/usr/bin/env python3
'''
Generates text fallback fillers for the
Cataclysm Dark Days Ahead game tilesets.
'''

import csv
import json
import os
import pyvips
import re
import sys

from pathlib import Path

# settings
DIR = 'text_fallback_fillers'
GAME_DIR = '../Cataclysm-DDA'
FONT = 'Liberation Sans Narrow, Condensed'
SHADOW_BLEND_MODE = 'add'
SHADOW_OFFSET = {
    'x': 1,
    'y': 1
}
JSON_DUMP_ARGS = {}
DEFAULT_COLOR = 'black'
LIGHT_GRAY = (200, 200, 200)
PINK = (255, 192, 203)

TYPES = {
    'default': {
        'canvas_dimensions': (32, 32),
        'text_box': {'width': 32, 'height': 32},
        'font_size': 10,
        'text_gravity': 'north-west',
        'canvas_gravity': 'north-west',
    },
    'monster': {
        'canvas_dimensions': (32, 64),
        'text_box': {'width': 48, 'height': 32},
        'font_size': 10,
        'text_gravity': 'north-west',
        'canvas_gravity': 'south',
        'background': 'backgrounds/creature.png',
        'vips_methods': {
            'rot90': {},
        }
    }
}

# constants
COLOR_DEFS_DIR = 'data/raw/colors.json'
COLOR_PREFIXES = ('i', 'c', 'h')
UNDEFINED_COLOR = 'undefined'
ZWSP = '\u200b'
THIN_SPACE = '\u2009'
APOSTROPHE = '\u0301'  # '\u00B4'  # '\u02BC'
VOWELS = ('A', 'E', 'I', 'O', 'U', 'Y')
NO_BREAKS_BEFORE = (*VOWELS, ' ', None)


def context_loop(text):
    '''
    Loop through a list with previous and upcoming values
    '''
    text = list(text)

    offsets = \
        [None] + text[:-1],\
        text,\
        text[1:] + [None],\
        text[2:] + [None, None]

    return list(zip(*offsets))  # TODO: verify list is required


def shorten_text(text):
    '''
    Prepare text for measuring length without added special characters
    '''
    # removing uninformative prefixes
    text = re.sub(r'^(A|a|The|pair of)\s', '', text)
    # removing states in parentheses
    text = re.sub(r'\([^\(]\)$', '', text)
    # & is special in Pango text layout engine
    text = text.replace('&', '|')

    return text


def add_textbreaks(text, start=6):
    '''
    Workaround absense of pango.WRAP_CHAR support in pyvips
    by adding zero-width spaces after defined index
    where it's appropriate to break a word,
    replace some characters with similar-looking but thinner ones.
    '''
    result = text[:start]

    for prev1, character, next1, next2 in context_loop(text[start:]):
        if character == ' ':
            # U+200A HAIR SPACE is too thin in some cases
            result += THIN_SPACE
        elif character == '\'':
            # accent is close enough but doesn't require horizontal space
            result += APOSTROPHE
        elif character == character.upper() or prev1 == ' ':
            # do not break off one character.
            # TODO: verify it's not covered by the NO_BREAKS_BEFORE check
            result += character
        else:
            if next1 in NO_BREAKS_BEFORE or next2 in NO_BREAKS_BEFORE:
                result += character
            else:
                result += character + ZWSP

    return result


def convert_color_name_from_defs(name):
    '''
    Make color names from the Cataclysm-DDA/data/raw/ definitions
    look closer to Cataclysm-DDA/data/json/ field values.
    '''
    new_name = re.sub('^L', 'light', name)
    new_name = re.sub('^D', 'dark', new_name)

    return new_name.lower()


def load_color_defs(filepath):
    '''
    Load default color definitions from CDDA
    '''
    with open(filepath) as fh:
        color_defs = json.load(fh)[0]

    output = {  # these are not defined explicitly in the game files
        'lightgray': LIGHT_GRAY,
        'pink': PINK,
    }
    for color_name, value in color_defs.items():
        if color_name == 'type':
            continue
        output[convert_color_name_from_defs(color_name)] = value

    return output


def colors_from_field(value):
    '''
    Convert compound color from Cataclysm-DDA/data/json/ field value
    to a tuple of two colors, dropping prefixes.
    TODO: re-evaluate prefixes role.
    '''
    # removing underlines between parts of one color
    value = re.sub(r'(light|dark)_', '\\1', value)
    # split colors, removing prefixes
    value = [p for p in value.split('_') if p not in COLOR_PREFIXES]

    color_fg = value.pop(0)
    if value:
        color_bg = value.pop(0)
        assert not value  # there should be no more than 2 colors
    else:
        color_bg = UNDEFINED_COLOR
    return (color_fg, color_bg)


def output(type_, id_, text, color_fg, color_bg, dir_tree=True):
    '''
    Create directory structure, generate and write files.
    '''
    # get type settings
    if type_ in TYPES:
        type_settings = TYPES[type_]
    else:
        type_settings = TYPES['default']

    canvas_dimensions = type_settings['canvas_dimensions']
    text_box = type_settings['text_box']
    font_size = type_settings['font_size']
    text_gravity = type_settings['text_gravity']
    canvas_gravity = type_settings['canvas_gravity']
    background = type_settings.get('background')  # FIXME: use
    vips_methods = type_settings.get('vips_methods', {})

    # setup output directory
    size_dir = 'tff_' + 'x'.join(map(str, canvas_dimensions))

    if dir_tree:
        dirpath = Path(os.path.join(size_dir, type_, id_))
        dirpath.mkdir(parents=True, exist_ok=True)
    else:
        dirpath = Path(DIR)

    filepath_json = os.path.join(dirpath, f'{id_}.json')
    filepath_png = os.path.join(dirpath, f'{id_}.png')

    # write JSON
    with open(filepath_json, 'w') as fp:
        json_dict = [{'id': id_, 'fg': id_, 'bg': ''}]
        json.dump(json_dict, fp, **JSON_DUMP_ARGS)

    # prepare text
    text = shorten_text(text)
    if len(text) > 4:
        text = add_textbreaks(text, 4)

    # render colored text image
    original_text = pyvips.Image.text(
        text, font=f'{FONT} {font_size}',
        dpi=72, **text_box)[0]  # autofit_dpi=True)[0]
    boxed_text = original_text.copy(interpretation='srgb')\
        .gravity(text_gravity, *text_box.values())
    text_color = boxed_text.new_from_image(color_fg)
    text_image = text_color.bandjoin(boxed_text)

    # render shadow
    shadow_image = render_shadow(boxed_text, color_fg, color_bg)

    # add shadow to the text image
    final = text_image.composite2(
        shadow_image, SHADOW_BLEND_MODE, **SHADOW_OFFSET)

    # per-type operations
    for method, method_arguments in vips_methods.items():
        final = getattr(final, method)(**method_arguments)

    final = final.gravity(canvas_gravity, *canvas_dimensions)

    final.write_to_file(filepath_png)


def render_shadow(text, color_fg, color_bg, method='mostly_black', blur=0.5):
    '''
    Generate a shadow image from a copy of rendered text image
    '''
    shadow = text.copy()

    if method == 'mostly_black':
        brightness = sum(color_fg) / 3
        if brightness > 32:
            bg_color = [0, 0, 0]
        else:
            bg_color = [255, 255, 255]
        shadow_color = shadow.new_from_image(bg_color)

    elif method == 'invert_all':
        shadow_color = shadow.new_from_image(color_fg)\
            .colourspace('b-w')\
            .invert()\
            .colourspace('srgb')

    elif method == 'invert_undefined':
        if color_bg == UNDEFINED_COLOR:
            shadow_color = shadow.new_from_image(color_fg)\
                .colourspace('b-w')\
                .invert()\
                .colourspace('srgb')
        else:
            shadow_color = shadow.new_from_image(color_bg)

    return shadow_color.bandjoin(shadow).gaussblur(blur)


if __name__ == '__main__':
    color_defs_filepath = os.path.join(GAME_DIR, COLOR_DEFS_DIR)
    color_defs = load_color_defs(color_defs_filepath)

    input_filepath = sys.argv[1]
    with open(input_filepath) as fh:
        reader = csv.reader(fh)
        next(reader)  # skip header
        for row in reader:
            type_, id_, name, color, looks_like, copy_from = row
            color_fg, color_bg = colors_from_field(color or DEFAULT_COLOR)
            color_fg = color_defs[color_fg]
            color_bg = color_defs.get(color_bg, UNDEFINED_COLOR)
            if id_ and name:
                print(id_)
                output(type_.lower(), id_, name, color_fg, color_bg)
