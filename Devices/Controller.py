from PyQt5.QtWidgets import QWidget
from PyQt5.QtCore import pyqtSignal

class Controller(QWidget):
    joystickModeChangedSignal = pyqtSignal(bool)
    keyboardModeChangedSignal = pyqtSignal(bool)

    def __init__(self, virtual:bool):
        super().__init__()
        if virtual: from Scripts.PS4Controller.PS4Controller_v2 import PS4Controller
        else: 
            import sys
            sys.path.append(r'C:\Users\GloveBox\Documents\Python Scripts\PS4Controller')
            from PS4Controller_v2 import PS4Controller

        print('Connecting to PS4 Controller')
        self.controller = PS4Controller()
        print('PS4 Controller connected')

    def setJoystickEnabled(self, enabled:bool, useSave=False):
        enabled = bool(enabled)
        if useSave:
            if enabled: enabled = self.savedJoystickMode
            else: self.savedJoystickMode = self.controller.joystick_mode
        if self.controller.joystick_mode == enabled: return
        self.controller.setJoystickMode(enabled)
        self.joystickModeChangedSignal.emit(enabled)

    def setKeyboardEnabled(self, enabled:bool, useSave=False):
        enabled = bool(enabled)
        if useSave:
            if enabled: enabled = self.savedKeyboardMode
            else: self.savedKeyboardMode = self.controller.keyboard_mode
        if self.controller.keyboard_mode == enabled: return
        self.controller.setKeyboardMode(enabled)
        self.keyboardModeChangedSignal.emit(enabled)

    def setControllerEnabled(self, enabled, useSave=False):
        self.setJoystickEnabled(enabled, useSave)
        self.setKeyboardEnabled(enabled, useSave)

    def getKeyboardEnabled(self):
        return self.controller.keyboard_mode

    def getJoystickEnabled(self):
        return self.controller.joystick_mode

    def set_left_stick_horizontal_axis_virtual_axis_function(self, func): self.controller.left_stick_horizontal_axis.setVirutalAxisFunction(func)
    def set_left_stick_vertical_axis_virtual_axis_function(self, func): self.controller.left_stick_vertical_axis.setVirutalAxisFunction(func)
    def set_right_stick_horizontal_axis_virtual_axis_function(self, func): self.controller.right_stick_horizontal_axis.setVirutalAxisFunction(func)
    def set_right_stick_vertical_axis_virtual_axis_function(self, func): self.controller.right_stick_vertical_axis.setVirutalAxisFunction(func)
    def set_left_trigger_axis_virtual_axis_function(self, func): self.controller.left_trigger_axis.setVirutalAxisFunction(func)
    def set_right_trigger_axis_virtual_axis_function(self, func): self.controller.right_trigger_axis.setVirutalAxisFunction(func)

    def set_left_stick_horizontal_axis_function(self, func): self.controller.left_stick_horizontal_axis.setFunction(func)
    def set_left_stick_vertical_axis_function(self, func): self.controller.left_stick_vertical_axis.setFunction(func)
    def set_right_stick_horizontal_axis_function(self, func): self.controller.right_stick_horizontal_axis.setFunction(func)
    def set_right_stick_vertical_axis_function(self, func): self.controller.right_stick_vertical_axis.setFunction(func)
    def set_left_trigger_axis_function(self, func): self.controller.left_trigger_axis.setFunction(func)
    def set_right_trigger_axis_function(self, func): self.controller.right_trigger_axis.setFunction(func)
    def set_cross_button_function(self, func): self.controller.cross_button.setFunction(func)
    def set_circle_button_function(self, func): self.controller.circle_button.setFunction(func)
    def set_square_button_function(self, func): self.controller.square_button.setFunction(func)
    def set_triangle_button_function(self, func): self.controller.triangle_button.setFunction(func)
    def set_left_bumper_button_function(self, func): self.controller.left_bumper_button.setFunction(func)
    def set_right_bumper_button_function(self, func): self.controller.right_bumper_button.setFunction(func)
    def set_left_trigger_button_function(self, func): self.controller.left_trigger_button.setFunction(func)
    def set_right_trigger_button_function(self, func): self.controller.right_trigger_button.setFunction(func)
    def set_share_button_function(self, func): self.controller.share_button.setFunction(func)
    def set_options_button_function(self, func): self.controller.options_button.setFunction(func)
    def set_left_stick_button_function(self, func): self.controller.left_stick_button.setFunction(func)
    def set_right_stick_button_function(self, func): self.controller.right_stick_button.setFunction(func)
    def set_ps_button_function(self, func): self.controller.ps_button.setFunction(func)
    def set_touch_pad_button_function(self, func): self.controller.touch_pad_button.setFunction(func)
    def set_horizontal_hat_function(self, func): self.controller.horizontal_hat.setFunction(func)
    def set_vertical_hat_function(self, func): self.controller.vertical_hat.setFunction(func)

    def eventLoop(self):
        self.controller.eventLoop()

    def close(self): return self.controller.close()
