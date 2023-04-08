import datetime

import tkinter as tk

from widgets.event_menu import EventMenu

from utilities.functions import show_error, light_or_dark_mode_text, widget_pressed, widget_released
from utilities.constants import NUMBER_DAYS_IN_WEEK, EVENT_LABEL_WRAPLENGTH

class WeekWidget:
    """
    Class for weekly event megawidget
    """
    def __init__(self, parent, root):
        """
        Sets up the week component of the GUI on which events are displayed
        """
        # Parent Hourglass
        self._parent = parent

        # Root window
        self._root = root

        # Frame for all week-related widgets
        self._week_frame = tk.Frame(self._root, borderwidth=0, highlightthickness=0)
        self._week_frame.grid(row=0, column=0, rowspan=2, padx=(6, 3), pady=(6, 3), ipadx=6, ipady=6, sticky='NWSE')
        
        self._week_frame.rowconfigure(0, weight=0)
        self._week_frame.rowconfigure(1, weight=0)
        self._week_frame.rowconfigure(2, weight=1)

        for i in range(NUMBER_DAYS_IN_WEEK):
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
        self._previous_week_label.bind('<ButtonRelease>', lambda event: widget_released(event.widget, self._parent.colors))
        self._previous_week_label.grid(row=0, column=0, sticky='NWSE')

        # Button to go to current week
        self._current_week_label = tk.Label(self._week_buttons_frame, text=' current ', justify='center', borderwidth=0, highlightthickness=0)
        self._current_week_label.bind('<Button-1>', self._current_week)
        self._current_week_label.bind('<ButtonRelease>', lambda event: widget_released(event.widget, self._parent.colors))
        self._current_week_label.grid(row=0, column=1, sticky='NS')

        # Button to go to next week
        self._next_week_label = tk.Label(self._week_buttons_frame, text=' next →', justify='right', borderwidth=0, highlightthickness=0)
        self._next_week_label.bind('<Button-1>', self._next_week)
        self._next_week_label.bind('<ButtonRelease>', lambda event: widget_released(event.widget, self._parent.colors))
        self._next_week_label.grid(row=0, column=2, sticky='NWSE')

        # Display week widgets
        self._week_days_labels = []
        self._week_days = []
        self._week_day_separators = [[] for _ in range(NUMBER_DAYS_IN_WEEK)]
        self._week_day_time_references = [[] for _ in range(NUMBER_DAYS_IN_WEEK)]

        for i in range(NUMBER_DAYS_IN_WEEK):
            # Label for the day of the week and the date
            self._week_days_labels.append(tk.Label(self._week_frame, anchor='w'))

            # Frame for each day
            self._week_days.append(tk.Frame(self._week_frame))
            self._week_days[i].bind('<Button-1>', lambda event, i=i: self._parent.update_event_entry_date(i))
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
        self.update_week()
    
    def update_week(self):
        """
        Updates displayed week and show all scheduled events for that week
        """
        self._displayed_days = ['' for _ in range(NUMBER_DAYS_IN_WEEK)]
        self._week_events_labels = [[] for _ in range(NUMBER_DAYS_IN_WEEK)]

        # Date of first day of week
        self._week_label.config(text='week of ' + self._parent.displayed_sunday.strftime('%m/%d') + ', ' + str(self._parent.displayed_sunday.year))

        # Display scheduled events by day
        try:
            for i in range(NUMBER_DAYS_IN_WEEK):
                # Clear the day
                self._clear_day(self._week_days[i])

                # Display the day of the week and the date
                displayed_day = self._parent.displayed_sunday + datetime.timedelta(days=i)
                year = displayed_day.strftime('%Y')
                month = displayed_day.strftime('%m')
                day = displayed_day.strftime('%d')
                key = (year, month, day)

                self._displayed_days[i] = key
                self._week_days_labels[i].config(text=displayed_day.strftime('%A').lower() + ' ' + day)
                
                # Retrieve events for the day
                events = self._parent.schedule.get(self._displayed_days[i])

                # Display each event
                if events is not None:
                    for event_id, event_info in events.items():
                        self._week_events_labels[i].append(tk.Label(self._week_days[i], text=event_info.get('hour') + ':' + event_info.get('minute') + ' ' + event_info.get('description').strip(), anchor='nw', justify='left'))
                        self._week_events_labels[i][-1].config({'foreground': light_or_dark_mode_text(tuple(int(event_info.get('hex_color')[1:][j:j + 2], 16) for j in (0, 2, 4)))})
                        self._week_events_labels[i][-1].config({'background': event_info.get('hex_color')})
                        self._week_events_labels[i][-1].config({'wraplength': EVENT_LABEL_WRAPLENGTH})
                        self._week_events_labels[i][-1].bind('<Button-1>', lambda event: event.widget.lift())
                        self._week_events_labels[i][-1].bind('<Button-2>', lambda event, key=key, event_id=event_id: self._schedule_edit_remove(key, event_id))

                        # Event display size based on duration
                        y = self._fraction_of_day(int(event_info.get('hour')), int(event_info.get('minute')))

                        if event_info.get('duration_hour') == '0'.zfill(2) and event_info.get('duration_minute') == '0'.zfill(2):
                            self._week_events_labels[i][-1].place(relx=0.05, rely=y)
                        else:
                            h = self._fraction_of_day(int(event_info.get('duration_hour')), int(event_info.get('duration_minute')))
                            self._week_events_labels[i][-1].place(relx=0.05, rely=y, relheight=h)

        except Exception as e:
            show_error('unable to load or update events.')

    def change_week(self, num=None, day=None, widget=None):
        """
        Updates displayed week; accepts either, but not both, of the keyword arguments num and day

        num: Number of weeks to change by (negative for previous, positive for next), int
        day: A day in the week to change to, datetime
        widget: The widget that called this function, if called from the calendar, tkinter widget
        """
        if widget is not None:
            widget_pressed(widget, self._parent.colors)
        
        if num is not None:
            self._parent.displayed_sunday = self._parent.displayed_sunday + num * datetime.timedelta(days=NUMBER_DAYS_IN_WEEK)
        elif day is not None:
            self._parent.displayed_sunday = day - datetime.timedelta(days=(day.isoweekday() % NUMBER_DAYS_IN_WEEK))
        
        self.update_week()

    def _current_week(self, *args):
        """
        Updates displayed week to reflect the current week
        """
        widget_pressed(self._current_week_label, self._parent.colors)

        self._parent.now = datetime.datetime.now()
        self._parent.displayed_sunday = self._parent.now - datetime.timedelta(days=(self._parent.now.isoweekday() % NUMBER_DAYS_IN_WEEK))

        self.update_week()
    
    def _previous_week(self, *args):
        """
        Updates displayed week to reflect the previous week
        """
        widget_pressed(self._previous_week_label, self._parent.colors)
        self.change_week(num=-1)

    def _next_week(self, *args):
        """
        Updates displayed week to reflect the next week
        """
        widget_pressed(self._next_week_label, self._parent.colors)
        self.change_week(num=1)
        
    def _schedule_edit_remove(self, key, event_id):
        """
        Edits or removes a scheduled event and, optionally, its recurrences, if any

        key: Tuple of strings, (yyyy, mm, dd)
        event_id: unique identifier of the event, UUID, string
        """
        try:
            # Retrieve event info
            value = self._parent.schedule.get(key)
            event_info = value.get(event_id)

            if value is not None and event_info is not None:
                popup = EventMenu(self._parent, self._root, key, event_info)
                result = popup.show()
                popup = None

                # Edit or remove event(s) based on user response
                if result[0] == 'remove':
                    del self._parent.schedule[key][event_id]

                elif result[0] == 'remove_all':
                    keys_list = []
                    recurrence_id = event_info.get('recurrence_id')

                    for date_key, events in self._parent.schedule.items():
                        for uuid_key, info in events.items():
                            if info.get('recurrence_id') == recurrence_id:
                                keys_list.append((date_key, uuid_key))
                    
                    for item in keys_list:
                        del self._parent.schedule[item[0]][item[1]]

                elif result[0] == 'edit':
                    self._parent.schedule[key][event_id] = result[1]
                
                elif result[0] == 'edit_all':
                    recurrence_id = event_info.get('recurrence_id')

                    for date_key, events in self._parent.schedule.items():
                        for uuid_key, info in events.items():
                            if info.get('recurrence_id') == recurrence_id:
                                self._parent.schedule[date_key][uuid_key] = result[1]
        except Exception as e:
            show_error('no such scheduled event.')
        
        # Update displayed week
        self.update_week()
    
    def _clear_day(self, parent):
        """
        Clears displayed events of a day

        parent: The day to clear, tk.Frame
        """
        for child in parent.winfo_children():
            # Do not clear visual, non-event elements
            if not any(child in element for element in self._week_day_time_references) and not any(child in element for element in self._week_day_separators):
                child.destroy()
    
    def _fraction_of_day(self, hour, minute):
        """
        Returns the fraction of the day corresponding to the given time

        hour: Hour, int
        minute: Minute, int
        return: Fraction of the day, float
        """
        return (hour * 60 + minute) / (24 * 60)
    
    def change_colors(self):
        """
        Changes colors for this megawidget and all descendant widgets based on current theme mode
        """
        # Change color for all descendant widgets
        self._week_frame.config({'background': self._parent.colors.get('widget_color')})

        for widget in self._week_days:
            widget.config({'background': self._parent.colors.get('widget_color')})
        
        for widget in self._week_days_labels:
            widget.config({'foreground': self._parent.colors.get('label_text_color')})
            widget.config({'background': self._parent.colors.get('widget_color')})

        for day in self._week_day_separators:
            for widget in day:
                widget.config({'background': self._parent.colors.get('background_color')})

        for day in self._week_day_time_references:
            for widget in day:
                if type(widget) is tk.LabelFrame:
                    widget.config({'foreground': self._parent.colors.get('faint_text_color')})
                    widget.config({'background': self._parent.colors.get('widget_color')})
                elif type(widget) is tk.Frame:
                    widget.config({'background': self._parent.colors.get('faint_display_color')})

        self._week_buttons_frame.config({'background': self._parent.colors.get('widget_color')})

        for widget in [self._week_label, self._previous_week_label, self._current_week_label, self._next_week_label]:
            widget.config({'foreground': self._parent.colors.get('label_text_color')})
            widget.config({'background': self._parent.colors.get('widget_color')})