from tkinter import *
from tkinter import ttk
import tkinter.messagebox
import pickle

HEADER_COLOUR = "#BAB2B5"


def is_num(new_value, type_int=False):
    """
    validation to int and float function for entry widgets

    :param new_value: String of current contents of entry widget
    :param type_int: True if validating to an int, False if validating to a float (default False)
    :return: True if current contents of entry widget can be converted to the type specified by type_int
    """

    if new_value == "":
        return True
    try:
        if type_int:
            int(new_value)
        else:
            float(new_value)
        return True
    except ValueError:
        return False


def price_string_to_int(price):
    """
    converts the string form '$xx.xx' to a float xx.xx

    :param price: string in form '$xx.xx'
    :return: the float of price with the sign stripped (xx.xx)
    """
    return float(price.strip('$'))


class InventorySystemGUI:
    def __init__(self, parent):
        # Entry widget validation commands
        vcmd_validate_float = (root.register(is_num), '%P')
        vcmd_validate_int = (root.register(lambda new_value: is_num(new_value, type_int=True)), '%P')

        self.selected_item_iid = None
        self.item_data = []

        self.home_frame = Frame(parent)
        self.home_frame.pack()
        self.active_frame = self.home_frame

        header_frame = Frame(self.home_frame, bg=HEADER_COLOUR)
        header_frame.grid(row=0, column=1, sticky=E + W)

        search_label = Label(header_frame, text="Search by Name", bg=HEADER_COLOUR)
        search_label.grid(row=0, column=1, sticky=E)
        self.search_val = StringVar()
        self.search_val.trace_add("write", lambda a, b, c: self.search())
        self.search_entry = Entry(header_frame, textvariable=self.search_val)
        self.search_entry.grid(row=0, column=2, sticky=W)
        clear_search_btn = Button(header_frame, text="Clear", command=lambda: self.search_val.set(""))
        clear_search_btn.grid(row=0, column=3, sticky=E, padx=5)

        filter_label = Label(header_frame, text="Filter by:", bg=HEADER_COLOUR, anchor=E)
        filter_label.grid(row=0, column=4, sticky=E, ipadx=25)

        self.filter_options = ("A-Z", "Z-A", "Price Low-High", "Price High-Low", "Qty Low-High", "Qty High-Low")
        self.filter_option = StringVar()
        self.filter_option.set(self.filter_options[0])
        self.filter_option.trace_add("write", lambda a, b, c: self.prepare_sort())
        filter_dropdown = OptionMenu(header_frame, self.filter_option, *self.filter_options)
        filter_dropdown.configure(width=20)
        filter_dropdown.grid(row=0, column=5, sticky=E + W, padx=5, pady=4)

        self.hidden_items = []

        # Sidebar Frame (buttons)
        self.sidebar_frame = Frame(self.home_frame)
        self.sidebar_frame.grid(row=0, column=0, rowspan=3, sticky="nsew")

        self.focus_btn = Button(self.sidebar_frame, text="Focus",
                                command=lambda: self.update_selected_item())
        self.focus_btn.grid(row=0, column=0, sticky=N + E + W, padx=10, pady=10)

        add_item_btn = Button(self.sidebar_frame, text="Add New Item",
                              command=lambda: self.activate_frame(self.add_item_frame))
        add_item_btn.grid(row=1, column=0, sticky=N + E + W, padx=10, pady=10)
        self.delete_item_btn = Button(self.sidebar_frame, text="Delete Item", command=self.delete_item)
        self.delete_item_btn.grid(row=2, column=0, sticky=N + E + W, padx=10, pady=10)
        self.delete_all_btn = Button(self.sidebar_frame, text="Delete All", command=self.delete_all)
        self.delete_all_btn.grid(row=3, column=0, sticky=N + E + W, padx=10)

        reset_btn = Button(self.sidebar_frame, text="Restore From Save", command=self.reset_items, anchor=S)
        reset_btn.grid(row=4, column=0, sticky=N + E + W + S, padx=10, pady=30)

        save_btn = Button(self.sidebar_frame, text="Save Items", command=self.save_items)
        save_btn.grid(row=6, column=0, sticky=N + E + W, padx=10, pady=10)

        # Styling for the treeview
        style = ttk.Style()
        style.theme_use("default")

        # Creating the empty treeview
        self.tree_frame = Frame(self.home_frame)
        self.tree_frame.grid(row=2, column=1, sticky="ew")
        self.item_tree = ttk.Treeview(self.tree_frame, selectmode='browse')
        self.item_tree.pack(side='left', fill='x', expand='1')

        vsb = ttk.Scrollbar(self.tree_frame, orient="vertical", command=self.item_tree.yview)
        vsb.pack(side='right', fill='y')

        self.item_tree.configure(yscrollcommand=vsb.set)

        self.item_tree["columns"] = ("1", "2", "3")
        self.item_tree['show'] = 'headings'
        self.item_tree.column("1", width=200, minwidth=120, anchor='w')
        self.item_tree.column("2", width=80, minwidth=80, anchor='e')
        self.item_tree.column("3", width=80, minwidth=80, anchor='e')
        self.item_tree.heading("1", text="Name", anchor='w')
        self.item_tree.heading("2", text="Price", anchor='e')
        self.item_tree.heading("3", text="Quantity", anchor='e')

        # Creating 'Sell/Restock' items frame
        sell_restock_frame = Frame(self.home_frame)
        sell_restock_frame.grid(row=3, column=1, columnspan=2, sticky="nsew")
        sell_restock_label = Label(sell_restock_frame, text="Enter a number to sell/restock the selected item")
        sell_restock_label.grid(row=0, column=0, columnspan=3, sticky="ew")

        self.sell_restock_quantity = StringVar()
        sell_restock_entry = Entry(sell_restock_frame, textvariable=self.sell_restock_quantity, validate="all",
                                   validatecommand=vcmd_validate_int)
        sell_restock_entry.grid(row=1, column=0)
        self.sell_item_btn = Button(sell_restock_frame, text="Sell",
                                    command=lambda: self.update_quantity(sell=True))
        self.sell_item_btn.grid(row=1, column=1, sticky="ew", ipadx=12, padx=20, pady=4)
        self.restock_item_btn = Button(sell_restock_frame, text="Restock",
                                       command=lambda: self.update_quantity(sell=False))
        self.restock_item_btn.grid(row=1, column=2, sticky="ew")

        # Selects first row/item in tree by default
        self.update_selected_item()

        # Creating 'Add items' frame
        self.add_item_frame = Frame(parent)
        add_item_title = Label(self.add_item_frame, text="Add New Product", bg=HEADER_COLOUR)
        add_item_title.grid(row=0, column=0, sticky=E + W, ipady=8)
        tkinter.ttk.Separator(self.add_item_frame, orient=HORIZONTAL).grid(column=0, row=1, columnspan=2, sticky='ew')

        self.name_var = StringVar()
        self.price_var = StringVar()
        self.quantity_var = StringVar()

        enter_name_label = Label(self.add_item_frame, text="Name of Product")
        enter_name_label.grid(row=2, column=0)

        self.name_entry = Entry(self.add_item_frame, textvariable=self.name_var)
        self.name_entry.grid(row=3, column=0)

        enter_price_label = Label(self.add_item_frame, text="Sale Price")
        enter_price_label.grid(row=6, column=0)
        price_entry = Entry(self.add_item_frame, textvariable=self.price_var, validate="all",
                            validatecommand=vcmd_validate_float)
        price_entry.grid(row=7, column=0)
        enter_quantity_label = Label(self.add_item_frame, text="Quantity")
        enter_quantity_label.grid(row=8, column=0)
        quantity_entry = Entry(self.add_item_frame, textvariable=self.quantity_var, validate="all",
                               validatecommand=vcmd_validate_int)
        quantity_entry.grid(row=9, column=0)

        button_frame = Frame(self.add_item_frame)
        button_frame.grid(row=10, column=0)
        cancel_addition_btn = Button(button_frame, text="Back",
                                     command=lambda: self.activate_frame(self.home_frame))
        cancel_addition_btn.grid(row=0, column=0, ipadx=20, padx=5)
        clear_btn = Button(button_frame, text="Clear", command=self.clear_add_item_inputs)
        clear_btn.grid(row=0, column=1, pady=8, padx=5, ipadx=20)
        submit_btn = Button(button_frame, text="Complete Item", command=self.add_item)
        submit_btn.grid(row=0, column=2, pady=8, padx=5)

        # Read and load up item information from external file
        self.load_items()

    def prepare_sort(self):
        """
        Prepares parameters for sort() based on which filter is selected

        :return: None
        """
        option_index = self.filter_options.index(self.filter_option.get())
        # Determines which column should be sorted and how to process each type of data for comparison
        if option_index == 0 or option_index == 1:
            col = 1

            def command(x):
                return str(x[0]).lower().strip()
        elif option_index == 2 or option_index == 3:
            col = 2

            def command(x):
                return float(x[0].strip('$'))

        else:
            col = 3

            def command(x):
                return int(x[0])

        # Every second item in list requires reverse sorting
        reverse = False if option_index % 2 == 0 else True
        self.sort(col, command, reverse)

    def sort(self, col, command, reverse):
        """
        Sorts shown items in list based on parameters prepared by on_filter_change()

        :param col: column to sort by
        :param command: command to call on each item before sorting
        :param reverse: Boolean: should the order of items be reversed once sorted?
        :return: None
        """

        # Gets and sorts all shown value-item pairs in treeview
        values = [(self.item_tree.set(k, col), k) for k in self.item_tree.get_children('')]
        values.sort(reverse=reverse, key=command)

        # Rearrange items in sorted positions
        for index, (val, k) in enumerate(values):
            self.item_tree.move(k, '', index)
        self.update_selected_item()

    def load_items(self):
        """
        Attempts to populate the treeview with loaded item data from external file named 'item_data'

        :return: None
        """
        try:
            with open('item_data', 'rb') as f:
                self.item_data = pickle.load(f)

            # Treat empty list the same as empty file
            if len(self.item_data) == 0:
                raise EOFError

            # Add all items to treeview
            for i in range(len(self.item_data)):
                self.item_tree.insert("", 'end', values=(
                    self.item_data[i][0], "${:,.2f}".format(self.item_data[i][1]),
                    self.item_data[i][2]))

            self.prepare_sort()
        except FileNotFoundError:
            tkinter.messagebox.showerror("File Not Found", "Please ensure that there is a non-empty file "
                                                           "called 'item_data' in the same folder as "
                                                           "this program. A new file was created, "
                                                           "but you can try re-downloading the latest version"
                                                           " from GitHub")
            new_file = open("item_data", "x")
            new_file.close()
            # Message boxes steal focus from root window which cannot be restored by clicking, so focus is forced
            root.focus_force()
        except EOFError:
            tkinter.messagebox.showwarning("Empty File", "The data file was empty, so no data was loaded")
            root.focus_force()

    def get_selected_item_info(self):
        """
        Gets values from the 'values' property of the selected treeview item

        :return: A list of the values from the 'values' property of the selected treeview item
        """

        info = self.item_tree.item(self.item_tree.selection()[0], 'values')
        return [info[0], info[1], int(info[2])]

    def search(self):
        """
        Shows only items in the treeview which have the search term within their name

        :return: None
        """
        # Check if any shown items should be hidden
        for item in self.item_tree.get_children():
            if self.search_val.get().strip().lower() not in self.item_tree.item(item, "values")[0].strip().lower():
                self.hidden_items.append(item)
                # Deselect hidden items which were selected and handle reselection of new item
                if item == self.selected_item_iid:
                    self.item_tree.selection_remove(item)
                    self.item_tree.detach(item)
                    self.update_selected_item()
                else:
                    self.item_tree.detach(item)
        # Check if any hidden items should be shown
        new_hidden_item_list = []
        for item in self.hidden_items:
            # Checks if item should stay hidden
            if self.search_val.get().strip().lower() not in self.item_tree.item(item, "values")[0].strip().lower():
                # Items in list cannot be deleted while iterating.
                # Stores items in a temp list and then dumps into original list once complete
                new_hidden_item_list.append(item)
            else:
                # Shows item
                self.item_tree.reattach(item, "", len(self.item_tree.get_children()))
        self.hidden_items = new_hidden_item_list
        self.update_selected_item()

        # Sorts updated shown items
        self.prepare_sort()

    def delete_item(self):
        """
        Deletes the selected treeview item and handles refocusing

        :return: None
        """
        confirm = tkinter.messagebox.askokcancel("Delete selected item", "This action cannot be undone. Proceed?",
                                                 icon="warning")
        if confirm:
            self.update_selected_item()
            # Try to select the next item
            new_selected_item = self.item_tree.next(self.selected_item_iid)
            # If the deleted item is the last item, select the previous item instead
            if new_selected_item == "":
                new_selected_item = self.item_tree.prev(self.selected_item_iid)
            self.item_tree.delete(self.selected_item_iid)
            self.item_tree.focus(new_selected_item)
            self.item_tree.selection_set(new_selected_item)
            self.update_selected_item()

    def delete_all(self):
        """
        Delete all items in treeview (shown and hidden)

        :return: None
        """
        confirm = tkinter.messagebox.askokcancel("Delete all items",
                                                 "All items will be deleted, including hidden items. "
                                                 "This action cannot be undone. Proceed?",
                                                 icon="warning")
        if confirm:
            # Unpack all shown items in order to delete
            self.item_tree.delete(*self.item_tree.get_children())
            self.hidden_items.clear()
            self.update_selected_item()

    def reset_items(self):
        """
        Repopulate treeview using last saved version of external file named 'item_data'.

        :return: None
        """
        confirm = tkinter.messagebox.askokcancel("Reset Items",
                                                 "Items will be reset to last saved state. "
                                                 "Any unsaved changes will be lost. "
                                                 "This action cannot be undone. Proceed?",
                                                 icon='warning')
        if confirm:
            # Warn user if restored data will be empty
            try:
                with open('item_data', 'rb') as f:
                    self.item_data = pickle.load(f)
                if len(self.item_data) == 0:
                    raise EOFError
            except EOFError:
                confirm = tkinter.messagebox.askokcancel("Empty File", "The data file is empty, do you want to load "
                                                                       "empty data?", icon="warning")
                if not confirm:
                    return

            # Restore data by wiping existing data then reloading
            self.item_tree.delete(*self.item_tree.get_children())
            self.hidden_items.clear()
            self.load_items()
            self.update_selected_item()
            self.search_val.set("")
            tkinter.messagebox.showinfo("Success",
                                        "Successfully restored items")

    def activate_frame(self, frame):
        """
        Activates a frame and hides the current frame to provide the effect of 'changing screens'
        :param frame: frame to activate
        :return: None
        """
        self.active_frame.pack_forget()
        self.active_frame = frame
        frame.pack()

        self.clear_add_item_inputs()
        self.update_selected_item()

    def update_selected_item(self):
        """
        Handles selecting a new item when the selected item is hidden or removed to ensure an item is always selected
        where possible. Disables selection-dependent buttons if no selection is possible (empty treeview)

        :return: None
        """
        # If no item selected
        if len(self.item_tree.selection()) == 0:
            try:
                new_selection = self.item_tree.get_children()[0]
                self.item_tree.focus(new_selection)
                self.item_tree.selection_set(new_selection)
            # If tree is empty
            except IndexError:
                # Disable selection-dependent buttons
                self.selected_item_iid = None
                self.focus_btn.configure(state=DISABLED)
                self.sell_item_btn.configure(state=DISABLED)
                self.restock_item_btn.configure(state=DISABLED)
                self.delete_item_btn.configure(state=DISABLED)
                self.delete_all_btn.configure(state=NORMAL if len(self.hidden_items) > 0 else DISABLED)
                return

        # Update selected item and re-enable selection-dependent buttons
        self.selected_item_iid = self.item_tree.selection()[0]
        self.focus_btn.configure(state=NORMAL)
        self.sell_item_btn.configure(state=NORMAL)
        self.restock_item_btn.configure(state=NORMAL)
        self.delete_item_btn.configure(state=NORMAL)
        self.delete_all_btn.configure(state=NORMAL)
        self.item_tree.see(self.selected_item_iid)

    def clear_add_item_inputs(self):
        """
        Clears all Entry_widget fields from the 'Add Item' screen and focuses on the 'Name' Entry Widget

        :return: None
        """
        self.name_entry.focus()
        self.name_var.set("")
        self.price_var.set("")
        self.quantity_var.set("")

    def add_item(self):
        """
        Adds a new item to the treeview based on the user-entered properties in the "Add Item" screen

        :return: None
        """

        # Displays error if any of the mandatory fields are empty
        if self.name_var.get() == "" or self.price_var.get() == "" or self.quantity_var.get() == "":
            tkinter.messagebox.showerror("Input Error",
                                         "Please ensure that all mandatory fields are completed")
        else:
            # Makes a list of all existing names in tree
            all_names = [self.item_tree.item(item, 'values')[0].strip().lower() for item in
                         self.item_tree.get_children()]
            # Check for duplicate name, case insensitive
            if self.name_var.get().strip().lower() in all_names:
                confirm = tkinter.messagebox.askokcancel("Duplicate Entry",
                                                         "New item has same name as existing item. "
                                                         "Existing item will NOT be overwritten. Proceed?",
                                                         icon='warning')
                if not confirm:
                    return

            # Insert the new item at the end, then update the treeview
            self.item_tree.insert("", 'end', values=(
                self.name_var.get(), "${:,.2f}".format(float(self.price_var.get())),
                int(self.quantity_var.get())))

            self.update_selected_item()
            self.activate_frame(self.home_frame)
            self.search()
            self.prepare_sort()
            tkinter.messagebox.showinfo("Success",
                                        "Successfully added item (may be hidden due to filters)")

    def update_quantity(self, sell):
        """
        Changes the quantity of the selected item in the treeview based on the user-entered value and whether they
        choose to sell (subtract) or restock (add)

        :param sell: True if selling, False if restocking
        :return: None
        """
        try:
            current_info = self.get_selected_item_info()
            if int(self.sell_restock_quantity.get()) == 0:
                raise ValueError
            else:
                # Additional checks when subtracting (selling) since resultant quantity can't be negative
                if sell:
                    if int(self.sell_restock_quantity.get()) > current_info[2]:
                        tkinter.messagebox.showerror("Input Error",
                                                     "Number sold cannot exceed stocked quantity")
                        return
                    current_info[2] -= int(self.sell_restock_quantity.get())
                else:
                    current_info[2] += int(self.sell_restock_quantity.get())

                # Update selected item quantity to new calculated value
                self.item_tree.set(self.item_tree.selection()[0], column=3,
                                   value=current_info[2])

                tkinter.messagebox.showinfo("Success",
                                            "Successfully {} {} units of '{}'".format(
                                                "sold" if sell else "restocked",
                                                self.sell_restock_quantity.get(),
                                                current_info[0]))
        # Handles user submitting the default empty string in Entry Widgets.
        # Also catches raised exception when '0' is entered
        except ValueError:
            tkinter.messagebox.showerror("Input Error",
                                         "Please enter a positive number")
        self.sell_restock_quantity.set("")
        self.prepare_sort()

    def save_items(self):
        """
        Overwrites the external item_data file with data from both the shown and hidden treeview items
        :return:
        """
        # Warns the user that the data they are about to save is empty
        if self.item_tree.get_children() == () and len(self.hidden_items) == 0:
            confirm = tkinter.messagebox.askokcancel("No Items", "You are attempting to update the external file to "
                                                                 "No Data. This "
                                                                 "action cannot be undone.  Proceed?",
                                                     icon='warning')
        else:
            confirm = tkinter.messagebox.askokcancel("Save Items",
                                                     "The external file will be updated and overwritten. This "
                                                     "action cannot be undone. Proceed?",
                                                     icon='warning')
        if not confirm:
            return

        # Make a list of all items in the treeview, shown and hidden
        item_list = []
        for item in self.item_tree.get_children():
            values = self.item_tree.item(item, "values")
            item_list.append((values[0], price_string_to_int(values[1]), int(values[2])))
        for item in self.hidden_items:
            values = self.item_tree.item(item, "values")
            item_list.append((values[0], price_string_to_int(values[1]), int(values[2])))

        # Overwrites existing info in the file with new list of all treeview items
        item_file = open('item_data', 'wb')
        pickle.dump(item_list, item_file)
        item_file.close()
        tkinter.messagebox.showinfo("Success",
                                    "Successfully Updated Saved Items")


# Main routine
if __name__ == "__main__":
    root = Tk()
    application = InventorySystemGUI(root)
    root.mainloop()
