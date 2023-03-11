import sys
import copy
from PyQt5 import QtCore, QtGui, QtWidgets, Qt
from PyQt5.QtGui import QPixmap, QColor, QPainter, QKeySequence
from PyQt5.QtWidgets import QLabel, QApplication, QShortcut


# Class to make a Node
class Stack:
    def __init__(self):
        self.top = -1
        # self.size_input = size_input
        self.array = []

    def isEmpty(self):
        return True if self.top == -1 else False

    def peek(self):
        return self.array[-1]

    def pop(self):
        if not self.isEmpty():
            self.top -= 1
            return self.array.pop()
        else:
            return 'Stack is Empty'

    def push(self, op):
        self.top += 1
        self.array.append(op)


class Canvas(QLabel):
    def __init__(self,height, width, background_color=QColor('#FFFFFF')):
        super().__init__()
        qpixmap = QPixmap(int(height), int(width))
        qpixmap.fill(background_color)
        self.setPixmap(qpixmap)
        self.pen_color = QColor('#000000')
        self.stckIn = Stack()
        self.stckUndo = Stack()
        self.stckRedo = Stack()
        self.stckColorUno = Stack()
        self.stckColorRedo = Stack()

    def set_pen_color(self, color):
        self.pen_color = QtGui.QColor(color)

    def draw_point(self, x, y):
        painter = QPainter(self.pixmap())
        p = painter.pen()
        p.setWidth(4)
        p.setColor(self.pen_color)
        painter.setPen(p)
        painter.drawPoint(x, y)
        painter.end()
        self.update()

    def draw_line(self, x0, y0, x1, y1):
        painter = QPainter(self.pixmap())
        p = painter.pen()
        p.setWidth(4)
        p.setColor(self.pen_color)
        painter.setPen(p)
        painter.drawLine(x0, y0, x1, y1)
        painter.end()
        self.update()

    def mousePressEvent(self, e: QtGui.QMouseEvent):
        self.draw_point(e.x(), e.y())
        self.past_point = (e.x(), e.y())

        self.stckIn.push((e.x(), e.y()))

    def mouseMoveEvent(self, e):
        self.draw_line(self.past_point[0], self.past_point[1], e.x(), e.y())
        self.past_point = (e.x(), e.y())

        self.stckIn.push((e.x(), e.y()))

    def mouseReleaseEvent(self, e):
        self.past_point = tuple()
        self.stckUndo.push(self.stckIn)
        self.stckColorUno.push(self.pen_color)
        while not self.stckColorRedo.isEmpty():
            self.stckColorRedo.pop()
        while not self.stckRedo.isEmpty():
            self.stckRedo.pop()
        self.stckIn = Stack()
        self.update()

    def draw_line_stack(self,stck):
        c = stck.peek()
        self.past_point = (c[0], c[1])
        while not stck.isEmpty():
            c = stck.pop()
            self.draw_line(self.past_point[0], self.past_point[1], c[0], c[1])
            self.past_point = (c[0], c[1])

    def undo(self):
        if not self.stckUndo.isEmpty():
            canvas = self.pixmap()
            canvas.fill(QColor('#FFFFFF'))
            self.update()
            self.stckRedo.push(self.stckUndo.pop())
            newStack = copy.deepcopy(self.stckUndo)
            self.stckColorRedo.push(self.stckColorUno.pop())
            color = copy.deepcopy(self.stckColorUno)
            while not newStack.isEmpty():
                stck = newStack.pop()
                self.pen_color = color.pop()
                self.draw_line_stack(stck)
        else:
            pass

    def redo(self):
        if not self.stckRedo.isEmpty():
            stck = self.stckRedo.peek()
            self.pen_color = self.stckColorRedo.peek()
            self.stckUndo.push(self.stckRedo.pop())
            self.stckColorUno.push(self.stckColorRedo.pop())
            self.draw_line_stack(stck)
        else:
            pass


class PaletteButton(QtWidgets.QPushButton):

    def __init__(self, color):
        super().__init__()
        self.setFixedSize(QtCore.QSize(32, 32))
        self.color = color
        self.setStyleSheet("background-color: %s;" % color + "border-radius : 15; ")


class MainWindow(QtWidgets.QMainWindow):

    def __init__(self):
        super().__init__()
        self.colors = [
            '#000002', '#868687', '#900124', '#ed2832', '#2db153', '#13a5e7', '#4951cf',
            '#fdb0ce', '#fdca0f', '#eee3ab', '#9fdde8', '#7a96c2', '#cbc2ec', '#a42f3b',
            '#f45b7a', '#c24998', '#81588d', '#bcb0c2', '#dbcfc2',
        ]
        app = QApplication.instance()
        screen = app.primaryScreen()
        geometry = screen.availableGeometry()
        self.canvas = Canvas(geometry.width()*0.60, geometry.height()*0.7)
        w = QtWidgets.QWidget()
        w.setStyleSheet("background-color: #313234")
        l = QtWidgets.QVBoxLayout()  # vertical layout
        w.setLayout(l)
        l.addWidget(self.canvas)

        self.shortcut_undo = QShortcut(QKeySequence('Ctrl+z'), self)
        self.shortcut_undo.activated.connect(self.on_undo)

        self.shortcut_redo = QShortcut(QKeySequence('Ctrl+y'), self)
        self.shortcut_redo.activated.connect(self.on_redo)

        palette = QtWidgets.QHBoxLayout()  # horizontal layout
        self.add_palette_button(palette)
        l.addLayout(palette)

        self.setCentralWidget(w)

    def on_redo(self):
        self.canvas.redo()

    def on_undo(self):
        self.canvas.undo()

    def add_palette_button(self, palette):
        for c in self.colors:
            item = PaletteButton(c)
            item.pressed.connect(self.set_canvas_color)
            palette.addWidget(item)

    def set_canvas_color(self):
        sender = self.sender()
        self.canvas.set_pen_color(sender.color)


app = QtWidgets.QApplication(sys.argv)
window = MainWindow()
window.setWindowFlags(QtCore.Qt.WindowCloseButtonHint | QtCore.Qt.WindowMinimizeButtonHint)
window.show()
app.exec_()

# Window dimensions
