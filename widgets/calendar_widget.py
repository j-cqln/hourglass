import calendar
import datetime

import tkinter as tk

from utilities.constants import NUMBER_DISPLAY_WEEKS_IN_MONTH, NUMBER_DAYS_IN_WEEK, NUMBER_MONTHS_IN_YEAR
from utilities.functions import widget_pressed, widget_released

class CalendarWidget:
    """
    Class for the monthly calendar megawidget
    """
    def __init__(self, parent, root):
        """
        Sets up the monthly calendar component of the GUI
        """
        # Parent Hourglass
        self._parent = parent

        # Root window
        self._root = root
        
        # Currently displayed month and year in the calendar
        self._displayed_month = self._parent.now.month
        self._displayed_year = self._parent.now.year

        # Frame for the calendar
        self._calendar_frame = tk.Frame(root, borderwidth=0, highlightthickness=0)
        self._calendar_frame.grid(row=0, column=1, padx=(3, 6), pady=(6, 3), sticky='NWSE')
        
        self._calendar_frame.rowconfigure(0, weight=1)
        self._calendar_frame.rowconfigure(1, weight=1)

        for i in range(NUMBER_DISPLAY_WEEKS_IN_MONTH + 1):
            self._calendar_frame.rowconfigure(i + 2, weight=1)

        for i in range(NUMBER_DAYS_IN_WEEK):
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
        self._previous_month_label.bind('<ButtonRelease>', lambda event: widget_released(event.widget, self._parent.colors))
        self._previous_month_label.grid(row=0, column=0, sticky='NWSE')

        # Button to go to current month
        self._current_month_label = tk.Label(self._month_buttons_frame, text=' current ', justify='center', borderwidth=0, highlightthickness=0)
        self._current_month_label.bind('<Button-1>', self._current_month)
        self._current_month_label.bind('<ButtonRelease>', lambda event: widget_released(event.widget, self._parent.colors))
        self._current_month_label.grid(row=0, column=1, sticky='NS')

        # Button to go to next month
        self._next_month_label = tk.Label(self._month_buttons_frame, text=' next →', justify='right', borderwidth=0, highlightthickness=0)
        self._next_month_label.bind('<Button-1>', self._next_month)
        self._next_month_label.bind('<ButtonRelease>', lambda event: widget_released(event.widget, self._parent.colors))
        self._next_month_label.grid(row=0, column=2, sticky='NWSE')

        # Label for month and year
        self._month_label = tk.Label(self._calendar_frame, justify='center', borderwidth=0, highlightthickness=0)
        self._month_label.grid(row=1, column=0, columnspan=7, sticky='NWSE')

        # Labels for days of the week
        self._calendar_week_days_labels = []

        for i in range(NUMBER_DAYS_IN_WEEK):
            self._calendar_week_days_labels.append(tk.Label(self._calendar_frame, justify='right'))
            self._calendar_week_days_labels[-1].grid(row=2, column=i, sticky='NWSE')
        
        # Labels for days of the month
        self._calendar_month_days_labels = [[] for _ in range(NUMBER_DISPLAY_WEEKS_IN_MONTH)]

        for i in range(NUMBER_DISPLAY_WEEKS_IN_MONTH):
            for j in range(NUMBER_DAYS_IN_WEEK):
                self._calendar_month_days_labels[i].append(tk.Label(self._calendar_frame, justify='right'))
                self._calendar_month_days_labels[i][-1].grid(row=i + 3, column=j, sticky='NWSE')
        
        # Update displayed month with dates
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
        
        for i in range((calendar.monthrange(self._displayed_year, self._displayed_month)[0] + 1) % NUMBER_DAYS_IN_WEEK):
            calendar_list.insert(9, '')
        
        while len(calendar_list) < (2 + NUMBER_DAYS_IN_WEEK + NUMBER_DISPLAY_WEEKS_IN_MONTH * NUMBER_DAYS_IN_WEEK):
            calendar_list.insert(len(calendar_list), '')
        
        self._month_label.config({'text': ' '.join(calendar_list[:2])})

        # Labels for weekdays
        for i in range(NUMBER_DAYS_IN_WEEK):
            self._calendar_week_days_labels[i].config({'text': calendar_list[i + 2]})
        
        # Labels for days of the month
        for i in range(NUMBER_DISPLAY_WEEKS_IN_MONTH):
            for j in range(NUMBER_DAYS_IN_WEEK):
                self._calendar_month_days_labels[i][j].config({'text': calendar_list[i * NUMBER_DAYS_IN_WEEK + j + 2 + NUMBER_DAYS_IN_WEEK]})

                try:
                    widget = self._calendar_month_days_labels[i][j]
                    day = datetime.datetime(self._displayed_year, self._displayed_month, int(self._calendar_month_days_labels[i][j].cget('text')))
                    self._calendar_month_days_labels[i][j].bind('<Button-1>', lambda event, day=day, widget=widget: self._parent.change_week(day=day, widget=widget))
                    self._calendar_month_days_labels[i][j].bind('<ButtonRelease>', lambda event, widget=widget: widget_released(widget, self._parent.colors))
                except:
                    pass
    
    def _current_month(self, *args):
        """
        Updates displayed month to reflect the current month
        """
        widget_pressed(self._current_month_label, self._parent.colors)

        self._parent.now = datetime.datetime.now()
        self._displayed_month = self._parent.now.month
        self._displayed_year = self._parent.now.year

        self._update_month()

    def _previous_month(self, *args):
        """
        Updates displayed month to reflect the previous month
        """
        widget_pressed(self._previous_month_label, self._parent.colors)

        if self._displayed_month == 1:
            self._displayed_month = NUMBER_MONTHS_IN_YEAR
            self._displayed_year = self._displayed_year - 1
        else:
            self._displayed_month = self._displayed_month - 1
        
        self._update_month()

    def _next_month(self, *args):
        """
        Updates displayed month to reflect the next month
        """
        widget_pressed(self._next_month_label, self._parent.colors)

        if self._displayed_month == NUMBER_MONTHS_IN_YEAR:
            self._displayed_month = 1
            self._displayed_year = self._displayed_year + 1
        else:
            self._displayed_month = self._displayed_month + 1
        
        self._update_month()
    
    def change_colors(self):
        """
        Changes colors for this megawidget and all descendant widgets based on current theme mode
        """
        # Change color for all descendant widgets
        self._calendar_frame.config({'background': self._parent.colors.get('widget_color')})

        self._month_buttons_frame.config({'background': self._parent.colors.get('widget_color')})

        for widget in [self._previous_month_label,
                        self._current_month_label,
                        self._next_month_label,
                        self._month_label]:
            widget.config({'foreground': self._parent.colors.get('label_text_color')})
            widget.config({'background': self._parent.colors.get('widget_color')})

        for widget in self._calendar_week_days_labels:
            widget.config({'foreground': self._parent.colors.get('label_text_color')})
            widget.config({'background': self._parent.colors.get('widget_color')})

        for day in self._calendar_month_days_labels:
            for widget in day:
                widget.config({'foreground': self._parent.colors.get('label_text_color')})
                widget.config({'background': self._parent.colors.get('widget_color')})