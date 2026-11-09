"""Original synthetic control layout with deliberate and valid intersections."""
from PySide6.QtCore import Qt
from PySide6.QtWidgets import QLabel, QPushButton, QVBoxLayout, QWidget


class Station(QWidget):
    def __init__(self, repaired=False):
        super().__init__()
        self.setWindowTitle('Synthetic station')
        self.repaired = repaired
        self.toggle = QPushButton('Collapse details', self)
        self.toggle.setCheckable(True)
        self.panel = QWidget(self)
        self.status = QLabel('Station status: READY', self.panel)
        self.action = QPushButton('Run sample', self.panel)
        self.badge = QLabel('i', self.action)  # Intentional child decoration.
        self.badge.setGeometry(4, 3, 12, 14)
        self.badge.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents)
        if repaired:
            layout = QVBoxLayout(self)
            layout.addWidget(self.toggle)
            layout.addWidget(self.panel)
            details = QVBoxLayout(self.panel)
            details.addWidget(self.status)
            details.addWidget(self.action)
        else:
            self.toggle.setGeometry(12, 12, 180, 32)
            self.panel.setGeometry(12, 54, 280, 80)
            self.status.setGeometry(0, 0, 150, 30)
            self.action.setGeometry(85, 0, 250, 32)  # Overlap and right clipping.
        self.toggle.toggled.connect(self.set_collapsed)
        self.resize(360, 190)

    def set_collapsed(self, collapsed):
        if self.repaired:
            self.panel.setVisible(not collapsed)
        self.toggle.setText('Expand details' if collapsed else 'Collapse details')
