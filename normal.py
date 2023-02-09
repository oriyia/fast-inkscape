from Xlib import X, XK
import typing


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
    return True


def paste_style(self, combination):
    """
    This creates the style depending on the combination of keys.
    """
    # Stolen from TikZ
    # pt = 1.327 # pixels
    # w = 0.4 * pt
    # thick_width = 0.8 * pt
    # very_thick_width = 1.2 * pt
    #
    # # my_dict: Dict[str, Any] = {"data": n}
    # style: typing.Dict[str, Any] = {
    #     'stroke-opacity': 1,
    # }
    #
    # if 'n' in combination:
    #     style['fill'] = 'black'
    #     style['fill-opacity'] = 0.12
    #
    print('paste_style')
