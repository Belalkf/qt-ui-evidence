"""Original synthetic row-preference fixture; no project imports or settings."""
from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QHBoxLayout, QLabel, QSpinBox, QTableWidget, QTableWidgetItem,
    QVBoxLayout, QWidget,
)


class Inventory(QWidget):
    def __init__(self, repaired=False, rows=12):
        super().__init__()
        self.setWindowTitle('Synthetic inventory')
        layout = QVBoxLayout(self)
        controls = QHBoxLayout()
        controls.addWidget(QLabel('Rows to display:'))
        self.preference = QSpinBox()
        self.preference.setRange(1, 10)
        self.preference.setValue(3)
        controls.addWidget(self.preference)
        layout.addLayout(controls)
        self.table = QTableWidget(rows, 2)
        self.table.setHorizontalHeaderLabels(['Item', 'Count'])
        self.table.verticalHeader().setDefaultSectionSize(28)
        self.table.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        for row in range(rows):
            self.table.setItem(row, 0, QTableWidgetItem('Sample %02d' % (row + 1)))
            self.table.setItem(row, 1, QTableWidgetItem(str(row * 2)))
        layout.addWidget(self.table)
        self.resize(420, 360)
        self.set_rows(3)
        if repaired:
            self.preference.valueChanged.connect(self.set_rows)

    def set_rows(self, count):
        height = (self.table.horizontalHeader().height()
                  + self.table.frameWidth() * 2
                  + count * self.table.verticalHeader().defaultSectionSize())
        self.table.setFixedHeight(height)
