#!/usr/bin/python3
import threading
import Xlib
from Xlib.display import Display
from Xlib import X, XK
from Xlib.protocol import event
from Xlib import error

from normal import determine_type_action


class WindowManager():
    def __init__(self, window_id):
        self.window_id = window_id
        self.display = Display()
        self.screen = self.display.screen()
        self.root = self.screen.root

        self.window_resource = self.display.create_resource_object('window', window_id)
        self.determine_type_action = determine_type_action
        self.list_grab_keys = [57, 58, 108]

    def create_event(self, name_class, keycode, state_buttons):
        return name_class(
            time=X.CurrentTime,
            root=self.root,
            window=self.window_resource,
            same_screen=0, child=X.NONE,
            root_x=0, root_y=0, event_x=0, event_y=0,
            state=state_buttons,
            detail=keycode
        )

    def press_key(self, key, mask=X.NONE):
        keycode = self.string_to_keycode(key)
        self.window_resource.send_event(
            self.create_event(event.KeyPress, keycode, mask),
            propagate=True
        )
        self.window_resource.send_event(
            self.create_event(event.KeyRelease, keycode, mask),
            propagate=True
        )
        self.display.flush()
        self.display.sync()

    def string_to_keycode(self, key):
        keysym = XK.string_to_keysym(key)
        keycode = self.display.keysym_to_keycode(keysym)
        return keycode

    def grab(self, list_grab_keys):
        print('Захватываем клавиши')
        for key in list_grab_keys:
            self.window_resource.grab_key(
                key, X.AnyModifier, True, X.GrabModeAsync, X.GrabModeAsync
            )
        # self.window_resource.ungrab_key(
        #     self.string_to_keycode('Super_L'), X.AnyModifier
        # )
        # self.window_resource.ungrab_key(
        #     self.string_to_keycode('Alt_L'), X.AnyModifier
        # )
        self.window_resource.change_attributes(
            event_mask=X.KeyReleaseMask | X.KeyPressMask | X.StructureNotifyMask
        )

    def ungrab(self):
        self.window_resource.ungrab_key(X.AnyKey, X.AnyModifier)

    def track_events(self, desired_events):
        self.grab(self.list_grab_keys)
        while True:
            next_event = self.display.next_event()
            type_event = next_event.type
            id_event = next_event.window.id

            if type_event in desired_events:
                self.display.allow_events(X.ReplayKeyboard, X.CurrentTime)
                self.determine_type_action(self, next_event)

            if type_event == X.DestroyNotify:
                if id_event == self.window_id:
                    self.ungrab()
                    return


def create_window_manager(window_id, desired_events):
    window_manager = WindowManager(window_id)
    window_manager.track_events(desired_events)


def create_thread_manager(name_function, args_function):
    thread = threading.Thread(
        target=name_function,
        args=args_function
    )
    thread.start()


def find_window(window, desired_name_window):
    data_window = window.get_wm_class()

    if (data_window and desired_name_window in data_window[0]):
        return True
    else:
        return False


def main():
    display = Display()
    screen = display.screen()
    root = screen.root

    desired_name_window = 'inkscape'
    desired_events = [X.KeyPress, X.KeyRelease]

    # работа скрипта, если окно inkscape уже создано
    for window in root.query_tree().children:
        result_find_window = find_window(window, desired_name_window)

        # если окно inkscape найдено, создаем поток для него
        if result_find_window:
            create_thread_manager(create_window_manager, [window.id, desired_events])

    # бесконечный цикл ждет когда будет событие CreateNotify (создание окна), и
    # если это окно inkscape, то скрипт начнет выполнять свою работу
    root.change_attributes(event_mask=X.SubstructureNotifyMask | X.KeyPressMask)
    while True:
        next_event = display.next_event()
        if next_event.type == X.CreateNotify:
            window = next_event.window
            try:
                result_find_window = find_window(window, desired_name_window)
                if result_find_window:
                    create_thread_manager(create_window_manager, [window.id, desired_events])
            except error.BadWindow:
                pass


if __name__ == '__main__':
    main()
