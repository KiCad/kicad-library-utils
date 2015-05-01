#!/usr/bin/env python

from __future__ import print_function
import sys, platform

if platform.system() == 'Windows':
    try:
        import colorama
        colorama.init()
    except:
        print('To print using colors you have to install colorama')
        print('Please, execute: "pip install colorama" and try again')
        sys.exit()

color = {
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

def replace_tabs(s):
    return s.replace('\t', '    ')

def do_print(func, text):
    # get the color according to function name
    s = color[func.__name__.replace('print_','')]
    # replace tabs by space
    s += replace_tabs(text)
    # restore the regular color
    s += color['regular']

    print(s)

def print_regular(text): do_print(print_regular, text)
def print_black(text): do_print(print_black, text)
def print_red(text): do_print(print_red, text)
def print_green(text): do_print(print_green, text)
def print_brown(text): do_print(print_brown, text)
def print_blue(text): do_print(print_blue, text)
def print_purple(text): do_print(print_purple, text)
def print_cyan(text): do_print(print_cyan, text)
def print_gray(text): do_print(print_gray, text)
def print_dark_gray(text): do_print(print_dark_gray, text)
def print_light_red(text): do_print(print_light_red, text)
def print_light_green(text): do_print(print_light_green, text)
def print_yellow(text): do_print(print_yellow, text)
def print_light_blue(text): do_print(print_light_blue, text)
def print_light_purple(text): do_print(print_light_purple, text)
def print_light_cyan(text): do_print(print_light_cyan, text)
def print_white(text): do_print(print_white, text)
