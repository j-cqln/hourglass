import uuid

import tkinter as tk

from widgets.to_do_menu import ToDoMenu

from utilities.constants import CHECKBUTTON_OFF, CHECKBUTTON_ON
from utilities.functions import show_error

class ToDoWidget:
    """
    Class for to-do list megawidget
    """
    def __init__(self, parent, root):
        """
        Sets up the to-do list component of the GUI
        """
        # Parent Hourglass
        self._parent = parent

        # Root window
        self._root = root

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

        # List of checkbuttons for tasks
        self._to_do_list_display = []

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
    
    def _to_do_list_toggle(self, item):
        """
        Toggles the check box for an item

        item: To-do list item, string
        """
        try:
            index = self._parent.to_do_list.index(item)

            if self._parent.to_do_list[index].get('completion') == str(CHECKBUTTON_OFF):
                self._parent.to_do_list[index]['completion'] = str(CHECKBUTTON_ON)
            else:
                self._parent.to_do_list[index]['completion'] = str(CHECKBUTTON_OFF)
        except Exception as e:
            show_error('no such to-do list task.')
        
        self._update_to_do()
    
    def _to_do_list_add(self, description):
        """
        Adds an item to the to-do list

        description: Description of the to-do list item to be added, string
        """
        key = str(uuid.uuid4())
        item = {'key': key, 'completion': str(CHECKBUTTON_OFF), 'description': description}
        self._parent.to_do_list.append(item)

        self._update_to_do()
    
    def _to_do_list_edit_remove(self, index, total, item):
        """
        Edits or removes an item from the to-do list

        index: The index of the clicked item in the to-do list, int
        total: The number of items in the to-do list, int
        item: Item to be removed, string
        """
        try:
            # Retrieve item key
            key = self._parent.to_do_list[index].get('key')

            if key is not None:
                popup = ToDoMenu(self._parent, self._root, index, total, item)
                result = popup.show()
                popup = None

                # Edit or remove item based on user response
                if result[0] == 'remove':
                    if self._parent.to_do_list[index]['key'] == key:
                        del self._parent.to_do_list[index]

                elif result[0] == 'edit':
                    if self._parent.to_do_list[index]['key'] == key:
                        del self._parent.to_do_list[index]
                        self._parent.to_do_list.insert(result[1], result[2])
        except Exception as e:
            show_error('no such to-do list task.')
        
        # Update displayed to-do list
        self._update_to_do()
    
    def _to_do_entry_focus(self, *args):
        """
        Focuses on the to-do entry widget, remove prompt text if it is displayed
        """
        if self._to_do_entry.get() == ' add new to-do...':
            self._to_do_entry.delete(1, tk.END)
            
        self._to_do_entry.config({'foreground': self._parent.colors.get('entry_text_color')})

    def _to_do_entry_unfocus(self, *args):
        """
        Unfocuses from the to-do entry widget, restoring prompt text if no text entered
        """
        if self._to_do_entry.get() == '' or self._to_do_entry.get() == ' ':
            self._to_do_entry.delete(0, tk.END)
            self._to_do_entry.insert(0, ' add new to-do...')

        self._to_do_entry.config({'foreground': self._parent.colors.get('prompt_text_color')})
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
        self._to_do_list_display = []
        self._to_do_list_button_states = [tk.IntVar() for _ in range(len(self._parent.to_do_list))]

        try:
            # Clear displayed items
            self._clear_to_do_list_display()

            # Display all to-do list items
            total = len(self._parent.to_do_list)

            for i in range(total):
                item = self._parent.to_do_list[i]
                self._to_do_list_button_states[i].set(int(item.get('completion')))

                self._to_do_list_display.append(tk.Checkbutton(self._to_do_list_frame, text=item.get('description'), variable=self._to_do_list_button_states[i], onvalue=CHECKBUTTON_ON, offvalue=CHECKBUTTON_OFF, anchor='w', justify='left', command=lambda item=item: self._to_do_list_toggle(item)))
                self._to_do_list_display[-1].config({'foreground': self._parent.colors.get('label_text_color')})
                self._to_do_list_display[-1].config({'background': self._parent.colors.get('widget_color')})
                self._to_do_list_display[-1].config({'highlightthickness': 0})
                self._to_do_list_display[-1].bind('<Button-2>', lambda event, i=i, total=total, item=item: self._to_do_list_edit_remove(i, total, item))
                self._to_do_list_display[-1].grid(row=i, column=0, padx=(2, 2), sticky='NWSE')
        except Exception as e:
            show_error('unable to load or update to-do list.')
    
    def _clear_to_do_list_display(self):
        """
        Clears displayed to-do list items
        """
        for child in self._to_do_list_frame.winfo_children():
            child.destroy()
    
    def change_colors(self):
        """
        Changes colors for this megawidget and all descendant widgets based on current theme mode
        """
        # Change color for all descendant widgets
        self._to_do_frame.config({'background': self._parent.colors.get('widget_color')})

        self._to_do_label.config({'foreground': self._parent.colors.get('label_text_color')})
        self._to_do_label.config({'background': self._parent.colors.get('widget_color')})
        
        self._to_do_list_frame.config({'background': self._parent.colors.get('widget_color')})

        for widget in self._to_do_list_display:
            widget.config({'foreground': self._parent.colors.get('label_text_color')})
            widget.config({'background': self._parent.colors.get('widget_color')})
        
        self._to_do_entry.config({'foreground': self._parent.colors.get('prompt_text_color')})
        self._to_do_entry.config({'background': self._parent.colors.get('widget_color')})