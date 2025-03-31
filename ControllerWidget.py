from pyqtgraph import LayoutWidget, JoystickButton
from PyQt5.QtWidgets import QLabel, QComboBox, QCheckBox

class ControllerWidget(LayoutWidget):
    def __init__(self, main):
        super().__init__()
        from GloveboxWindow import GloveboxWindow # for autocomplete
        self.main:GloveboxWindow = main
        self.controller = self.main.devices.controller
        self.stage = self.main.devices.stage
        self.objective = self.main.devices.objective
        self.filterWheel = self.main.devices.filterWheel
        self.camera = self.main.devices.camera
        self.shutter = self.main.devices.shutter
        
    def createGUI(self):
        self.addWidget(QLabel('Joystick for XY stage'), 0, 0)
        
        self.focusJoystickCombobox = QComboBox()
        self.focusJoystickCombobox.addItem('Joystick for Z Stage')
        self.focusJoystickCombobox.addItem('Joystick for MCM Stage')
        self.focusJoystickCombobox.currentIndexChanged.connect(self.swapJoystickZFunction)
        self.addWidget(self.focusJoystickCombobox, 0, 1) 
        
        self.leftScreenJoystick = JoystickButton()
        self.leftScreenJoystick.setFixedSize(30, 30)
        self.addWidget(self.leftScreenJoystick, 1, 0)
        
        self.rightScreenJoystick = JoystickButton()
        self.rightScreenJoystick.setFixedSize(30, 30)
        self.addWidget(self.rightScreenJoystick, 1, 1)
        
        useKeyboardCheckbox = QCheckBox('Use Keyboard')
        useKeyboardCheckbox.stateChanged.connect(self.controller.setKeyboardEnabled)
        self.controller.keyboardModeChangedSignal.connect(useKeyboardCheckbox.setChecked)
        self.addWidget(useKeyboardCheckbox, 2, 0)

        useJoystickCheckbox = QCheckBox('Use Controller')
        useJoystickCheckbox.setChecked(True)
        useJoystickCheckbox.stateChanged.connect(self.controller.setJoystickEnabled)
        self.controller.joystickModeChangedSignal.connect(useJoystickCheckbox.setChecked)
        self.addWidget(useJoystickCheckbox, 2, 1)

        self.setControllerFunctions()

    def swapJoystickZFunction(self, i:int):
        if i == 0: self.controller.set_right_stick_vertical_axis_function(lambda value: self.stage.setZ(value * self.stage.getNormalizedZSpeed(self.main.secPerTick), True))
        else: self.controller.set_right_stick_vertical_axis_function(lambda value: self.objective.setZ(value * 0.05, True))

    def setControllerFunctions(self):
        self.controller.set_left_stick_horizontal_axis_virtual_axis_function(lambda: self.leftScreenJoystick.getState()[0])
        self.controller.set_left_stick_vertical_axis_virtual_axis_function(lambda: self.leftScreenJoystick.getState()[1])
        self.controller.set_right_stick_horizontal_axis_virtual_axis_function(lambda: self.rightScreenJoystick.getState()[0])
        self.controller.set_right_stick_vertical_axis_virtual_axis_function(lambda: self.rightScreenJoystick.getState()[1])
        # self.controller.set_left_trigger_axis_virtual_axis_function()
        # self.controller.set_right_trigger_axis_virtual_axis_function()

        self.controller.set_left_stick_horizontal_axis_function(lambda value: self.stage.setX(-value * self.stage.getNormalizedXYSpeed(self.main.secPerTick), True))
        self.controller.set_left_stick_vertical_axis_function(lambda value: self.stage.setY(value * self.stage.getNormalizedXYSpeed(self.main.secPerTick), True))
        # self.controller.set_right_stick_horizontal_axis_function()
        self.controller.set_right_stick_vertical_axis_function(lambda value: self.stage.setZ(value * self.stage.getNormalizedZSpeed(self.main.secPerTick), True))
        # self.controller.set_left_trigger_axis_virtual_axis_function()
        # self.controller.set_right_trigger_axis_virtual_axis_function()

        # self.controller.set_cross_button_function(self.capture) # TODO
        self.controller.set_circle_button_function(lambda: self.camera.setSlider('PL' if self.camera.getSlider() == 'WL' else 'WL'))
        self.controller.set_square_button_function(lambda: self.filterWheel.setFilter(1 if self.filterWheel.getFilter() == 4 else 4))
        self.controller.set_triangle_button_function(lambda: self.shutter.setOpen(not self.shutter.getOpen()))
        self.controller.set_left_bumper_button_function(lambda: self.objective.setObjective(self.objective.objectives[(self.objective.objectives.index(self.objective.objective) - 1) % len(self.objective.objectives)]))
        self.controller.set_right_bumper_button_function(lambda: self.objective.setObjective(self.objective.objectives[(self.objective.objectives.index(self.objective.objective) + 1) % len(self.objective.objectives)]))
        self.controller.set_left_trigger_button_function(lambda: self.objective.setZ(0.05, True))
        self.controller.set_right_trigger_button_function(lambda: self.objective.setZ(-0.05, True))
        # self.controller.set_share_button_function()
        self.controller.set_options_button_function(lambda: None if self.main.ScanWidget.plane is None else self.stage.setZ(self.main.ScanWidget.calcZ(self.stage.getX(), self.stage.getY(), self.main.ScanWidget.plane)))
        self.controller.set_left_stick_button_function(self.main.StageControlWidget.fastModeCheckbox.toggle)
        self.controller.set_right_stick_button_function(self.main.StageControlWidget.slowModeCheckbox.toggle)
        # self.controller.set_ps_button_function()
        # self.controller.set_touch_pad_button_function()

        self.controller.set_horizontal_hat_function(lambda val: self.stage.setXYSpeed(val, True))
        self.controller.set_vertical_hat_function(lambda val: self.stage.setZSpeed(val, True))

    def eventLoop(self):
        self.controller.eventLoop()

if __name__ == '__main__': import Glovebox