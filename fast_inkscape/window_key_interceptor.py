#!/usr/bin/python3
import threading
from Xlib.display import Display
from Xlib import X, XK
from Xlib.protocol import event
from Xlib import error

from normal import replay_keys


# перехватывает нажатия, взамен отправляет свои нажатия
class WindowKeyInterceptor:
    def __init__(self, window_id):
        self.window_id = window_id
        self.display = Display()
        self.screen = self.display.screen()
        self.root = self.screen.root

        self.window_resource = self.display.create_resource_object('window', window_id)
        self.grippable_keys = {
            'n': 57, 'm': 58, 'Shift_R': 108, 'w': 25, 't': 28, 'a': 38,
        }

    def string_to_keycode(self, key) -> int:
        keysym = XK.string_to_keysym(key)
        keycode = self.display.keysym_to_keycode(keysym)
        return keycode

    def create_event(self, name_event, keycode, state_buttons):
        event =  name_event(
            time=X.CurrentTime,
            root=self.root,
            window=self.window_resource,
            same_screen=0, child=X.NONE,
            root_x=0, root_y=0, event_x=0, event_y=0,
            state=state_buttons,
            detail=keycode
        )
        return event

    def press_key(self, key, mask=X.NONE) -> None:
        keycode = self.string_to_keycode(key)
        for type_event in [event.KeyPress, event.KeyRelease]:
            new_event = self.create_event(type_event, keycode, mask)
            self.window_resource.send_event(new_event, propagate=True)

    def grab_keys(self, grippable_keys):
        print('Захватываем клавиши')
        for key in list(grippable_keys.values()):
            self.window_resource.grab_key(
                key, X.AnyModifier, True, X.GrabModeAsync, X.GrabModeAsync
            )
        self.window_resource.change_attributes(
            event_mask=X.KeyReleaseMask | X.KeyPressMask | X.StructureNotifyMask
        )

    def ungrab_keys(self):
        self.window_resource.ungrab_key(X.AnyKey, X.AnyModifier)

    def start_intercepting(self):
        self.grab_keys(self.grippable_keys)
        click_events = []
        while True:
            next_event = self.display.next_event()
            type_event = next_event.type
            id_event = next_event.window.id

            if type_event == X.KeyPress:
                click_events.append(next_event)

            # как только первое отпускание клавиши делаем подмену
            if type_event == X.KeyRelease and click_events:
                self.display.allow_events(X.ReplayKeyboard, X.CurrentTime)
                key, mask = replay_keys(self, click_events)
                click_events.clear()
                self.press_key(key, mask)
                self.display.flush()
                self.display.sync()

            if type_event == X.DestroyNotify:
                if id_event == self.window_id:
                    self.ungrab_keys()
                    return


def create_thread_manager(name_function, args_function):
    thread = threading.Thread(
        target=name_function,
        args=args_function
    )
    thread.start()


def check_name_window(window, desired_name_window) -> bool:
    data_window = window.get_wm_class()
    if (data_window and desired_name_window in data_window[0]):
        return True
    else:
        return False


def is_window_exists(root, name_window) -> int | None:
    for window in root.query_tree().children:
        if check_name_window(window, name_window):
            return window.id
    return None


def search_window(name_window) -> int:
    display = Display()
    screen = display.screen()
    root = screen.root
    window_id = is_window_exists(root, name_window)
    if window_id:
        return window_id

    root.change_attributes(event_mask=X.SubstructureNotifyMask | X.KeyPressMask)
    while True:
        next_event = display.next_event()
        if next_event.type == X.CreateNotify:
            window = next_event.window
            try:
                window_id = is_window_exists(window, name_window)
                if window_id:
                    return window_id
            except error.BadWindow:
                pass


def main():
    desired_name_window = 'inkscape'
    while True:
        print("Начинаем поиск окна -----------------------------------------")
        window_id = search_window(desired_name_window)
        if window_id:
            print('Окно найдено, активируем захват')
            # create_thread_manager(create_window_manager, [window_id, desired_events])
            interceptor = WindowKeyInterceptor(window_id)
            interceptor.start_intercepting()
            print('Окно закрыто')


if __name__ == '__main__':
    main()
