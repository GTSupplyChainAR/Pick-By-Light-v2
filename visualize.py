import logging
import os
import utils
import time
import random
from constants import EMPTY_LIGHT_LAYOUT, ALL_DISPLAYS

try:
    import Tkinter as tk
except ImportError:
    # For Python 3.6+
    import tkinter as tk


logger = logging.getLogger(os.path.basename(__file__))
logger = utils.configure_logger(logger)

LAYOUT = [
    [None, None, None, None, None, None, None, None, None, None, None, None, None],
    [None, 'A11', 'A12', 'A13', None, 'B11', 'B12', 'B13', None, None, None, None, None],
    [None, 'A21', 'A22', 'A23', None, 'B21', 'B22', 'B23', None, 'C11', 'C12', 'C13', None],
    [None, 'A31', 'A32', 'A33', None, 'B31', 'B32', 'B33', None, None, None, None, None],
    [None, 'A41', 'A42', 'A43', None, 'B41', 'B42', 'B43', None, None, None, None, None],
    [None, None, None, None, None, None, None, None, None, None, None, None, None]
]

BINS = [cell for row in LAYOUT for cell in row if cell is not None]

CANVAS_CELL_WIDTH = 80
CANVAS_CELL_HEIGHT = 40

CANVAS_NUM_ROWS = 6
CANVAS_NUM_COLS = 13

BLANK_DISPLAY = None


class LightRackVisualizer(object):
    def __init__(self):

        self.tk_main = tk.Tk()
        self.canvas = tk.Canvas(
            master=self.tk_main,
            width=CANVAS_CELL_WIDTH * CANVAS_NUM_COLS,
            height=CANVAS_CELL_HEIGHT * CANVAS_NUM_ROWS)
        self.canvas.pack()
        self.canvas.master.title("Rack Visualization!")

        self.active_bins = {}

    def run(self, alongside_function):
        self.tk_main.after(1000, alongside_function)
        self.tk_main.mainloop()

    def change_display(self, bin_tag, value):
        if bin_tag is ALL_DISPLAYS:
            self.active_bins = {}
        elif value is BLANK_DISPLAY:
            self.active_bins.pop(bin_tag)
        else:
            self.active_bins[bin_tag] = value

        self._render()

    def _get_bin_location(self, bin_tag):
        for r in range(CANVAS_NUM_ROWS):
            for c in range(CANVAS_NUM_COLS):
                if LAYOUT[r][c] == bin_tag:
                    return r, c

    def _get_bin_color(self, bin_tag):
        if bin_tag[0] == 'C':
            return 'gray'
        elif bin_tag[1] == '1':
            return 'red'
        elif bin_tag[1] == '2':
            return 'yellow'
        elif bin_tag[1] == '3':
            return 'green'
        elif bin_tag[1] == '4':
            return 'blue'
        raise ValueError('Unknown bin tag: %s' % bin_tag)

    def _render(self):
        self.canvas.delete('all')

        # Render Rack A and B vertical lines
        for c in range(1, 9):
            self.canvas.create_line(
                c * CANVAS_CELL_WIDTH,
                1 * CANVAS_CELL_HEIGHT,
                c * CANVAS_CELL_WIDTH,
                5 * CANVAS_CELL_HEIGHT,
                fill='black',
            )

        # Render Rack A and B horizontal lines
        for r in range(1, 6):
            # Rack A
            self.canvas.create_line(
                1 * CANVAS_CELL_WIDTH,
                r * CANVAS_CELL_HEIGHT,
                4 * CANVAS_CELL_WIDTH,
                r * CANVAS_CELL_HEIGHT
            )

            # Rack B
            self.canvas.create_line(
                5 * CANVAS_CELL_WIDTH,
                r * CANVAS_CELL_HEIGHT,
                8 * CANVAS_CELL_WIDTH,
                r * CANVAS_CELL_HEIGHT
            )

        # Render receive bins vertical lines
        for c in range(9, 13):
            self.canvas.create_line(
                c * CANVAS_CELL_WIDTH,
                2 * CANVAS_CELL_HEIGHT,
                c * CANVAS_CELL_WIDTH,
                3 * CANVAS_CELL_HEIGHT,
                fill='black',
            )

        # Render receive bins horizontal lines
        for r in range(2, 4):
            self.canvas.create_line(
                9 * CANVAS_CELL_WIDTH,
                r * CANVAS_CELL_HEIGHT,
                12 * CANVAS_CELL_WIDTH,
                r * CANVAS_CELL_HEIGHT
            )

        # Draw selected bins
        for bin_tag in self.active_bins:
            bin_r, bin_c = self._get_bin_location(bin_tag)
            bin_color = self._get_bin_color(bin_tag)

            self.canvas.create_rectangle(
                bin_c * CANVAS_CELL_WIDTH,
                bin_r * CANVAS_CELL_HEIGHT,
                (bin_c + 1) * CANVAS_CELL_WIDTH,
                (bin_r + 1) * CANVAS_CELL_HEIGHT,
                fill=bin_color,
            )

        # Add text labels
        for r in range(CANVAS_NUM_ROWS):
            for c in range(CANVAS_NUM_COLS):
                bin_tag = LAYOUT[r][c]

                if bin_tag is None:
                    continue

                if bin_tag in self.active_bins:
                    bin_count = self.active_bins[bin_tag]
                    text = '%02d' % (bin_count, )
                else:
                    text = bin_tag

                self.canvas.create_text(
                    (c + 0.5) * CANVAS_CELL_WIDTH,
                    (r + 0.5) * CANVAS_CELL_HEIGHT,
                    text=text,
                    anchor=tk.CENTER,
                )

        self.canvas.update()


if __name__ == '__main__':
    visualizer = LightRackVisualizer()

    def run_visualizer():

        active_bins = set()

        while True:

            random_bin = random.choice(BINS)
            next_display = random.choice([0, 1, BLANK_DISPLAY])

            if next_display is BLANK_DISPLAY:
                if random_bin in active_bins:
                    active_bins.remove(random_bin)
                else:
                    continue
            else:
                active_bins.add(random_bin)

            visualizer.change_display(random_bin, next_display)

            # time.sleep(1)

    visualizer.run(run_visualizer)
