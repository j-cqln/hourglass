import tkinter as tk
from tkinter import messagebox

from utilities.functions import widget_pressed, widget_released

class SettingsWidget:
    """
    Class for settings megawidget
    """
    def __init__(self, parent, root):
        """
        Sets up the settings component of the GUI
        """
        # Parent Hourglass
        self._parent = parent

        # Root window
        self._root = root

        # Frame for all settings widgets
        self._settings_frame = tk.Frame(self._root, borderwidth=0, highlightthickness=0)
        self._settings_frame.grid(row=3, column=1, padx=(6, 6), pady=(3, 7), sticky='NWSE')
        
        self._settings_frame.rowconfigure(0, weight=1)
        self._settings_frame.columnconfigure(0, weight=2)
        self._settings_frame.columnconfigure(1, weight=1)
        self._settings_frame.columnconfigure(2, weight=1)
        self._settings_frame.columnconfigure(3, weight=1)
        self._settings_frame.columnconfigure(4, weight=1)

        # For saving into text file
        self._save_label = tk.Label(self._settings_frame, text='save', borderwidth=0, highlightthickness=0)
        self._save_label.bind('<Button-1>', lambda event: self._save())
        self._save_label.bind('<ButtonRelease>', lambda event: widget_released(self._save_label, self._parent.colors))
        self._save_label.grid(row=0, column=1, padx=(0, 3), sticky='NWSE')

        # For toggling notifications
        self._notification_label = tk.Label(self._settings_frame, text='⌛︎: on', borderwidth=0, highlightthickness=0)
        self._notification_label.bind('<Button-1>', self._toggle_notify)
        self._notification_label.bind('<ButtonRelease>', lambda event: widget_released(self._notification_label, self._parent.colors))
        self._notification_label.grid(row=0, column=2, padx=(3, 3), sticky='NWSE')

        # For switching between light/dark mode
        self._theme_mode_label = tk.Label(self._settings_frame, borderwidth=0, highlightthickness=0)
        self._theme_mode_label.bind('<Button-1>', self._set_theme_mode)
        self._theme_mode_label.grid(row=0, column=3, padx=(3, 3), sticky='NWSE')

        # For how-to/help
        self._how_to_label = tk.Label(self._settings_frame, text='?', borderwidth=0, highlightthickness=0)
        self._how_to_label.bind('<Button-1>', self._show_how_to)
        self._how_to_label.grid(row=0, column=4, padx=(3, 0), sticky='NWSE')

        # Set the theme
        self._set_theme_mode(change=False)
    
    def _save(self, *args):
        """
        Saves current schedule and to-do list
        """
        widget_pressed(self._save_label, self._parent.colors)

        # Save schedule and to-do list
        self._parent.save()
    
    def _toggle_notify(self, *args):
        """
        Toggles notifications on or off
        """
        widget_pressed(self._notification_label, self._parent.colors)

        self._parent.notify_mode = not self._parent.notify_mode
        
        if self._parent.notify_mode:
            self._notification_label.config({'text': '⌛︎: on'})
        else:
            self._notification_label.config({'text': '⌛︎: off'})
    
    def _set_theme_mode(self, change=True, *args):
        """
        Sets theme mode for application

        change: Whether to change between light/dark mode, boolean
        """
        if change:
            self._parent.is_dark_mode = not self._parent.is_dark_mode
            self._parent.change_colors()
        
        if self._parent.is_dark_mode:
            self._theme_mode_label.config(text='☾')
        else:
            self._theme_mode_label.config(text='☼')
    
    def _show_how_to(self, *args):
        """
        Displays how-to message
        """
        msg = messagebox.showinfo('your hourglass',
                                    'press enter to add event/task\n' +
                                    'right click to edit/remove\n\n' +
                                    'click on days in monthly calendar ' +
                                    'to display events for that week\n\n' +
                                    'sun/moon → light/dark mode\n' +
                                    'pencil → custom event color')
    
    def change_colors(self):
        """
        Changes colors for this megawidget and all descendant widgets based on current theme mode
        """
        # Change color for all descendant widgets
        self._settings_frame.config({'background': self._parent.colors.get('background_color')})

        for widget in [self._save_label, self._notification_label, self._theme_mode_label, self._how_to_label]:
            widget.config({'foreground': self._parent.colors.get('label_text_color')})
            widget.config({'background': self._parent.colors.get('widget_color')})