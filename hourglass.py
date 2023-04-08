# Libraries
import os
import sys
import uuid
import calendar
import datetime

import tkinter as tk
from tkinter import font

from widgets.calendar_widget import CalendarWidget
from widgets.event_entry_widget import EventEntryWidget
from widgets.settings_widget import SettingsWidget
from widgets.to_do_widget import ToDoWidget
from widgets.week_widget import WeekWidget

from utilities.functions import show_info, show_error, handle_exception, widget_focus
from utilities.constants import NUMBER_DAYS_IN_WEEK

class Hourglass:
    """
    Class for the Hourglass application

    Creates a GUI calendar and to-do list application
    """
    def __init__(self):
        """
        Initializes the Hourglass class
        """
        # Current moment
        self.now = datetime.datetime.now()

        # Sunday of the week for which events are displayed
        self.displayed_sunday = self.now - datetime.timedelta(days=(self.now.isoweekday() % NUMBER_DAYS_IN_WEEK))

        # Default mode is dark mode
        self.is_dark_mode = True
        
        # Colorway used by application
        self.colors = {}

        # Schedule dictionary
        # {(year, month, day): {{event_id: {event_info}},
        #                       {event_id: {event_info}}, ... }}
        self.schedule = {}

        # To-do list
        self.to_do_list = []

        # Location and name of schedule and tasks files
        self._file_location = os.path.join(os.path.dirname('__file__'), 'data/')
        self._schedule_file_name = 'schedule.txt'
        self._to_do_list_file_name = 'tasks.txt'
        self._schedule_old_file_name = 'schedule_old.txt'
        self._to_do_list_old_file_name = 'tasks_old.txt'

        # Read from schedule and to-do list files
        self._schedule_read(self._schedule_file_name)
        self._to_do_read(self._to_do_list_file_name)

        # GUI
        self._root = tk.Tk()

        # Font
        self._root.option_add('*Font', 'helvetica')

        # Adjust default GUI size based on screen size
        self._screen_width = self._root.winfo_screenwidth()
        self._screen_height = self._root.winfo_screenheight()
        self._width = int(self._screen_width * 0.7)
        self._height = int(self._screen_height * 0.7)
        self._root.geometry('{}x{}'.format(self._width, self._height))
        self._root.update()

        # Adjust minimum and maximum size that GUI can be resized as
        self._root.minsize(int(self._root.winfo_width() * 0.8), int(self._root.winfo_height() * 0.8))
        self._root.maxsize(int(self._root.winfo_width() * 1.2), int(self._root.winfo_height() * 1.2))

        # Row and column weights for widget placement
        self._root.columnconfigure(0, weight=6)
        self._root.columnconfigure(1, weight=1)
        
        self._root.rowconfigure(0, weight=1)
        self._root.rowconfigure(1, weight=5)

        # Register the callback on the tk window
        self._root.report_callback_exception = handle_exception
        
        # Set up GUI title and GUI widgets
        self._set_title()
        self._week_widget = WeekWidget(self, self._root)
        self._event_entry_widget = EventEntryWidget(self, self._root)
        self._calendar_widget = CalendarWidget(self, self._root)
        self._to_do_widget = ToDoWidget(self, self._root)
        self._settings_widget = SettingsWidget(self, self._root)

        # Set the colorway
        self._set_colors()

        # Change display colors to set colorway
        self.change_colors()

        # Allow all components of the GUI to be focusable on left click
        self._root.bind_all('<Button-1>', lambda event: widget_focus(event.widget))

        # Set up notification function
        self.notify_mode = True
        self._notify()

        # Application loop
        self._root.mainloop()

        # Write to schedule and to-do list files
        try:
            self._schedule_write(self._schedule_file_name)
            self._to_do_write(self._to_do_list_file_name)
        except:
            # Display an error message then exit the application
            show_error('unable to write to schedule or to-do list files.')
            sys.exit(1)
    
    def _set_title(self):
        """
        Sets the title of the GUI window; calls itself each second to update
        """
        # Set title using current month and year
        self.now = datetime.datetime.now()
        self._root.title('hourglass  -  ' + self.now.strftime('%B %Y').lower())

        # Update again after 1 second
        self._root.after(1000, self._set_title)
    
    def _notify(self):
        """
        Checks for upcoming events and notifies user
        """
        self.now = datetime.datetime.now()
        
        try:
            if self.notify_mode:
                # Check for upcoming events in the current day and the next day
                for i in range(2):
                    date = self.now + datetime.timedelta(days=i)
                    year = date.strftime('%Y')
                    month = date.strftime('%m')
                    day = date.strftime('%d')

                    key = (year, month, day)
                    value = self.schedule.get(key)

                    if value is not None:
                        for event_id, event_info in value.items():
                            delta = datetime.datetime(year=int(year), month=int(month), day=int(day), hour=int(event_info.get('hour')), minute=int(event_info.get('minute'))) - self.now
                            
                            # Ten minute notification
                            if delta.total_seconds() < 600 and delta.total_seconds() > 60 and event_info.get('ten_minute_notified') is False:
                                event_info['ten_minute_notified'] = True
                                show_info(message='in ' + str(max(2, int(delta.total_seconds() / 60))) + ' minutes:\n' + event_info.get('description'))
                            
                            # One minute notification
                            elif delta.total_seconds() < 60 and delta.total_seconds() > 0 and event_info.get('one_minute_notified') is False:
                                event_info['one_minute_notified'] = True
                                show_info(message='in 1 minute:\n' + event_info.get('description'))
        except:
            pass
        
        # Update again after 1 second
        self._root.after(1000, self._notify)

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
                self.schedule = {}

                # Read events from file
                lines = self._schedule_file.readlines()

                for line in lines:
                    key = (line[:4], line[4:6], line[6:8])
                    event_id = str(uuid.uuid4())
                    event_info = {'hour': line[8:10], 'minute': line[10:12], 'duration_hour': line[12:14], 'duration_minute': line[14:16], 'hex_color': line[16:23], 'recurrence_id': line[23:59], 'frequency': line[59:66], 'amount': line[66:69], 'description': line[69:].strip(), 'ten_minute_notified': False, 'one_minute_notified': False}
                    
                    self.schedule.setdefault(key, {}).update({event_id: event_info})
                
                # Close schedule file
                self._schedule_file.close()
        except:
            # Display an error message then exit the application
            show_error('unable to read from schedule file.')
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
                for key in self.schedule:
                    for event_id, event_info in self.schedule[key].items():
                        line = key[0] + key[1] + key[2] + event_info.get('hour') + event_info.get('minute') + event_info.get('duration_hour') + event_info.get('duration_minute') + event_info.get('hex_color') + event_info.get('recurrence_id') + event_info.get('frequency') + event_info.get('amount') + event_info.get('description').strip() + '\n'
                        self._schedule_file.write(line)
                
                # Close schedule file
                self._schedule_file.close()
        except:
            # Display an error message then exit the application
            show_error('unable to write to schedule file.')
            sys.exit(1)
    
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
                self.to_do_list = []

                # Read from to-do list file
                lines = self._to_do_list_file.readlines()

                for line in lines:
                    key = str(uuid.uuid4())
                    contents = line.strip()
                    item = {'key': key, 'completion': contents[0], 'description': contents[1:]}
                    self.to_do_list.append(item)
                
                # Close to-do list file
                self._to_do_list_file.close()
        except:
            # Display an error message then exit the application
            show_error('unable to read from to-do list file.')
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
                for item in self.to_do_list:
                    self._to_do_list_file.write(item.get('completion') + item.get('description').strip() + '\n')
                
                # Close to-do list file
                self._to_do_list_file.close()
        except:
            # Display an error message then exit the application
            show_error('unable to write to to-do list file.')
            sys.exit(1)

    def save(self):
        """
        Saves current schedule and to-do list
        """
        self._schedule_write(self._schedule_old_file_name)
        self._to_do_write(self._to_do_list_old_file_name)
    
    def update_event_entry_date(self, days):
        """
        Updates event entry date based on the displayed day clicked by the user
        
        days: The clicked day represented as the number of days after the displayed Sunday, int
        """
        self._event_entry_widget.update_event_entry_date(days)

    def update_week(self):
        """
        Updates displayed week and show all scheduled events for that week
        """
        self._week_widget.update_week()
    
    def change_week(self, num=None, day=None, widget=None):
        """
        Updates displayed week; accepts either, but not both, of the keyword arguments num and day

        num: Number of weeks to change by (negative for previous, positive for next), int
        day: A day in the week to change to, datetime
        widget: The widget that called this function, if called from the calendar, tkinter widget
        """
        self._week_widget.change_week(num=num, day=day, widget=widget)
    
    def _set_colors(self):
        """
        Sets colors used by application based on light or dark mode
        """
        if self.is_dark_mode:
            # Dark mode colors
            self.colors = {
                        'prompt_text_color': '#838383',
                        'entry_text_color': '#c2c2c2',
                        'label_text_color': '#c2c2c2',
                        'menu_text_color': '#ebebeb',
                        'background_color': '#2c2c2c',
                        'widget_color': '#383838',
                        'pressed_widget_color': '#2e2e2e',
                        'faint_text_color': '#494949',
                        'faint_display_color': '#424242'
                        }
        else:
            # Light mode colors
            self.colors = {
                        'prompt_text_color': '#797979',
                        'entry_text_color': '#4b4b4b',
                        'label_text_color': '#4b4b4b',
                        'menu_text_color': '#505050',
                        'background_color': '#d3d3d3',
                        'widget_color': '#b3b3b3',
                        'pressed_widget_color': '#969696',
                        'faint_text_color': '#a5a5a5',
                        'faint_display_color': '#a1a1a1'
                        }
    
    def change_colors(self):
        """
        Changes colors for window and megawidgets based on current theme mode
        """
        # Set colorway to be used
        self._set_colors()

        # Change root color
        self._root.config({'background': self.colors.get('background_color')})
        
        # Change color for all megawidgets
        self._week_widget.change_colors()
        self._event_entry_widget.change_colors()
        self._calendar_widget.change_colors()
        self._to_do_widget.change_colors()
        self._settings_widget.change_colors()

if __name__ == '__main__':
    Hourglass()