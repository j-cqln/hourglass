import tkinter as tk

from utilities.constants import CHECKBUTTON_OFF, CHECKBUTTON_ON
from utilities.functions import widget_pressed, widget_released

class ToDoMenu:
    """
    Class for the to-do edit/remove menu

    Creates a GUI popup for Hourglass
    """
    def __init__(self, parent, root, index, total, item):
        """
        Initializes the ToDoMenu class

        parent: Parent widget, tkinter widget
        darkmode: Whether the parent is currently in dark mode or not, boolean
        index: The index of the clicked item in the to-do list, int
        total: The number of items in the to-do list, int
        item: The to-do list item, dict
        """
        # Paren Hourglass
        self._parent = parent

        # Set to-do list item information
        self._item = item.copy()
        self._index = index
        self._total = total
        self._selected = None

        # Window
        self._root = tk.Toplevel(root)

        # Title
        self._root.title('edit to-do...')
        
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
        self._root.rowconfigure(1, weight=1)
        self._root.rowconfigure(2, weight=0)

        # Set up widgets
        self._index_completion_setup()
        self._text_setup()
        self._buttons_setup()

        # Change display colors based on theme
        self._change_colors()
    
    def _index_completion_setup(self):
        """
        Sets up the to-do item index and completion status component of the popup window
        """
        # Frame for to-do task index
        self._index_completion_frame = tk.Frame(self._root, borderwidth=0, highlightthickness=0)
        self._index_completion_frame.grid(row=0, column=0, padx=(6, 6), pady=(6, 3), sticky='NWSE')
        
        self._index_completion_frame.columnconfigure(0, weight=0)
        self._index_completion_frame.columnconfigure(1, weight=0)

        # Item index
        self._index_label = tk.Label(self._index_completion_frame, text='rank:', borderwidth=0, highlightthickness=0)
        self._index_label.grid(row=0, column=0, sticky='NWSE')

        # For selecting item index
        self._current_item_index = tk.IntVar(self._index_completion_frame)
        self._current_item_index.set(self._index + 1)
        self._dropdown_indices = [i for i in range(1, self._total + 1)]
        self._hour_selection_menu = tk.OptionMenu(self._index_completion_frame, self._current_item_index, *self._dropdown_indices)
        self._hour_selection_menu.config({'borderwidth': 0, 'highlightthickness': 0})
        self._hour_selection_menu.grid(row=0, column=1, padx=(3, 3), pady=(2, 0), sticky='NWSE')

        # For selecting item completion
        self._completion = tk.IntVar(self._index_completion_frame)
        self._completion.set(self._item.get('completion'))
        self._completion_checkbutton = tk.Checkbutton(self._index_completion_frame, text='complete', variable=self._completion, onvalue=CHECKBUTTON_ON, offvalue=CHECKBUTTON_OFF, anchor='w', justify='left')
        self._completion_checkbutton.config({'highlightthickness': 0})
        self._completion_checkbutton.grid(row=0, column=2, padx=(3, 0), pady=(2, 0), sticky='NWSE')

    def _text_setup(self):
        """
        Sets up the to-do item description component of the popup window
        """
        # To-do item description
        self._text = tk.Text(self._root, width=1, height=1, borderwidth=0, highlightthickness=0)
        self._text.insert(tk.END, self._item.get('description'))
        self._text.grid(row=1, column=0, padx=(6, 6), pady=(3, 3), sticky='NWSE')

    def _buttons_setup(self):
        """
        Sets up the edit/remove and cancel buttons of the popup window
        """
        # Frame for buttons
        self._buttons_frame = tk.Frame(self._root, borderwidth=0, highlightthickness=0)
        self._buttons_frame.grid(row=2, column=0, padx=(6, 6), pady=(3, 6), sticky='NWSE')

        self._buttons_frame.columnconfigure(0, weight=3)
        self._buttons_frame.columnconfigure(1, weight=2)
        self._buttons_frame.columnconfigure(2, weight=2)

        # Edit button
        self._edit_button = tk.Label(self._buttons_frame, text='edit', borderwidth=0, highlightthickness=0)
        self._edit_button.bind('<Button-1>', lambda event: self._select(event.widget, 'edit'))
        self._edit_button.bind('<ButtonRelease>', lambda event: widget_released(event.widget, self._parent.colors))
        self._edit_button.grid(row=0, column=0, padx=(100, 3), sticky='NWSE')

        # Remove button
        self._remove_button = tk.Label(self._buttons_frame, text='remove', borderwidth=0, highlightthickness=0)
        self._remove_button.bind('<Button-1>', lambda event: self._select(event.widget, 'remove'))
        self._remove_button.bind('<ButtonRelease>', lambda event: widget_released(event.widget, self._parent.colors))
        self._remove_button.grid(row=0, column=1, padx=(3, 3), sticky='NWSE')

        # Cancel button
        self._cancel_button = tk.Label(self._buttons_frame, text='cancel', borderwidth=0, highlightthickness=0)
        self._cancel_button.bind('<Button-1>', lambda event: self._select(event.widget, None))
        self._cancel_button.bind('<ButtonRelease>', lambda event: widget_released(event.widget, self._parent.colors))
        self._cancel_button.grid(row=0, column=2, padx=(3, 0), sticky='NWSE')
    
    def _select(self, widget, selection):
        """
        Selects action for to-do item

        widget: The widget clicked by the user to make the selection
        selection: Action for the to-do item, either the strings 'edit', 'remove', or None for cancel
        """
        widget_pressed(widget, self._parent.colors)

        self._selected = selection

        if selection is not None:
            self._item['completion'] = str(self._completion.get())
            self._item['description'] = self._text.get('1.0', tk.END).strip()

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
                if parent is self._index_completion_frame:
                    child.config({'foreground': self._parent.colors.get('label_text_color')})
                    child.config({'background': self._parent.colors.get('background_color')})
                else:
                    child.config({'foreground': self._parent.colors.get('label_text_color')})
                    child.config({'background': self._parent.colors.get('widget_color')})
            
            elif type(child) is tk.OptionMenu:
                child.config({'foreground': self._parent.colors.get('menu_text_color')})
                child.config({'background': self._parent.colors.get('background_color')})
            
            elif type(child) is tk.Checkbutton:
                child.config({'foreground': self._parent.colors.get('label_text_color')})
                child.config({'background': self._parent.colors.get('background_color')})
            
            elif type(child) is tk.Text:
                child.config({'foreground': self._parent.colors.get('prompt_text_color')})
                child.config({'background': self._parent.colors.get('widget_color')})

            elif type(child) is tk.Frame:
                child.config({'background': self._parent.colors.get('background_color')})

    def show(self):
        """
        Shows the popup window and waits for it to be closed, then returning the user's modifications to the to-do list item

        return: Tuple containing the selection of the user, the to-do item index, and modifications of the to-do item information
        """
        self._root.deiconify()
        self._root.wait_window(self._root)
        return (self._selected, self._current_item_index.get() - 1, self._item)