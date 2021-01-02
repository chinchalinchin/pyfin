from PyQt5 import QtGui, QtCore, QtWidgets

def get_title_font():
    font = QtGui.QFont('Arial', 12)
    font.setBold(True)
    font.setUnderline(True)
    return font

def get_subtitle_font():
    font = QtGui.QFont('Arial', 10)
    font.setItalic(True)
    font.setUnderline(True)
    return font

def get_msg_font():
    font = QtGui.QFont('Arial', 8)
    font.setItalic(True)
    return font

def get_result_font():
    font = QtGui.QFont('Arial', 8)
    font.setBold(True)
    return font

def get_label_font():
    font = QtGui.QFont('Arial', 8)
    font.setBold(True)
    return font

class PortfolioWidget(QtWidgets.QWidget):
    def __init__(self, widget_title, min_function, opt_function):
        super().__init__()
        self.title = QtWidgets.QLabel(widget_title, alignment=QtCore.Qt.AlignTop)
        self.title.setFont(get_title_font())

        self.result = QtWidgets.QLabel("Result", alignment=QtCore.Qt.AlignRight)
        self.result.setFont(get_result_font())
        self.result.hide()

        self.result_table = QtWidgets.QTableWidget()
        self.result_table.hide()

        self.left_title = QtWidgets.QLabel("Portfolio")
        self.left_title.setFont(get_subtitle_font())

        self.right_title = QtWidgets.QLabel("Contraints")
        self.right_title.setFont(get_subtitle_font())

        self.message = QtWidgets.QLabel("Please separate symbols with a comma", alignment=QtCore.Qt.AlignBottom)
        self.message.setFont(get_msg_font())  

        self.target_label = QtWidgets.QLabel("Target Return")
        self.target_label.setFont(get_label_font())

        self.portfolio_label = QtWidgets.QLabel("Investment")
        self.portfolio_label.setFont(get_label_font())

        self.minimize_button = QtWidgets.QPushButton("Minimize Portfolio Volatility")
        self.minimize_button.setAutoDefault(True)
        self.minimize_button.clicked.connect(min_function)

        self.optimize_button = QtWidgets.QPushButton("Optimize Subject To Constraint")
        self.optimize_button.setAutoDefault(True)
        self.optimize_button.clicked.connect(opt_function)

        self.clear_button = QtWidgets.QPushButton("Clear")
        self.clear_button.setAutoDefault(True)
        self.clear_button.clicked.connect(self.clear)

        self.symbol_input = QtWidgets.QLineEdit()
        self.symbol_input.setMaxLength(100)
        self.symbol_input.returnPressed.connect(min_function)

        self.target_return = QtWidgets.QLineEdit()
        self.target_return.setValidator(QtGui.QDoubleValidator(-10.0000, 10.0000, 4))
        self.target_return.returnPressed.connect(opt_function)

        self.portfolio_value = QtWidgets.QLineEdit()
        self.portfolio_value.setValidator(QtGui.QDoubleValidator(0, 1000000, 2))

        self.first_layer = QtWidgets.QVBoxLayout()
        self.second_layer = QtWidgets.QHBoxLayout()
        self.left_layout = QtWidgets.QVBoxLayout()
        self.right_layout = QtWidgets.QVBoxLayout()


        self.first_layer.addWidget(self.title)
        self.first_layer.addWidget(self.result)
        self.first_layer.addWidget(self.result_table)
        # Left Panel Layout
        self.left_layout.addWidget(self.left_title)
        self.left_layout.addWidget(self.message)
        self.left_layout.addWidget(self.symbol_input)
        self.left_layout.addWidget(self.minimize_button)
        # Right Panel Layout
        self.right_layout.addWidget(self.right_title)
        self.right_layout.addWidget(self.portfolio_label)
        self.right_layout.addWidget(self.portfolio_value)
        self.right_layout.addWidget(self.target_label)
        self.right_layout.addWidget(self.target_return)
        self.right_layout.addWidget(self.optimize_button)
        # Layering
        self.second_layer.addLayout(self.left_layout)
        self.second_layer.addLayout(self.right_layout)
        self.first_layer.addLayout(self.second_layer)
        self.first_layer.addWidget(self.clear_button)
        self.first_layer.addStretch()

        self.setLayout(self.first_layer)
        
    @QtCore.Slot()
    def clear(self):
        self.symbol_input.clear()
        self.target_return.clear()
        self.portfolio_value.clear()
        self.result_table.clear()
        self.result_table.hide()
        self.result.clear()
        self.result.hide()

# Base Widget to get asset symbol input
class SymbolWidget(QtWidgets.QWidget):
    def __init__(self, widget_title, button_msg):
        super().__init__()
        self.title = QtWidgets.QLabel(widget_title, alignment=QtCore.Qt.AlignTop)
        self.title.setFont(get_title_font())

        self.message = QtWidgets.QLabel("Please separate symbols with a comma", alignment=QtCore.Qt.AlignBottom)
        self.message.setFont(get_msg_font())    

        self.calculate_button = QtWidgets.QPushButton(button_msg)
        self.calculate_button.setAutoDefault(True)
            # emits 'clicked' when return is pressed

        self.clear_button = QtWidgets.QPushButton("Clear")
        self.clear_button.setAutoDefault(True)
            # emits 'clicked' when return is pressed
        
        self.symbol_input = QtWidgets.QLineEdit()
        self.symbol_input.setMaxLength(100)

class CalculateWidget(SymbolWidget):
    def __init__(self, widget_title, button_msg, calculate_function):
        super().__init__(widget_title=widget_title, button_msg=button_msg)

        self.result = QtWidgets.QLabel("Result", alignment=QtCore.Qt.AlignRight)
        self.result.setFont(get_result_font())
        self.result.hide()
        
        self.layout = QtWidgets.QVBoxLayout()

        self.layout.addWidget(self.title)
        self.layout.addStretch()
        self.layout.addWidget(self.result)
        self.layout.addWidget(self.message)
        self.layout.addWidget(self.symbol_input)
        self.layout.addWidget(self.calculate_button)
        self.layout.addWidget(self.clear_button)

        self.setLayout(self.layout)

        self.clear_button.clicked.connect(self.clear)
        self.calculate_button.clicked.connect(calculate_function)
        self.symbol_input.returnPressed.connect(calculate_function)

    @QtCore.Slot()
    def clear(self):
        self.symbol_input.clear()
        self.result.hide()

class TableWidget(SymbolWidget):
    def __init__(self, widget_title, button_msg, table_function):
        super().__init__(widget_title=widget_title, button_msg=button_msg)

        self.table = QtWidgets.QTableWidget()
        self.table.hide()

        self.layout = QtWidgets.QVBoxLayout()
    
        self.layout.addWidget(self.title)
        self.layout.addStretch()
        self.layout.addWidget(self.table)
        self.layout.addWidget(self.message)
        self.layout.addWidget(self.symbol_input)
        self.layout.addWidget(self.calculate_button)
        self.layout.addWidget(self.clear_button)

        self.setLayout(self.layout)

        self.clear_button.clicked.connect(self.clear)
        self.calculate_button.clicked.connect(table_function)
        self.symbol_input.returnPressed.connect(table_function)
    
        self.displayed = False
        self.figure = None

    @QtCore.Slot()
    def clear(self):
        self.symbol_input.clear()
        self.table.clear()
        self.table.hide()

# NOTE: display_function MUST set displayed = True and set
#       figure to FigureCanvasAgg object
class GraphWidget(SymbolWidget):
    def __init__(self, widget_title, button_msg, display_function):
        super().__init__(widget_title=widget_title, button_msg=button_msg)
        
        self.layout = QtWidgets.QVBoxLayout()
    
        self.layout.addWidget(self.title)
        self.layout.addStretch()
        self.layout.addWidget(self.message)
        self.layout.addWidget(self.symbol_input)
        self.layout.addWidget(self.calculate_button)
        self.layout.addWidget(self.clear_button)

        self.setLayout(self.layout)

        self.clear_button.clicked.connect(self.clear)
        self.calculate_button.clicked.connect(display_function)
        self.symbol_input.returnPressed.connect(display_function)
    
        self.displayed = False
        self.figure = None

    @QtCore.Slot()
    def clear(self):
        self.symbol_input.clear()
        if self.displayed:
            self.displayed = False
            self.layout.removeWidget(self.figure)
            self.figure.deleteLater()
            self.figure = None