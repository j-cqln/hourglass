import sys

import tkinter as tk
from tkinter import messagebox

def show_info(message):
    """
    Displays info with given message

    message: Info message, string
    """
    msg = messagebox.showinfo('hourglass notification', message)

def show_error(message):
    """
    Displays error with given message

    message: Error message, string
    """
    msg = messagebox.showerror('hourglass error', message)

def handle_exception(exception, value, traceback):
    """
    Callback function that handles exceptions.
    """
    msg = messagebox.showwarning('hourglass error', 'unexpected error:\n' + exception.__name__ + ':' + repr(value))
    sys.exit(1)

def light_or_dark_mode_text(rgb):
    """
    Returns the text color to be used on the given background color

    rgb: Given background color, tuple
    return: Hex color, string
    """
    light_mode_display_text_color = '#4b4b4b'
    dark_mode_display_text_color = '#c2c2c2'

    r, g, b = rgb
    
    # Formula from alienryderflex.com/hsp.html
    if (0.299 * r**2 + 0.587 * g**2 + 0.114 * b**2) > 16256:
        return light_mode_display_text_color
    else:
        return dark_mode_display_text_color
    
def widget_pressed(widget, colors):
    """
    Sets widget to pressed appearance

    widget: The pressed widget, tkinter widget
    """
    widget.config({'background': colors.get('pressed_widget_color')})

def widget_released(widget, colors):
    """
    Restores given widget to unpressed appearance
    
    widget: The pressed widget, tkinter widget
    """
    widget.config({'background': colors.get('widget_color')})

def widget_focus(widget):
    """
    If widget exists, sets focus on it

    widget: The widget to focus on, tkinter widget
    """
    try:
        if widget.winfo_exists():
            widget.focus_set()
    except:
        pass