from Xlib import X, XK
from constants import TARGET
from clipboard import copy


pressed_keys = set()

events = []

def event_to_string(self, event, char):
    mods = []
    if event.state & X.ShiftMask:
        mods.append('Shift')

    if event.state & X.ControlMask:
        mods.append('Control')

    a =  ''.join(mod + '+' for mod in mods) + (char if char else '?')
    print(f'event_to_string: {a}')
    return a


def replay(self):
    pass


def determine_type_action(self, event):
    keycode = event.detail
    keysym = self.display.keycode_to_keysym(keycode, 0)
    char = XK.keysym_to_string(keysym)
    print(f'Зафиксировано нажатие или отпускание {char}')

    events.append(event)

    # если фиксируем нажатие то пока просто его добавляем
    if event.type == X.KeyPress and char:
        pressed_keys.add(event_to_string(self, event, char))
        return

    if event.type != X.KeyRelease:
        return

    # и только когда событие "отпускание клавиши", то продолжается работа
    is_process_keystrokes = False
    if len(pressed_keys) > 1:
        paste_style(self, pressed_keys)
        is_process_keystrokes = True
    elif len(pressed_keys) == 1:
        # Get the only element in pressed
        ev = next(iter(pressed_keys))
        is_process_keystrokes = handle_single_key(self, ev)

    # replay events to Inkscape if we couldn't handle them
    if not is_process_keystrokes:
        replay(self)

    events.clear()
    pressed_keys.clear()


def handle_single_key(self, ev):
    print('handle_single_key')
    if ev == 'w':
        # Pencil
        self.press_key('p')
    else:
        return False
    return True


def paste_style(self, combination):
    """
    This creates the style depending on the combination of keys.
    """
    print('paste_style')
    # Stolen from TikZ
    pt = 1.327 # pixels
    w = 0.4 * pt
    thick_width = 0.8 * pt
    very_thick_width = 1.2 * pt


    style = {
        'stroke-opacity': 1,
        'fill': 'white',
        'fill-opacity': 1
    }

    if 'n' in combination:
        style['fill'] = 'black'
        style['fill-opacity'] = 0.12

    if 'm' in combination:
        style['stroke'] = 'black'
        style['stroke-width'] = w
        style['marker-end'] = 'none'
        style['marker-start'] = 'none'
        style['stroke-dasharray'] = 'none'

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

    style_string = ';'.join('{}: {}'.format(key, value)
        for key, value in sorted(style.items(), key=lambda x: x[0])
    )

    svg += f'<inkscape:clipboard style="{style_string}" /></svg>'

    copy(svg, target=TARGET)

    self.press_key('v', X.ControlMask | X.ShiftMask)
