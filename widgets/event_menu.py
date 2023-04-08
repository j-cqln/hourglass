import calendar

import tkinter as tk
from tkinter.colorchooser import askcolor

from utilities.constants import NUMBER_HOURS_IN_DAY, NUMBER_MINUTES_IN_HOUR
from utilities.functions import light_or_dark_mode_text, widget_pressed, widget_released

class EventMenu:
    """
    Class for the event edit/remove menu

    Creates a GUI popup for Hourglass
    """
    def __init__(self, parent, root, key, event_info):
        """
        Initializes the EventMenu class

        parent: Parent widget, tkinter widget
        darkmode: Whether the parent is currently in dark mode or not, boolean
        key: Tuple of strings, (yyyy, mm, dd)
        event_info: Event information, dict
        minutes_in_hour: The number of minutes in an hour, int
        hours_in_day: The number of hours in a day, int
        """
        # Parent Hourglass
        self._parent = parent

        # Set event information
        self._key = key
        self._event_info = event_info.copy()
        self._current_event_hex = self._event_info.get('hex_color')
        self._selected = None

        # Window
        self._root = tk.Toplevel(root)

        # Title
        self._root.title('edit event...')
        
        # Font
        self._root.option_add('*Font', 'helvetica')

        # Set window size
        self._width = 500
        self._height = 300
        self._root.geometry('{}x{}'.format(self._width, self._height))

        # Set window position
        self._x = root.winfo_x() + int(root.winfo_width() / 4)
        self._y = root.winfo_y() + int(root.winfo_height() / 4)
        self._root.geometry('+{}+{}'.format(self._x, self._y))

        # Window not resizable
        self._root.wm_resizable(False, False)
        self._root.update()

        # Row and column weights for widget placement
        self._root.columnconfigure(0, weight=1)
        
        self._root.rowconfigure(0, weight=0)
        self._root.rowconfigure(1, weight=0)
        self._root.rowconfigure(2, weight=0)
        self._root.rowconfigure(3, weight=1)
        self._root.rowconfigure(4, weight=0)

        # Set up widgets
        self._date_recurrence_setup()
        self._time_color_duration_setup()
        self._text_setup()
        self._buttons_setup()

        # Change display colors based on theme
        self._change_colors()
    
    def _date_recurrence_setup(self):
        """
        Sets up the event date and event recurrence component of the popup window
        """
        # Frame for date and recurrence
        self._date_recurrence_frame = tk.Frame(self._root, borderwidth=0, highlightthickness=0)
        self._date_recurrence_frame.grid(row=0, column=0, padx=(6, 6), pady=(6, 3), sticky='NWSE')
        
        self._date_recurrence_frame.columnconfigure(0, weight=0)
        self._date_recurrence_frame.columnconfigure(1, weight=0)

        # Event date
        self._date_label = tk.Label(self._date_recurrence_frame, text=calendar.month_name[int(self._key[1])] + ' ' + self._key[2] + ', ' + self._key[0], borderwidth=0, highlightthickness=0)
        self._date_label.grid(row=0, column=0, padx=(0, 3), sticky='NWSE')

        # Event recurrence
        if self._event_info.get('frequency').strip() == 'none':
            recurrence_text = 'Not recurring'
        else:
            recurrence_text = 'Recurring ' + self._event_info.get('frequency').strip() + ', ' + str(int(self._event_info.get('amount'))) + ' times'
        
        self._recurrence_label = tk.Label(self._date_recurrence_frame, text=recurrence_text, borderwidth=0, highlightthickness=0)
        self._recurrence_label.grid(row=0, column=1, padx=(3, 0), sticky='NWSE')

    def _time_color_duration_setup(self):
        """
        Sets up the event time, color, and event duration component of the popup window
        """
        # Frame for start time and color
        self._time_color_frame = tk.Frame(self._root, borderwidth=0, highlightthickness=0)
        self._time_color_frame.grid(row=1, column=0, padx=(6, 6), pady=(3, 3), sticky='NWSE')
        
        self._time_color_frame.columnconfigure(0, weight=1)

        for i in range(4):
            self._time_color_frame.columnconfigure(i, weight=0)

        # Frame for duration
        self._duration_frame = tk.Frame(self._root, borderwidth=0, highlightthickness=0)
        self._duration_frame.grid(row=2, column=0, padx=(6, 6), pady=(3, 3), sticky='NWSE')

        # For selecting color
        self._color_selection_label = tk.Label(self._time_color_frame, text='   ✏   ', borderwidth=0, highlightthickness=0)
        self._color_selection_label.bind('<Button-1>', self._choose_color)
        self._color_selection_label.grid(row=0, column=0, padx=(0, 3), sticky='NWSE')

        # For selecting event start time
        # For selecting event start hour
        self._current_event_hour = tk.StringVar(self._time_color_frame)
        self._current_event_hour.set(self._event_info.get('hour'))
        self._dropdown_hours = [str(i).zfill(2) for i in range(0, NUMBER_HOURS_IN_DAY)]
        self._hour_selection_menu = tk.OptionMenu(self._time_color_frame, self._current_event_hour, *self._dropdown_hours)
        self._hour_selection_menu.config({'borderwidth': 0, 'highlightthickness': 0})
        self._hour_selection_menu.grid(row=0, column=1, padx=(3, 0), pady=(2, 0), sticky='NWSE')

        # For hour:minute formatting
        self._time_separator_label = tk.Label(self._time_color_frame, text=':', justify='center', borderwidth=0, highlightthickness=0)
        self._time_separator_label.grid(row=0, column=2, sticky='NWSE')

        # For selecting event start minute
        self._current_event_minute = tk.StringVar(self._time_color_frame)
        self._current_event_minute.set(self._event_info.get('minute'))
        self._dropdown_minutes = [str(i).zfill(2) for i in range(NUMBER_MINUTES_IN_HOUR)]
        self._minute_selection_menu = tk.OptionMenu(self._time_color_frame, self._current_event_minute, *self._dropdown_minutes)
        self._minute_selection_menu.config({'borderwidth': 0, 'highlightthickness': 0})
        self._minute_selection_menu.grid(row=0, column=3, padx=(1, 0), pady=(2, 0), sticky='NWSE')

        # For selecting event duration
        # Duration label
        self._event_duration_label = tk.Label(self._duration_frame, text='duration (optional):', justify='center', borderwidth=0, highlightthickness=0)
        self._event_duration_label.grid(row=0, column=0, pady=(0, 2), sticky='NWSE')

        # For selecting duration hour
        self._current_event_duration_hour = tk.StringVar(self._duration_frame)
        self._current_event_duration_hour.set(self._event_info.get('duration_hour'))
        self._dropdown_duration_hour = [str(i).zfill(2) for i in range(NUMBER_HOURS_IN_DAY)]
        self._duration_hour_menu = tk.OptionMenu(self._duration_frame, self._current_event_duration_hour, *self._dropdown_duration_hour)
        self._duration_hour_menu.grid(row=0, column=1, padx=(3, 3), sticky='NWSE')

        # Duration hour label
        self._event_duration_hour_label = tk.Label(self._duration_frame, text='hour(s)', justify='center', borderwidth=0, highlightthickness=0)
        self._event_duration_hour_label.grid(row=0, column=2, pady=(0, 2), sticky='NWSE')

        # For selecting duration minute
        self._current_event_duration_minute = tk.StringVar(self._duration_frame)
        self._current_event_duration_minute.set(self._event_info.get('duration_minute'))
        self._dropdown_duration_minute = [str(i).zfill(2) for i in range(NUMBER_MINUTES_IN_HOUR)]
        self._duration_minute_menu = tk.OptionMenu(self._duration_frame, self._current_event_duration_minute, *self._dropdown_duration_minute)
        self._duration_minute_menu.grid(row=0, column=3, padx=(3, 3), sticky='NWSE')

        # Duration minute label
        self._event_duration_minute_label = tk.Label(self._duration_frame, text='minute(s)', justify='center', borderwidth=0, highlightthickness=0)
        self._event_duration_minute_label.grid(row=0, column=4, padx=(0, 3), pady=(0, 2), sticky='NWSE')

    def _text_setup(self):
        """
        Sets up the event description component of the popup window
        """
        # Event description
        self._text = tk.Text(self._root, width=1, height=1, borderwidth=0, highlightthickness=0)
        self._text.insert(tk.END, self._event_info.get('description'))
        self._text.grid(row=3, column=0, padx=(6, 6), pady=(3, 3), sticky='NWSE')

    def _buttons_setup(self):
        """
        Sets up the edit/remove and cancel buttons of the popup window
        """
        # Frame for buttons
        self._buttons_frame = tk.Frame(self._root, borderwidth=0, highlightthickness=0)
        self._buttons_frame.grid(row=4, column=0, padx=(6, 6), pady=(3, 6), sticky='NWSE')

        self._buttons_frame.columnconfigure(0, weight=3)

        for i in range(1, 5):
            self._buttons_frame.columnconfigure(i, weight=2)

        # Edit button
        self._edit_button = tk.Label(self._buttons_frame, text='edit', borderwidth=0, highlightthickness=0)
        self._edit_button.bind('<Button-1>', lambda event: self._select(event.widget, 'edit'))
        self._edit_button.bind('<ButtonRelease>', lambda event: widget_released(event.widget, self._parent.colors))
        self._edit_button.grid(row=0, column=0, padx=(50, 3), sticky='NWSE')

        # Edit all button
        self._edit_all_button = tk.Label(self._buttons_frame, text='edit all', borderwidth=0, highlightthickness=0)

        if self._event_info.get('frequency').strip() != 'none':
            self._edit_all_button.bind('<Button-1>', lambda event: self._select(event.widget, 'edit_all'))

        self._edit_all_button.bind('<ButtonRelease>', lambda event: widget_released(event.widget, self._parent.colors))
        self._edit_all_button.grid(row=0, column=1, padx=(3, 3), sticky='NWSE')

        # Remove button
        self._remove_button = tk.Label(self._buttons_frame, text='remove', borderwidth=0, highlightthickness=0)
        self._remove_button.bind('<Button-1>', lambda event: self._select(event.widget, 'remove'))
        self._remove_button.bind('<ButtonRelease>', lambda event: widget_released(event.widget, self._parent.colors))
        self._remove_button.grid(row=0, column=2, padx=(3, 3), sticky='NWSE')

        # Remove all button
        self._remove_all_button = tk.Label(self._buttons_frame, text='remove all', borderwidth=0, highlightthickness=0)

        if self._event_info.get('frequency').strip() != 'none':
            self._remove_all_button.bind('<Button-1>', lambda event: self._select(event.widget, 'remove_all'))

        self._remove_all_button.bind('<ButtonRelease>', lambda event: widget_released(event.widget, self._parent.colors))
        self._remove_all_button.grid(row=0, column=3, padx=(3, 3), sticky='NWSE')

        # Cancel button
        self._cancel_button = tk.Label(self._buttons_frame, text='cancel', borderwidth=0, highlightthickness=0)
        self._cancel_button.bind('<Button-1>', lambda event: self._select(event.widget, None))
        self._cancel_button.bind('<ButtonRelease>', lambda event: widget_released(event.widget, self._parent.colors))
        self._cancel_button.grid(row=0, column=4, padx=(3, 0), sticky='NWSE')
    
    def _choose_color(self, *args):
        """
        Selects color for event
        """
        self._color_selection_dialog = askcolor(title='choose new event color...')
        self._color_selection_label.config({'background': self._color_selection_dialog[1]})
        self._current_event_hex = self._color_selection_dialog[1]
        
        # If a color was selected
        if self._color_selection_dialog[0] is not None:
            (r, g, b) = self._color_selection_dialog[0]
            self._color_selection_label.config({'foreground': light_or_dark_mode_text((r, g, b))})
    
    def _select(self, widget, selection):
        """
        Selects action for event

        widget: The widget clicked by the user to make the selection
        selection: Action for the event, either the strings 'edit', 'edit_all', 'remove', 'remove_all', or None for cancel
        """
        widget_pressed(widget, self._parent.colors)

        self._selected = selection

        if selection is not None:
            self._event_info['hour'] = self._current_event_hour.get()
            self._event_info['minute'] = self._current_event_minute.get()
            self._event_info['duration_hour'] = self._current_event_duration_hour.get()
            self._event_info['duration_minute'] = self._current_event_duration_minute.get()
            self._event_info['hex_color'] = self._current_event_hex
            self._event_info['description'] = self._text.get('1.0', tk.END).strip()

        self._root.destroy()
    
    def _change_colors(self, parent=None):
        """
        Changes colors for widget and all descendant widgets based on current theme mode

        parent: Widget to change color for, tkinter widget
        """
        # If no widget provided, start at root
        if parent is None:
            parent = self._root
            parent.config({'background': self._parent.colors.get('background_color')})
        
        # Change color for all descendant widgets
        for child in parent.winfo_children():
            if child.winfo_children():
                self._change_colors(parent=child)

            if type(child) is tk.Label:
                if child is self._color_selection_label:
                    child.config({'foreground': light_or_dark_mode_text(tuple(int(self._current_event_hex[1:][i:i + 2], 16) for i in (0, 2, 4)))})
                    child.config({'background': self._current_event_hex})
                elif parent is self._date_recurrence_frame:
                    child.config({'foreground': self._parent.colors.get('entry_text_color')})
                    child.config({'background': self._parent.colors.get('background_color')})
                elif parent is self._time_color_frame:
                    child.config({'foreground': self._parent.colors.get('label_text_color')})
                    child.config({'background': self._parent.colors.get('background_color')})
                elif parent is self._duration_frame:
                    child.config({'foreground': self._parent.colors.get('prompt_text_color')})
                    child.config({'background': self._parent.colors.get('background_color')})
                elif self._event_info.get('frequency').strip() == 'none' and child in [self._edit_all_button, self._remove_all_button]:
                    child.config({'foreground': self._parent.colors.get('faint_text_color')})
                    child.config({'background': self._parent.colors.get('widget_color')})
                else:
                    child.config({'foreground': self._parent.colors.get('label_text_color')})
                    child.config({'background': self._parent.colors.get('widget_color')})
            
            elif type(child) is tk.OptionMenu:
                child.config({'foreground': self._parent.colors.get('menu_text_color')})
                child.config({'background': self._parent.colors.get('background_color')})
            
            elif type(child) is tk.Text:
                child.config({'foreground': self._parent.colors.get('prompt_text_color')})
                child.config({'background': self._parent.colors.get('widget_color')})

            elif type(child) is tk.Frame:
                child.config({'background': self._parent.colors.get('background_color')})

    def show(self):
        """
        Shows the popup window and waits for it to be closed, then returning the user's modifications to the event

        return: Tuple containing the selection of the user and the modifications to the event information
        """
        self._root.deiconify()
        self._root.wait_window(self._root)
        return (self._selected, self._event_info)