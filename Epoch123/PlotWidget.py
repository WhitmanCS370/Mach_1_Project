import numpy as np
from PySide6.QtWidgets import QWidget, QMenu, QVBoxLayout, QFileDialog
from PySide6.QtGui import QAction
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
import matplotlib.pyplot as plt
from matplotlib.widgets import SpanSelector
import soundfile as sf
import logging
import os


class PlotWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.figure, self.ax = plt.subplots()
        self.canvas = FigureCanvas(self.figure)
        self.line = None
        self.position_line = None
        self.selection_rect = None
        self.selected_region = None
        self.span_selector = None

        # Initialize data attributes
        self.data = None
        self.fs = None
        self.audio = None

        # Initialize undo and redo stacks
        self.undo_stack = []
        self.redo_stack = []
        self.data_stack = []

        # Set up the canvas layout
        layout = QVBoxLayout(self)
        layout.addWidget(self.canvas)
        self.setLayout(layout)
        self.setup_plot()
        self.connect_events()

    def setup_plot(self):
        """Initial configuration for the plot appearance."""
        self.figure.subplots_adjust(left=0, bottom=0, right=1, top=1, wspace=0, hspace=0)
        self.ax.set_facecolor('black')
        self.figure.patch.set_facecolor('black')

        for axis in ['x', 'y']:
            self.ax.tick_params(axis=axis, colors='orange', direction='out')
        self.ax.grid(color='orange', linestyle='-', linewidth=0.25, alpha=0.5)
        self.ax.set_axisbelow(False)

        self.position_line = self.ax.axvline(0, color='gray', lw=1, zorder=3)

    def connect_events(self):
        """Connect plot events for interaction."""
        self.canvas.mpl_connect('button_press_event', self.on_click)
        self.reset_span_selector()

    def reset_span_selector(self):
        """Reset the SpanSelector to enable new selections."""
        if self.span_selector:
            self.span_selector.disconnect_events()
        self.span_selector = SpanSelector(self.ax, self.on_select, 'horizontal', useblit=True, props=dict(alpha=0.3, facecolor='pink'))


    def set_ticks(self, duration, data_length, xmin=None, xmax=None):
        """Dynamically set the ticks based on the current zoom level or total data length."""
        if xmin is not None and xmax is not None:
            xticks = np.linspace(xmin, xmax, 10)  # Create 10 ticks within the zoomed range
            time_labels = np.char.mod('%.2f', np.linspace(xmin / self.fs, xmax / self.fs, 10))
        else:
            xticks = np.linspace(0, data_length, 10)
            time_labels = np.char.mod('%.2f', np.linspace(0, duration, 10))

        time_labels[0] = ''  # Avoid overlapping the y-axis
        self.ax.set_xticks(xticks)
        self.ax.set_xticklabels(time_labels, color='orange', fontsize=8, ha='left', va='bottom', y=0.01)

        yticks = np.linspace(-1.6, 1.6, 15)
        self.ax.set_yticks(yticks)
        amplitude_labels = np.char.mod('%.1f', yticks)
        amplitude_labels[0], amplitude_labels[-1] = '', ''  # Avoid overlap
        self.ax.set_yticklabels(amplitude_labels, color='orange', fontsize=8, ha='left', va='top', x=0.02)

    def update_plot(self, data, fs, audio):
        """Update the plot with new audio data."""
        self.audio = audio
        self.data = data
        self.fs = fs
        x_data = np.arange(len(data))

        if self.line is None:
            self.line, = self.ax.plot(x_data, data, color='purple', lw=0.5)
        else:
            self.line.set_data(x_data, data)

        self.position_line.set_xdata([0])
        self.ax.set_xlim(0, len(data))
        self.set_ticks(audio.duration_seconds, len(data))
        self.canvas.draw_idle()
        self.reset_span_selector()

    def on_click(self, event):
        """Handle plot selection clicks."""
        if event.button == 1 and self.selected_region and event.inaxes == self.ax:
            xmin, xmax = self.selected_region
            if not (xmin <= event.xdata <= xmax):
                self.clear_selection()

    def on_select(self, xmin, xmax):
        """Handle the selection of a region using SpanSelector."""
        if xmax - xmin > 1:
            self.selected_region = (xmin, xmax)
            if self.selection_rect:
                self.selection_rect.remove()
            self.selection_rect = self.ax.axvspan(xmin, xmax, color='pink', alpha=0.3)
            self.position_line.set_xdata([xmin])
        else:
            self.position_line.set_xdata([0])
        self.canvas.draw_idle()

    def clear_selection(self):
        """Clear the selection rectangle and reset the position line."""
        if self.selection_rect:
            self.selection_rect.remove()
        self.selection_rect = None
        self.selected_region = None
        self.position_line.set_xdata([0])
        self.canvas.draw_idle()

    def on_click(self, event):
        """Clear selection if clicked outside the current selected region."""
        if event.button == 1:  # Left click
            if self.selected_region and event.inaxes == self.ax:
                xmin, xmax = self.selected_region
                if not (xmin <= event.xdata <= xmax):
                    self.clear_selection()
        elif event.button == 3:  # Right click
            if self.selected_region:
                xmin, xmax = self.selected_region
                if xmin <= event.xdata <= xmax:
                    self.context_menu(event, 'selected_region')
                else:
                    self.context_menu(event)

    def contextMenuEvent(self, event):
        """Override the context menu event to display the menu only when right-clicking on the widget."""
        if self.selected_region:
            self.context_menu(event, 'selected_region')
        else:
            self.context_menu(event)

    def context_menu(self, event, context=None):
        """Display a context menu with various audio processing options."""
        menu = QMenu()

        if context == 'selected_region':
            zoom_action = QAction('Zoom into selected region', self)
            zoom_action.triggered.connect(self.zoom_into_selected)
            menu.addAction(zoom_action)

        zoom_out_action = QAction('Zoom out', self)
        zoom_out_action.triggered.connect(self.zoom_out)
        menu.addAction(zoom_out_action)

        if context == 'selected_region':
            crop_selected_action = QAction('Crop selected region', self)
            crop_selected_action.triggered.connect(self.crop_selected)
            menu.addAction(crop_selected_action)

            crop_unselected_action = QAction('Crop unselected region', self)
            crop_unselected_action.triggered.connect(self.crop_unselected)
            menu.addAction(crop_unselected_action)

        undo_action = QAction('Undo last action', self)
        undo_action.triggered.connect(self.undo_last_action)
        menu.addAction(undo_action)

        redo_action = QAction('Redo last action', self)
        redo_action.triggered.connect(self.redo_last_action)
        menu.addAction(redo_action)

        reset_plot_action = QAction('Reset plot', self)
        reset_plot_action.triggered.connect(self.reset_plot)
        menu.addAction(reset_plot_action)

        save_action = QAction('Save plot', self)
        save_action.triggered.connect(self.save_plot)
        menu.addAction(save_action)

        global_point = self.mapToGlobal(event.pos())
        menu.exec_(global_point)

        # Reset the SpanSelector after closing the context menu
        self.reset_span_selector()

    def zoom_out(self):
        if self.data is not None:
            self.ax.set_xlim(0, len(self.data))
            self.canvas.draw_idle()
            # Add the current state to the undo stack
            self.undo_stack.append(self.data)
            self.redo_stack.append(self.data)
            self.set_ticks(self.audio.duration_seconds, len(self.data))
            # Reset the selected region
            self.clear_selection()

    def zoom_into_selected(self):
        """Zoom into the currently selected region and adjust ticks accordingly."""
        if self.selected_region:
            xmin, xmax = self.selected_region
            self.undo_stack.append((np.copy(self.data), (self.ax.get_xlim())))  # Save current data and view limits
            self.ax.set_xlim(xmin, xmax)
            self.set_ticks(None, None, xmin, xmax)  # Update ticks for the zoomed region
            self.clear_selection()
            self.canvas.draw_idle()

    def crop_selected(self):
        """Crop the audio data to only include the selected region."""
        if self.selected_region:
            xmin, xmax = self.selected_region
            self.undo_stack.append((np.copy(self.data), (self.ax.get_xlim())))  # Save current data and view limits
            self.data = self.data[int(xmin):int(xmax)]
            self.clear_selection()
            self.update_plot(self.data, self.fs, self.audio)

    def crop_unselected(self):
        """Crop the audio data to exclude the selected region."""
        if self.selected_region:
            xmin, xmax = self.selected_region
            self.undo_stack.append((np.copy(self.data), (self.ax.get_xlim())))  # Save current data and view limits
            self.data = np.concatenate((self.data[:int(xmin)], self.data[int(xmax):]))
            self.clear_selection()
            self.update_plot(self.data, self.fs, self.audio)

    def undo_last_action(self):
        if self.undo_stack:
            last_state, last_view = self.undo_stack.pop()
            self.redo_stack.append((np.copy(self.data), (self.ax.get_xlim())))  # Save current state before undo
            self.data = last_state
            self.update_plot(self.data, self.fs, self.audio)
            # clear selection if any
            self.clear_selection()
            self.ax.set_xlim(last_view)  # Restore view limits
            self.canvas.draw_idle()

    def redo_last_action(self):
        if self.redo_stack:
            next_state, next_view = self.redo_stack.pop()
            self.undo_stack.append((np.copy(self.data), (self.ax.get_xlim())))  # Save current state before redo
            self.data = next_state
            self.update_plot(self.data, self.fs, self.audio)
            # clear selection if any
            self.clear_selection()
            self.ax.set_xlim(next_view)  # Restore view limits
            self.canvas.draw_idle()

    def save_plot(self):
        file_path, _ = QFileDialog.getSaveFileName(self, "Save Image", os.path.join(os.path.expanduser("~"), 'Downloads'), "Images (*.png)")
        if file_path:
            self.figure.savefig(file_path, facecolor='black')
            logging.info(f"Plot saved to {file_path}")

    def reset_plot(self):
        if self.data_stack:
            self.data = np.copy(self.data_stack[0])
            # clear selection if any
            self.clear_selection()
            self.update_plot(self.data, self.fs, self.audio)
