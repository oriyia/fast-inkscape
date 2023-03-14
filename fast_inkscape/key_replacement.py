from Xlib import X, XK
from Xlib.protocol import event
from loguru import logger
from pathlib import Path

from constants import TARGET
from terminal_tool_box import copy_file, copy_text, enter_text_in_editor, save_image_pdf_extension, paste_object, save_object

def get_symbols_events(self, events: list) -> set:
    key_mods = []
    pressed_keys = set()
    for event in events:
        keycode = event.detail
        keysym = self.display.keycode_to_keysym(keycode, 0)
        symbol = XK.keysym_to_string(keysym)
        logger.info(f"Keycode {keycode}")
        if event.state & X.ShiftMask:
            key_mods.append('Shift')
        if event.state & X.ControlMask:
            key_mods.append('Control')
        symbols_event =  ''.join(mod + '+' for mod in key_mods) + (symbol if symbol else '?')
        logger.info(f"Зафиксировано {symbols_event}")
        pressed_keys.add(symbols_event)
    return pressed_keys


@logger.catch
def replace_events(self, press_release_events: list, press_events: list, path_name_image: Path) -> list:
    symbols = get_symbols_events(self, press_events)
    if len(symbols) > 1:
        new_events = paste_style(self, symbols)
    elif len(symbols) == 1:
        new_events =  handle_single_key(self, symbols, press_release_events, path_name_image)
    else:
        new_events = press_release_events
    return new_events


# def replace_events(self, press_release_events: list, press_events) -> tuple[str, int]:
#     symbols = get_symbols_events(self, press_events)
#     if len(symbols) > 1:
#         new_symbol, mask = paste_style(self, symbols)
#     elif len(symbols) == 1:
#         new_symbol, mask =  handle_single_key(self, symbols, press_release_events)
#     else:
#         new_symbol = 'c'
#         mask = X.NONE
#     return new_symbol, mask
#
#
def handle_single_key(self, symbols: set, events: list, path_name_image: Path) -> list:
    logger.info('Активируем инструмент')
    if 'w' in symbols:
        # Pencil
        return self.create_events('p', X.NONE)
    elif 'x' in symbols:
        # Прилипание
        return self.create_events('percent', X.ShiftMask)
    elif 'f' in symbols:
        enter_text_in_editor()
        return self.create_events('s', X.NONE)
    elif 'a' in symbols:
        # paste object
        result = paste_object()
        if result == 0:
            return self.create_events('v', X.ControlMask)
        else:
            return self.create_events('s', X.NONE)
    elif 'v' in symbols:
        # save object
        save_object(self)
        return self.create_events('s', X.NONE)
    elif 'g' in symbols:
        # Сохранить изображение
        save_image_pdf_extension(path_name_image)
        return self.create_events('s', X.ControlMask)
    elif 'z' in symbols:
        # Delete
        return self.create_events('Delete', X.NONE)
    else:
        logger.info('Ниодно событие не совпало, отправляем как есть')
        return events


def paste_style(self, symbols) -> list:
    """
    This creates the style depending on the symbols of keys.
    """
    # Stolen from TikZ
    pt = 2.3225 # pixels
    w = 0.4 * pt
    thick_width = 0.68 * pt
    very_thick_width = 0.895 * pt


    style = {
        'fill': 'none',
        'fill-opacity': 1,
        'stroke': 'black',
        'stroke-opacity': 1,
        'stroke-width': w,
        'stroke-dasharray': 'none',
        'marker-end': 'none',
        'marker-start': 'none',
        'paint-order': 'markers fill stroke',
    }

    if 'a' in symbols:
        style['stroke-dasharray'] = 'none'

    if 's' in symbols:
        style['stroke-dasharray'] = f'{w}, {2*pt}'

    if 'd' in symbols:
        style['stroke-dasharray'] = f'{3*pt}, {3*pt}'

    if 'x' in symbols:
        w = thick_width
        style['stroke-width'] = w

    if 'c' in symbols:
        w = very_thick_width
        style['stroke-width'] = w

    if 'f' in symbols:
        style['fill'] = '#e1edff'

    if 'q' in symbols:
        style['stroke-dasharray'] = 'none'
        style['marker-end'] = f'url(#marker-arrow-{w})'

    if 'w' in symbols:
        style['stroke-dasharray'] = f'{w},{2*pt}'
        style['marker-end'] = f'url(#marker-arrow-{w})'

    if 'e' in symbols:
        style['stroke-dasharray'] = f'{3*pt},{3*pt}'
        style['marker-end'] = f'url(#marker-arrow-{w})'

    if 'r' in symbols:
        style['marker-start'] = f'url(#marker-arrow-{w})'

    svg = '''
          <?xml version="1.0" encoding="UTF-8" standalone="no"?>
          <svg>
          '''

    if ('marker-end' in style and style['marker-end'] != 'none') or \
            ('marker-start' in style and style['marker-start'] != 'none'):
        svg += f'''
                <defs id="marker-defs">
                <marker
                id="marker-arrow-{w}"
                orient="auto-start-reverse"
                refY="0" refX="0"
                markerHeight="1.690" markerWidth="0.911">
                  <g transform="scale({(2.40 * w + 3.87)/(4.5*w)})">
                    <path
                       d="M -1.55415,2.0722 C -1.42464,1.29512 0,0.1295 0.38852,0 0,-0.1295 -1.42464,-1.29512 -1.55415,-2.0722"
                       style="fill:none;stroke:#000000;stroke-width:{0.6};stroke-linecap:round;stroke-linejoin:round;stroke-miterlimit:10;stroke-dasharray:none;stroke-opacity:1"
                       inkscape:connector-curvature="0" />
                   </g>
                </marker>
                </defs>
                '''

    style_string = ';'.join('{}:{}'.format(key, value)
        for key, value in sorted(style.items(), key=lambda x: x[0])
    )
    logger.info(f"{style_string}")

    svg += f'<inkscape:clipboard style="{style_string}" /></svg>'

    copy_text(svg, target=TARGET)
    logger.info('Вставляем стиль')
    return self.create_events('v', X.ControlMask | X.ShiftMask)
