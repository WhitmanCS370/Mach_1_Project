from PySide6.QtWidgets import QPushButton
from PySide6.QtCore import Qt

class Button(QPushButton):
    def __init__(self, text, callback=None, setFixedWidth=None):
        super().__init__(text)
        self.styles = """
            QPushButton {
                background-color: #574B90; /* Green background */
                color: white;             /* White text */
                padding: 10px 20px;       /* Padding around the text */
                text-align: center;       /* Center the text */
                font-size: 14px;          /* Font size */
                margin: 4px 2px;          /* Margin around the button */
            }
            QPushButton:hover {
                background-color: #786FA6; /* Darker green when hovered */
            }
        """
        self.setStyleSheet(self.styles)
        self.setCursor(Qt.PointingHandCursor)
        if setFixedWidth:
            self.setFixedWidth(setFixedWidth)
        if callback:
            self.clicked.connect(callback)

