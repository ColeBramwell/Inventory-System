from tkinter import *
from tkinter import ttk
import tkinter.messagebox
import pickle

HEADER_COLOUR = "#BAB2B5"


def is_num(new_value, type_int=False):
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
        self.filter_option.trace_add("write", lambda a, b, c: self.on_filter_change())
        filter_dropdown = OptionMenu(header_frame, self.filter_option, *self.filter_options)
        filter_dropdown.configure(width=20)
        filter_dropdown.grid(row=0, column=5, sticky=E + W, padx=5, pady=4)

        self.hidden_items = []

        # Sidebar Frame (buttons)
        self.sidebar_frame = Frame(self.home_frame)
        self.sidebar_frame.grid(row=0, column=0, rowspan=3, sticky="nsew")

        self.focus_btn = Button(self.sidebar_frame, text="Focus",
                                command=lambda: self.item_tree.see(self.selected_item_iid))
        self.focus_btn.grid(row=0, column=0, sticky=N + E + W, padx=10, pady=10)

        add_item_btn = Button(self.sidebar_frame, text="Add New Item",
                              command=lambda: self.activate_frame(self.add_item_frame))
        add_item_btn.grid(row=1, column=0, sticky=N + E + W, padx=10, pady=10)
        self.delete_item_btn = Button(self.sidebar_frame, text="Delete Item", command=self.delete_item)
        self.delete_item_btn.grid(row=2, column=0, sticky=N + E + W, padx=10, pady=10)
        self.delete_all_btn = Button(self.sidebar_frame, text="Delete All", command=self.delete_all)
        self.delete_all_btn.grid(row=3, column=0, sticky=N + E + W, padx=10)

        reset_btn = Button(self.sidebar_frame, text="Reset Items", command=self.reset_items)
        reset_btn.grid(row=4, column=0, sticky=N + E + W, padx=10, pady=10)

        save_btn = Button(self.sidebar_frame, text="Save Items")
        save_btn.grid(row=5, column=0, sticky=N + E + W, padx=10, pady=30)

        # styling the tree
        style = ttk.Style()
        style.theme_use("default")

        """style.configure("Treeview",
                        background=""
        )
        style.configure("Treeview.Heading",  background="Blue")

        style.map("Treeview", background=[("selected", "#123C69")])"""

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

        # sell/restock items frame
        sell_restock_frame = Frame(self.home_frame)
        sell_restock_frame.grid(row=3, column=1, columnspan=2, sticky="nsew")
        sell_restock_label = Label(sell_restock_frame, text="Enter a number to sell/restock the selected item")
        sell_restock_label.grid(row=0, column=0, columnspan=3, sticky="ew")

        self.sell_restock_quantity = StringVar()
        sell_restock_entry = Entry(sell_restock_frame, textvariable=self.sell_restock_quantity, validate="all",
                                   validatecommand=vcmd_validate_int)
        sell_restock_entry.grid(row=1, column=0)
        self.sell_item_btn = Button(sell_restock_frame, text="Sell",
                                    command=self.sell_item)
        self.sell_item_btn.grid(row=1, column=1, sticky="ew", ipadx=12, padx=20, pady=4)
        self.restock_item_btn = Button(sell_restock_frame, text="Restock",
                                       command=self.restock_item)
        self.restock_item_btn.grid(row=1, column=2, sticky="ew")

        # selects first row/item in tree by default
        self.update_selected_item()

        # ADD ITEMS FRAME
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
        enter_description_label = Label(self.add_item_frame, text="Description (optional)")
        enter_description_label.grid(row=4, column=0)
        self.description_entry = Text(self.add_item_frame, height=3, width=25)
        self.description_entry.grid(row=5, column=0)
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
        clear_btn = Button(button_frame, text="Clear", command=self.clear_all_inputs)
        clear_btn.grid(row=0, column=1, pady=8, padx=5, ipadx=20)
        submit_btn = Button(button_frame, text="Complete Item", command=self.add_item)
        submit_btn.grid(row=0, column=2, pady=8, padx=5)

        # reading and setting up item information from file
        self.load_items()

    def on_filter_change(self):
        option_index = self.filter_options.index(self.filter_option.get())
        # establishes column that should be sorted and how to process each
        # type of data for comparison
        if option_index == 0 or option_index == 1:
            col = 1

            # restructure these command definitions, as they don't need to be
            # redefined every iteration
            def command(x):
                return str(x[0])
        elif option_index == 2 or option_index == 3:
            col = 2

            # probably could be more efficient/compact by using a library
            def command(number):
                number = number[0].strip('$')
                [num, dec] = number.rsplit('.')
                dec = int(dec)
                aside = str(dec)
                x = int('1' + '0' * len(aside))
                price = float(dec) / x
                num = num.replace(',', '')
                num = int(num)
                price = num + price
                return price
        else:
            col = 3

            def command(x):
                return int(x[0])
        # every second item in list requires reverse sorting
        reverse = False if option_index % 2 == 0 else True
        self.sort(self.item_tree, col, command, reverse)

    def sort(self, tv, col, command, reverse):
        values = [(tv.set(k, col), k) for k in tv.get_children('')]
        values.sort(reverse=reverse, key=command)

        # rearrange items in sorted positions
        for index, (val, k) in enumerate(values):
            tv.move(k, '', index)
        self.update_selected_item()

    def load_items(self):
        with open('item_data', 'rb') as f:
            self.item_data = pickle.load(f)

        # add all items to tree
        for i in range(len(self.item_data)):
            self.item_tree.insert("", 'end', values=(
                self.item_data[i][0], "${:,.2f}".format(self.item_data[i][1]),
                self.item_data[i][2]))
        self.on_filter_change()

    def get_selected_item_info(self):
        info = self.item_tree.item(self.item_tree.selection()[0], 'values')
        return [info[0], info[1], int(info[2])]

    def search(self):
        # check if any shown items should be hidden
        for item in self.item_tree.get_children():
            if self.search_val.get().strip().lower() not in self.item_tree.item(item, "values")[0].strip().lower():
                self.hidden_items.append(item)
                # deselect hidden items which were selected
                if item == self.selected_item_iid:  # updates multiple times when hiding objects,
                    self.item_tree.selection_remove(item)
                    self.item_tree.detach(item)
                    self.update_selected_item()
                else:
                    self.item_tree.detach(item)
        # check if any hidden items should be shown
        new_hidden_item_list = []
        for item in self.hidden_items:
            if self.search_val.get().strip().lower() not in self.item_tree.item(item, "values")[0].strip().lower():
                # hacky solution since cant delete items while iterating - stores items in a temp list and
                # dump into main list once complete
                new_hidden_item_list.append(item)
            else:
                self.item_tree.reattach(item, "", len(self.item_tree.get_children()))
        self.hidden_items = new_hidden_item_list
        self.update_selected_item()

        # might be quite inefficient to sort every time as list size grows
        self.on_filter_change()

    def delete_item(self):
        confirm = tkinter.messagebox.askokcancel("Delete selected item", "This action cannot be undone. Proceed?",
                                                 icon="warning")
        if confirm:
            self.update_selected_item()
            new_selected_item = self.item_tree.next(self.selected_item_iid)
            self.item_tree.delete(self.selected_item_iid)
            self.item_tree.focus(new_selected_item)
            self.item_tree.selection_set(new_selected_item)
            self.update_selected_item()

    def delete_all(self):
        confirm = tkinter.messagebox.askokcancel("Delete all items", "This action cannot be undone. Proceed?",
                                                 icon="warning")
        if confirm:
            self.item_tree.delete(*self.item_tree.get_children())
            self.update_selected_item()

    def reset_items(self):
        confirm = tkinter.messagebox.askokcancel("Reset Items",
                                                 "Items will be reset to last saved state. "
                                                 "This action cannot be undone. Proceed?",
                                                 icon='warning')
        if confirm:
            self.item_tree.delete(*self.item_tree.get_children())
            self.load_items()
            self.update_selected_item()

    def activate_frame(self, frame):
        self.active_frame.pack_forget()
        self.active_frame = frame
        frame.pack()

        self.clear_all_inputs()
        self.update_selected_item()

    def update_selected_item(self):
        if len(self.item_tree.selection()) == 0:
            try:
                new_selection = self.item_tree.get_children()[0]
                self.item_tree.focus(new_selection)
                self.item_tree.selection_set(new_selection)
            except IndexError:
                self.selected_item_iid = None
                self.focus_btn.configure(state=DISABLED)
                self.sell_item_btn.configure(state=DISABLED)
                self.restock_item_btn.configure(state=DISABLED)
                self.delete_item_btn.configure(state=DISABLED)
                self.delete_all_btn.configure(state=DISABLED)
                return

        self.selected_item_iid = self.item_tree.selection()[0]
        self.focus_btn.configure(state=NORMAL)
        self.sell_item_btn.configure(state=NORMAL)
        self.restock_item_btn.configure(state=NORMAL)
        self.delete_item_btn.configure(state=NORMAL)
        self.delete_all_btn.configure(state=NORMAL)
        self.item_tree.see(self.selected_item_iid)

    def clear_all_inputs(self):
        self.name_entry.focus()
        self.name_var.set("")
        self.description_entry.delete('1.0', END)
        self.price_var.set("")
        self.quantity_var.set("")

    def add_item(self):
        # displays error if any of the mandatory fields are empty
        if self.name_var.get() == "" or self.price_var.get() == "" or self.quantity_var.get() == "":
            tkinter.messagebox.showerror("Input Error",
                                         "Please ensure that all mandatory fields are completed")
        else:
            # makes a list of all existing names in tree
            all_names = [self.item_tree.item(item, 'values')[0].strip().lower() for item in
                         self.item_tree.get_children()]
            # check for duplicate, case insensitive
            if self.name_var.get().strip().lower() in all_names:
                confirm = tkinter.messagebox.askokcancel("Duplicate Entry",
                                                         "New item has same name as existing item. "
                                                         "Existing item will NOT be overwritten. Proceed?",
                                                         icon='warning')
                if not confirm:
                    return

            self.item_tree.insert("", 'end', values=(
                self.name_var.get(), "${:,.2f}".format(float(self.price_var.get())),
                int(self.quantity_var.get())))

            self.update_selected_item()
            self.activate_frame(self.home_frame)
            self.search()
            tkinter.messagebox.showinfo("Success",
                                        "Successfully added item (may be hidden due to filters)")

    def sell_item(self):
        try:
            current_info = self.get_selected_item_info()
            if int(self.sell_restock_quantity.get()) > current_info[2]:
                tkinter.messagebox.showerror("Input Error",
                                             "Number sold cannot exceed stocked quantity")
            else:
                current_info[2] -= int(self.sell_restock_quantity.get())
                self.item_tree.set(self.item_tree.selection()[0], column=3,
                                   value=current_info[2])

                tkinter.messagebox.showinfo("Success",
                                            "Successfully sold {} units of '{}'".format(
                                                self.sell_restock_quantity.get(),
                                                current_info[0]))
        # handles user submitting the empty string
        except ValueError:
            tkinter.messagebox.showerror("Input Error",
                                         "Please enter a number")
        self.sell_restock_quantity.set("")
        self.on_filter_change()

    def restock_item(self):
        try:
            current_info = self.get_selected_item_info()
            current_info[2] += int(self.sell_restock_quantity.get())
            self.item_tree.set(self.item_tree.selection()[0], column=3,
                               value=current_info[2])

            tkinter.messagebox.showinfo("Success",
                                        "Successfully restocked {} units of '{}'".format(
                                            self.sell_restock_quantity.get(),
                                            current_info[0]))
        except ValueError:
            tkinter.messagebox.showerror("Input Error",
                                         "Please enter a number")
        self.sell_restock_quantity.set("")
        self.on_filter_change()


class Product:
    def __init__(self, name, description, price, quantity):
        self.name = name
        self.description = description
        self.price = price
        self.quantity = quantity


# main routine
if __name__ == "__main__":
    root = Tk()
    application = InventorySystemGUI(root)
    root.mainloop()
    root.grid_columnconfigure(0, weight=1)
