import pygame
import keyboard

class PS4Controller:
    def __init__(self):
        pygame.init()
        pygame.joystick.init()
        if pygame.joystick.get_count() > 0:
            self.joystick = pygame.joystick.Joystick(0)
            self.joystick.init()
            self.joystick_mode = True
            self.joystick_connected = True
            self.keyboard_mode = False
        else:
            self.joystick_mode = False
            self.joystick_connected = False
            self.keyboard_mode = True

        self.axes_enabled = True
        self.buttons_enabled = True
        self.hats_enabled = True

        self.inputs = []

        # pygame v1
        # Axes
        self.left_stick_horizontal_axis = self.Axis(self, 0, posKeys='d', negKeys='a', posExclKeys='shift', negExclKeys='shift')
        self.left_stick_vertical_axis = self.Axis(self, 1, posKeys='w', negKeys='s', posExclKeys='shift', negExclKeys='shift')
        self.right_stick_horizontal_axis = self.Axis(self, 2, posKeys='l', negKeys='j', posExclKeys='shift', negExclKeys='shift')
        self.right_stick_vertical_axis = self.Axis(self, 3, posKeys='i', negKeys='k', posExclKeys='shift', negExclKeys='shift')
        self.left_trigger_axis = self.Axis(self, 5) # keyboard button same as left_trigger_button
        self.right_trigger_axis = self.Axis(self, 4) # keyboard button same as right_trigger_button

        # Buttons
        self.cross_button = self.Button(self, 0, keys=['shift', 'k'])
        self.circle_button = self.Button(self, 1, keys=['shift', 'l'])
        self.square_button = self.Button(self, 2, keys=['shift', 'j'])
        self.triangle_button = self.Button(self, 3, keys=['shift', 'i'])
        self.left_bumper_button = self.Button(self, 4, keys='q')
        self.right_bumper_button = self.Button(self, 5, keys='e')
        self.left_trigger_button = self.Button(self, 6, keys='u')
        self.right_trigger_button = self.Button(self, 7, keys='o')
        self.share_button = self.Button(self, 8, keys='r')
        self.options_button = self.Button(self, 9, keys='y')
        self.left_stick_button = self.Button(self, 10, keys='x')
        self.right_stick_button = self.Button(self, 11, keys='m')
        self.ps_button = self.Button(self, 12, keys='b')
        self.touch_pad_button = self.Button(self, 13, keys=' ')

        # Hat/D-Pad
        self.horizontal_hat = self.Hat(self, 0, posKeys=['shift', 'd'], negKeys=['shift', 'a'])
        self.vertical_hat = self.Hat(self, 1, posKeys=['shift', 'w'], negKeys=['shift', 's'])
        
    def setAxesEnabled(self, enabled:bool): self.axes_enabled = bool(enabled)
    def setButtonsEnabled(self, enabled:bool): self.buttons_enabled = bool(enabled)
    def setHatsEnabled(self, enabled:bool): self.hats_enabled = bool(enabled)
    def setEnabled(self, enabled:bool):
        self.setAxesEnabled(enabled)
        self.setButtonsEnabled(enabled)
        self.setHatsEnabled(enabled)
    
    def setKeyboardMode(self, enabled:bool): self.keyboard_mode = bool(enabled)
    def setJoystickMode(self, enabled:bool): self.joystick_mode = bool(enabled)

    def close(self): pygame.quit()
        
    def eventLoop(self):
        for event in pygame.event.get():
            pass
        if pygame.joystick.get_count() > 0: self.joystick_connected = True
        else: self.joystick_connected = False
        for input in self.inputs: input.eventLoop()

    class Axis:
        def __init__(self, controller, index:int, posKeys=None, negKeys=None, posExclKeys=None, negExclKeys=None):
            self.controller = controller
            self.index = index
            controller.inputs.append(self)
            self.func = lambda val: None
            self.setPositiveKeys(posKeys, posExclKeys)
            self.setNegativeKeys(negKeys, negExclKeys)
            self.virtual_axis_function = lambda: 0
            self.threshold = 0.1
        
        def setFunction(self, func):
            self.func = func

        def setThreshold(self, threshold:float):
            self.threshold = threshold

        def setVirutalAxisFunction(self, func):
            self.virtual_axis_function = func

        def setPositiveKeys(self, keys=None, exclKeys=None):
            self.posKeys = [keys] if isinstance(keys, str) else keys
            self.posExclKeys = [exclKeys] if isinstance(exclKeys, str) else exclKeys

        def setNegativeKeys(self, keys=None, exclKeys=None):
            self.negKeys = [keys] if isinstance(keys, str) else keys
            self.negExclKeys = [exclKeys] if isinstance(exclKeys, str) else exclKeys

        def eventLoop(self):
            if self.controller.axes_enabled:
                if self.controller.joystick_connected and self.controller.joystick_mode:
                    value = self.controller.joystick.get_axis(self.index)
                    if abs(value) > self.threshold: self.func(value)
                if self.controller.keyboard_mode:
                    value = self.virtual_axis_function()
                    if abs(value) > self.threshold: self.func(value)
                    elif self.posKeys is not None and all(keyboard.is_pressed(key) for key in self.posKeys) and (self.posExclKeys is None or not any(keyboard.is_pressed(key) for key in self.posExclKeys)): self.func(1)
                    elif self.negKeys is not None and all(keyboard.is_pressed(key) for key in self.negKeys) and (self.negExclKeys is None or not any(keyboard.is_pressed(key) for key in self.negExclKeys)): self.func(-1)

    class Button:
        def __init__(self, controller, index:int, keys=None, exclKeys=None):
            self.controller = controller
            self.index = index
            controller.inputs.append(self)
            self.func = lambda: None
            self.setKeys(keys, exclKeys)
        
        def setFunction(self, func):
            self.func = func

        def setKeys(self, keys=None, exclKeys=None):
            self.keys = [keys] if isinstance(keys, str) else keys
            self.exclKeys = [exclKeys] if isinstance(exclKeys, str) else exclKeys

        def eventLoop(self):
            if self.controller.buttons_enabled:
                if (self.controller.joystick_connected and self.controller.joystick_mode and self.controller.joystick.get_button(self.index)) or (self.controller.keyboard_mode and self.keys is not None and all(keyboard.is_pressed(key) for key in self.keys) and (self.exclKeys is None or not any(keyboard.is_pressed(key) for key in self.exclKeys))):
                    self.func()

    class Hat:
        def __init__(self, controller, index:int, posKeys=None, negKeys=None, posExclKeys=None, negExclKeys=None):
            self.controller = controller
            self.index = index
            controller.inputs.append(self)
            self.func = lambda val: None
            self.setPositiveKeys(posKeys, posExclKeys)
            self.setNegativeKeys(negKeys, negExclKeys)
        
        def setFunction(self, func):
            self.func = func

        def setPositiveKeys(self, keys=None, exclKeys=None):
            self.posKeys = [keys] if isinstance(keys, str) else keys
            self.posExclKeys = [exclKeys] if isinstance(exclKeys, str) else exclKeys

        def setNegativeKeys(self, keys=None, exclKeys=None):
            self.negKeys = [keys] if isinstance(keys, str) else keys
            self.negExclKeys = [exclKeys] if isinstance(exclKeys, str) else exclKeys

        def eventLoop(self):
            if self.controller.hats_enabled:
                if self.controller.joystick_connected and self.controller.joystick_mode:
                    value = self.controller.joystick.get_hat(0)[self.index]
                    if value != 0: self.func(value)
                if self.controller.keyboard_mode:
                    if self.posKeys is not None and all(keyboard.is_pressed(key) for key in self.posKeys) and (self.posExclKeys is None or not any(keyboard.is_pressed(key) for key in self.posExclKeys)): self.func(1)
                    elif self.negKeys is not None and all(keyboard.is_pressed(key) for key in self.negKeys) and (self.negExclKeys is None or not any(keyboard.is_pressed(key) for key in self.negExclKeys)): self.func(-1)


if __name__ == '__main__':
    import time
    c = PS4Controller()

    c.left_stick_horizontal_axis.setFunction(lambda val: print('left_stick_horizontal_axis', val))
    c.left_stick_vertical_axis.setFunction(lambda val: print('left_stick_vertical_axis', val))
    c.right_stick_horizontal_axis.setFunction(lambda val: print('right_stick_horizontal_axis', val))
    c.right_stick_vertical_axis.setFunction(lambda val: print('right_stick_vertical_axis', val))
    c.left_trigger_axis.setFunction(lambda val: print('left_trigger_axis', val))
    c.right_trigger_axis.setFunction(lambda val: print('right_trigger_axis', val))

    c.cross_button.setFunction(lambda: print('cross_button'))
    c.circle_button.setFunction(lambda: print('circle_button'))
    c.square_button.setFunction(lambda: print('square_button'))
    c.triangle_button.setFunction(lambda: print('triangle_button'))
    c.left_bumper_button.setFunction(lambda: print('left_bumper_button'))
    c.right_bumper_button.setFunction(lambda: print('right_bumper_button'))
    c.left_trigger_button.setFunction(lambda: print('left_trigger_button'))
    c.right_trigger_button.setFunction(lambda: print('right_trigger_button'))
    c.share_button.setFunction(lambda: print('share_button'))
    c.options_button.setFunction(lambda: print('options_button'))
    c.left_stick_button.setFunction(lambda: print('left_stick_button'))
    c.right_stick_button.setFunction(lambda: print('right_stick_button'))
    c.ps_button.setFunction(lambda: print('ps_button'))
    c.touch_pad_button.setFunction(lambda: print('touch_pad_button'))

    c.horizontal_hat.setFunction(lambda val: print('horizontal_hat', val))
    c.vertical_hat.setFunction(lambda val: print('vertical_hat', val))

    while time.perf_counter() < 30:
        c.eventLoop()
        time.sleep(0.05)

    c.close()