import uuid
import calendar
import datetime

import tkinter as tk
from tkinter.colorchooser import askcolor

from utilities.constants import NUMBER_YEARS, NUMBER_MONTHS_IN_YEAR, NUMBER_HOURS_IN_DAY, NUMBER_MINUTES_IN_HOUR, NUMBER_EVENT_RECURRENCE, CHECKBUTTON_OFF, CHECKBUTTON_ON
from utilities.functions import light_or_dark_mode_text

class EventEntryWidget:
    """
    Class for megawidget for entering event information
    """
    def __init__(self, parent, root):
        """
        Sets up the GUI component for entering event information
        """
        # Parent Hourglass
        self._parent = parent

        # Root window
        self._root = root

        # Sunday to Saturday calendar
        self._new_event_calendar = calendar.Calendar(firstweekday=6)
        
        # Frame for all event entry widgets
        self._event_entry_frame = tk.Frame(self._root, borderwidth=0, highlightthickness=0)
        self._event_entry_frame.grid(row=2, column=0, rowspan=2, padx=(6, 6), pady=(3, 6), sticky='NWSE')

        self._event_entry_frame.rowconfigure(0, weight=0)
        self._event_entry_frame.rowconfigure(1, weight=0)
        self._event_entry_frame.columnconfigure(0, weight=1)

        # Frame for primary event information
        self._event_entry_primary_frame = tk.Frame(self._event_entry_frame, borderwidth=0, highlightthickness=0)
        self._event_entry_primary_frame.grid(row=0, column=0, pady=(0, 3), sticky='NWSE')

        self._event_entry_primary_frame.columnconfigure(0, weight=11)
        self._event_entry_primary_frame.columnconfigure(1, weight=1)

        for i in range(2, 9):
            self._event_entry_primary_frame.columnconfigure(i, weight=0)

        self._event_entry_primary_frame.columnconfigure(9, weight=2)

        # Frame for secondary event information
        self._event_entry_secondary_frame = tk.Frame(self._event_entry_frame, borderwidth=0, highlightthickness=0)
        self._event_entry_secondary_frame.grid(row=1, column=0, pady=(3, 0), sticky='NWSE')
        
        for i in range(10):
            self._event_entry_secondary_frame.columnconfigure(i, weight=0)
        
        # For entering event description
        self._event_entry_variable = tk.StringVar(self._event_entry_primary_frame)
        self._event_entry = tk.Entry(self._event_entry_primary_frame, textvariable=self._event_entry_variable, borderwidth=0, highlightthickness=0)
        self._event_entry.insert(0, ' add new event...')
        self._event_entry.bind('<FocusIn>', self._event_entry_focus)
        self._event_entry.bind('<FocusOut>', self._event_entry_unfocus)
        self._event_entry.bind('<Return>', self._event_entry_enter)
        self._event_entry.grid(row=0, column=0, padx=(0, 3), sticky='NWSE')

        # For selecting color
        self._color_selection_label = tk.Label(self._event_entry_primary_frame, text='✏', borderwidth=0, highlightthickness=0)
        self._color_selection_label.bind('<Button-1>', self._choose_color)
        self._color_selection_label.grid(row=0, column=1, padx=(3, 3), sticky='NWSE')

        # For selecting event date; possible days update based on currently selected month
        # For selecting event year
        self._current_event_year = tk.StringVar(self._event_entry_primary_frame)
        self._current_event_year.set(str(self._parent.now.year))
        self._current_event_year.trace('w', self._update_time_date_menu)
        self._dropdown_years = [str(i) for i in range(self._parent.now.year - NUMBER_YEARS, self._parent.now.year + NUMBER_YEARS + 1)]
        self._year_selection_menu = tk.OptionMenu(self._event_entry_primary_frame, self._current_event_year, *self._dropdown_years)
        self._year_selection_menu.config({'borderwidth': 0, 'highlightthickness': 0})
        self._year_selection_menu.grid(row=0, column=2, padx=(2, 3), pady=(2, 0), sticky='NWSE')

        # For selecting event month
        self._current_event_month = tk.StringVar(self._event_entry_primary_frame)
        self._current_event_month.set(str(self._parent.now.month).zfill(2))
        self._current_event_month.trace('w', self._update_time_date_menu)
        self._dropdown_months = [str(i).zfill(2) for i in range(1, NUMBER_MONTHS_IN_YEAR + 1)]
        self._month_selection_menu = tk.OptionMenu(self._event_entry_primary_frame, self._current_event_month, *self._dropdown_months)
        self._month_selection_menu.config({'borderwidth': 0, 'highlightthickness': 0})
        self._month_selection_menu.grid(row=0, column=3, padx=(3, 1), pady=(2, 0), sticky='NWSE')
        
        # For month/day formatting
        self._date_separator_label = tk.Label(self._event_entry_primary_frame, text='/', justify='center', borderwidth=0, highlightthickness=0)
        self._date_separator_label.grid(row=0, column=4, sticky='NWSE')

        # For selecting event day
        self._current_event_day = tk.StringVar(self._event_entry_primary_frame)
        self._current_event_day.set(str(self._parent.now.day).zfill(2))

        self._dropdown_days = []
        for day in self._new_event_calendar.itermonthdays(self._parent.now.year, self._parent.now.month):
            if day != 0:
                self._dropdown_days.append(str(day).zfill(2))
        
        self._day_selection_menu = tk.OptionMenu(self._event_entry_primary_frame, self._current_event_day, *self._dropdown_days)
        self._day_selection_menu.config({'borderwidth': 0, 'highlightthickness': 0})
        self._day_selection_menu.grid(row=0, column=5, padx=(1, 3), pady=(2, 0), sticky='NWSE')

        # For selecting event start time
        # For selecting event start hour
        self._current_event_hour = tk.StringVar(self._event_entry_primary_frame)
        self._current_event_hour.set(str(self._parent.now.hour).zfill(2))
        self._dropdown_hours = [str(i).zfill(2) for i in range(0, NUMBER_HOURS_IN_DAY)]
        self._hour_selection_menu = tk.OptionMenu(self._event_entry_primary_frame, self._current_event_hour, *self._dropdown_hours)
        self._hour_selection_menu.config({'borderwidth': 0, 'highlightthickness': 0})
        self._hour_selection_menu.grid(row=0, column=6, padx=(3, 0), pady=(2, 0), sticky='NWSE')

        # For hour:minute formatting
        self._time_separator_label = tk.Label(self._event_entry_primary_frame, text=':', justify='center', borderwidth=0, highlightthickness=0)
        self._time_separator_label.grid(row=0, column=7, sticky='NWSE')

        # For selecting event start minute
        self._current_event_minute = tk.StringVar(self._event_entry_primary_frame)
        self._current_event_minute.set(str(self._parent.now.minute).zfill(2))
        self._dropdown_minutes = [str(i).zfill(2) for i in range(NUMBER_MINUTES_IN_HOUR)]
        self._minute_selection_menu = tk.OptionMenu(self._event_entry_primary_frame, self._current_event_minute, *self._dropdown_minutes)
        self._minute_selection_menu.config({'borderwidth': 0, 'highlightthickness': 0})
        self._minute_selection_menu.grid(row=0, column=8, padx=(1, 0), pady=(2, 0), sticky='NWSE')

        # For selecting event duration
        # Duration label
        self._event_duration_label = tk.Label(self._event_entry_secondary_frame, text='duration (optional):', justify='center', borderwidth=0, highlightthickness=0)
        self._event_duration_label.grid(row=0, column=0, pady=(0, 2), sticky='NWSE')

        # For selecting duration hour
        self._current_event_duration_hour = tk.StringVar(self._event_entry_secondary_frame)
        self._current_event_duration_hour.set('0'.zfill(2))
        self._dropdown_duration_hour = [str(i).zfill(2) for i in range(NUMBER_HOURS_IN_DAY)]
        self._duration_hour_menu = tk.OptionMenu(self._event_entry_secondary_frame, self._current_event_duration_hour, *self._dropdown_duration_hour)
        self._duration_hour_menu.grid(row=0, column=1, padx=(3, 3), sticky='NWSE')

        # Duration hour label
        self._event_duration_hour_label = tk.Label(self._event_entry_secondary_frame, text='hour(s)', justify='center', borderwidth=0, highlightthickness=0)
        self._event_duration_hour_label.grid(row=0, column=2, pady=(0, 2), sticky='NWSE')

        # For selecting duration minute
        self._current_event_duration_minute = tk.StringVar(self._event_entry_secondary_frame)
        self._current_event_duration_minute.set('0'.zfill(2))
        self._dropdown_duration_minute = [str(i).zfill(2) for i in range(NUMBER_MINUTES_IN_HOUR)]
        self._duration_minute_menu = tk.OptionMenu(self._event_entry_secondary_frame, self._current_event_duration_minute, *self._dropdown_duration_minute)
        self._duration_minute_menu.grid(row=0, column=3, padx=(3, 3), sticky='NWSE')

        # Duration minute label
        self._event_duration_minute_label = tk.Label(self._event_entry_secondary_frame, text='minute(s)', justify='center', borderwidth=0, highlightthickness=0)
        self._event_duration_minute_label.grid(row=0, column=4, padx=(0, 3), pady=(0, 2), sticky='NWSE')

        # For selecting event recurrence
        # Recurrence label
        self._event_recurrence_prompt_label = tk.Label(self._event_entry_secondary_frame, text='recurring', justify='center', borderwidth=0, highlightthickness=0)
        self._event_recurrence_prompt_label.grid(row=0, column=5, padx=(5, 0), pady=(0, 2), sticky='NWSE')

        # For selecting event recurrence frequency
        self._current_event_recurrence_frequency = tk.StringVar(self._event_entry_secondary_frame)
        self._current_event_recurrence_frequency.set('none')
        self._dropdown_event_recurrence_frequency = ['none', 'daily', 'weekly', 'monthly', 'yearly']
        self._event_recurrence_frequency_dictionary = {'none': None, 'daily': 1, 'weekly': 7, 'monthly': 30, 'yearly': 365}
        self._event_recurrence_frequency_menu = tk.OptionMenu(self._event_entry_secondary_frame, self._current_event_recurrence_frequency, *self._dropdown_event_recurrence_frequency)
        self._event_recurrence_frequency_menu.grid(row=0, column=6, padx=(3, 2), sticky='NWSE')

        # For selecting event recurrence amount
        self._current_event_recurrence_amount = tk.StringVar(self._event_entry_secondary_frame)
        self._current_event_recurrence_amount.set(1)
        self._dropdown_event_recurrence_amount = [i for i in range(1, NUMBER_EVENT_RECURRENCE + 1)] + [12, 14, 15, 30, 60, 90, 180, 365]
        self._event_recurrence_amount_menu = tk.OptionMenu(self._event_entry_secondary_frame, self._current_event_recurrence_amount, *self._dropdown_event_recurrence_amount)
        self._event_recurrence_amount_menu.grid(row=0, column=7, padx=(2, 3), sticky='NWSE')

        # Recurrence amount label
        self._event_recurrence_times_label = tk.Label(self._event_entry_secondary_frame, text='times', justify='center', borderwidth=0, highlightthickness=0)
        self._event_recurrence_times_label.grid(row=0, column=8, padx=(0, 0), pady=(0, 2), sticky='NWSE')

        # Leap years check box
        self._leap_years_mode = tk.IntVar(self._event_entry_secondary_frame)
        self._leap_years_mode.set(CHECKBUTTON_ON)
        self._leap_years_checkbutton = tk.Checkbutton(self._event_entry_secondary_frame, text='leap years?', variable=self._leap_years_mode, onvalue=CHECKBUTTON_ON, offvalue=CHECKBUTTON_OFF, anchor='w', justify='left')
        self._leap_years_checkbutton.grid(row=0, column=9, padx=(3, 3), pady=(0, 2), sticky='NWSE')
        
        # Bug: entry widgets do not immediately display correctly without text widget on screen
        # Temporary bug fix
        self._placeholder_frame_widget = tk.Label(self._event_entry_primary_frame, borderwidth=0, highlightthickness=0)
        self._placeholder_frame_widget.grid(row=0, column=9)

        self._placeholder_text_widget = tk.Text(self._event_entry_primary_frame, height=1, width=1, takefocus=0, borderwidth=0, highlightthickness=0)
        self._placeholder_text_widget.config({'state': 'disabled'})
        self._placeholder_text_widget.grid(row=0, column=9, in_=self._placeholder_frame_widget)
        self._placeholder_text_widget.lower()
    
    def _choose_color(self, *args):
        """
        Selects color for event
        """
        self._color_selection_dialog = askcolor(title='choose new event color...')
        self._color_selection_label.config({'background': self._color_selection_dialog[1]})
        self._current_event_hex = self._color_selection_dialog[1]
        
        if self._color_selection_dialog[0] is not None:
            (r, g, b) = self._color_selection_dialog[0]
            self._color_selection_label.config({'foreground': light_or_dark_mode_text((r, g, b))})
    
    def _schedule_add(self, key, hour, minute, duration_hour, duration_minute, hex_color, description, frequency, amount, leap_years):
        """
        Adds an event to the schedule

        key: Tuple of strings, (yyyy, mm, dd)
        hour: Event start time hour, hh, string
        minute: Event start minute, mm, string
        duration_hour: Event duration hour, hh, string
        duration_minute: Event duration minute, mm, string
        hex_color: Hex color, string
        description: Event description, string
        frequency: Event recurrence frequency, string
        amount: Event recurrence amount, string
        leap_years: Whether to account for leap years for yearly recurring events, int
        """
        # Event and recurrence UUID
        event_id = str(uuid.uuid4())
        recurrence_id = str(uuid.uuid4())

        # Whether event is recurring
        delta = self._event_recurrence_frequency_dictionary.get(frequency)

        # Recurrence amount formatting
        if delta is None:
            amount = '1'
        
        amount = amount.zfill(3)

        # Add event
        event_info = {'hour': hour, 'minute': minute, 'duration_hour': duration_hour, 'duration_minute': duration_minute, 'hex_color': hex_color, 'recurrence_id': recurrence_id, 'frequency': frequency.rjust(7), 'amount': amount, 'description': description, 'ten_minute_notified': False, 'one_minute_notified': False}
        self._parent.schedule.setdefault(key, {}).update({event_id: event_info})

        # If event is recurring, add its recurrences
        if delta is not None:
            # Leap years mode
            if leap_years == CHECKBUTTON_ON and frequency == 'yearly':
                for i in range(1, int(amount)):
                    try:
                        # Recurrence date
                        date = datetime.datetime(int(key[0]) + i, int(key[1]), int(key[2]))
                        new_key = (str(date.year), str(date.month).zfill(2), str(date.day).zfill(2))

                        # UUID of this recurrence
                        event_id = str(uuid.uuid4())

                        # Add recurrence
                        self._parent.schedule.setdefault(new_key, {}).update({event_id: event_info})
                    except:
                        pass
            else:
                for i in range(1, int(amount)):
                    # Recurrence date
                    date = datetime.datetime(int(key[0]), int(key[1]), int(key[2])) + datetime.timedelta(days=i * delta)
                    new_key = (str(date.year), str(date.month).zfill(2), str(date.day).zfill(2))

                    # UUID of this recurrence
                    event_id = str(uuid.uuid4())

                    # Add recurrence
                    self._parent.schedule.setdefault(new_key, {}).update({event_id: event_info})

        # Update displayed week
        self._parent.update_week()
    
    def _update_time_date_menu(self, *args):
        """
        Updates event day options based on currently selected year and month
        """
        event_year = int(self._current_event_year.get())

        # Retrieve month without leading zero
        if self._current_event_month.get()[0] == '0':
            event_month = int(self._current_event_month.get()[1])
        else:
            event_month = int(self._current_event_month.get())

        self._dropdown_days = []

        # Set options for day based on selected month and year
        for day in self._new_event_calendar.itermonthdays(event_year, event_month):
            if day != 0:
                self._dropdown_days.append(str(day).zfill(2))
        
        if self._current_event_day.get() not in self._dropdown_days:
            self._current_event_day.set(self._dropdown_days[0])
        
        self._day_selection_menu['menu'].delete(0, tk.END)

        for day in self._dropdown_days:
            self._day_selection_menu['menu'].add_command(label=day, command=lambda day=day: self._current_event_day.set(day))
    
    def update_event_entry_date(self, days):
        """
        Updates event entry date based on the displayed day clicked by the user
        
        days: The clicked day represented as the number of days after the displayed Sunday, int
        """
        clicked_day = self._parent.displayed_sunday + datetime.timedelta(days=days)

        self._current_event_year.set(str(clicked_day.year))
        self._current_event_month.set(str(clicked_day.month).zfill(2))
        self._current_event_day.set(str(clicked_day.day).zfill(2))
    
    def _event_entry_focus(self, *args):
        """
        Focuses on the event entry widget, remove prompt text if it is displayed
        """
        if self._event_entry.get() == ' add new event...':
            self._event_entry.delete(1, tk.END)
            
        self._event_entry.config({'foreground': self._parent.colors.get('entry_text_color')})

    def _event_entry_unfocus(self, *args):
        """
        Unfocuses from the event entry widget, restoring prompt text if no text entered
        """
        if self._event_entry.get() == '' or self._event_entry.get() == ' ':
            self._event_entry.delete(0, tk.END)
            self._event_entry.insert(0, ' add new event...')

        self._event_entry.config({'foreground': self._parent.colors.get('prompt_text_color')})
        self._root.focus_set()

    def _event_entry_enter(self, *args):
        """
        When enter is pressed and focus is on the event entry widget, remove focus and add event
        """
        if self._event_entry.get() != ' add new event...':
            self._schedule_add(self._get_event_date(),
                                self._get_event_hour(),
                                self._get_event_minute(),
                                self._get_event_duration_hour(),
                                self._get_event_duration_minute(),
                                self._current_event_hex,
                                self._event_entry.get().strip(),
                                self._current_event_recurrence_frequency.get(),
                                self._current_event_recurrence_amount.get(),
                                self._leap_years_mode.get())
            self._event_entry.delete(0, tk.END)

        self._event_entry_unfocus()
    
    def _get_event_date(self):
        """
        Returns the current event date entered as a tuple

        return: Tuple of strings, (yyyy, mm, dd)
        """
        return (self._current_event_year.get(),
                self._current_event_month.get(),
                self._current_event_day.get())

    def _get_event_hour(self):
        """
        Returns the current event start hour entered

        return: Event start hour, hh, string
        """
        return self._current_event_hour.get()

    def _get_event_minute(self):
        """
        Returns the current event start minute entered

        return: Event start minute, mm, string
        """
        return self._current_event_minute.get()
    
    def _get_event_duration_hour(self):
        """
        Returns the current event duration hour entered

        return: Event duration hour, hh, string
        """
        return self._current_event_duration_hour.get()
    
    def _get_event_duration_minute(self):
        """
        Returns the current event duration minute entered

        return: Event duration minute, mm, string
        """
        return self._current_event_duration_minute.get()
    
    def change_colors(self):
        """
        Changes colors for this megawidget and all descendant widgets based on current theme mode
        """
        # Change color for all descendant widgets
        self._event_entry_frame.config({'background': self._parent.colors.get('background_color')})

        self._event_entry_primary_frame.config({'background': self._parent.colors.get('background_color')})

        self._event_entry_secondary_frame.config({'background': self._parent.colors.get('background_color')})

        self._event_entry.config({'foreground': self._parent.colors.get('prompt_text_color')})
        self._event_entry.config({'background': self._parent.colors.get('widget_color')})

        self._color_selection_label.config({'foreground': self._parent.colors.get('label_text_color')})
        self._color_selection_label.config({'background': self._parent.colors.get('widget_color')})
        self._current_event_hex = self._color_selection_label.cget('background')

        for widget in [self._year_selection_menu,
                        self._month_selection_menu,
                        self._day_selection_menu,
                        self._hour_selection_menu,
                        self._minute_selection_menu,
                        self._duration_hour_menu,
                        self._duration_minute_menu,
                        self._event_recurrence_frequency_menu,
                        self._event_recurrence_amount_menu]:
            widget.config({'foreground': self._parent.colors.get('menu_text_color')})
            widget.config({'background': self._parent.colors.get('background_color')})

        for widget in [self._date_separator_label,
                        self._time_separator_label]:
            widget.config({'foreground': self._parent.colors.get('label_text_color')})
            widget.config({'background': self._parent.colors.get('background_color')})
        
        for widget in [self._event_duration_label,
                        self._event_duration_label,
                        self._event_duration_hour_label,
                        self._event_duration_minute_label,
                        self._event_recurrence_prompt_label,
                        self._event_recurrence_times_label]:
            widget.config({'foreground': self._parent.colors.get('prompt_text_color')})
            widget.config({'background': self._parent.colors.get('background_color')})

        self._leap_years_checkbutton.config({'foreground': self._parent.colors.get('prompt_text_color')})
        self._leap_years_checkbutton.config({'background': self._parent.colors.get('background_color')})

        for widget in [self._placeholder_frame_widget, self._placeholder_text_widget]:
            widget.config({'foreground': self._parent.colors.get('background_color')})
            widget.config({'background': self._parent.colors.get('background_color')})