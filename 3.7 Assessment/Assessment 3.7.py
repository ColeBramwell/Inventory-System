from tkinter import *
from tkinter import ttk
import tkinter.messagebox

HEADER_COLOUR = "light grey"


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

        header_frame = Frame(self.home_frame, bg=HEADER_COLOUR)
        header_frame.grid(row=0, column=0, sticky=E + W)

        title_label = Label(header_frame, text="Inventory Tracking System", bg=HEADER_COLOUR)
        title_label.grid(row=0, column=0, sticky=W, ipady=8)
        add_item_btn = Button(header_frame, text="Add Item", command=lambda: self.activate_frame(self.add_item_frame))
        add_item_btn.grid(row=0, column=1, sticky=E + W)
        sell_item_btn = Button(header_frame, text="Sell Item",
                               command=lambda: self.activate_frame(self.sell_item_frame))
        sell_item_btn.grid(row=0, column=2, sticky=E + W, padx=10)
        restock_item_btn = Button(header_frame, text="Restock Item")
        restock_item_btn.grid(row=0, column=3, sticky=E + W)

        test_btn = Button(header_frame, text="Scrollbar Pos", command=self.get_scrollbar_pos)
        test_btn.grid(row=0, column=4, sticky=E + W)

        subheader_frame = Frame(self.home_frame)
        subheader_frame.grid(row=1, column=0, sticky=E + W)
        subheader_frame.grid_columnconfigure(0, weight=6)
        subheader_frame.grid_columnconfigure(1, weight=1)
        subheader_frame.grid_columnconfigure(2, weight=1)

        # testing stretching labels and then anchoring text left to enable whole widget to be clickable
        name_header_label = Label(subheader_frame, text="Name", anchor='w')
        name_header_label.bind("<Button>", self.mouse_click)
        name_header_label.grid(row=0, column=0, sticky="nesw")
        price_header_label = Label(subheader_frame, text="Price", anchor='w')
        price_header_label.grid(row=0, column=1, sticky="nesw", ipadx=20)
        quantity_header_label = Label(subheader_frame, text="Quantity", anchor='w')
        quantity_header_label.grid(row=0, column=2, sticky="nesw")
        tkinter.ttk.Separator(subheader_frame, orient=HORIZONTAL).grid(column=0, row=1, columnspan=5, sticky='ew')

        self.canvas_container = Frame(self.home_frame)
        self.scrollable_canvas = Canvas(self.canvas_container)
        self.scrollable_canvas.pack(side=LEFT, fill="both", expand="yes")
        self.scrollbar = ttk.Scrollbar(self.canvas_container, orient="vertical", command=self.scrollable_canvas.yview)
        self.scrollbar.pack(side=RIGHT, fill="y")

        self.scrollable_canvas.configure(yscrollcommand=self.scrollbar.set)
        self.scrollable_canvas.bind('<Configure>', lambda e: self.scrollable_canvas.configure(
            scrollregion=self.scrollable_canvas.bbox('all')))
        self.scrollable_canvas.bind_all("<MouseWheel>", self._on_mousewheel)

        self.items_frame = Frame(self.scrollable_canvas)
        self.scrollable_canvas.create_window((0, 0), window=self.items_frame, anchor="s")

        # shits the bed for some reason when isn't in row 2
        self.canvas_container.grid(row=2, column=0, ipadx=20, ipady=20)

        self.default_items = [Product("Gorgeous T-Shirt", "", 55, 3), Product("Amazing Shorts", "", 39, 19),
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

        # which row to highlight by default
        self.active_row = 0

        # doesn't work
        self.scrollable_canvas.yview_moveto(0.0)

        self.update_items()

        # ADD ITEMS FRAME
        self.add_item_frame = Frame(parent)
        add_item_title = Label(self.add_item_frame, text="Add New Product", bg=HEADER_COLOUR)
        add_item_title.grid(row=0, column=0, sticky=E + W, ipady=8)
        tkinter.ttk.Separator(self.add_item_frame, orient=HORIZONTAL).grid(column=0, row=1, columnspan=2, sticky='ew')

        self.name_var = StringVar()
        self.price_var = StringVar()
        self.quantity_var = StringVar()

        # setting up input validation for numerical-only (float) entry widgets
        vcmd_add_item = (root.register(is_num), '%P')

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
                            validatecommand=vcmd_add_item)
        price_entry.grid(row=7, column=0)
        enter_quantity_label = Label(self.add_item_frame, text="Quantity")
        enter_quantity_label.grid(row=8, column=0)
        quantity_entry = Entry(self.add_item_frame, textvariable=self.quantity_var, validate="all",
                               validatecommand=vcmd_add_item)
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
        self.sell_item_subtitle = Label(self.sell_item_frame,
                                        text="Selling: " + self.default_items[self.active_row].name)
        self.sell_item_subtitle.grid(row=2, column=0, sticky=E + W, ipady=4)
        self.sell_item_quantity = Label(self.sell_item_frame,
                                        text="Quantity Remaining: " + str(self.default_items[self.active_row].quantity))
        self.sell_item_quantity.grid(row=3, column=0, sticky=E + W, ipady=4)

        sell_prompt_label = Label(self.sell_item_frame, text="How many items would you like to sell?", anchor=S)
        sell_prompt_label.grid(row=4, column=0, sticky=E + W, ipady=10, pady=5)
        self.sell_quantity = StringVar()

        # setting up input validation for numerical-only (int) entry widget
        vcmd_sell_item = (root.register(lambda new_value: is_num(new_value, type_int=True)), '%P')

        sell_quantity_entry = Entry(self.sell_item_frame, textvariable=self.sell_quantity, validate="all",
                                    validatecommand=vcmd_sell_item)
        sell_quantity_entry.grid(row=5, column=0, sticky=E + W)

        sell_button_frame = Frame(self.sell_item_frame)
        sell_button_frame.grid(row=6, column=0)
        sell_cancel_btn = Button(sell_button_frame, text="Back", command=lambda: self.activate_frame(self.home_frame))
        sell_cancel_btn.grid(row=0, column=0, padx=10, pady=10, ipadx=10)
        sell_confirm_btn = Button(sell_button_frame, text="Confirm", command=self.sell_item)
        sell_confirm_btn.grid(row=0, column=1, padx=10)

    def get_scrollbar_pos(self):
        print(self.scrollable_canvas.yview())
        self.scrollable_canvas.yview_moveto(0.0)

    def _on_mousewheel(self, event):
        self.scrollable_canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")

    def mouse_click(self, row):
        self.active_row = row
        self.update_items()

    def activate_frame(self, frame):
        self.active_frame.pack_forget()
        self.active_frame = frame
        frame.pack()

        self.clear_all_inputs()

        if frame == self.sell_item_frame:
            self.sell_item_subtitle.configure(text="Selling: " + self.default_items[self.active_row].name)
            self.sell_item_quantity.configure(
                text="Quantity Remaining: " + str(self.default_items[self.active_row].quantity))

    def clear_all_inputs(self):
        self.name_entry.focus()
        self.name_var.set("")
        self.description_entry.delete('1.0', END)
        self.price_var.set("")
        self.quantity_var.set("")
        self.sell_quantity.set("")

    def update_items(self):
        # update the scroll region to account for possible changes in the item window height
        self.scrollable_canvas.bind('<Configure>', lambda e: self.scrollable_canvas.configure(
            scrollregion=self.scrollable_canvas.bbox('all')))

        # destroy and recreate the item frame to wipe all objects in it, prevents multiple overlapping grids
        # from occuring,
        # NOT a permanent solution
        self.items_frame.destroy()
        self.items_frame = Frame(self.scrollable_canvas)
        self.scrollable_canvas.create_window((0, 0), window=self.items_frame, anchor="s")

        # BAD solution, ideally only update what has changed, saves computing power for larger lists
        for i in range(len(self.default_items)):
            if i == self.active_row:
                colour = "light blue"
            else:
                colour = "#F0F0F0"
            name_temp_label = Label(self.items_frame, text=self.default_items[i].name, bg=colour, anchor=W)
            name_temp_label.bind("<Button>", lambda event, row=i: self.mouse_click(row))
            name_temp_label.grid(row=2 * i + 2, column=0, sticky="nsew")
            price_temp_label = Label(self.items_frame, text="$" + str(self.default_items[i].price), bg=colour, anchor=W)
            price_temp_label.bind("<Button>", lambda event, row=i: self.mouse_click(row))
            price_temp_label.grid(row=2 * i + 2, column=1, sticky="nsew", ipadx=20)
            quantity_temp_label = Label(self.items_frame, text=self.default_items[i].quantity, bg=colour, anchor=W)
            quantity_temp_label.bind("<Button>", lambda event, row=i: self.mouse_click(row))
            quantity_temp_label.grid(row=2 * i + 2, column=2, sticky="nsew")
            tkinter.ttk.Separator(self.items_frame, orient=HORIZONTAL).grid(column=0, row=2 * i + 3, columnspan=3,
                                                                            sticky='ew')

        # has no effect for some reason
        self.items_frame.grid_columnconfigure(0, weight=6)
        self.items_frame.grid_columnconfigure(1, weight=1)
        self.items_frame.grid_columnconfigure(2, weight=1)


    def add_item(self):
        # displays error if any of the mandatory fields are empty
        if self.name_var.get() == "" or self.price_var.get() == "" or self.quantity_var.get() == "":
            tkinter.messagebox.showerror("Input Error",
                                         "Please ensure that all mandatory fields are completed")
        else:
            self.default_items.append(
                Product(self.name_var.get(), self.description_entry.get("1.0", "end-1c"), self.price_var.get(),
                        self.quantity_var.get()))
            self.activate_frame(self.home_frame)
            self.update_items()

    def sell_item(self):
        if int(self.sell_quantity.get()) > self.default_items[self.active_row].quantity:
            tkinter.messagebox.showerror("Input Error",
                                         "Number sold cannot exceed stocked quantity")
        else:
            self.default_items[self.active_row].quantity -= int(self.sell_quantity.get())
            self.update_items()
            tkinter.messagebox.showinfo("Success",
                                        "Successfully sold {} units of '{}'".format(self.sell_quantity.get(),
                                                                                    self.default_items[
                                                                                        self.active_row].name))
            self.activate_frame(self.home_frame)



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
