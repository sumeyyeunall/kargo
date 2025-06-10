import tkinter as tk
from tkinter import ttk, messagebox
from decimal import Decimal
import uuid
from typing import Dict, Optional
from datetime import datetime

from src.models.product import Product
from src.models.customer import Customer
from src.models.order_factory import OrderFactory
from src.inventory.inventory_manager import InventoryManager
from src.data.storage import JsonStorage


class LoginScreen:
    def __init__(self, root, storage: JsonStorage, on_customer_login, on_admin_login):
        self.root = root
        self.storage = storage
        self.on_customer_login = on_customer_login
        self.on_admin_login = on_admin_login

        self.frame = ttk.Frame(root)
        self.frame.pack(expand=True, fill='both', padx=20, pady=20)

        # Title
        title = ttk.Label(self.frame, text="E-commerce System Login", font=('Helvetica', 16))
        title.pack(pady=20)

        # Login Frame
        login_frame = ttk.LabelFrame(self.frame, text="Login")
        login_frame.pack(fill='x', padx=10, pady=5)

        ttk.Label(login_frame, text="Email:").pack(padx=5, pady=2)
        self.email = tk.StringVar()
        ttk.Entry(login_frame, textvariable=self.email).pack(padx=5, pady=2, fill='x')

        ttk.Label(login_frame, text="Password:").pack(padx=5, pady=2)
        self.password = tk.StringVar()
        ttk.Entry(login_frame, textvariable=self.password, show="*").pack(padx=5, pady=2, fill='x')

        # Buttons
        btn_frame = ttk.Frame(self.frame)
        btn_frame.pack(pady=20)

        ttk.Button(btn_frame, text="Customer Login",
                   command=self.customer_login).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="Admin Login",
                   command=self.admin_login).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="Register New Customer",
                   command=self.show_registration).pack(side=tk.LEFT, padx=5)

    def customer_login(self):
        """Handle customer login."""
        customer = self.storage.authenticate_customer(self.email.get(), self.password.get())
        if customer:
            # Ensure customer data has an 'id' field
            if 'id' not in customer:
                customer['id'] = str(uuid.uuid4())  # Generate a new ID if missing
            self.frame.destroy()
            self.on_customer_login(customer)
        else:
            messagebox.showerror("Error", "Invalid email or password")

    def admin_login(self):
        """Handle admin login."""
        if self.storage.authenticate_admin(self.email.get(), self.password.get()):
            self.frame.destroy()
            self.on_admin_login()
        else:
            messagebox.showerror("Error", "Invalid admin credentials")

    def show_registration(self):
        """Show the registration screen."""
        self.frame.destroy()
        RegistrationScreen(self.root, self.storage, self.show_login)

    def show_login(self):
        """Show the login screen again."""
        self.frame.destroy()
        LoginScreen(self.root, self.storage, self.on_customer_login, self.on_admin_login)


class RegistrationScreen:
    def __init__(self, root, storage: JsonStorage, on_back):
        self.root = root
        self.storage = storage
        self.on_back = on_back

        self.frame = ttk.Frame(root)
        self.frame.pack(expand=True, fill='both', padx=20, pady=20)

        # Title
        title = ttk.Label(self.frame, text="Customer Registration", font=('Helvetica', 16))
        title.pack(pady=20)

        # Registration Form
        form_frame = ttk.LabelFrame(self.frame, text="Registration Details")
        form_frame.pack(fill='x', padx=10, pady=5)

        # Form fields
        fields = [
            ("Name:", "name"),
            ("Email:", "email"),
            ("Password:", "password"),
            ("Address:", "address"),
            ("Phone:", "phone")
        ]

        self.entries = {}
        for label, field in fields:
            ttk.Label(form_frame, text=label).pack(padx=5, pady=2)
            var = tk.StringVar()
            entry = ttk.Entry(form_frame, textvariable=var)
            if field == "password":
                entry.configure(show="*")
            entry.pack(padx=5, pady=2, fill='x')
            self.entries[field] = var

        # Buttons
        btn_frame = ttk.Frame(self.frame)
        btn_frame.pack(pady=20)

        ttk.Button(btn_frame, text="Register",
                   command=self.register).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="Back to Login",
                   command=self.back_to_login).pack(side=tk.LEFT, padx=5)

    def register(self):
        """Handle customer registration."""
        try:
            # Generate a UUID for the new customer
            customer_id = str(uuid.uuid4())

            success = self.storage.register_customer(
                id=customer_id,  # Pass the generated ID
                name=self.entries["name"].get(),
                email=self.entries["email"].get(),
                password=self.entries["password"].get(),
                address=self.entries["address"].get(),
                phone=self.entries["phone"].get()
            )

            if success:
                messagebox.showinfo("Success", "Registration successful! Please login.")
                self.back_to_login()
            else:
                messagebox.showerror("Error", "Email already registered")
        except Exception as e:
            messagebox.showerror("Error", f"Registration failed: {str(e)}")

    def back_to_login(self):
        """Go back to login screen."""
        self.frame.destroy()
        self.on_back()


class CustomerApp:
    def __init__(self, root, storage: JsonStorage, customer_data: Dict):
        self.root = root
        self.storage = storage
        self.customer_data = customer_data
        self.inventory_manager = InventoryManager()

        self.frame = ttk.Frame(root)
        self.frame.pack(expand=True, fill='both', padx=10, pady=5)

        # Welcome message
        welcome = ttk.Label(self.frame,
                            text=f"Welcome, {customer_data['name']}!",
                            font=('Helvetica', 14))
        welcome.pack(pady=10)

        # Create notebook for tabs
        self.notebook = ttk.Notebook(self.frame)
        self.notebook.pack(expand=True, fill='both')

        # Create tabs
        self.create_products_view()
        self.create_orders_tab()

    def create_products_view(self):
        """Create the products view tab."""
        products_frame = ttk.Frame(self.notebook)
        self.notebook.add(products_frame, text='Available Products')

        # Products list
        self.products_list = ttk.Treeview(products_frame,
                                          columns=('ID', 'Name', 'Price', 'Stock'),
                                          show='headings')

        self.products_list.heading('ID', text='ID')
        self.products_list.heading('Name', text='Name')
        self.products_list.heading('Price', text='Price')
        self.products_list.heading('Stock', text='Stock')

        self.products_list.pack(fill='both', expand=True, padx=5, pady=5)

        # Order form
        order_frame = ttk.LabelFrame(products_frame, text="Place Order")
        order_frame.pack(fill='x', padx=5, pady=5)

        ttk.Label(order_frame, text="Quantity:").pack(side=tk.LEFT, padx=5)
        self.order_quantity = tk.StringVar(value="1")
        ttk.Entry(order_frame, textvariable=self.order_quantity, width=10).pack(side=tk.LEFT, padx=5)

        ttk.Label(order_frame, text="Shipping:").pack(side=tk.LEFT, padx=5)
        self.shipping_type = tk.StringVar(value="fast")
        ttk.Combobox(order_frame, textvariable=self.shipping_type,
                     values=["fast", "economic", "drone"], width=15).pack(side=tk.LEFT, padx=5)

        ttk.Button(order_frame, text="Place Order",
                   command=self.place_order).pack(side=tk.LEFT, padx=5)

        self.update_products_list()

    def create_orders_tab(self):
        """Create the orders history tab."""
        orders_frame = ttk.Frame(self.notebook)
        self.notebook.add(orders_frame, text='My Orders')

        # Orders list
        self.orders_list = ttk.Treeview(orders_frame,
                                        columns=('ID', 'Date', 'Total', 'Status'),
                                        show='headings')

        self.orders_list.heading('ID', text='Order ID')
        self.orders_list.heading('Date', text='Date')
        self.orders_list.heading('Total', text='Total')
        self.orders_list.heading('Status', text='Status')

        self.orders_list.pack(fill='both', expand=True, padx=5, pady=5)

        self.update_orders_list()

    def update_products_list(self):
        """Update the products list."""
        for item in self.products_list.get_children():
            self.products_list.delete(item)

        for product in self.inventory_manager.get_all_products().values():
            self.products_list.insert('', 'end', values=(
                product.id,
                product.name,
                f"${product.price}",
                product.stock_quantity
            ))

    def update_orders_list(self):
        """Update the orders list."""
        for item in self.orders_list.get_children():
            self.orders_list.delete(item)

        orders = self.storage.load_data('orders', default=[])

        # Safely get customer ID with a default value
        customer_id = self.customer_data.get('id')
        if not customer_id:
            messagebox.showerror("Error", "Customer ID not found")
            return

        customer_orders = [order for order in orders
                           if order.get('customer_id') == customer_id]

        for order in customer_orders:
            self.orders_list.insert('', 'end', values=(
                order.get('id', 'N/A'),
                order.get('date', 'N/A'),
                f"${order.get('total_price', '0')}",
                order.get('status', 'unknown')
            ))

    def place_order(self):
        """Place a new order."""
        selection = self.products_list.selection()
        if not selection:
            messagebox.showwarning("Warning", "Please select a product")
            return

        try:
            product_id = self.products_list.item(selection[0])['values'][0]
            product = self.inventory_manager.get_product(product_id)

            if not product:
                messagebox.showerror("Error", "Product not found")
                return

            quantity = int(self.order_quantity.get())
            customer = Customer(
                id=self.customer_data['id'],
                name=self.customer_data['name'],
                email=self.customer_data['email'],
                address=self.customer_data['address'],
                phone=self.customer_data['phone']
            )

            order = OrderFactory.create_order(
                customer=customer,
                products=[(product, quantity)],
                shipping_type=self.shipping_type.get(),
                shipping_address=customer.address,
            )

            if order:
                # Save order
                orders = self.storage.load_data('orders', default=[])
                orders.append({
                    'id': order.id,
                    'customer_id': customer.id,  # Make sure this is the correct ID
                    'total_price': str(order.total_price),
                    'shipping_cost': str(order.shipping_cost),
                    'status': order.status.value,
                    'date': datetime.now().isoformat()
                })
                self.storage.save_data('orders', orders)

                self.update_products_list()
                self.update_orders_list()

                messagebox.showinfo("Success",
                                    f"Order placed successfully!\n"
                                    f"Total price: ${order.total_price}\n"
                                    f"Shipping cost: ${order.shipping_cost}\n"
                                    f"Estimated delivery: {order.shipping_strategy.get_estimated_days()} days"
                                    )
            else:
                messagebox.showerror("Error", "Failed to create order. Please check product availability.")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to place order: {str(e)}")


class AdminApp:
    def __init__(self, root, storage: JsonStorage):
        self.root = root
        self.storage = storage
        self.inventory_manager = InventoryManager()

        self.frame = ttk.Frame(root)
        self.frame.pack(expand=True, fill='both', padx=10, pady=5)

        # Welcome message
        welcome = ttk.Label(self.frame, text="Admin Dashboard", font=('Helvetica', 14))
        welcome.pack(pady=10)

        # Create notebook for tabs
        self.notebook = ttk.Notebook(self.frame)
        self.notebook.pack(expand=True, fill='both')

        # Create tabs
        self.create_products_tab()
        self.create_orders_tab()
        self.create_customers_tab()  # Yeni müşteri yönetim sekmesi

        # Load initial data
        self.load_initial_data()

    def load_initial_data(self):
        """Load products from storage to inventory manager."""
        products_data = self.storage.load_data('products', {})
        for product_id, product_data in products_data.items():
            try:
                product = Product(
                    id=product_id,
                    name=product_data['name'],
                    description=product_data.get('description', ''),
                    price=Decimal(product_data['price']),
                    category=product_data.get('category', ''),
                    stock_quantity=int(product_data.get('stock_quantity', 0))
                )
                self.inventory_manager.add_product(product)
            except Exception as e:
                print(f"Error loading product {product_id}: {str(e)}")

    def create_products_tab(self):
        """Create the products management tab."""
        products_frame = ttk.Frame(self.notebook)
        self.notebook.add(products_frame, text='Manage Products')

        # Product form
        form_frame = ttk.LabelFrame(products_frame, text="Product Details")
        form_frame.pack(fill='x', padx=5, pady=5)

        # Form fields
        fields = [
            ("ID:", "id"),
            ("Name*:", "name"),
            ("Description:", "description"),
            ("Price*:", "price"),
            ("Category:", "category"),
            ("Stock*:", "stock")
        ]

        self.product_entries = {}
        for i, (label, field) in enumerate(fields):
            ttk.Label(form_frame, text=label).grid(row=i, column=0, padx=5, pady=2, sticky='e')
            var = tk.StringVar()

            if field == "description":
                # Description için Text widget kullan
                text_widget = tk.Text(form_frame, height=4, width=30)
                text_widget.grid(row=i, column=1, padx=5, pady=2, sticky='ew')
                self.product_entries[field] = text_widget
            else:
                entry = ttk.Entry(form_frame, textvariable=var, width=32)
                if field == "id":  # ID alanını düzenlenemez yap
                    entry.config(state='readonly')
                entry.grid(row=i, column=1, padx=5, pady=2, sticky='ew')
                self.product_entries[field] = var

        # Buttons frame
        button_frame = ttk.Frame(form_frame)
        button_frame.grid(row=len(fields), column=0, columnspan=2, pady=10)

        ttk.Button(button_frame, text="Add New",
                   command=self.add_product).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Update",
                   command=self.update_product).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Delete",
                   command=self.delete_product).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Clear Form",
                   command=self.clear_product_form).pack(side=tk.LEFT, padx=5)

        # Products list with scrollbar
        list_frame = ttk.Frame(products_frame)
        list_frame.pack(fill='both', expand=True, padx=5, pady=5)

        # Treeview with scrollbars
        self.products_list = ttk.Treeview(list_frame,
                                          columns=('ID', 'Name', 'Price', 'Stock', 'Category'),
                                          show='headings')

        # Configure columns
        self.products_list.heading('ID', text='ID')
        self.products_list.heading('Name', text='Name')
        self.products_list.heading('Price', text='Price')
        self.products_list.heading('Stock', text='Stock')
        self.products_list.heading('Category', text='Category')

        self.products_list.column('ID', width=100, anchor='center')
        self.products_list.column('Name', width=150, anchor='w')
        self.products_list.column('Price', width=80, anchor='e')
        self.products_list.column('Stock', width=60, anchor='center')
        self.products_list.column('Category', width=120, anchor='w')

        # Add scrollbars
        y_scroll = ttk.Scrollbar(list_frame, orient='vertical', command=self.products_list.yview)
        x_scroll = ttk.Scrollbar(list_frame, orient='horizontal', command=self.products_list.xview)
        self.products_list.configure(yscrollcommand=y_scroll.set, xscrollcommand=x_scroll.set)

        # Grid layout
        self.products_list.grid(row=0, column=0, sticky='nsew')
        y_scroll.grid(row=0, column=1, sticky='ns')
        x_scroll.grid(row=1, column=0, sticky='ew')

        # Configure row/column weights
        list_frame.rowconfigure(0, weight=1)
        list_frame.columnconfigure(0, weight=1)

        # Bind selection event
        self.products_list.bind('<<TreeviewSelect>>', self.on_product_select)

        # Search frame
        search_frame = ttk.Frame(products_frame)
        search_frame.pack(fill='x', padx=5, pady=5)

        ttk.Label(search_frame, text="Search:").pack(side=tk.LEFT, padx=5)
        self.search_var = tk.StringVar()
        search_entry = ttk.Entry(search_frame, textvariable=self.search_var, width=30)
        search_entry.pack(side=tk.LEFT, padx=5)
        search_entry.bind('<KeyRelease>', self.search_products)

        ttk.Button(search_frame, text="Refresh",
                   command=self.update_products_list).pack(side=tk.RIGHT, padx=5)

        # Initial data load
        self.update_products_list()

    def create_orders_tab(self):
        """Create the orders management tab."""
        orders_frame = ttk.Frame(self.notebook)
        self.notebook.add(orders_frame, text='Manage Orders')

        # Orders list with scrollbar
        list_frame = ttk.Frame(orders_frame)
        list_frame.pack(fill='both', expand=True, padx=5, pady=5)

        self.orders_list = ttk.Treeview(list_frame,
                                        columns=('ID', 'Customer', 'Date', 'Total', 'Status'),
                                        show='headings')

        # Configure columns
        self.orders_list.heading('ID', text='Order ID')
        self.orders_list.heading('Customer', text='Customer')
        self.orders_list.heading('Date', text='Date')
        self.orders_list.heading('Total', text='Total')
        self.orders_list.heading('Status', text='Status')

        self.orders_list.column('ID', width=100, anchor='center')
        self.orders_list.column('Customer', width=150, anchor='w')
        self.orders_list.column('Date', width=120, anchor='center')
        self.orders_list.column('Total', width=80, anchor='e')
        self.orders_list.column('Status', width=100, anchor='center')

        # Add scrollbars
        y_scroll = ttk.Scrollbar(list_frame, orient='vertical', command=self.orders_list.yview)
        x_scroll = ttk.Scrollbar(list_frame, orient='horizontal', command=self.orders_list.xview)
        self.orders_list.configure(yscrollcommand=y_scroll.set, xscrollcommand=x_scroll.set)

        # Grid layout
        self.orders_list.grid(row=0, column=0, sticky='nsew')
        y_scroll.grid(row=0, column=1, sticky='ns')
        x_scroll.grid(row=1, column=0, sticky='ew')

        # Configure row/column weights
        list_frame.rowconfigure(0, weight=1)
        list_frame.columnconfigure(0, weight=1)

        # Order status update frame
        update_frame = ttk.LabelFrame(orders_frame, text="Order Actions")
        update_frame.pack(fill='x', padx=5, pady=5)

        ttk.Label(update_frame, text="Status:").pack(side=tk.LEFT, padx=5)
        self.new_status = tk.StringVar(value="processing")
        status_combo = ttk.Combobox(update_frame, textvariable=self.new_status,
                                    values=["created", "confirmed", "processing",
                                            "shipped", "delivered", "cancelled"],
                                    state='readonly', width=15)
        status_combo.pack(side=tk.LEFT, padx=5)

        ttk.Button(update_frame, text="Update Status",
                   command=self.update_order_status).pack(side=tk.LEFT, padx=5)

        ttk.Button(update_frame, text="View Details",
                   command=self.view_order_details).pack(side=tk.LEFT, padx=5)

        ttk.Button(update_frame, text="Refresh",
                   command=self.update_orders_list).pack(side=tk.RIGHT, padx=5)

        # Initial data load
        self.update_orders_list()

    def create_customers_tab(self):
        """Create the customers management tab."""
        customers_frame = ttk.Frame(self.notebook)
        self.notebook.add(customers_frame, text='Manage Customers')

        # Customers list with scrollbar
        list_frame = ttk.Frame(customers_frame)
        list_frame.pack(fill='both', expand=True, padx=5, pady=5)

        self.customers_list = ttk.Treeview(list_frame,
                                           columns=('ID', 'Name', 'Email', 'Phone', 'Orders'),
                                           show='headings')

        # Configure columns
        self.customers_list.heading('ID', text='ID')
        self.customers_list.heading('Name', text='Name')
        self.customers_list.heading('Email', text='Email')
        self.customers_list.heading('Phone', text='Phone')
        self.customers_list.heading('Orders', text='Orders')

        self.customers_list.column('ID', width=100, anchor='center')
        self.customers_list.column('Name', width=150, anchor='w')
        self.customers_list.column('Email', width=200, anchor='w')
        self.customers_list.column('Phone', width=120, anchor='center')
        self.customers_list.column('Orders', width=80, anchor='center')

        # Add scrollbars
        y_scroll = ttk.Scrollbar(list_frame, orient='vertical', command=self.customers_list.yview)
        x_scroll = ttk.Scrollbar(list_frame, orient='horizontal', command=self.customers_list.xview)
        self.customers_list.configure(yscrollcommand=y_scroll.set, xscrollcommand=x_scroll.set)

        # Grid layout
        self.customers_list.grid(row=0, column=0, sticky='nsew')
        y_scroll.grid(row=0, column=1, sticky='ns')
        x_scroll.grid(row=1, column=0, sticky='ew')

        # Configure row/column weights
        list_frame.rowconfigure(0, weight=1)
        list_frame.columnconfigure(0, weight=1)

        # Customer actions frame
        action_frame = ttk.LabelFrame(customers_frame, text="Customer Actions")
        action_frame.pack(fill='x', padx=5, pady=5)

        ttk.Button(action_frame, text="View Details",
                   command=self.view_customer_details).pack(side=tk.LEFT, padx=5)

        ttk.Button(action_frame, text="Delete Customer",
                   command=self.delete_customer).pack(side=tk.LEFT, padx=5)

        ttk.Button(action_frame, text="Refresh",
                   command=self.update_customers_list).pack(side=tk.RIGHT, padx=5)

        # Search frame
        search_frame = ttk.Frame(customers_frame)
        search_frame.pack(fill='x', padx=5, pady=5)

        ttk.Label(search_frame, text="Search:").pack(side=tk.LEFT, padx=5)
        self.customer_search_var = tk.StringVar()
        search_entry = ttk.Entry(search_frame, textvariable=self.customer_search_var, width=30)
        search_entry.pack(side=tk.LEFT, padx=5)
        search_entry.bind('<KeyRelease>', self.search_customers)

        # Initial data load
        self.update_customers_list()

    # Product management methods
    def on_product_select(self, event):
        """Fill form when product is selected."""
        selection = self.products_list.selection()
        if not selection:
            return

        product_id = self.products_list.item(selection[0])['values'][0]
        product = self.inventory_manager.get_product(product_id)

        if product:
            self.product_entries['id'].set(product.id)
            self.product_entries['name'].set(product.name)

            # Description için Text widget'ı temizle ve yeni içerik ekle
            description_widget = self.product_entries['description']
            description_widget.delete('1.0', tk.END)
            description_widget.insert('1.0', product.description)

            self.product_entries['price'].set(str(product.price))
            self.product_entries['category'].set(product.category)
            self.product_entries['stock'].set(str(product.stock_quantity))

    def clear_product_form(self):
        """Clear the product form."""
        for field, widget in self.product_entries.items():
            if field == 'description':
                widget.delete('1.0', tk.END)
            else:
                if isinstance(widget, tk.StringVar):
                    widget.set('')

    def add_product(self):
        """Add a new product."""
        try:
            # Gerekli alanları kontrol et
            name = self.product_entries['name'].get().strip()
            price = self.product_entries['price'].get().strip()
            stock = self.product_entries['stock'].get().strip()

            if not name or not price or not stock:
                messagebox.showwarning("Warning", "Please fill in all required fields (*)")
                return

            product = Product(
                id=str(uuid.uuid4()),
                name=name,
                description=self.product_entries['description'].get("1.0", tk.END).strip(),
                price=Decimal(price),
                category=self.product_entries['category'].get().strip(),
                stock_quantity=int(stock)
            )

            self.inventory_manager.add_product(product)
            self.save_products()
            self.update_products_list()
            self.clear_product_form()
            messagebox.showinfo("Success", "Product added successfully!")
        except ValueError as e:
            messagebox.showerror("Error", f"Invalid input: {str(e)}")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to add product: {str(e)}")

    def update_product(self):
        """Update an existing product."""
        try:
            product_id = self.product_entries['id'].get()
            if not product_id:
                messagebox.showwarning("Warning", "Please select a product to update")
                return

            # Gerekli alanları kontrol et
            name = self.product_entries['name'].get().strip()
            price = self.product_entries['price'].get().strip()
            stock = self.product_entries['stock'].get().strip()

            if not name or not price or not stock:
                messagebox.showwarning("Warning", "Please fill in all required fields (*)")
                return

            product = self.inventory_manager.get_product(product_id)
            if not product:
                messagebox.showerror("Error", "Product not found")
                return

            # Ürün bilgilerini güncelle
            product.name = name
            product.description = self.product_entries['description'].get("1.0", tk.END).strip()
            product.price = Decimal(price)
            product.category = self.product_entries['category'].get().strip()
            product.stock_quantity = int(stock)

            self.save_products()
            self.update_products_list()
            messagebox.showinfo("Success", "Product updated successfully!")
        except ValueError as e:
            messagebox.showerror("Error", f"Invalid input: {str(e)}")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to update product: {str(e)}")

    def delete_product(self):
        """Delete the selected product."""
        try:
            product_id = self.product_entries['id'].get()
            if not product_id:
                messagebox.showwarning("Warning", "Please select a product to delete")
                return

            product = self.inventory_manager.get_product(product_id)
            if not product:
                messagebox.showerror("Error", "Product not found")
                return

            if messagebox.askyesno("Confirm Delete",
                                   f"Are you sure you want to delete '{product.name}'?\nThis action cannot be undone."):
                self.inventory_manager.remove_product(product_id)
                self.save_products()
                self.update_products_list()
                self.clear_product_form()
                messagebox.showinfo("Success", "Product deleted successfully!")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to delete product: {str(e)}")

    def save_products(self):
        """Save all products to storage."""
        self.storage.save_data('products', {
            p.id: {
                'id': p.id,
                'name': p.name,
                'description': p.description,
                'price': str(p.price),
                'category': p.category,
                'stock_quantity': p.stock_quantity
            }
            for p in self.inventory_manager.get_all_products().values()
        })

    def update_products_list(self):
        """Update the products list."""
        for item in self.products_list.get_children():
            self.products_list.delete(item)

        for product in self.inventory_manager.get_all_products().values():
            self.products_list.insert('', 'end', values=(
                product.id,
                product.name,
                f"${product.price:.2f}",
                product.stock_quantity,
                product.category
            ))

    def search_products(self, event=None):
        """Search products by name or category."""
        search_term = self.search_var.get().lower()

        for item in self.products_list.get_children():
            values = self.products_list.item(item)['values']
            if (search_term in values[1].lower() or  # Name
                    search_term in values[4].lower()):  # Category
                self.products_list.item(item, tags=('match',))
                self.products_list.selection_set(item)
            else:
                self.products_list.item(item, tags=('no_match',))
                self.products_list.selection_remove(item)

    # Order management methods
    def update_orders_list(self):
        """Update the orders list."""
        for item in self.orders_list.get_children():
            self.orders_list.delete(item)

        try:
            orders = self.storage.load_data('orders', default=[])
            customers = self.storage.load_data('customers', default={})

            for order in orders:
                if not isinstance(order, dict):
                    continue

                customer_id = order.get('customer_id')
                customer_name = "Unknown"

                # Find customer name
                for customer in customers.values():
                    if isinstance(customer, dict) and customer.get('id') == customer_id:
                        customer_name = customer.get('name', 'Unknown')
                        break

                # Format date if exists
                order_date = order.get('date', '')
                if order_date:
                    try:
                        dt = datetime.fromisoformat(order_date)
                        order_date = dt.strftime('%Y-%m-%d %H:%M')
                    except ValueError:
                        pass

                self.orders_list.insert('', 'end', values=(
                    order.get('id', 'N/A'),
                    customer_name,
                    order_date,
                    f"${Decimal(order.get('total_price', '0')):.2f}",
                    order.get('status', 'unknown').capitalize()
                ))
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load orders: {str(e)}")

    def update_order_status(self):
        """Update the status of selected order."""
        selection = self.orders_list.selection()
        if not selection:
            messagebox.showwarning("Warning", "Please select an order")
            return

        try:
            order_id = self.orders_list.item(selection[0])['values'][0]
            new_status = self.new_status.get()

            orders = self.storage.load_data('orders', default=[])

            updated = False
            for order in orders:
                if order['id'] == order_id:
                    order['status'] = new_status
                    updated = True
                    break

            if updated:
                self.storage.save_data('orders', orders)
                self.update_orders_list()
                messagebox.showinfo("Success", "Order status updated successfully!")
            else:
                messagebox.showerror("Error", "Order not found")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to update order status: {str(e)}")

    def view_order_details(self):
        """Show details of the selected order."""
        selection = self.orders_list.selection()
        if not selection:
            messagebox.showwarning("Warning", "Please select an order")
            return

        try:
            order_id = self.orders_list.item(selection[0])['values'][0]
            orders = self.storage.load_data('orders', default=[])
            products = self.storage.load_data('products', default={})
            customers = self.storage.load_data('customers', default={})

            order = next((o for o in orders if o['id'] == order_id), None)
            if not order:
                messagebox.showerror("Error", "Order not found")
                return

            # Find customer
            customer = next((c for c in customers.values()
                             if isinstance(c, dict) and c.get('id') == order.get('customer_id')), None)

            # Create details window
            details_window = tk.Toplevel(self.root)
            details_window.title(f"Order Details - {order_id}")
            details_window.geometry("600x400")

            # Main frame
            main_frame = ttk.Frame(details_window)
            main_frame.pack(fill='both', expand=True, padx=10, pady=10)

            # Order info
            info_frame = ttk.LabelFrame(main_frame, text="Order Information")
            info_frame.pack(fill='x', padx=5, pady=5)

            ttk.Label(info_frame, text=f"Order ID: {order.get('id', 'N/A')}").pack(anchor='w')
            ttk.Label(info_frame, text=f"Date: {order.get('date', 'N/A')}").pack(anchor='w')
            ttk.Label(info_frame, text=f"Status: {order.get('status', 'unknown').capitalize()}").pack(anchor='w')
            ttk.Label(info_frame, text=f"Total: ${Decimal(order.get('total_price', '0')):.2f}").pack(anchor='w')
            ttk.Label(info_frame, text=f"Shipping Cost: ${Decimal(order.get('shipping_cost', '0')):.2f}").pack(
                anchor='w')

            # Customer info
            if customer:
                customer_frame = ttk.LabelFrame(main_frame, text="Customer Information")
                customer_frame.pack(fill='x', padx=5, pady=5)

                ttk.Label(customer_frame, text=f"Name: {customer.get('name', 'N/A')}").pack(anchor='w')
                ttk.Label(customer_frame, text=f"Email: {customer.get('email', 'N/A')}").pack(anchor='w')
                ttk.Label(customer_frame, text=f"Phone: {customer.get('phone', 'N/A')}").pack(anchor='w')
                ttk.Label(customer_frame, text=f"Address: {customer.get('address', 'N/A')}").pack(anchor='w')

            # Products list
            products_frame = ttk.LabelFrame(main_frame, text="Ordered Products")
            products_frame.pack(fill='both', expand=True, padx=5, pady=5)

            # Treeview for products
            tree = ttk.Treeview(products_frame, columns=('Product', 'Quantity', 'Price'), show='headings')
            tree.heading('Product', text='Product')
            tree.heading('Quantity', text='Quantity')
            tree.heading('Price', text='Price')

            tree.column('Product', width=200, anchor='w')
            tree.column('Quantity', width=80, anchor='center')
            tree.column('Price', width=100, anchor='e')

            # Add scrollbar
            scrollbar = ttk.Scrollbar(products_frame, orient='vertical', command=tree.yview)
            tree.configure(yscrollcommand=scrollbar.set)

            tree.pack(side='left', fill='both', expand=True)
            scrollbar.pack(side='right', fill='y')

            # Add products to treeview
            order_items = order.get('items', [])
            for item in order_items:
                product = products.get(item.get('product_id', ''), {})
                product_name = product.get('name', 'Unknown Product')
                quantity = item.get('quantity', 1)
                price = Decimal(item.get('price', '0'))

                tree.insert('', 'end', values=(
                    product_name,
                    quantity,
                    f"${price:.2f}"
                ))

        except Exception as e:
            messagebox.showerror("Error", f"Failed to load order details: {str(e)}")

    # Customer management methods
    def update_customers_list(self):
        """Update the customers list."""
        for item in self.customers_list.get_children():
            self.customers_list.delete(item)

        try:
            customers = self.storage.load_data('customers', default={})
            orders = self.storage.load_data('orders', default=[])

            for customer_id, customer in customers.items():
                if not isinstance(customer, dict):
                    continue

                # Count orders for this customer
                order_count = sum(1 for o in orders
                                  if isinstance(o, dict) and o.get('customer_id') == customer_id)

                self.customers_list.insert('', 'end', values=(
                    customer.get('id', 'N/A'),
                    customer.get('name', 'Unknown'),
                    customer.get('email', 'N/A'),
                    customer.get('phone', 'N/A'),
                    order_count
                ))
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load customers: {str(e)}")

    def view_customer_details(self):
        """Show details of the selected customer."""
        selection = self.customers_list.selection()
        if not selection:
            messagebox.showwarning("Warning", "Please select a customer")
            return

        try:
            customer_id = self.customers_list.item(selection[0])['values'][0]
            customers = self.storage.load_data('customers', default={})
            orders = self.storage.load_data('orders', default=[])

            customer = customers.get(customer_id)
            if not customer:
                messagebox.showerror("Error", "Customer not found")
                return

            # Create details window
            details_window = tk.Toplevel(self.root)
            details_window.title(f"Customer Details - {customer.get('name', 'Unknown')}")
            details_window.geometry("500x400")

            # Main frame
            main_frame = ttk.Frame(details_window)
            main_frame.pack(fill='both', expand=True, padx=10, pady=10)

            # Customer info
            info_frame = ttk.LabelFrame(main_frame, text="Customer Information")
            info_frame.pack(fill='x', padx=5, pady=5)

            ttk.Label(info_frame, text=f"Name: {customer.get('name', 'N/A')}").pack(anchor='w')
            ttk.Label(info_frame, text=f"Email: {customer.get('email', 'N/A')}").pack(anchor='w')
            ttk.Label(info_frame, text=f"Phone: {customer.get('phone', 'N/A')}").pack(anchor='w')
            ttk.Label(info_frame, text=f"Address: {customer.get('address', 'N/A')}").pack(anchor='w')
            ttk.Label(info_frame, text=f"Registration Date: {customer.get('registration_date', 'N/A')}").pack(
                anchor='w')

            # Orders list
            orders_frame = ttk.LabelFrame(main_frame, text="Customer Orders")
            orders_frame.pack(fill='both', expand=True, padx=5, pady=5)

            # Treeview for orders
            tree = ttk.Treeview(orders_frame, columns=('Order ID', 'Date', 'Total', 'Status'), show='headings')
            tree.heading('Order ID', text='Order ID')
            tree.heading('Date', text='Date')
            tree.heading('Total', text='Total')
            tree.heading('Status', text='Status')

            tree.column('Order ID', width=100, anchor='center')
            tree.column('Date', width=120, anchor='center')
            tree.column('Total', width=80, anchor='e')
            tree.column('Status', width=100, anchor='center')

            # Add scrollbar
            scrollbar = ttk.Scrollbar(orders_frame, orient='vertical', command=tree.yview)
            tree.configure(yscrollcommand=scrollbar.set)

            tree.pack(side='left', fill='both', expand=True)
            scrollbar.pack(side='right', fill='y')

            # Add orders to treeview
            customer_orders = [o for o in orders
                               if isinstance(o, dict) and o.get('customer_id') == customer_id]

            for order in customer_orders:
                # Format date if exists
                order_date = order.get('date', '')
                if order_date:
                    try:
                        dt = datetime.fromisoformat(order_date)
                        order_date = dt.strftime('%Y-%m-%d %H:%M')
                    except ValueError:
                        pass

                tree.insert('', 'end', values=(
                    order.get('id', 'N/A'),
                    order_date,
                    f"${Decimal(order.get('total_price', '0')):.2f}",
                    order.get('status', 'unknown').capitalize()
                ))

        except Exception as e:
            messagebox.showerror("Error", f"Failed to load customer details: {str(e)}")

    def delete_customer(self):
        """Delete the selected customer."""
        selection = self.customers_list.selection()
        if not selection:
            messagebox.showwarning("Warning", "Please select a customer")
            return

        try:
            customer_id = self.customers_list.item(selection[0])['values'][0]
            customers = self.storage.load_data('customers', default={})

            if customer_id not in customers:
                messagebox.showerror("Error", "Customer not found")
                return

            customer_name = customers[customer_id].get('name', 'this customer')

            if messagebox.askyesno("Confirm Delete",
                                   f"Are you sure you want to delete '{customer_name}'?\nThis will also delete all their orders."):
                # Delete customer
                del customers[customer_id]
                self.storage.save_data('customers', customers)

                # Delete customer's orders
                orders = self.storage.load_data('orders', default=[])
                orders = [o for o in orders
                          if isinstance(o, dict) and o.get('customer_id') != customer_id]
                self.storage.save_data('orders', orders)

                self.update_customers_list()
                self.update_orders_list()
                messagebox.showinfo("Success", "Customer and their orders deleted successfully!")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to delete customer: {str(e)}")

    def search_customers(self, event=None):
        """Search customers by name or email."""
        search_term = self.customer_search_var.get().lower()

        for item in self.customers_list.get_children():
            values = self.customers_list.item(item)['values']
            if (search_term in values[1].lower() or  # Name
                    search_term in values[2].lower()):  # Email
                self.customers_list.item(item, tags=('match',))
                self.customers_list.selection_set(item)
            else:
                self.customers_list.item(item, tags=('no_match',))
                self.customers_list.selection_remove(item)


def main():
    root = tk.Tk()
    root.title("E-commerce System")
    root.geometry("800x600")

    storage = JsonStorage()
    if not storage.load_data('products'):
        storage.save_data('products', {})
    if not storage.load_data('orders'):
        storage.save_data('orders', [])
    if not storage.load_data('customers'):
        storage.save_data('customers', {})
    if not storage.load_data('admins'):
        storage.save_data('admins', {})

    def on_customer_login(customer_data):
        CustomerApp(root, storage, customer_data)

    def on_admin_login():
        AdminApp(root, storage)

    LoginScreen(root, storage, on_customer_login, on_admin_login)

    root.mainloop()


if __name__ == "__main__":
    main()