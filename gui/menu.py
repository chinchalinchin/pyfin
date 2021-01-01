import sys
import random
from PySide6 import QtCore, QtWidgets, QtGui

from gui.functions import RiskProfileWidget

WIDGET_ORDER = ["RiskProfile"]
# DESIGN: menu widget holds other widgets. when you click the function button,
# it will hide the menu widget and show the function widget. a button on 
# the function widget will cause the function widget to hide and the menu
# widget to redisplay
class MenuWidget(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()
        self.title = QtWidgets.QLabel("Pynance", alignment=QtCore.Qt.AlignTop)

        self.back_button = QtWidgets.QPushButton("Menu")
        self.back_button.hide()

        self.widget_buttons = [ QtWidgets.QPushButton("Risk-Profile") ]

        # Function Widgets
        self.function_widgets = [ RiskProfileWidget() ]

        self.layout = QtWidgets.QVBoxLayout()

        self.layout.addWidget(self.title)
    
        for button in self.widget_buttons:
            this_widget = self.widget_buttons.index(button)
            button.clicked.connect(lambda args = this_widget: self.show_widget(args))
            button.show()
            self.layout.addWidget(button)

        for widget in self.function_widgets:
            widget.hide()
            self.layout.addWidget(widget)

        self.layout.addWidget(self.back_button)

        self.setLayout(self.layout)
        
        self.back_button.clicked.connect(self.clear)

    @QtCore.Slot()
    def show_widget(self, this_widget):
        print('clicked')

        for button in self.widget_buttons:
            button.hide()

        self.back_button.show()
        
        self.function_widgets[this_widget].show()

    @QtCore.Slot()
    def clear(self):
        for widget in self.function_widgets:
            widget.hide()
        for button in self.widget_buttons:
            button.show()
        self.back_button.hide()

if __name__ == "__main__":
    app = QtWidgets.QApplication([])

    widget = MenuWidget()
    widget.resize(800, 600)
    widget.show()

    sys.exit(app.exec_())