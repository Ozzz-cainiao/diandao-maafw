"""In-memory test controller. Never connects to or sends input to a real device."""
import numpy as np
from maa.controller import CustomController

class OfflineController(CustomController):
    def __init__(self, image=None):
        self.image = image if image is not None else np.zeros((1600, 720, 3), dtype=np.uint8)
        self.actions = []
        super().__init__()
    def connect(self): return True
    def request_uuid(self): return 'diandao-offline-test'
    def get_features(self): return 0
    def start_app(self, intent):
        self.actions.append(('launch', intent))
        return True
    def stop_app(self, intent): return False
    def screencap(self): return self.image
    def click(self, x, y):
        self.actions.append(('click', x, y))
        return True
    def click_key(self, keycode):
        self.actions.append(('key', keycode))
        return True
    def swipe(self, *args): return False
    def touch_down(self, *args): return False
    def touch_move(self, *args): return False
    def touch_up(self, *args): return False
    def input_text(self, *args): return False
    def key_down(self, *args): return False
    def key_up(self, *args): return False
