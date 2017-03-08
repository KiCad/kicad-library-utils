#!/usr/bin/env python

# -*- coding: utf-8 -*-

from __future__ import print_function
import sys, platform

class PrintColor(object):
    """
    A class to print colorized text using ANSI escape sequences
    """
    def __init__(self, tab_size=4, use_color=True, max_width=0, indentation=0):
        self._color = {
            'regular':'\033[0m',
            'black':'\033[0;30m',
            'red':'\033[0;31m',
            'green':'\033[0;32m',
            'brown':'\033[0;33m',
            'blue':'\033[0;34m',
            'purple':'\033[0;35m',
            'cyan':'\033[0;36m',
            'gray':'\033[0;37m',
            'dark_gray':'\033[1;30m',
            'light_red':'\033[1;31m',
            'light_green':'\033[1;32m',
            'yellow':'\033[1;33m',
            'light_blue':'\033[1;34m',
            'light_purple':'\033[1;35m',
            'light_cyan':'\033[1;36m',
            'white':'\033[1;37m',
            }

        self._tab_size = tab_size
        self._use_color = use_color
        self._max_width = max_width
        self._indentation = indentation

        if platform.system() == 'Windows':
            try:
                import colorama
                colorama.init()
            except:
                print('To print using colors you have to install colorama. Try to install it using: "pip install colorama"')
                print('[Continuing using no color mode]\n')
                self._use_color = False


    def _replace_tabs(self, text):
        if self._tab_size == 0:
            return text

        return text.replace('\t', ' ' * self._tab_size)

    def _do_print(self, color_name, text, max_width=None, indentation=None):
        # uses the global definition if there is no local definitions for max_width and indentation
        if not max_width: max_width = self._max_width
        if not indentation: indentation = self._indentation

        # break the text in lines with max_width
        if max_width > 0:
            s = 0
            lines = []
            n_lines = int(len(text) / max_width) + 1
            for n in range(n_lines):
                # calculates the end index
                e = s + max_width
                # extract the line
                line = text[s:e]
                # get the index of the last space before the line ends
                # except when is the last line
                n = e if (n_lines == (n + 1)) else line.rfind(' ')
                # cut off the line in the space position
                line = line[0:n]
                # append line to the list
                lines.append(line)
                # calculates the start index
                s += n + 1
        # if there is not max width there is only one line
        else:
            lines = [text]

        # print lines
        for line in lines:
            # insert indentation
            line = ' ' * indentation + line

            # replace tabs by space
            line = self._replace_tabs(line)

            # apply color
            if self._use_color:
                # get the color according to function name
                color = self._color[color_name]
                # restore the regular color
                regular = self._color['regular']
                # construct the final line
                line = color + line + regular

            try:
                print(line)
            except:
                print("ERROR printing output")

    def regular(self, text, max_width=None, indentation=None):
        self._do_print(sys._getframe().f_code.co_name, text, max_width, indentation)
    def black(self, text, max_width=None, indentation=None):
        self._do_print(sys._getframe().f_code.co_name, text, max_width, indentation)
    def red(self, text, max_width=None, indentation=None):
        self._do_print(sys._getframe().f_code.co_name, text, max_width, indentation)
    def green(self, text, max_width=None, indentation=None):
        self._do_print(sys._getframe().f_code.co_name, text, max_width, indentation)
    def brown(self, text, max_width=None, indentation=None):
        self._do_print(sys._getframe().f_code.co_name, text, max_width, indentation)
    def blue(self, text, max_width=None, indentation=None):
        self._do_print(sys._getframe().f_code.co_name, text, max_width, indentation)
    def purple(self, text, max_width=None, indentation=None):
        self._do_print(sys._getframe().f_code.co_name, text, max_width, indentation)
    def cyan(self, text, max_width=None, indentation=None):
        self._do_print(sys._getframe().f_code.co_name, text, max_width, indentation)
    def gray(self, text, max_width=None, indentation=None):
        self._do_print(sys._getframe().f_code.co_name, text, max_width, indentation)
    def dark_gray(self, text, max_width=None, indentation=None):
        self._do_print(sys._getframe().f_code.co_name, text, max_width, indentation)
    def light_red(self, text, max_width=None, indentation=None):
        self._do_print(sys._getframe().f_code.co_name, text, max_width, indentation)
    def light_green(self, text, max_width=None, indentation=None):
        self._do_print(sys._getframe().f_code.co_name, text, max_width, indentation)
    def yellow(self, text, max_width=None, indentation=None):
        self._do_print(sys._getframe().f_code.co_name, text, max_width, indentation)
    def light_blue(self, text, max_width=None, indentation=None):
        self._do_print(sys._getframe().f_code.co_name, text, max_width, indentation)
    def light_purple(self, text, max_width=None, indentation=None):
        self._do_print(sys._getframe().f_code.co_name, text, max_width, indentation)
    def light_cyan(self, text, max_width=None, indentation=None):
        self._do_print(sys._getframe().f_code.co_name, text, max_width, indentation)
    def white(self, text, max_width=None, indentation=None):
        self._do_print(sys._getframe().f_code.co_name, text, max_width, indentation)

if __name__ == '__main__':
    msg = "Lorem ipsum dolor sit amet, consectetur adipiscing elit. Praesent ullamcorper lectus sed metus condimentum viverra. Class aptent taciti sociosqu ad litora torquent per conubia nostra, per inceptos himenaeos. Fusce ipsum lectus, tristique at turpis id, sagittis egestas leo. Sed vel ex nec libero laoreet hendrerit sed quis sem. Quisque laoreet enim sapien, id placerat eros venenatis sit amet. Mauris faucibus condimentum interdum. Vivamus nec bibendum arcu, at convallis metus. Integer feugiat ante id orci placerat, ut laoreet purus dapibus. Ut facilisis volutpat urna, vel condimentum enim tincidunt non. Vestibulum tempor tristique aliquet. Class aptent taciti sociosqu ad litora torquent per conubia nostra, per inceptos himenaeos. Quisque tortor tortor, semper at justo ac, elementum posuere nulla."
    printer = PrintColor(max_width=100, indentation=4)
    printer.red(msg)
    printer.blue(msg, 50, 2)
    printer.yellow(msg)
    printer.gray(msg, 100, 20)

    printer2 = PrintColor()
    printer2.brown(msg)
    printer2.purple(msg, 50, 2)
    printer2.light_blue(msg)
    printer2.cyan(msg, 100, 20)
