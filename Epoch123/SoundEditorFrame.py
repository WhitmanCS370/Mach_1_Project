from PySide6.QtWidgets import QFrame, QVBoxLayout, QHBoxLayout, QComboBox, QLabel, QLineEdit, QWidget
from PySide6.QtCore import Qt
from GUIElements import Button, LineEdit, Slider, GuiWidget
from WaveformPlotWidget import WaveformPlotWidget

class SoundEditorFrame(QFrame):
    def __init__(self, parent):
        super().__init__(parent)
        
        self.parent = parent
        self.layout = QVBoxLayout()
        self.setLayout(self.layout)

        self.audio = None

        self.setStyleSheet("background-color: #333333; color: white;")
        self.plot_widget = WaveformPlotWidget(parent)
        self.set_nav_buttons()
        self.set_editor()
        self.layout.addWidget(self.plot_widget)

    def set_nav_buttons(self):
        nav_layout = QHBoxLayout()
        self.add_button_to_layout(Button("Go Back", self.parent.show_file_nav_widget, setFixedWidth=100), nav_layout)
        self.add_button_to_layout(Button("Save", None, setFixedWidth=100), nav_layout)
        audio_buttons = self.plot_widget.audio_buttons()
        nav_layout.addWidget(audio_buttons)
        nav_layout.setSpacing(0)
        nav_layout.setContentsMargins(0, 0, 0, 0)
        self.layout.addLayout(nav_layout)
        # self.layout.addStretch()

    def add_button_to_layout(self, button, layout=None):
        layout.addWidget(button)

    def set_editor(self):
        self.editor_layout = QVBoxLayout()
        self.layout.addLayout(self.editor_layout)

        self.editor_widget_1 = QWidget()
        self.editor_widget_1_layout = QHBoxLayout()
        # menu layout
        self.add_menu_to_layout(["Low Pass", "High Pass", "Butterworth"])
        self.add_menu_to_layout(["Waveform", "Spectrogram"])
        # add a input to change the audio's speed
        speed_input = LineEdit(placeholder="1.0", setFixedWidth=50)
        speed_widget = GuiWidget(label_text="Speed: ", gui_elements=[speed_input], setFixedWidth=110)
        self.editor_layout.addWidget(speed_widget)
        volume_slider = Slider(Qt.Horizontal, 0, 100, 1, setFixedWidth=200)
        volume_widget = GuiWidget(label_text="Volume: ", gui_elements=[volume_slider], setFixedWidth=200)
        trim_imput = LineEdit(placeholder="0.0", setFixedWidth=50)
        trim_button = Button("Trim", None, setFixedWidth=75, setFixedHeight=30)
        trim_widget = GuiWidget(gui_elements=[trim_button, trim_imput], setFixedWidth=150)
        self.editor_layout.addWidget(trim_widget)

        self.editor_layout.addWidget(volume_widget)


    def add_menu_to_layout(self, items):
        layout = QHBoxLayout()
        menu = QComboBox()
        for item in items:
            menu.addItem(item)
        layout.addWidget(menu)
        self.editor_layout.addLayout(layout)

    def add_input_to_layout(self, label_text):
        layout = QHBoxLayout()
        label = QLabel(label_text)
        layout.addWidget(label)
        input_field = QLineEdit()
        layout.addWidget(input_field)
        self.editor_layout.addLayout(layout)