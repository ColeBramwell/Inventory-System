from tkinter import *
from tkinter import ttk
import tkinter.messagebox

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
        self.home_frame = Frame(parent)
        self.home_frame.pack()
        self.active_frame = self.home_frame

        vcmd_validate_float = (root.register(is_num), '%P')
        vcmd_validate_int = (root.register(lambda new_value: is_num(new_value, type_int=True)), '%P')

        header_frame = Frame(self.home_frame, bg=HEADER_COLOUR)
        header_frame.grid(row=0, column=0, sticky=E + W, columnspan=2)

        title_label = Label(header_frame, text="Inventory Tracking System", bg=HEADER_COLOUR, anchor="w")
        title_label.grid(row=0, column=0, sticky=W, ipady=8, padx=5, ipadx=40)

        search_label = Label(header_frame, text="Search by Name", bg=HEADER_COLOUR)
        search_label.grid(row=0, column=1, sticky=E)
        self.search_val = StringVar()
        self.search_val.trace_add("write", lambda a, b, c: self.search())
        self.search_entry = Entry(header_frame, textvariable=self.search_val)
        self.search_entry.grid(row=0, column=2, sticky=W)
        clear_search_btn = Button(header_frame, text="Clear", command=lambda: self.search_val.set(""))
        clear_search_btn.grid(row=0, column=3, sticky=E, padx=5)

        self.hidden_items = []

        # Sidebar Frame (buttons)
        self.sidebar_frame = Frame(self.home_frame)
        self.sidebar_frame.grid(row=2, column=0, sticky="nsew")

        self.sell_item_btn = Button(self.sidebar_frame, text="Sell Item",
                                    command=lambda: self.activate_frame(self.sell_item_frame))
        self.sell_item_btn.grid(row=0, column=0, sticky=E + W, padx=10, pady=10)
        self.restock_item_btn = Button(self.sidebar_frame, text="Restock Item",
                                       command=lambda: self.activate_frame(self.restock_item_frame))
        self.restock_item_btn.grid(row=1, column=0, sticky=E + W, padx=10)

        add_item_btn = Button(self.sidebar_frame, text="Add New Item",
                              command=lambda: self.activate_frame(self.add_item_frame))
        add_item_btn.grid(row=2, column=0, sticky=N + E + W, padx=10, pady=10)
        self.delete_item_btn = Button(self.sidebar_frame, text="Delete Item", command=self.delete_item)
        self.delete_item_btn.grid(row=3, column=0, sticky=N + E + W, padx=10, pady=10)
        self.delete_all_btn = Button(self.sidebar_frame, text="Delete All", command=self.delete_all)
        self.delete_all_btn.grid(row=4, column=0, sticky=N + E + W, padx=10)

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
        self.item_tree.column("1", width=200, anchor='w')
        self.item_tree.column("2", width=80, anchor='e', stretch=TRUE)
        self.item_tree.column("3", width=80, anchor='e')
        self.item_tree.heading("1", text="Name", anchor='w')
        self.item_tree.heading("2", text="Price", anchor='e')
        self.item_tree.heading("3", text="Quantity", anchor='e')

        # where the 2d gridded items will be stored
        self.items_list_grid = []
        self.default_items = [Product("Gorgeous T-Shirts", "", 55, 3), Product("Amazing Shorts", "", 39, 19),
                              Product("Cute Crop Top", "", 40, 3), Product("Snazzy Jacket", "", 169, 2),
                              Product("Gorgeous T-Shirt", "", 55, 3), Product("Amazing Shorts", "", 39, 19),
                              Product("Cute Crop Top", "", 40, 3), Product("Snazzy Jacket", "", 169, 2),
                              Product("Gorgeous T-Shirt", "", 55, 3), Product("Amazing Shorts", "", 39, 19),
                              Product("Cute Crop Top", "", 40, 3), Product("Snazzy Jacket", "", 169, 2),
                              Product("Gorgeous T-Shirt", "", 55, 3), Product("Amazing Shorts", "", 39, 19),
                              Product("Cute Crop Top", "", 40, 3), Product("Snazzy Jacket", "", 169, 2),
                              Product("Gorgeous T-Shirt", "", 55, 3), Product("Amazing Shorts", "", 39, 19),
                              Product("Cute Crop Top", "", 40, 3), Product("Snazzy Jacket", "", 169, 2),
                              ]

        # add all items to tree
        for i in range(len(self.default_items)):
            self.item_tree.insert("", 'end', values=(
                self.default_items[i].name, "${:,.2f}".format(self.default_items[i].price),
                self.default_items[i].quantity))

        # selects first row/item by default
        self.update_selected_item()

        sell_restock_frame = Frame(self.home_frame)
        sell_restock_frame.grid(row=3, column=0, columnspan=2, sticky="nsew")
        sell_restock_label = Label(sell_restock_frame, text="Enter a number to sell/restock the selected item", anchor=CENTER)
        sell_restock_label.grid(row=0, column=0, columnspan=3, sticky="ew")

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

        # SELL ITEM FRAME
        self.sell_item_frame = Frame(parent)
        sell_item_title = Label(self.sell_item_frame, text="Sell Product", bg=HEADER_COLOUR)
        sell_item_title.grid(row=0, column=0, sticky=E + W, ipady=8)
        tkinter.ttk.Separator(self.sell_item_frame, orient=HORIZONTAL).grid(row=1, column=0, columnspan=2, sticky='ew')
        self.sell_item_subtitle = Label(self.sell_item_frame)
        self.sell_item_subtitle.grid(row=2, column=0, sticky=E + W, ipady=4)
        self.sell_item_quantity = Label(self.sell_item_frame)
        self.sell_item_quantity.grid(row=3, column=0, sticky=E + W, ipady=4)

        sell_prompt_label = Label(self.sell_item_frame, text="How many items would you like to sell?", anchor=S)
        sell_prompt_label.grid(row=4, column=0, sticky=E + W, ipady=10, pady=5)
        self.sell_quantity = StringVar()

        sell_quantity_entry = Entry(self.sell_item_frame, textvariable=self.sell_quantity, validate="all",
                                    validatecommand=vcmd_validate_int)
        sell_quantity_entry.grid(row=5, column=0, sticky=E + W, ipadx=20)

        sell_button_frame = Frame(self.sell_item_frame)
        sell_button_frame.grid(row=6, column=0)
        sell_cancel_btn = Button(sell_button_frame, text="Back", command=lambda: self.activate_frame(self.home_frame))
        sell_cancel_btn.grid(row=0, column=0, padx=10, pady=10, ipadx=10)
        sell_confirm_btn = Button(sell_button_frame, text="Confirm", command=self.sell_item)
        sell_confirm_btn.grid(row=0, column=1, padx=10)

        # Almost identical to sell item frame, fix?
        self.restock_item_frame = Frame(parent)
        restock_item_title = Label(self.restock_item_frame, text="Restock Product", bg=HEADER_COLOUR)
        restock_item_title.grid(row=0, column=0, sticky=E + W, ipady=8)
        tkinter.ttk.Separator(self.restock_item_frame, orient=HORIZONTAL).grid(row=1, column=0, columnspan=2,
                                                                               sticky='ew')
        self.restock_item_subtitle = Label(self.restock_item_frame)
        self.restock_item_subtitle.grid(row=2, column=0, sticky=E + W, ipady=4)
        self.restock_item_quantity = Label(self.restock_item_frame)
        self.restock_item_quantity.grid(row=3, column=0, sticky=E + W, ipady=4)

        restock_prompt_label = Label(self.restock_item_frame, text="How many items would you like to restock?",
                                     anchor=S)
        restock_prompt_label.grid(row=4, column=0, sticky=E + W, ipady=10, pady=5)
        self.restock_quantity = StringVar()

        restock_quantity_entry = Entry(self.restock_item_frame, textvariable=self.restock_quantity, validate="all",
                                       validatecommand=vcmd_validate_int)
        restock_quantity_entry.grid(row=5, column=0, sticky=E + W, ipadx=20)

        restock_button_frame = Frame(self.restock_item_frame)
        restock_button_frame.grid(row=6, column=0)
        restock_cancel_btn = Button(restock_button_frame, text="Back",
                                    command=lambda: self.activate_frame(self.home_frame))
        restock_cancel_btn.grid(row=0, column=0, padx=10, pady=10, ipadx=10)
        restock_confirm_btn = Button(restock_button_frame, text="Confirm", command=self.restock_item)
        restock_confirm_btn.grid(row=0, column=1, padx=10)

    def get_selected_item_info(self):
        info = self.item_tree.item(self.item_tree.selection()[0], 'values')
        return [info[0], info[1], int(info[2])]

    def search(self):
        # check if any shown items should be hidden
        for item in self.item_tree.get_children():
            if self.search_val.get().strip().lower() not in self.item_tree.item(item, "values")[0].strip().lower():
                self.hidden_items.append(item)
                # deselect hidden items

                if item == self.selected_item_iid:  # updates multiple times when hiding objects,
                    # doesn't handle newly added rows yet
                    self.item_tree.selection_remove(item)
                    self.item_tree.detach(item)
                    self.update_selected_item()
                    print("updated", self.selected_item_iid)
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

    def activate_frame(self, frame):  # some yucky repetitiveness here
        self.active_frame.pack_forget()
        self.active_frame = frame
        frame.pack()

        self.clear_all_inputs()
        self.update_selected_item()

        if frame == self.sell_item_frame:
            self.sell_item_subtitle.configure(
                text="Selling: " + str(self.item_tree.item(self.selected_item_iid, "values")[0]))
            self.sell_item_quantity.configure(
                text="Quantity Remaining: " + str(self.item_tree.item(self.selected_item_iid, "values")[2]))

        if frame == self.restock_item_frame:
            self.restock_item_subtitle.configure(
                text="Restocking: " + str(self.item_tree.item(self.selected_item_iid, "values")[0]))
            self.restock_item_quantity.configure(
                text="Quantity Remaining: " + str(self.item_tree.item(self.selected_item_iid, "values")[2]))

    def update_selected_item(self):
        if len(self.item_tree.selection()) == 0:
            try:
                new_selection = self.item_tree.get_children()[0]
                self.item_tree.focus(new_selection)
                self.item_tree.selection_set(new_selection)

                # restructure so this block only runs once
                self.selected_item_iid = self.item_tree.get_children()[0]
                self.sell_item_btn.configure(state=NORMAL)
                self.restock_item_btn.configure(state=NORMAL)
                self.delete_item_btn.configure(state=NORMAL)
                self.delete_all_btn.configure(state=NORMAL)

            except IndexError:
                self.selected_item_iid = None
                self.sell_item_btn.configure(state=DISABLED)
                self.restock_item_btn.configure(state=DISABLED)
                self.delete_item_btn.configure(state=DISABLED)
                self.delete_all_btn.configure(state=DISABLED)

        else:
            self.selected_item_iid = self.item_tree.selection()[0]
            self.sell_item_btn.configure(state=NORMAL)
            self.restock_item_btn.configure(state=NORMAL)
            self.delete_item_btn.configure(state=NORMAL)
            self.delete_all_btn.configure(state=NORMAL)

    def clear_all_inputs(self):
        self.name_entry.focus()
        self.name_var.set("")
        self.description_entry.delete('1.0', END)
        self.price_var.set("")
        self.quantity_var.set("")
        self.sell_quantity.set("")
        self.restock_quantity.set("")

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
                _continue = tkinter.messagebox.askyesno("Duplicate Entry",
                                                        "New item has same name as existing item. "
                                                        "Existing item will NOT be overwritten. Proceed?",
                                                        icon='warning')
                if not _continue:
                    return

            self.item_tree.insert("", 'end', values=(
                self.name_var.get(), "${:,.2f}".format(float(self.price_var.get())),
                int(self.quantity_var.get())))

            self.update_selected_item()
            self.activate_frame(self.home_frame)

    def sell_item(self):
        try:
            current_info = self.get_selected_item_info()
            if int(self.sell_quantity.get()) > current_info[2]:
                tkinter.messagebox.showerror("Input Error",
                                             "Number sold cannot exceed stocked quantity")
            else:
                current_info[2] -= int(self.sell_quantity.get())
                self.item_tree.set(self.item_tree.selection()[0], column=3,
                                   value=current_info[2])

                tkinter.messagebox.showinfo("Success",
                                            "Successfully sold {} units of '{}'".format(self.sell_quantity.get(),
                                                                                        current_info[0]))
                self.activate_frame(self.home_frame)
        # handles user submitting the empty string
        except ValueError:
            tkinter.messagebox.showerror("Input Error",
                                         "Please enter a number")

    # very similar to sell_item()
    def restock_item(self):
        try:
            current_info = self.get_selected_item_info()
            current_info[2] += int(self.restock_quantity.get())
            self.item_tree.set(self.item_tree.selection()[0], column=3,
                               value=current_info[2])

            tkinter.messagebox.showinfo("Success",
                                        "Successfully restocked {} units of '{}'".format(self.restock_quantity.get(),
                                                                                         current_info[0]))
            self.activate_frame(self.home_frame)
        except ValueError:
            tkinter.messagebox.showerror("Input Error",
                                         "Please enter a number")


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
