# Libraries
import os
import sys
import uuid
import calendar
import datetime

import tkinter as tk
from tkinter import font
from tkinter import messagebox
from tkinter.colorchooser import askcolor

class Hourglass:
    """
    Class for the Hourglass application

    Creates a GUI calendar and to-do list application
    """
    def __init__(self):
        """
        Initializes the Hourglass class
        """
        # Constants for time units
        self._NUMBER_MINUTES_IN_HOUR = 60
        self._NUMBER_HOURS_IN_DAY = 24
        self._NUMBER_DAYS_IN_WEEK = 7
        self._NUMBER_MONTHS_IN_YEAR = 12
        self._NUMBER_YEARS = 10

        # Number of recurrences for recurring events (in addition to some special values, the user can schedule 1 to n recurrences, where n is this constant)
        self._NUMBER_EVENT_RECURRENCE = 10

        # Number of weeks (including those with fewer days than the days in week constant above) in a month to display
        self._NUMBER_DISPLAY_WEEKS_IN_MONTH = 6

        # Maximum width of each event on the schedule in screen units
        self._EVENT_LABEL_WRAPLENGTH = 100

        # Constants for on/off values of check boxes
        self._CHECKBUTTON_ON = 1
        self._CHECKBUTTON_OFF = 0

        # Current moment
        self._now = datetime.datetime.now()

        # Sunday of the week for which events are displayed
        self._displayed_sunday = self._now - datetime.timedelta(days=(self._now.isoweekday() % self._NUMBER_DAYS_IN_WEEK))

        # Currently displayed month and year in the calendar
        self._displayed_month = self._now.month
        self._displayed_year = self._now.year

        # Default mode is dark mode
        self._is_dark_mode = True
        
        # Set colors used by application
        self._set_colors(self._is_dark_mode)
        self._dark_mode_display_text_color = '#c2c2c2'
        self._light_mode_display_text_color = '#4b4b4b'

        # GUI
        self._root = tk.Tk()

        # Font
        self._root.option_add('*Font', 'helvetica')

        # Adjust default GUI size based on screen size
        self._screen_width = self._root.winfo_screenwidth()
        self._screen_height = self._root.winfo_screenheight()
        self._width = int(self._screen_width * 0.7)
        self._height = int(self._screen_height * 0.7)
        self._root.geometry('%sx%s' % (self._width, self._height))
        self._root.update()

        # Adjust minimum and maximum size that GUI can be resized as
        self._root.minsize(int(self._root.winfo_width() * 0.8), int(self._root.winfo_height() * 0.8))
        self._root.maxsize(int(self._root.winfo_width() * 1.2), int(self._root.winfo_height() * 1.2))

        # Row and column weights for widget placement
        self._root.columnconfigure(0, weight=6)
        self._root.columnconfigure(1, weight=1)
        
        self._root.rowconfigure(0, weight=1)
        self._root.rowconfigure(1, weight=5)

        # Location and name of schedule and tasks files
        self._file_location = os.path.dirname('__file__')
        self._schedule_file_name = 'schedule.txt'
        self._to_do_list_file_name = 'tasks.txt'
        self._schedule_old_file_name = 'schedule_old.txt'
        self._to_do_list_old_file_name = 'tasks_old.txt'

        # Read from schedule and to-do list files
        self._schedule_read(self._schedule_file_name)
        self._to_do_read(self._to_do_list_file_name)
        
        # Set up GUI title and GUI widgets
        self._set_title()
        self._week_setup()
        self._event_entry_setup()
        self._calendar_setup()
        self._to_do_setup()
        self._settings_setup()

        # Set the theme
        self._set_theme_mode(change=False)

        # Allow all components of the GUI to be focusable on left click
        self._root.bind_all('<Button-1>', lambda event: self._widget_focus(event.widget))

        # Set up notification function
        self._notify()

        # Application loop
        self._root.mainloop()

        # Write to schedule and to-do list files
        try:
            self._schedule_write(self._schedule_file_name)
            self._to_do_write(self._to_do_list_file_name)
        except:
            # Display an error message then exit the application
            self._show_error('unable to write to schedule or to-do list files.')
            sys.exit(1)
    
    def _set_title(self):
        """
        Sets the title of the GUI window; calls itself each second to update
        """
        # Set title using current month and year
        self._now = datetime.datetime.now()
        self._root.title('hourglass  -  ' + self._now.strftime('%B %Y').lower())

        # Update again after 1 second
        self._root.after(1000, self._set_title)
    
    def _notify(self):
        """
        Checks for upcoming events and notifies user
        """
        self._now = datetime.datetime.now()
        
        try:
            # Check for upcoming events in the current day and the next day
            for i in range(2):
                date = self._now + datetime.timedelta(days=i)
                year = date.strftime('%Y')
                month = date.strftime('%m')
                day = date.strftime('%d')

                key = (year, month, day)
                value = self._schedule.get(key)

                if value is not None:
                    for event_id, event_info in value.items():
                        delta = datetime.datetime(year=int(year), month=int(month), day=int(day), hour=int(event_info.get('hour')), minute=int(event_info.get('minute'))) - self._now
                        
                        # Ten minute notification
                        if delta.total_seconds() < 600 and delta.total_seconds() > 60 and event_info.get('ten_minute_notified') is False:
                            event_info['ten_minute_notified'] = True
                            messagebox.showinfo(message='in ' + str(max(2, int(delta.total_seconds() / 60))) + ' minutes:\n' + event_info.get('description'))
                        
                        # One minute notification
                        elif delta.total_seconds() < 60 and delta.total_seconds() > 0 and event_info.get('one_minute_notified') is False:
                            event_info['one_minute_notified'] = True
                            messagebox.showinfo(message='in 1 minute:\n' + event_info.get('description'))
        except:
            pass
        
        # Update again after 1 second
        self._root.after(1000, self._notify)
    
    def _week_setup(self):
        """
        Sets up the week component of the GUI on which events are displayed
        """
        # Frame for all week-related widgets
        self._week_frame = tk.Frame(self._root, borderwidth=0, highlightthickness=0)
        self._week_frame.grid(row=0, column=0, rowspan=2, padx=(6, 3), pady=(6, 3), ipadx=6, ipady=6, sticky='NWSE')
        
        self._week_frame.rowconfigure(0, weight=0)
        self._week_frame.rowconfigure(1, weight=0)
        self._week_frame.rowconfigure(2, weight=1)

        for i in range(self._NUMBER_DAYS_IN_WEEK):
            self._week_frame.columnconfigure(i, weight=1, uniform='weekday')
        
        # Label indicating which week
        self._week_label = tk.Label(self._week_frame, anchor='w')
        self._week_label.grid(row=0, column=0, columnspan=2, padx=(3, 0), pady=(3, 0), sticky='NWS')

        # Frame for previous, current, and next week buttons
        self._week_buttons_frame = tk.Frame(self._week_frame, borderwidth=0, highlightthickness=0)
        self._week_buttons_frame.grid(row=0, column=4, columnspan=3, sticky='NSE')
        self._week_buttons_frame.columnconfigure(0, weight=1)
        self._week_buttons_frame.columnconfigure(1, weight=2)
        self._week_buttons_frame.columnconfigure(2, weight=1)

        # Button to go to previous week
        self._previous_week_label = tk.Label(self._week_buttons_frame, text='← prev. ', justify='left', borderwidth=0, highlightthickness=0)
        self._previous_week_label.bind('<Button-1>', self._previous_week)
        self._previous_week_label.bind('<ButtonRelease>', lambda event: self._widget_released(event.widget))
        self._previous_week_label.grid(row=0, column=0, sticky='NWSE')

        # Button to go to current week
        self._current_week_label = tk.Label(self._week_buttons_frame, text=' current ', justify='center', borderwidth=0, highlightthickness=0)
        self._current_week_label.bind('<Button-1>', self._current_week)
        self._current_week_label.bind('<ButtonRelease>', lambda event: self._widget_released(event.widget))
        self._current_week_label.grid(row=0, column=1, sticky='NS')

        # Button to go to next week
        self._next_week_label = tk.Label(self._week_buttons_frame, text=' next →', justify='right', borderwidth=0, highlightthickness=0)
        self._next_week_label.bind('<Button-1>', self._next_week)
        self._next_week_label.bind('<ButtonRelease>', lambda event: self._widget_released(event.widget))
        self._next_week_label.grid(row=0, column=2, sticky='NWSE')

        # Display week widgets
        self._week_days_labels = []
        self._week_days = []
        self._week_day_separators = [[] for _ in range(self._NUMBER_DAYS_IN_WEEK)]
        self._week_day_time_references = [[] for _ in range(self._NUMBER_DAYS_IN_WEEK)]

        for i in range(self._NUMBER_DAYS_IN_WEEK):
            # Label for the day of the week and the date
            self._week_days_labels.append(tk.Label(self._week_frame, anchor='w'))

            # Frame for each day
            self._week_days.append(tk.Frame(self._week_frame))
            self._week_days[i].grid(row=2, column=i, sticky='NWSE')

            self._week_days[i].columnconfigure(0, weight=0)
            self._week_days[i].columnconfigure(1, weight=1)

            # Visual differences between first day of week and others
            if i == 0:
                self._week_days_labels[i].grid(row=1, column=i, padx=(3, 0), sticky='NWS')

                # References to indicate time of day (first day of week has time)
                self._week_day_time_references[i].append(tk.LabelFrame(self._week_days[i], text='00:00', labelanchor='nw', borderwidth=0, highlightthickness=0))
                self._week_day_time_references[i][-1].place(relx=0, rely=0, relwidth=1, relheight=0.05)

                self._week_day_time_references[i].append(tk.LabelFrame(self._week_days[i], text='06:00', labelanchor='sw', borderwidth=0, highlightthickness=0))
                self._week_day_time_references[i][-1].place(relx=0, rely=0.23, relwidth=1, relheight=0.05)

                self._week_day_time_references[i].append(tk.LabelFrame(self._week_days[i], text='12:00', labelanchor='sw', borderwidth=0, highlightthickness=0))
                self._week_day_time_references[i][-1].place(relx=0, rely=0.48, relwidth=1, relheight=0.05)

                self._week_day_time_references[i].append(tk.LabelFrame(self._week_days[i], text='18:00', labelanchor='sw', borderwidth=0, highlightthickness=0))
                self._week_day_time_references[i][-1].place(relx=0, rely=0.73, relwidth=1, relheight=0.05)
                
            else:
                self._week_days_labels[i].grid(row=1, column=i, sticky='NWS')

                # Separates adjacent days visually
                self._week_day_separators[i].append(tk.Frame(self._week_days[i], borderwidth=0, highlightthickness=0))
                self._week_day_separators[i][-1].place(relx=0, rely=0, relwidth=0.01, relheight=1)
            
            # References to indicate time of day
            self._week_day_time_references[i].append(tk.Frame(self._week_days[i], borderwidth=0, highlightthickness=0))
            self._week_day_time_references[i][-1].place(relx=0.01, rely=0, relwidth=1, relheight=0.001)

            self._week_day_time_references[i].append(tk.Frame(self._week_days[i], borderwidth=0, highlightthickness=0))
            self._week_day_time_references[i][-1].place(relx=0.01, rely=0.2459, relwidth=1, relheight=0.001)

            self._week_day_time_references[i].append(tk.Frame(self._week_days[i], borderwidth=0, highlightthickness=0))
            self._week_day_time_references[i][-1].place(relx=0.01, rely=0.4959, relwidth=1, relheight=0.001)

            self._week_day_time_references[i].append(tk.Frame(self._week_days[i], borderwidth=0, highlightthickness=0))
            self._week_day_time_references[i][-1].place(relx=0.01, rely=0.7459, relwidth=1, relheight=0.001)
        
        # Update displayed week to include events
        self._update_week()
    
    def _event_entry_setup(self):
        """
        Sets up the GUI component for entering event information
        """
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
        self._current_event_year.set(str(self._now.year))
        self._current_event_year.trace('w', self._update_time_date_menu)
        self._dropdown_years = [str(i) for i in range(self._now.year - self._NUMBER_YEARS, self._now.year + self._NUMBER_YEARS + 1)]
        self._year_selection_menu = tk.OptionMenu(self._event_entry_primary_frame, self._current_event_year, *self._dropdown_years)
        self._year_selection_menu.config({'borderwidth': 0, 'highlightthickness': 0})
        self._year_selection_menu.grid(row=0, column=2, padx=(2, 3), pady=(2, 0), sticky='NWSE')

        # For selecting event month
        self._current_event_month = tk.StringVar(self._event_entry_primary_frame)
        self._current_event_month.set(str(self._now.month).zfill(2))
        self._current_event_month.trace('w', self._update_time_date_menu)
        self._dropdown_months = [str(i).zfill(2) for i in range(1, self._NUMBER_MONTHS_IN_YEAR + 1)]
        self._month_selection_menu = tk.OptionMenu(self._event_entry_primary_frame, self._current_event_month, *self._dropdown_months)
        self._month_selection_menu.config({'borderwidth': 0, 'highlightthickness': 0})
        self._month_selection_menu.grid(row=0, column=3, padx=(3, 1), pady=(2, 0), sticky='NWSE')
        
        # For month/day formatting
        self._date_separator_label = tk.Label(self._event_entry_primary_frame, text='/', justify='center', borderwidth=0, highlightthickness=0)
        self._date_separator_label.grid(row=0, column=4, sticky='NWSE')

        # For selecting event day
        self._current_event_day = tk.StringVar(self._event_entry_primary_frame)
        self._current_event_day.set(str(self._now.day).zfill(2))

        self._dropdown_days = []
        for day in self._new_event_calendar.itermonthdays(self._now.year, self._now.month):
            if day != 0:
                self._dropdown_days.append(str(day).zfill(2))
        
        self._day_selection_menu = tk.OptionMenu(self._event_entry_primary_frame, self._current_event_day, *self._dropdown_days)
        self._day_selection_menu.config({'borderwidth': 0, 'highlightthickness': 0})
        self._day_selection_menu.grid(row=0, column=5, padx=(1, 3), pady=(2, 0), sticky='NWSE')

        # For selecting event start time
        # For selecting event start hour
        self._current_event_hour = tk.StringVar(self._event_entry_primary_frame)
        self._current_event_hour.set(str(self._now.hour).zfill(2))
        self._dropdown_hours = [str(i).zfill(2) for i in range(0, self._NUMBER_HOURS_IN_DAY)]
        self._hour_selection_menu = tk.OptionMenu(self._event_entry_primary_frame, self._current_event_hour, *self._dropdown_hours)
        self._hour_selection_menu.config({'borderwidth': 0, 'highlightthickness': 0})
        self._hour_selection_menu.grid(row=0, column=6, padx=(3, 0), pady=(2, 0), sticky='NWSE')

        # For hour:minute formatting
        self._time_separator_label = tk.Label(self._event_entry_primary_frame, text=':', justify='center', borderwidth=0, highlightthickness=0)
        self._time_separator_label.grid(row=0, column=7, sticky='NWSE')

        # For selecting event start minute
        self._current_event_minute = tk.StringVar(self._event_entry_primary_frame)
        self._current_event_minute.set(str(self._now.minute).zfill(2))
        self._dropdown_minutes = [str(i).zfill(2) for i in range(self._NUMBER_MINUTES_IN_HOUR)]
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
        self._dropdown_duration_hour = [str(i).zfill(2) for i in range(self._NUMBER_HOURS_IN_DAY)]
        self._duration_hour_menu = tk.OptionMenu(self._event_entry_secondary_frame, self._current_event_duration_hour, *self._dropdown_duration_hour)
        self._duration_hour_menu.grid(row=0, column=1, padx=(3, 3), sticky='NWSE')

        # Duration hour label
        self._event_duration_hour_label = tk.Label(self._event_entry_secondary_frame, text='hour(s)', justify='center', borderwidth=0, highlightthickness=0)
        self._event_duration_hour_label.grid(row=0, column=2, pady=(0, 2), sticky='NWSE')

        # For selecting duration minute
        self._current_event_duration_minute = tk.StringVar(self._event_entry_secondary_frame)
        self._current_event_duration_minute.set('0'.zfill(2))
        self._dropdown_duration_minute = [str(i).zfill(2) for i in range(self._NUMBER_MINUTES_IN_HOUR)]
        self._duration_minute_menu = tk.OptionMenu(self._event_entry_secondary_frame, self._current_event_duration_minute, *self._dropdown_duration_minute)
        self._duration_minute_menu.grid(row=0, column=3, padx=(3, 3), sticky='NWSE')

        # Duration minute label
        self._event_duration_minute_label = tk.Label(self._event_entry_secondary_frame, text='minute(s)', justify='center', borderwidth=0, highlightthickness=0)
        self._event_duration_minute_label.grid(row=0, column=4, padx=(0, 3), pady=(0, 2), sticky='NWSE')

        # For selecting event recurrence
        # Recurrence label
        self._event_recurrence_label = tk.Label(self._event_entry_secondary_frame, text='recurring', justify='center', borderwidth=0, highlightthickness=0)
        self._event_recurrence_label.grid(row=0, column=5, padx=(5, 0), pady=(0, 2), sticky='NWSE')

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
        self._dropdown_event_recurrence_amount = [i for i in range(1, self._NUMBER_EVENT_RECURRENCE + 1)] + [12, 14, 30, 60, 90, 180, 365]
        self._event_recurrence_amount_menu = tk.OptionMenu(self._event_entry_secondary_frame, self._current_event_recurrence_amount, *self._dropdown_event_recurrence_amount)
        self._event_recurrence_amount_menu.grid(row=0, column=7, padx=(2, 3), sticky='NWSE')

        # Recurrence amount label
        self._event_recurrence_label = tk.Label(self._event_entry_secondary_frame, text='times', justify='center', borderwidth=0, highlightthickness=0)
        self._event_recurrence_label.grid(row=0, column=8, padx=(0, 0), pady=(0, 2), sticky='NWSE')

        # Leap years check box
        self._leap_years_mode = tk.IntVar()
        self._leap_years_mode.set(self._CHECKBUTTON_ON)
        self._leap_years_checkbutton = tk.Checkbutton(self._event_entry_secondary_frame, text='leap years?', variable=self._leap_years_mode, onvalue=self._CHECKBUTTON_ON, offvalue=self._CHECKBUTTON_OFF, anchor='w', justify='left')
        self._leap_years_checkbutton.grid(row=0, column=9, padx=(3, 3), pady=(0, 2), sticky='NWSE')
        
        # Bug: entry widgets do not immediately display correctly without text widget on screen
        # Temporary bug fix
        self._placeholder_frame_widget = tk.Label(self._event_entry_primary_frame, borderwidth=0, highlightthickness=0)
        self._placeholder_frame_widget.grid(row=0, column=9)

        self._placeholder_text_widget = tk.Text(self._event_entry_primary_frame, height=1, width=1, takefocus=0, borderwidth=0, highlightthickness=0)
        self._placeholder_text_widget.config({'state': 'disabled'})
        self._placeholder_text_widget.grid(row=0, column=9, in_=self._placeholder_frame_widget)
        self._placeholder_text_widget.lower()

    def _calendar_setup(self):
        """
        Sets up the monthly calendar component of the GUI
        """
        # Frame for the calendar
        self._calendar_frame = tk.Frame(self._root, borderwidth=0, highlightthickness=0)
        self._calendar_frame.grid(row=0, column=1, padx=(3, 6), pady=(6, 3), sticky='NWSE')
        
        self._calendar_frame.rowconfigure(0, weight=1)
        self._calendar_frame.rowconfigure(1, weight=1)

        for i in range(self._NUMBER_DISPLAY_WEEKS_IN_MONTH + 1):
            self._calendar_frame.rowconfigure(i + 2, weight=1)

        for i in range(self._NUMBER_DAYS_IN_WEEK):
            self._calendar_frame.columnconfigure(i, weight=1)
        
        # Frame for previous, current, next month buttons
        self._month_buttons_frame = tk.Frame(self._calendar_frame, borderwidth=0, highlightthickness=0)
        self._month_buttons_frame.grid(row=0, column=1, columnspan=5, sticky='NWSE')
        self._month_buttons_frame.columnconfigure(0, weight=1)
        self._month_buttons_frame.columnconfigure(1, weight=2)
        self._month_buttons_frame.columnconfigure(2, weight=1)

        # Button to go to previous month
        self._previous_month_label = tk.Label(self._month_buttons_frame, text='← prev. ', justify='left', borderwidth=0, highlightthickness=0)
        self._previous_month_label.bind('<Button-1>', self._previous_month)
        self._previous_month_label.bind('<ButtonRelease>', lambda event: self._widget_released(event.widget))
        self._previous_month_label.grid(row=0, column=0, sticky='NWSE')

        # Button to go to current month
        self._current_month_label = tk.Label(self._month_buttons_frame, text=' current ', justify='center', borderwidth=0, highlightthickness=0)
        self._current_month_label.bind('<Button-1>', self._current_month)
        self._current_month_label.bind('<ButtonRelease>', lambda event: self._widget_released(event.widget))
        self._current_month_label.grid(row=0, column=1, sticky='NS')

        # Button to go to next month
        self._next_month_label = tk.Label(self._month_buttons_frame, text=' next →', justify='right', borderwidth=0, highlightthickness=0)
        self._next_month_label.bind('<Button-1>', self._next_month)
        self._next_month_label.bind('<ButtonRelease>', lambda event: self._widget_released(event.widget))
        self._next_month_label.grid(row=0, column=2, sticky='NWSE')

        # Label for month and year
        self._month_label = tk.Label(self._calendar_frame, justify='center', borderwidth=0, highlightthickness=0)
        self._month_label.grid(row=1, column=0, columnspan=7, sticky='NWSE')

        # Labels for days of the week
        self._calendar_week_days_labels = []

        for i in range(self._NUMBER_DAYS_IN_WEEK):
            self._calendar_week_days_labels.append(tk.Label(self._calendar_frame, justify='right'))
            self._calendar_week_days_labels[-1].grid(row=2, column=i, sticky='NWSE')
        
        # Labels for days of the month
        self._calendar_month_days_labels = [[] for _ in range(self._NUMBER_DISPLAY_WEEKS_IN_MONTH)]

        for i in range(self._NUMBER_DISPLAY_WEEKS_IN_MONTH):
            for j in range(self._NUMBER_DAYS_IN_WEEK):
                self._calendar_month_days_labels[i].append(tk.Label(self._calendar_frame, justify='right'))
                self._calendar_month_days_labels[i][-1].grid(row=i + 3, column=j, sticky='NWSE')
        
        # Update displayed month with dates
        self._update_month()
    
    def _to_do_setup(self):
        """
        Sets up the to-do list component of the GUI
        """
        # Frame for to-do list
        self._to_do_frame = tk.Frame(self._root, borderwidth=0, highlightthickness=0)
        self._to_do_frame.grid(row=1, column=1, padx=(3, 6), pady=(3, 3), ipadx=6, ipady=6, sticky='NWSE')
        self._to_do_frame.grid_propagate(False)

        self._to_do_frame.rowconfigure(0, weight=0)
        self._to_do_frame.rowconfigure(1, weight=0)
        self._to_do_frame.columnconfigure(0, weight=0)

        # Label for title
        self._to_do_label = tk.Label(self._to_do_frame, text='✔︎ to-do list', anchor='w', borderwidth=0, highlightthickness=0)
        self._to_do_label.grid(row=0, column=0, padx=(3, 0), pady=(3, 4), sticky='NWSE')

        # Frame for tasks in to-do list
        self._to_do_list_frame = tk.Frame(self._to_do_frame, borderwidth=0, highlightthickness=0)
        self._to_do_list_frame.grid(row=1, column=0, sticky='NWSE')

        # For entering tasks
        self._to_do_entry_variable = tk.StringVar(self._root)
        self._to_do_entry = tk.Entry(self._root, textvariable=self._to_do_entry_variable, borderwidth=0, highlightthickness=0)
        self._to_do_entry.insert(0, ' add new to-do...')
        self._to_do_entry.bind('<FocusIn>', self._to_do_entry_focus)
        self._to_do_entry.bind('<FocusOut>', self._to_do_entry_unfocus)
        self._to_do_entry.bind('<Return>', self._to_do_entry_enter)
        self._to_do_entry.grid(row=2, column=1, padx=(3, 6), pady=(3, 3), sticky='NWSE')

        # Update to-do list to display tasks
        self._update_to_do()

    def _settings_setup(self):
        """
        Sets up the settings component of the GUI
        """
        # Frame for all settings widgets
        self._settings_frame = tk.Frame(self._root, borderwidth=0, highlightthickness=0)
        self._settings_frame.grid(row=3, column=1, padx=(6, 6), pady=(3, 7), sticky='NWSE')
        
        self._settings_frame.rowconfigure(0, weight=1)
        self._settings_frame.columnconfigure(0, weight=3)
        self._settings_frame.columnconfigure(1, weight=1)
        self._settings_frame.columnconfigure(2, weight=1)
        self._settings_frame.columnconfigure(3, weight=1)

        # For saving
        self._save_label = tk.Label(self._settings_frame, text='save', borderwidth=0, highlightthickness=0)
        self._save_label.bind('<Button-1>', lambda event: self._save())
        self._save_label.bind('<ButtonRelease>', lambda event: self._widget_released(self._save_label))
        self._save_label.grid(row=0, column=1, padx=(0, 3), sticky='NWSE')

        # For switching between light/dark mode
        self._theme_mode_label = tk.Label(self._settings_frame, borderwidth=0, highlightthickness=0)
        self._theme_mode_label.bind('<Button-1>', self._set_theme_mode)
        self._theme_mode_label.grid(row=0, column=2, padx=(3, 3), sticky='NWSE')

        # For how-to/help
        self._how_to_label = tk.Label(self._settings_frame, text='?', borderwidth=0, highlightthickness=0)
        self._how_to_label.bind('<Button-1>', self._show_how_to)
        self._how_to_label.grid(row=0, column=3, padx=(3, 0), sticky='NWSE')

    def _schedule_read(self, file_name):
        """
        Reads from schedule file

        file_name: Name of the file to read from, string
        """
        try:
            # If the schedule file does not exist, create it
            self._schedule_file_location = os.path.join(self._file_location, file_name)

            if not os.path.exists(self._schedule_file_location):
                with open(self._schedule_file_location, 'x') as opened_file:
                    self._schedule_file = opened_file
            
            # Open and read
            with open(self._schedule_file_location, 'r') as opened_file:
                self._schedule_file = opened_file
                
                # Schedule dictionary
                # {(year, month, day): {{event_id: {event_info}},
                #                       {event_id: {event_info}}, ... }}
                self._schedule = {}

                # Read events from file
                lines = self._schedule_file.readlines()

                for line in lines:
                    key = (line[:4], line[4:6], line[6:8])
                    event_id = str(uuid.uuid4())
                    event_info = {'hour': line[8:10], 'minute': line[10:12], 'duration_hour': line[12:14], 'duration_minute': line[14:16], 'hex_color': line[16:23], 'recurrence_id': line[23:59], 'frequency': line[59:66], 'amount': line[66:69], 'description': line[69:].strip(), 'ten_minute_notified': False, 'one_minute_notified': False}
                    
                    self._schedule.setdefault(key, {}).update({event_id: event_info})
                
                # Close schedule file
                self._schedule_file.close()
        except:
            # Display an error message then exit the application
            self._show_error('unable to read from schedule file.')
            sys.exit(1)
    
    def _schedule_write(self, file_name):
        """
        Writes to schedule file

        file_name: Name of the file to write to, string
        """
        try:
            # If the schedule file does not exist, create it
            self._schedule_file_location = os.path.join(self._file_location, file_name)

            if not os.path.exists(self._schedule_file_location):
                with open(self._schedule_file_location, 'x') as opened_file:
                    self._schedule_file = opened_file
            
            # Open and write
            with open(self._schedule_file_location, 'w') as opened_file:
                self._schedule_file = opened_file

                # Clear schedule file
                self._schedule_file.seek(0)
                self._schedule_file.truncate()

                # Write events into file
                for key in self._schedule:
                    for event_id, event_info in self._schedule[key].items():
                        line = key[0] + key[1] + key[2] + event_info.get('hour') + event_info.get('minute') + event_info.get('duration_hour') + event_info.get('duration_minute') + event_info.get('hex_color') + event_info.get('recurrence_id') + event_info.get('frequency') + event_info.get('amount') + event_info.get('description').strip() + '\n'
                        self._schedule_file.write(line)
                
                # Close schedule file
                self._schedule_file.close()
        except:
            # Display an error message then exit the application
            self._show_error('unable to write to schedule file.')
            sys.exit(1)
    
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
        # Add event
        event_id = str(uuid.uuid4())
        recurrence_id = str(uuid.uuid4())
        event_info = {'hour': hour, 'minute': minute, 'duration_hour': duration_hour, 'duration_minute': duration_minute, 'hex_color': hex_color, 'recurrence_id': recurrence_id, 'frequency': frequency.rjust(7), 'amount': amount.zfill(3), 'description': description, 'ten_minute_notified': False, 'one_minute_notified': False}

        self._schedule.setdefault(key, {}).update({event_id: event_info})

        # If event is recurring, add its recurrences
        delta = self._event_recurrence_frequency_dictionary.get(frequency)
        
        if delta is not None:
            # Leap years mode
            if leap_years == self._CHECKBUTTON_ON and frequency == 'yearly':
                for i in range(1, int(amount)):
                    try:
                        # Recurrence date
                        date = datetime.datetime(int(key[0]) + i, int(key[1]), int(key[2]))
                        new_key = (str(date.year), str(date.month).zfill(2), str(date.day).zfill(2))

                        # UUID of this recurrence
                        event_id = str(uuid.uuid4())

                        # Add recurrence
                        self._schedule.setdefault(new_key, {}).update({event_id: event_info})
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
                    self._schedule.setdefault(new_key, {}).update({event_id: event_info})

        # Update displayed week
        self._update_week()
    
    def _schedule_edit_remove(self, key, event_id):
        """
        Edits or removes a scheduled event and, optionally, its recurrences, if any

        key: Tuple of strings, (yyyy, mm, dd)
        event_id: unique identifier of the event, UUID, string
        """
        try:
            # Retrieve event info
            value = self._schedule.get(key)
            event_info = value.get(event_id)

            if value is not None and event_info is not None:
                popup = EventMenu(self._root, self._is_dark_mode, key, event_info, self._NUMBER_MINUTES_IN_HOUR, self._NUMBER_HOURS_IN_DAY)
                result = popup.show()
                popup = None

                # Edit or remove event(s) based on user response
                if result[0] == 'remove':
                    del self._schedule[key][event_id]

                elif result[0] == 'remove_all':
                    keys_list = []
                    recurrence_id = event_info.get('recurrence_id')

                    for date_key, events in self._schedule.items():
                        for uuid_key, info in events.items():
                            if info.get('recurrence_id') == recurrence_id:
                                keys_list.append((date_key, uuid_key))
                    
                    for item in keys_list:
                        del self._schedule[item[0]][item[1]]

                elif result[0] == 'edit':
                    self._schedule[key][event_id] = result[1]
                
                elif result[0] == 'edit_all':
                    recurrence_id = event_info.get('recurrence_id')

                    for date_key, events in self._schedule.items():
                        for uuid_key, info in events.items():
                            if info.get('recurrence_id') == recurrence_id:
                                self._schedule[date_key][uuid_key] = result[1]
        except:
            self._show_error('no such scheduled event.')
        
        # Update displayed week
        self._update_week()

    def _current_week(self, *args):
        """
        Updates displayed week to reflect the current week
        """
        self._widget_pressed(self._current_week_label)

        self._now = datetime.datetime.now()
        self._displayed_sunday = self._now - datetime.timedelta(days=(self._now.isoweekday() % self._NUMBER_DAYS_IN_WEEK))

        self._update_week()

    def _previous_week(self, *args):
        """
        Updates displayed week to reflect the previous week
        """
        self._widget_pressed(self._previous_week_label)
        self._change_week(num=-1)

    def _next_week(self, *args):
        """
        Updates displayed week to reflect the next week
        """
        self._widget_pressed(self._next_week_label)
        self._change_week(num=1)
    
    def _change_week(self, num=None, day=None, widget=None):
        """
        Updates displayed week; accepts either, but not both, of the keyword arguments num and day

        num: Number of weeks to change by (negative for previous, positive for next), int
        day: A day in the week to change to, datetime
        widget: The widget that called this function, if called from the calendar, tkinter widget
        """
        if widget is not None:
            self._widget_pressed(widget)
        
        if num is not None:
            self._displayed_sunday = self._displayed_sunday + num * datetime.timedelta(days=self._NUMBER_DAYS_IN_WEEK)
        elif day is not None:
            self._displayed_sunday = day - datetime.timedelta(days=(day.isoweekday() % self._NUMBER_DAYS_IN_WEEK))
        
        self._update_week()

    def _update_week(self):
        """
        Updates displayed week and show all scheduled events for that week
        """
        self._displayed_days = ['' for _ in range(self._NUMBER_DAYS_IN_WEEK)]
        self._week_events_labels = [[] for _ in range(self._NUMBER_DAYS_IN_WEEK)]

        # Date of first day of week
        self._week_label.config(text='week of ' + self._displayed_sunday.strftime('%m/%d') + ', ' + str(self._displayed_sunday.year))

        # Display scheduled events by day
        try:
            for i in range(self._NUMBER_DAYS_IN_WEEK):
                # Clear the day
                self._clear_day(self._week_days[i])

                # Display the day of the week and the date
                displayed_day = self._displayed_sunday + datetime.timedelta(days=i)
                year = displayed_day.strftime('%Y')
                month = displayed_day.strftime('%m')
                day = displayed_day.strftime('%d')
                key = (year, month, day)

                self._displayed_days[i] = key
                self._week_days_labels[i].config(text=displayed_day.strftime('%A').lower() + ' ' + day)
                
                # Retrieve events for the day
                events = self._schedule.get(self._displayed_days[i])

                # Display each event
                if events is not None:
                    for event_id, event_info in events.items():
                        self._week_events_labels[i].append(tk.Label(self._week_days[i], text=event_info.get('hour') + ':' + event_info.get('minute') + ' ' + event_info.get('description').strip(), anchor='nw', justify='left'))
                        self._week_events_labels[i][-1].config({'foreground': self._light_or_dark_mode_text(tuple(int(event_info.get('hex_color')[1:][j:j + 2], 16) for j in (0, 2, 4)))})
                        self._week_events_labels[i][-1].config({'background': event_info.get('hex_color')})
                        self._week_events_labels[i][-1].config({'wraplength': self._EVENT_LABEL_WRAPLENGTH})
                        self._week_events_labels[i][-1].bind('<Button-1>', lambda event: event.widget.lift())
                        self._week_events_labels[i][-1].bind('<Button-2>', lambda event, key=key, event_id=event_id: self._schedule_edit_remove(key, event_id))

                        # Event display size based on duration
                        y = self._fraction_of_day(int(event_info.get('hour')), int(event_info.get('minute')))

                        if event_info.get('duration_hour') == '0'.zfill(2) and event_info.get('duration_minute') == '0'.zfill(2):
                            self._week_events_labels[i][-1].place(relx=0.05, rely=y)
                        else:
                            h = self._fraction_of_day(int(event_info.get('duration_hour')), int(event_info.get('duration_minute')))
                            self._week_events_labels[i][-1].place(relx=0.05, rely=y, relheight=h)

        except:
            self._show_error('unable to load or update events.')
    
    def _current_month(self, *args):
        """
        Updates displayed month to reflect the current month
        """
        self._widget_pressed(self._current_month_label)

        self._now = datetime.datetime.now()
        self._displayed_month = self._now.month
        self._displayed_year = self._now.year

        self._update_month()

    def _previous_month(self, *args):
        """
        Updates displayed month to reflect the previous month
        """
        self._widget_pressed(self._previous_month_label)

        if self._displayed_month == 1:
            self._displayed_month = self._NUMBER_MONTHS_IN_YEAR
            self._displayed_year = self._displayed_year - 1
        else:
            self._displayed_month = self._displayed_month - 1
        
        self._update_month()

    def _next_month(self, *args):
        """
        Updates displayed month to reflect the next month
        """
        self._widget_pressed(self._next_month_label)

        if self._displayed_month == self._NUMBER_MONTHS_IN_YEAR:
            self._displayed_month = 1
            self._displayed_year = self._displayed_year + 1
        else:
            self._displayed_month = self._displayed_month + 1
        
        self._update_month()

    def _update_month(self):
        """
        Updates calendar to display selected month
        """
        # Format calendar for display
        calendar_string = calendar.TextCalendar(firstweekday=6).formatmonth(self._displayed_year, self._displayed_month).strip().lower()
        calendar_list = calendar_string.split()

        for i in range(len(calendar_list)):
            if i >= 2 and i <= 8:
                calendar_list[i] = calendar_list[i][0]
        
        for i in range((calendar.monthrange(self._displayed_year, self._displayed_month)[0] + 1) % self._NUMBER_DAYS_IN_WEEK):
            calendar_list.insert(9, '')
        
        while len(calendar_list) < (2 + self._NUMBER_DAYS_IN_WEEK + self._NUMBER_DISPLAY_WEEKS_IN_MONTH * self._NUMBER_DAYS_IN_WEEK):
            calendar_list.insert(len(calendar_list), '')
        
        self._month_label.config({'text': ' '.join(calendar_list[:2])})

        # Labels for weekdays
        for i in range(self._NUMBER_DAYS_IN_WEEK):
            self._calendar_week_days_labels[i].config({'text': calendar_list[i + 2]})
        
        # Labels for days of the month
        for i in range(self._NUMBER_DISPLAY_WEEKS_IN_MONTH):
            for j in range(self._NUMBER_DAYS_IN_WEEK):
                self._calendar_month_days_labels[i][j].config({'text': calendar_list[i * self._NUMBER_DAYS_IN_WEEK + j + 2 + self._NUMBER_DAYS_IN_WEEK]})

                try:
                    widget = self._calendar_month_days_labels[i][j]
                    day = datetime.datetime(self._displayed_year, self._displayed_month, int(self._calendar_month_days_labels[i][j].cget('text')))
                    self._calendar_month_days_labels[i][j].bind('<Button-1>', lambda event, day=day, widget=widget: self._change_week(day=day, widget=widget))
                    self._calendar_month_days_labels[i][j].bind('<ButtonRelease>', lambda event, widget=widget: self._widget_released(widget=widget))
                except:
                    pass
    
    def _event_entry_focus(self, *args):
        """
        Focuses on the event entry widget, remove prompt text if it is displayed
        """
        if self._event_entry.get() == ' add new event...':
            self._event_entry.delete(1, tk.END)
            
        self._event_entry.config({'foreground': self._entry_text_color})

    def _event_entry_unfocus(self, *args):
        """
        Unfocuses from the event entry widget, restoring prompt text if no text entered
        """
        if self._event_entry.get() == '' or self._event_entry.get() == ' ':
            self._event_entry.delete(0, tk.END)
            self._event_entry.insert(0, ' add new event...')

        self._event_entry.config({'foreground': self._prompt_text_color})
        self._root.focus_set()

    def _event_entry_enter(self, *args):
        """
        When enter is pressed and focus is on the event entry widget, remove focus and add event
        """
        if self._event_entry.get() != ' add new event...':
            self._schedule_add(self._get_event_date(), self._get_event_hour(), self._get_event_minute(), self._get_event_duration_hour(), self._get_event_duration_minute(), self._current_event_hex, self._event_entry.get().strip(), self._current_event_recurrence_frequency.get(), self._current_event_recurrence_amount.get(), self._leap_years_mode.get())
            self._event_entry.delete(0, tk.END)

        self._event_entry_unfocus()
    
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
    
    def _to_do_read(self, file_name):
        """
        Reads from to-do list file

        file_name: Name of the file to read from, string
        """
        try:
            # If the to-do list file does not exist, create it
            self._to_do_list_file_location = os.path.join(self._file_location, file_name)

            if not os.path.exists(self._to_do_list_file_location):
                with open(self._to_do_list_file_location, 'x') as opened_file:
                    self._to_do_list_file = opened_file
            
            # Open and read
            with open(self._to_do_list_file_location, 'r') as opened_file:
                self._to_do_list_file = opened_file

                # To-do list
                self._to_do_list = []

                # Read from to-do list file
                lines = self._to_do_list_file.readlines()

                for line in lines:
                    self._to_do_list.append(line.strip())
                
                # Close to-do list file
                self._to_do_list_file.close()
        except:
            # Display an error message then exit the application
            self._show_error('unable to read from to-do list file.')
            sys.exit(1)

    def _to_do_write(self, file_name):
        """
        Writes to to-do list file

        file_name: Name of the file to write to, string
        """
        try:
            # If the to-do list file does not exist, create it
            self._to_do_list_file_location = os.path.join(self._file_location, file_name)

            if not os.path.exists(self._to_do_list_file_location):
                with open(self._to_do_list_file_location, 'x') as opened_file:
                    self._to_do_list_file = opened_file
            
            # Open and write
            with open(self._to_do_list_file_location, 'w') as opened_file:
                self._to_do_list_file = opened_file
            
                # Clear to-do list file
                self._to_do_list_file.seek(0)
                self._to_do_list_file.truncate()

                # Write to to-do list file
                for item in self._to_do_list:
                    self._to_do_list_file.write(item.strip() + '\n')
                
                # Close to-do list file
                self._to_do_list_file.close()
        except:
            # Display an error message then exit the application
            self._show_error('unable to write to to-do list file.')
            sys.exit(1)

    def _to_do_list_toggle(self, item):
        """
        Toggles the check box for an item

        item: To-do list item, string
        """
        try:
            index = self._to_do_list.index(item)

            if self._to_do_list[index][0] == str(self._CHECKBUTTON_OFF):
                self._to_do_list[index] = str(self._CHECKBUTTON_ON) + self._to_do_list[index][1:]
            else:
                self._to_do_list[index] = str(self._CHECKBUTTON_OFF) + self._to_do_list[index][1:]
        except:
            self._show_error('no such to-do list task.')
        
        self._update_to_do()
    
    def _to_do_list_add(self, item):
        """
        Adds an item to the to-do list

        item: Item to be added, string
        """
        self._to_do_list.append(str(self._CHECKBUTTON_OFF) + item)

        self._update_to_do()
    
    def _to_do_list_remove(self, item):
        """
        Removes an item from the to-do list

        item: Item to be removed, string
        """
        popup = messagebox.askokcancel('remove task?', 'you are about to remove the task "' + item[1:] + '".', icon='warning')

        # Remove if user selects OK
        if popup:
            try:
                index = self._to_do_list.index(item)
                del self._to_do_list[index]
            except:
                self._show_error('no such to-do list task.')
        
        # Update displayed to-do list
        self._update_to_do()
    
    def _to_do_entry_focus(self, *args):
        """
        Focuses on the to-do entry widget, remove prompt text if it is displayed
        """
        if self._to_do_entry.get() == ' add new to-do...':
            self._to_do_entry.delete(1, tk.END)
            
        self._to_do_entry.config({'foreground': self._entry_text_color})

    def _to_do_entry_unfocus(self, *args):
        """
        Unfocuses from the to-do entry widget, restoring prompt text if no text entered
        """
        if self._to_do_entry.get() == '' or self._to_do_entry.get() == ' ':
            self._to_do_entry.delete(0, tk.END)
            self._to_do_entry.insert(0, ' add new to-do...')

        self._to_do_entry.config({'foreground': self._prompt_text_color})
        self._root.focus_set()

    def _to_do_entry_enter(self, *args):
        """
        When enter is pressed and focus is on the to-do entry widget, remove focus and add to-do
        """
        if self._to_do_entry.get() != ' add new to-do...':
            self._to_do_list_add(self._to_do_entry.get().strip())
            self._to_do_entry.delete(0, tk.END)

        self._to_do_entry_unfocus()
    
    def _update_to_do(self):
        """
        Updates to-do list to display current items
        """
        self._to_do_list_display = [[] for _ in range(len(self._to_do_list))]
        self._to_do_list_button_states = [tk.IntVar() for _ in range(len(self._to_do_list))]

        try:
            # Clear displayed items
            self._clear_to_do_list_display()

            # Display all to-do list items
            for i in range(len(self._to_do_list)):
                item = self._to_do_list[i]
                self._to_do_list_button_states[i].set(int(item[:1]))

                self._to_do_list_display.append(tk.Checkbutton(self._to_do_list_frame, text=item[1:], variable=self._to_do_list_button_states[i], onvalue=self._CHECKBUTTON_ON, offvalue=self._CHECKBUTTON_OFF, anchor='w', justify='left', command=lambda item=item: self._to_do_list_toggle(item)))
                self._to_do_list_display[-1].config({'foreground': self._label_text_color})
                self._to_do_list_display[-1].config({'background': self._widget_color})
                self._to_do_list_display[-1].config({'highlightthickness': 0})
                self._to_do_list_display[-1].bind('<Button-2>', lambda event, i=i, item=item: self._to_do_list_remove(item))
                self._to_do_list_display[-1].grid(row=i, column=0, padx=(2, 2), sticky='NWSE')
        except:
            self._show_error('unable to load or update to-do list.')
    
    def _save(self, *args):
        """
        Saves current schedule and to-do list
        """
        self._widget_pressed(self._save_label)

        # Save schedule and to-do list
        self._schedule_write(self._schedule_old_file_name)
        self._to_do_write(self._to_do_list_old_file_name)
    
    def _choose_color(self, *args):
        """
        Selects color for event
        """
        self._color_selection_dialog = askcolor(title='choose new event color...')
        self._color_selection_label.config({'background': self._color_selection_dialog[1]})
        self._current_event_hex = self._color_selection_dialog[1]
        
        if self._color_selection_dialog[0] is not None:
            (r, g, b) = self._color_selection_dialog[0]
            self._color_selection_label.config({'foreground': self._light_or_dark_mode_text((r, g, b))})

    def _set_theme_mode(self, change=True, *args):
        """
        Sets theme mode for application

        change: Whether to change between light/dark mode, boolean
        """
        if change:
            self._is_dark_mode = not self._is_dark_mode

        if self._is_dark_mode:
            self._theme_mode_label.config(text='☾')
        else:
            self._theme_mode_label.config(text='☼')
        
        self._set_colors(self._is_dark_mode)

        self._change_colors(parent=None)
    
    def _set_colors(self, darkmode):
        """
        Sets colors used by application
        """
        if darkmode:
            # Dark mode colors
            self._prompt_text_color = '#838383'
            self._entry_text_color = '#c2c2c2'
            self._label_text_color = '#c2c2c2'
            self._menu_text_color = '#ebebeb'
            self._background_color = '#2c2c2c'
            self._widget_color = '#383838'
            self._pressed_widget_color = '#2e2e2e'
            self._faint_text_color = '#494949'
            self._faint_display_color = '#424242'
        else:
            # Light mode colors
            self._prompt_text_color = '#797979'
            self._entry_text_color = '#4b4b4b'
            self._label_text_color = '#4b4b4b'
            self._menu_text_color = '#505050'
            self._background_color = '#d3d3d3'
            self._widget_color = '#b3b3b3'
            self._pressed_widget_color = '#969696'
            self._faint_text_color = '#a5a5a5'
            self._faint_display_color = '#a1a1a1'
    
    def _change_colors(self, parent=None):
        """
        Changes colors for widget and all descendant widgets based on current theme mode

        parent: Widget to change color for, tkinter widget
        """
        # If no widget provided, start at root
        if parent is None:
            parent = self._root
            parent.config({'background': self._background_color})
        
        # Change color for all descendant widgets
        for child in parent.winfo_children():
            if child.winfo_children():
                self._change_colors(parent=child)
            
            if child is self._placeholder_frame_widget or child is self._placeholder_text_widget:
                child.config({'foreground': self._background_color})
                child.config({'background': self._background_color})

            elif type(child) is tk.Label and parent not in self._week_days:
                if child in [self._time_separator_label, self._date_separator_label]:
                    child.config({'foreground': self._label_text_color})
                    child.config({'background': self._background_color})
                elif parent is self._event_entry_secondary_frame:
                    child.config({'foreground': self._prompt_text_color})
                    child.config({'background': self._background_color})
                else:
                    child.config({'foreground': self._label_text_color})
                    child.config({'background': self._widget_color})

                    if child is self._color_selection_label:
                        self._current_event_hex = child.cget('background')
            
            elif type(child) is tk.Entry:
                child.config({'foreground': self._prompt_text_color})
                child.config({'background': self._widget_color})
            
            elif type(child) is tk.LabelFrame:
                child.config({'foreground': self._faint_text_color})
                child.config({'background': self._widget_color})
            
            elif type(child) is tk.OptionMenu:
                child.config({'foreground': self._menu_text_color})
                child.config({'background': self._background_color})
            
            elif type(child) is tk.Checkbutton:
                if child is self._leap_years_checkbutton:
                    child.config({'foreground': self._prompt_text_color})
                    child.config({'background': self._background_color})
                else:
                    child.config({'foreground': self._label_text_color})
                    child.config({'background': self._widget_color})

            elif type(child) is tk.Frame:
                if child in [self._week_frame, self._week_buttons_frame, self._calendar_frame, self._month_buttons_frame, self._to_do_frame] or child is self._to_do_list_frame or child in self._week_days:
                    child.config({'background': self._widget_color})
                elif any(child in element for element in self._week_day_time_references):
                    child.config({'background': self._faint_display_color})
                else:
                    child.config({'background': self._background_color})
    
    def _widget_pressed(self, widget):
        """
        Sets widget to pressed appearance

        widget: The pressed widget, tkinter widget
        """
        widget.config({'background': self._pressed_widget_color})

    def _widget_released(self, widget):
        """
        Restores given widget to unpressed appearance
        
        widget: The pressed widget, tkinter widget
        """
        widget.config({'background': self._widget_color})
    
    def _widget_focus(self, widget):
        """
        If widget exists, sets focus on it

        widget: The widget to focus on, tkinter widget
        """
        try:
            if widget.winfo_exists():
                widget.focus_set()
        except:
            pass
    
    def _clear_day(self, parent):
        """
        Clears displayed events of a day

        parent: The day to clear, tk.Frame
        """
        for child in parent.winfo_children():
            # Do not clear visual, non-event elements
            if not any(child in element for element in self._week_day_time_references) and not any(child in element for element in self._week_day_separators):
                child.destroy()
    
    def _clear_to_do_list_display(self):
        """
        Clears displayed to-do list items
        """
        for child in self._to_do_list_frame.winfo_children():
            child.destroy()
    
    def _fraction_of_day(self, hour, minute):
        """
        Returns the fraction of the day corresponding to the given time

        hour: Hour, int
        minute: Minute, int
        return: Fraction of the day, float
        """
        return (hour * 60 + minute) / (24 * 60)

    def _light_or_dark_mode_text(self, rgb):
        """
        Returns the text color to be used on the given background color

        rgb: Given background color, tuple
        return: Hex color, string
        """
        r, g, b = rgb
        
        # Formula from alienryderflex.com/hsp.html
        if (0.299 * r**2 + 0.587 * g**2 + 0.114 * b**2) > 16256:
            return self._light_mode_display_text_color
        else:
            return self._dark_mode_display_text_color
    
    def _get_event_date(self):
        """
        Returns the current event date entered as a tuple

        return: Tuple of strings, (yyyy, mm, dd)
        """
        return (self._current_event_year.get(), self._current_event_month.get(), self._current_event_day.get())

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
    
    def _show_how_to(self, *args):
        """
        Displays how-to message
        """
        msg = messagebox.showinfo('your hourglass', 'press enter to add event/task\nright click to remove\n\nclick on days in monthly calendar to display events for that week\n\nsun/moon → light/dark mode\npencil → custom event color')
    
    def _show_error(self, message):
        """
        Displays error with given message

        message: Error message, string
        """
        msg = messagebox.showerror('hourglass error', message)

class EventMenu:
    """
    Class for the event edit/remove menu

    Creates a GUI popup for Hourglass
    """
    def __init__(self, parent, darkmode, key, event_info, minutes_in_hour, hours_in_day):
        """
        """
        self._NUMBER_MINUTES_IN_HOUR = minutes_in_hour
        self._NUMBER_HOURS_IN_DAY = hours_in_day

        self._set_colors(darkmode)
        self._dark_mode_display_text_color = '#c2c2c2'
        self._light_mode_display_text_color = '#4b4b4b'

        self._key = key
        self._event_info = event_info.copy()
        self._current_event_hex = self._event_info.get('hex_color')
        self._selected = None

        # Window
        self._root = tk.Toplevel(parent)

        # Title
        self._root.title('edit event...')
        
        # Font
        self._root.option_add('*Font', 'helvetica')

        # Set window size
        self._width = 500
        self._height = 300
        self._root.geometry('%sx%s' % (self._width, self._height))

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
        self._dropdown_hours = [str(i).zfill(2) for i in range(0, self._NUMBER_HOURS_IN_DAY)]
        self._hour_selection_menu = tk.OptionMenu(self._time_color_frame, self._current_event_hour, *self._dropdown_hours)
        self._hour_selection_menu.config({'borderwidth': 0, 'highlightthickness': 0})
        self._hour_selection_menu.grid(row=0, column=1, padx=(3, 0), pady=(2, 0), sticky='NWSE')

        # For hour:minute formatting
        self._time_separator_label = tk.Label(self._time_color_frame, text=':', justify='center', borderwidth=0, highlightthickness=0)
        self._time_separator_label.grid(row=0, column=2, sticky='NWSE')

        # For selecting event start minute
        self._current_event_minute = tk.StringVar(self._time_color_frame)
        self._current_event_minute.set(self._event_info.get('minute'))
        self._dropdown_minutes = [str(i).zfill(2) for i in range(self._NUMBER_MINUTES_IN_HOUR)]
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
        self._dropdown_duration_hour = [str(i).zfill(2) for i in range(self._NUMBER_HOURS_IN_DAY)]
        self._duration_hour_menu = tk.OptionMenu(self._duration_frame, self._current_event_duration_hour, *self._dropdown_duration_hour)
        self._duration_hour_menu.grid(row=0, column=1, padx=(3, 3), sticky='NWSE')

        # Duration hour label
        self._event_duration_hour_label = tk.Label(self._duration_frame, text='hour(s)', justify='center', borderwidth=0, highlightthickness=0)
        self._event_duration_hour_label.grid(row=0, column=2, pady=(0, 2), sticky='NWSE')

        # For selecting duration minute
        self._current_event_duration_minute = tk.StringVar(self._duration_frame)
        self._current_event_duration_minute.set(self._event_info.get('duration_minute'))
        self._dropdown_duration_minute = [str(i).zfill(2) for i in range(self._NUMBER_MINUTES_IN_HOUR)]
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
        self._edit_button.bind('<ButtonRelease>', lambda event: self._widget_released(event.widget))
        self._edit_button.grid(row=0, column=0, padx=(50, 3), sticky='NWSE')

        # Edit all button
        self._edit_all_button = tk.Label(self._buttons_frame, text='edit all', borderwidth=0, highlightthickness=0)

        if self._event_info.get('frequency').strip() != 'none':
            self._edit_all_button.bind('<Button-1>', lambda event: self._select(event.widget, 'edit_all'))

        self._edit_all_button.bind('<ButtonRelease>', lambda event: self._widget_released(event.widget))
        self._edit_all_button.grid(row=0, column=1, padx=(3, 3), sticky='NWSE')

        # Remove button
        self._remove_button = tk.Label(self._buttons_frame, text='remove', borderwidth=0, highlightthickness=0)
        self._remove_button.bind('<Button-1>', lambda event: self._select(event.widget, 'remove'))
        self._remove_button.bind('<ButtonRelease>', lambda event: self._widget_released(event.widget))
        self._remove_button.grid(row=0, column=2, padx=(3, 3), sticky='NWSE')

        # Remove all button
        self._remove_all_button = tk.Label(self._buttons_frame, text='remove all', borderwidth=0, highlightthickness=0)

        if self._event_info.get('frequency').strip() != 'none':
            self._remove_all_button.bind('<Button-1>', lambda event: self._select(event.widget, 'remove_all'))

        self._remove_all_button.bind('<ButtonRelease>', lambda event: self._widget_released(event.widget))
        self._remove_all_button.grid(row=0, column=3, padx=(3, 3), sticky='NWSE')

        # Cancel button
        self._cancel_button = tk.Label(self._buttons_frame, text='cancel', borderwidth=0, highlightthickness=0)
        self._cancel_button.bind('<Button-1>', lambda event: self._select(event.widget, None))
        self._cancel_button.bind('<ButtonRelease>', lambda event: self._widget_released(event.widget))
        self._cancel_button.grid(row=0, column=4, padx=(3, 0), sticky='NWSE')
    
    def _choose_color(self, *args):
        """
        Selects color for event
        """
        self._color_selection_dialog = askcolor(title='choose new event color...')
        self._color_selection_label.config({'background': self._color_selection_dialog[1]})
        self._current_event_hex = self._color_selection_dialog[1]
        
        if self._color_selection_dialog[0] is not None:
            (r, g, b) = self._color_selection_dialog[0]
            self._color_selection_label.config({'foreground': self._light_or_dark_mode_text((r, g, b))})
    
    def _select(self, widget, selection):
        """
        Selects action for event

        widget: The widget clicked by the user to make the selection
        selection: Action for the event, either the strings 'edit', 'edit_all', 'remove', 'remove_all', or None for cancel
        """
        self._widget_pressed(widget)

        self._selected = selection

        if selection is not None:
            self._event_info['hour'] = self._current_event_hour.get()
            self._event_info['minute'] = self._current_event_minute.get()
            self._event_info['duration_hour'] = self._current_event_duration_hour.get()
            self._event_info['duration_minute'] = self._current_event_duration_minute.get()
            self._event_info['hex_color'] = self._current_event_hex
            self._event_info['description'] = self._text.get('1.0', tk.END).strip()

        self._root.destroy()
    
    def _set_colors(self, darkmode):
        """
        Sets colors used by application
        """
        if darkmode:
            # Dark mode colors
            self._prompt_text_color = '#838383'
            self._entry_text_color = '#c2c2c2'
            self._label_text_color = '#c2c2c2'
            self._menu_text_color = '#ebebeb'
            self._background_color = '#2c2c2c'
            self._widget_color = '#383838'
            self._pressed_widget_color = '#2e2e2e'
            self._faint_text_color = '#494949'
            self._faint_display_color = '#424242'
        else:
            # Light mode colors
            self._prompt_text_color = '#797979'
            self._entry_text_color = '#4b4b4b'
            self._label_text_color = '#4b4b4b'
            self._menu_text_color = '#505050'
            self._background_color = '#d3d3d3'
            self._widget_color = '#b3b3b3'
            self._pressed_widget_color = '#969696'
            self._faint_text_color = '#a5a5a5'
            self._faint_display_color = '#a1a1a1'
    
    def _change_colors(self, parent=None):
        """
        Changes colors for widget and all descendant widgets based on current theme mode

        parent: Widget to change color for, tkinter widget
        """
        # If no widget provided, start at root
        if parent is None:
            parent = self._root
            parent.config({'background': self._background_color})
        
        # Change color for all descendant widgets
        for child in parent.winfo_children():
            if child.winfo_children():
                self._change_colors(parent=child)

            if type(child) is tk.Label:
                if child is self._color_selection_label:
                    child.config({'foreground': self._light_or_dark_mode_text(tuple(int(self._current_event_hex[1:][i:i + 2], 16) for i in (0, 2, 4)))})
                    child.config({'background': self._current_event_hex})
                elif parent is self._date_recurrence_frame:
                    child.config({'foreground': self._entry_text_color})
                    child.config({'background': self._background_color})
                elif parent is self._time_color_frame:
                    child.config({'foreground': self._label_text_color})
                    child.config({'background': self._background_color})
                elif parent is self._duration_frame:
                    child.config({'foreground': self._prompt_text_color})
                    child.config({'background': self._background_color})
                elif self._event_info.get('frequency').strip() == 'none' and child in [self._edit_all_button, self._remove_all_button]:
                    child.config({'foreground': self._faint_text_color})
                    child.config({'background': self._widget_color})
                else:
                    child.config({'foreground': self._label_text_color})
                    child.config({'background': self._widget_color})
            
            elif type(child) is tk.OptionMenu:
                child.config({'foreground': self._menu_text_color})
                child.config({'background': self._background_color})
            
            elif type(child) is tk.Text:
                child.config({'foreground': self._prompt_text_color})
                child.config({'background': self._widget_color})

            elif type(child) is tk.Frame:
                child.config({'background': self._background_color})
    
    def _light_or_dark_mode_text(self, rgb):
        """
        Returns the text color to be used on the given background color

        rgb: Given background color, tuple
        return: Hex color, string
        """
        r, g, b = rgb
        
        # Formula from alienryderflex.com/hsp.html
        if (0.299 * r**2 + 0.587 * g**2 + 0.114 * b**2) > 16256:
            return self._light_mode_display_text_color
        else:
            return self._dark_mode_display_text_color
    
    def _widget_pressed(self, widget):
        """
        Sets widget to pressed appearance

        widget: The pressed widget, tkinter widget
        """
        widget.config({'background': self._pressed_widget_color})

    def _widget_released(self, widget):
        """
        Restores given widget to unpressed appearance
        
        widget: The pressed widget, tkinter widget
        """
        widget.config({'background': self._widget_color})

    def show(self):
        """
        Shows the popup window and waits for it to be closed, then returning the user's modifications to the event

        return: Tuple containing the selection of the user and the modifications to the event information
        """
        self._root.deiconify()
        self._root.wait_window(self._root)
        return (self._selected, self._event_info)

if __name__ == '__main__':
    Hourglass()