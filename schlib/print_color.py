#!/usr/bin/env python

from __future__ import print_function
import sys, platform

class PrintColor(object):
    """
    A class to print colorized text using ANSI escape sequences
    """
    def __init__(self, tab_size=4, use_color=True):
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

    def _do_print(self, color_name, text):
        s = self._replace_tabs(text)

        if self._use_color:
            # get the color according to function name
            s = self._color[color_name]
            # replace tabs by space
            s += self._replace_tabs(text)
            # restore the regular color
            s += self._color['regular']

        print(s)

    def regular(self, text): self._do_print(sys._getframe().f_code.co_name, text)
    def black(self, text): self._do_print(sys._getframe().f_code.co_name, text)
    def red(self, text): self._do_print(sys._getframe().f_code.co_name, text)
    def green(self, text): self._do_print(sys._getframe().f_code.co_name, text)
    def brown(self, text): self._do_print(sys._getframe().f_code.co_name, text)
    def blue(self, text): self._do_print(sys._getframe().f_code.co_name, text)
    def purple(self, text): self._do_print(sys._getframe().f_code.co_name, text)
    def cyan(self, text): self._do_print(sys._getframe().f_code.co_name, text)
    def gray(self, text): self._do_print(sys._getframe().f_code.co_name, text)
    def dark_gray(self, text): self._do_print(sys._getframe().f_code.co_name, text)
    def light_red(self, text): self._do_print(sys._getframe().f_code.co_name, text)
    def light_green(self, text): self._do_print(sys._getframe().f_code.co_name, text)
    def yellow(self, text): self._do_print(sys._getframe().f_code.co_name, text)
    def light_blue(self, text): self._do_print(sys._getframe().f_code.co_name, text)
    def light_purple(self, text): self._do_print(sys._getframe().f_code.co_name, text)
    def light_cyan(self, text): self._do_print(sys._getframe().f_code.co_name, text)
    def white(self, text): self._do_print(sys._getframe().f_code.co_name, text)
