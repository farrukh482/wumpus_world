from IPython.display import display, HTML
from typing import NamedTuple
from tabulate import tabulate
import numpy as np
import sys


class P(NamedTuple):
    i: int
    j: int

    def __str__(self):
        return str('(' + str(self.i) + ',' + str(self.j) + ')')

    def __repr__(self):
        return self.__str__()


class Utils:

    # set this to True if unicode is supported in the interpreter
    unicode_supported = False

    # unicode symbols for characters of the game.
    def get_characters():
        if Utils.is_notebook():
            return {'wumpus': chr(128126), 'dead_wumpus': chr(128128), 'pit': chr(128371), 'breeze': chr(128168),
                    'stench': chr(128169), 'gold': chr(129351), 'agent': chr(129312)}
        else:
            return {'wumpus': 'W', 'dead_wumpus': 'D', 'pit': 'P', 'breeze': 'B',
                    'stench': 'S', 'gold': 'G', 'agent': 'A'}

    # unicode symbols for directional arrows etc.
    def get_direction():
        if Utils.is_notebook():
            return  {'bottom_left': chr(11184), 'bottom_right': chr(11185), 'top_left': chr(11186),
                    'top_right': chr(11187),
                    'left_top': chr(11188), 'right_top': chr(11189), 'left_bottom': chr(11190),
                    'right_bottom': chr(11191),
                    'left_right': chr(8646), 'right_left': chr(8644), 'top_bottom': chr(8645), 'bottom_top': chr(8693),
                    'left': chr(8678), 'right': chr(8680), 'top': chr(8679), 'bottom': chr(8681), 'target': chr(128392)}
        else:
            if Utils.unicode_supported:
                return {'bottom_left': chr(11168), 'bottom_right': chr(11169), 'top_left': chr(11170),
                        'top_right': chr(11171),
                        'left_top': chr(11172), 'right_top': chr(11173), 'left_bottom': chr(11174),
                        'right_bottom': chr(11175),
                        'left_right': chr(8646), 'right_left': chr(8644), 'top_bottom': chr(8645), 'bottom_top': chr(8693),
                        'left': chr(11104), 'right': chr(11106), 'top': chr(11105), 'bottom': chr(11107),
                        'target': chr(9673)}
            else:
                return {'bottom_left': 'Bl', 'bottom_right': 'Br', 'top_left': 'Tl', 'top_right': 'Tr',
                        'left_top': 'Lt', 'right_top': 'Rt', 'left_bottom': 'Lb', 'right_bottom': 'Rb',
                        'left_right': 'U', 'right_left': 'U', 'top_bottom': 'U', 'bottom_top': 'U',
                        'left': 'L', 'right': 'R', 'top': 'T', 'bottom': 'B', 'target': 'T'}

    def print_title(str):  # creates title with gray background
        if Utils.is_notebook():
            display(HTML('<b style="color:white;background:gray;padding:5px;text_decoration:underline">' + str + '</b>'))
        else:
            print("~~~   " + str + "   ~~~")

    def hr_tables(title1, title2, tbl1, tbl2):  # displays two tables side-by-side
        if Utils.is_notebook():
            display(HTML(
                '<table><tr><th style="text-align:center">' + title1 + '</th><th style="text-align:center">' + title2 + '</th></tr>'
                + '<tr style="background:white"><td style="padding:20px;border: 1px solid gray">' + tbl1 + '</td>'
                + '<td style="padding:20px;border: 1px solid gray">' + tbl2 + '</td></tr></table>'))
        else:
            print(tabulate([[tbl1]], tablefmt="psql", headers=[title1]))
            print(tabulate([[tbl2]], tablefmt="psql", headers=[title2]))

    def divider(title, color = 'blue'):
        wrapper = '=' * (30 - round(len(title) / 2))
        if Utils.is_notebook():
            display(HTML('<b style="color:' + color + '">' + wrapper + ' ' + title + ' ' + wrapper + '</b>'))
        else:
            print(wrapper + ' ' + title + ' ' + wrapper)

    def tbl_style(mtx, headers, index):  # evens out font-size for various symbols to present nicely
        if Utils.is_notebook():
            return (tabulate(mtx, tablefmt="html", showindex = index, headers= headers)
                    .replace('<td>', '<td style="border:1px solid black">')
                    .replace("<table", "<table style='border:1px solid black;font-size:20px;'")
                    .replace('{', '<b style="font-size:24px">').replace('}', '</b>'))
        else:
            return (tabulate(mtx, tablefmt="grid", showindex = index, headers= headers)
                    .replace('{', '').replace('}', ''))

    def tbl_display(mtx):
        if Utils.is_notebook():
            display(HTML(mtx))
        else:
            print(mtx)

    def tbl_print(mtx, headers=[]):
        if Utils.is_notebook():
            display(tabulate(mtx, tablefmt='html', headers=headers))
        else:
            print(tabulate(mtx, tablefmt='grid', headers=headers))

    def flip_mtx(mtx):  # flips matrix upside-down for presentation
        return np.array(mtx).T.tolist()[::-1]

    def adj_locs(x, y, w, h):  # adjacent locations: left, top, right, bottom
        return [Utils.opt_loc(x - 1, y, w, h), Utils.opt_loc(x, y + 1, w, h),
                Utils.opt_loc(x + 1, y, w, h), Utils.opt_loc(x, y - 1, w, h)]

    def opt_loc(x, y, w, h):  # location or None, if it doesnt exist
        return P(x, y) if 0 <= x < w and 0 <= y < h else None

    def is_notebook():
        try:
            return 'IPKernelApp' in get_ipython().config
        except NameError:
            return False
