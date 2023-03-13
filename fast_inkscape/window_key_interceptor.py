import threading
from Xlib.display import Display
from Xlib import X, XK
from Xlib.protocol import event
from Xlib import error
from loguru import logger

from normal import replay_keys
from config import config


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

    def string_to_keycode(self, key: str) -> int:
        keysym = XK.string_to_keysym(key)
        keycode = self.display.keysym_to_keycode(keysym)
        return keycode

    def create_event(self, name_event, keycode, state_buttons):
        event = name_event(
            time=X.CurrentTime,
            root=self.root,
            window=self.window_resource,
            same_screen=0, child=X.NONE,
            root_x=0, root_y=0, event_x=0, event_y=0,
            state=state_buttons,
            detail=keycode
        )
        return event

    def press_key(self, key: str, mask=X.NONE):
        keycode = self.string_to_keycode(key)
        for type_event in [event.KeyPress, event.KeyRelease]:
            new_event = self.create_event(type_event, keycode, mask)
            self.window_resource.send_event(new_event, propagate=True)

    def grab_keys(self, grippable_keys: dict):
        logger.info('Захватываем клавиши')
        for key in list(grippable_keys.values()):
            self.window_resource.grab_key(
                key, X.AnyModifier, True, X.GrabModeAsync, X.GrabModeAsync
            )
            logger.info(f"Захватили клавишу {key}")
        self.window_resource.change_attributes(
            event_mask=X.KeyReleaseMask | X.KeyPressMask | X.StructureNotifyMask
        )

    def ungrab_keys(self):
        self.window_resource.ungrab_key(X.AnyKey, X.AnyModifier)

    def start_intercepting(self):
        logger.success('Активируем захват')
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
                logger.info(f"Получилось {key}")
                # click_events.clear()
                # self.press_key(key, mask)
                # self.display.flush()
                # self.display.sync()

            if type_event == X.DestroyNotify:
                if id_event == self.window_id:
                    logger.info('Окно закрыли. Выполнение скрипта завершено.')
                    logger.info('------------------------------------------')
                    self.ungrab_keys()
                    return


def get_window_id(root, name_window: str) -> int | None:
    for window in root.query_tree().children:
        data_window = window.get_wm_class()
        if (data_window and name_window in data_window[0]):
            return window.id
    return None


def search_window(name_window: str) -> int | None:
    display = Display()
    screen = display.screen()
    root = screen.root
    logger.info("Начинаем поиск окна")
    window_id = get_window_id(root, name_window)
    logger.info(f"window_id: {window_id}")
    if window_id:
        logger.info("Окно найдено (было уже создано)")
        return window_id

    root.change_attributes(event_mask=X.SubstructureNotifyMask)
    while True:
        logger.info("Окно не было создано, ждем... запуска)")
        next_event = display.next_event()
        if next_event.type == X.CreateNotify:
            window = next_event.window
            try:
                window_id = get_window_id(window, name_window)
                if window_id:
                    logger.info("Окно найдено (только что создано)")
                    return window_id
            except error.BadWindow:
                return None


def run_window_key_interception(name_window: str):
    window_id = search_window(name_window)
    if window_id:
        interceptor_key = WindowKeyInterceptor(window_id)
        interceptor_key.start_intercepting()
    else:
        logger.warning("Не удалось запустить перехватчик клавиш окна")
