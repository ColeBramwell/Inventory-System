from tkinter import *
from tkinter import ttk
import tkinter.messagebox

HEADER_COLOUR = "light grey"


def validate(new_value):
    if new_value == "":
        return True
    try:
        float(new_value)
        return True
    except ValueError:
        return False


class InventorySystemGUI:
    def __init__(self, parent):
        self.home_frame = Frame(parent)
        self.home_frame.pack()
        self.active_frame = self.home_frame

        header_frame = Frame(self.home_frame)
        header_frame.grid(row=0, column=0, sticky=E + W, pady=5)
        title_label = Label(header_frame, text="Inventory Tracking System")
        title_label.grid(row=0, column=0, sticky=W)
        add_item_btn = Button(header_frame, text="Add Item", command=lambda: self.activate_frame(self.add_item_frame))
        add_item_btn.grid(row=0, column=1, sticky=E + W)
        sell_item_btn = Button(header_frame, text="Sell Item")
        sell_item_btn.grid(row=0, column=2, sticky=E + W, padx=10)
        restock_item_btn = Button(header_frame, text="Restock Item")
        restock_item_btn.grid(row=0, column=3, sticky=E + W)

        tkinter.ttk.Separator(self.home_frame, orient=HORIZONTAL).grid(column=0, row=1, columnspan=5, sticky='ew')



        """
        self.items_frame.grid(row=2, column=0, sticky=E + W)
        self.items_frame.grid_columnconfigure(0, weight=1)

        name_header_label = Label(self.items_frame, text="Name")
        name_header_label.grid(row=0, column=0, sticky=W)
        price_header_label = Label(self.items_frame, text="Price")
        price_header_label.grid(row=0, column=1, sticky=W, ipadx=20)
        quantity_header_label = Label(self.items_frame, text="Quantity")
        quantity_header_label.grid(row=0, column=2, sticky=W)
        tkinter.ttk.Separator(self.items_frame, orient=HORIZONTAL).grid(column=0, row=1, columnspan=5, sticky='ew')
        """


        self.wrapper1 = Frame(self.home_frame, height=30, width=10)

        self.mycanvas = Canvas(self.wrapper1)
        self.mycanvas.pack(side=LEFT, fill="both", expand="yes")

        self.yscrollbar = ttk.Scrollbar(self.wrapper1, orient="vertical", command=self.mycanvas.yview)
        self.yscrollbar.pack(side=RIGHT, fill="y")

        self.mycanvas.configure(yscrollcommand=self.yscrollbar.set)

        self.mycanvas.bind('<Configure>', lambda e: self.mycanvas.configure(scrollregion=self.mycanvas.bbox('all')))
        self.mycanvas.bind_all("<MouseWheel>", self._on_mousewheel)

        self.items_frame = Frame(self.mycanvas)
        self.mycanvas.create_window((0, 0), window=self.items_frame, anchor="nw")

        #breaks for some reason when row isn't 2
        self.wrapper1.grid(row=2, column=0, ipadx=20, ipady=20)
        
        

        self.default_items = [Product("Gorgeous T-Shirt", "", 55, 3), Product("Amazing Shorts", "", 39, 19),
                              Product("Cute Crop Top", "", 40, 3), Product("Snazzy Jacket", "", 169, 2),
                              Product("Cute Crop Top", "", 40, 3), Product("Snazzy Jacket", "", 169, 2),
                              Product("Cute Crop Top", "", 40, 3), Product("Snazzy Jacket", "", 169, 2),
                              Product("Cute Crop Top", "", 40, 3), Product("Snazzy Jacket", "", 169, 2),
                              Product("Cute Crop Top", "", 40, 3), Product("Cute Crop Top", "", 40, 3),
                              Product("Cute Crop Top", "", 40, 3), Product("Snazzy Jacket", "", 169, 2),
                              Product("Cute Crop Top", "", 40, 3), Product("Snazzy Jacket", "", 169, 2),
                              Product("Cute Crop Top", "", 40, 3), Product("Cute Crop Top", "", 40, 3),
                              ]

        self.update_items()



        # ADD ITEMS FRAME
        self.add_item_frame = Frame(parent)
        add_item_title = Label(self.add_item_frame, text="Add New Product", bg=HEADER_COLOUR)
        add_item_title.grid(row=0, column=0, sticky=E + W, ipady=8)
        tkinter.ttk.Separator(self.add_item_frame, orient=HORIZONTAL).grid(column=0, row=1, columnspan=2, sticky='ew')

        self.name_var = StringVar()
        self.price_var = StringVar()
        self.quantity_var = StringVar()

        # setting up input validation for numerical-only entry widgets
        vcmd = (root.register(validate), '%P')

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
        price_entry = Entry(self.add_item_frame, textvariable=self.price_var, validate="all", validatecommand=vcmd)
        price_entry.grid(row=7, column=0)
        enter_quantity_label = Label(self.add_item_frame, text="Quantity")
        enter_quantity_label.grid(row=8, column=0)
        quantity_entry = Entry(self.add_item_frame, textvariable=self.quantity_var, validate="all",
                               validatecommand=vcmd)
        quantity_entry.grid(row=9, column=0)

        button_frame = Frame(self.add_item_frame)
        button_frame.grid(row=10, column=0)
        cancel_addition_btn = Button(button_frame, text="Back",
                                     command=lambda: self.activate_frame(self.home_frame))
        cancel_addition_btn.grid(row=0, column=0, ipadx=20, padx=5)
        clear_btn = Button(button_frame, text="Clear", command=self.clear_new_item_input)
        clear_btn.grid(row=0, column=1, pady=8, padx=5, ipadx=20)
        submit_btn = Button(button_frame, text="Complete Item", command=self.add_item)
        submit_btn.grid(row=0, column=2, pady=8, padx=5)

    def _on_mousewheel(self, event):
        self.mycanvas.yview_scroll(int(-1 * (event.delta / 120)), "units")

    def activate_frame(self, frame):
        self.active_frame.pack_forget()
        self.active_frame = frame
        frame.pack()

        # wipes old input from last entered item when entering the 'enter new item' screen
        if frame == self.add_item_frame:
            self.clear_new_item_input()

    def clear_new_item_input(self):
        self.name_entry.focus()
        self.name_var.set("")
        self.description_entry.delete('1.0', END)
        self.price_var.set("")
        self.quantity_var.set("")

    def update_items(self):
        # yucky solution, find only the essential lines that need to run multiple times
        self.wrapper1 = Frame(self.home_frame, height=30, width=10)

        self.mycanvas = Canvas(self.wrapper1)
        self.mycanvas.pack(side=LEFT, fill="both", expand="yes")

        self.yscrollbar = ttk.Scrollbar(self.wrapper1, orient="vertical", command=self.mycanvas.yview)
        self.yscrollbar.pack(side=RIGHT, fill="y")

        self.mycanvas.configure(yscrollcommand=self.yscrollbar.set)

        self.mycanvas.bind('<Configure>', lambda e: self.mycanvas.configure(scrollregion=self.mycanvas.bbox('all')))

        self.items_frame = Frame(self.mycanvas)
        self.mycanvas.create_window((0, 0), window=self.items_frame, anchor="nw")

        self.wrapper1.grid(row=2, column=0, ipadx=20, ipady=20)

        for i in range(len(self.default_items)):
            name_temp_label = Label(self.items_frame, text=self.default_items[i].name)
            name_temp_label.grid(row=2 * i + 2, column=0, sticky=W)
            price_temp_label = Label(self.items_frame, text="$" + str(self.default_items[i].price))
            price_temp_label.grid(row=2 * i + 2, column=1, sticky=W, ipadx=20)
            quantity_temp_label = Label(self.items_frame, text=self.default_items[i].quantity)
            quantity_temp_label.grid(row=2 * i + 2, column=2, sticky=W)
            tkinter.ttk.Separator(self.items_frame, orient=HORIZONTAL).grid(column=0, row=2 * i + 3, columnspan=3,
                                                                            sticky='ew')

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
