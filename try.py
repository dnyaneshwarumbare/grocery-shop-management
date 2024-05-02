import tkinter as tk
from tkinter import messagebox, ttk
from sqlalchemy import create_engine, Column, Integer, String, Float, Date, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from datetime import date

# Create a SQLAlchemy engine for MySQL
DB_USER = 'root'
DB_PASSWORD = '123456'
DB_HOST = 'localhost'
DB_PORT = '3306'
DB_NAME = 'shop'

# Create the MySQL engine
engine = create_engine(f'mysql+pymysql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}', echo=True, pool_pre_ping=True)

Base = declarative_base()
Session = sessionmaker(bind=engine)

# Define database tables
class Item(Base):
    __tablename__ = 'items'

    id = Column(Integer, primary_key=True)
    name = Column(String(255), nullable=False)
    price = Column(Float, nullable=False)

class Transaction(Base):
    __tablename__ = 'transactions'

    id = Column(Integer, primary_key=True)
    user_name = Column(String(255), nullable=False)
    item_id = Column(Integer, ForeignKey('items.id'), nullable=False)
    quantity = Column(Integer, nullable=False)
    transaction_date = Column(Date, default=date.today)

    item = relationship("Item")

class Customer(Base):
    __tablename__ = 'customers'

    id = Column(Integer, primary_key=True)
    name = Column(String(255), nullable=False)
    email = Column(String(255), unique=True)
    phone = Column(String(20))

# Create tables in the database (MySQL)
Base.metadata.create_all(engine)

# Tkinter GUI setup
def add_item_click():
    item_name = item_name_entry.get().strip()
    item_price_str = item_price_entry.get().strip()

    try:
        item_price = float(item_price_str)
    except ValueError:
        messagebox.showerror("Error", "Please enter a valid item price.")
        return

    if item_name and item_price > 0:
        session = Session()
        new_item = Item(name=item_name, price=item_price)
        session.add(new_item)
        session.commit()
        session.close()
        messagebox.showinfo("Success", "Item added successfully!")

        # Clear entry fields after adding item
        item_name_entry.delete(0, tk.END)
        item_price_entry.delete(0, tk.END)
    else:
        messagebox.showerror("Error", "Please enter valid item details.")

def add_transaction_click():
    user_name = user_name_entry.get().strip()
    item_id = item_id_entry.get().strip()
    quantity_str = quantity_entry.get().strip()

    try:
        item_id = int(item_id)
        quantity = int(quantity_str)
    except ValueError:
        messagebox.showerror("Error", "Please enter valid item ID and quantity.")
        return

    if user_name and item_id and quantity > 0:
        session = Session()
        # Check if the item ID exists in the database
        item = session.query(Item).filter_by(id=item_id).first()
        if not item:
            messagebox.showerror("Error", "Item with the specified ID does not exist.")
            session.close()
            return

        new_transaction = Transaction(user_name=user_name, item_id=item_id, quantity=quantity)
        session.add(new_transaction)
        session.commit()
        session.close()
        messagebox.showinfo("Success", "Transaction added successfully!")

        # Clear entry fields after adding transaction
        user_name_entry.delete(0, tk.END)
        item_id_entry.delete(0, tk.END)
        quantity_entry.delete(0, tk.END)
    else:
        messagebox.showerror("Error", "Please enter valid transaction details.")

def display_items():
    session = Session()
    items = session.query(Item).all()
    session.close()

    item_display.delete(*item_display.get_children())  # Clear existing items
    for item in items:
        item_display.insert('', 'end', values=(item.id, item.name, item.price))

def display_transactions():
    session = Session()
    transactions = session.query(Transaction).all()

    transaction_display.delete(*transaction_display.get_children())  # Clear existing transactions
    for transaction in transactions:
        item_name = session.query(Item).filter_by(id=transaction.item_id).first().name
        transaction_display.insert('', 'end', values=(transaction.id, transaction.user_name, item_name, transaction.quantity, transaction.transaction_date))

def add_customer_click():
    customer_name = customer_name_entry.get().strip()
    customer_email = customer_email_entry.get().strip()

    if not customer_name or not customer_email:
        messagebox.showerror("Error", "Please enter valid customer details.")
        return

    customer_phone = customer_phone_entry.get().strip()  # Optional field

    session = Session()
    new_customer = Customer(name=customer_name, email=customer_email, phone=customer_phone)
    session.add(new_customer)
    session.commit()
    session.close()
    messagebox.showinfo("Success", "Customer added successfully!")

    # Clear entry fields after adding customer
    customer_name_entry.delete(0, tk.END)
    customer_email_entry.delete(0, tk.END)
    customer_phone_entry.delete(0, tk.END)

root = tk.Tk()
root.title("Grocery Shop")

# Add Item Section
tk.Label(root, text="Add Item").pack()
tk.Label(root, text="Item Name:").pack()
item_name_entry = tk.Entry(root)
item_name_entry.pack()

tk.Label(root, text="Item Price ($):").pack()
item_price_entry = tk.Entry(root)
item_price_entry.pack()

tk.Button(root, text="Add Item", command=add_item_click).pack()

# Add Transaction Section
tk.Label(root, text="Add Transaction").pack()
tk.Label(root, text="User Name:").pack()
user_name_entry = tk.Entry(root)
user_name_entry.pack()

tk.Label(root, text="Item ID:").pack()
item_id_entry = tk.Entry(root)
item_id_entry.pack()

tk.Label(root, text="Quantity:").pack()
quantity_entry = tk.Entry(root)
quantity_entry.pack()

tk.Button(root, text="Add Transaction", command=add_transaction_click).pack()

# Display Items Section with Scrollbar
item_frame = tk.Frame(root)
item_frame.pack(pady=10)

item_display = ttk.Treeview(item_frame, columns=('ID', 'Name', 'Price'), show='headings')
item_display.heading('#0', text='ID')
item_display.heading('#1', text='Name')
item_display.heading('#2', text='Price')
item_display.pack(side='left', fill='y')

item_scrollbar = ttk.Scrollbar(item_frame, orient='vertical', command=item_display.yview)
item_scrollbar.pack(side='right', fill='y')
item_display.configure(yscrollcommand=item_scrollbar.set)

tk.Button(root, text="Display Items", command=display_items).pack()

# Display Transactions Section with Scrollbar
transaction_frame = tk.Frame(root)
transaction_frame.pack(pady=10)

transaction_display = ttk.Treeview(transaction_frame, columns=('ID', 'User Name', 'Item Name', 'Quantity', 'Date'), show='headings')
transaction_display.heading('#0', text='ID')
transaction_display.heading('#1', text='User Name')
transaction_display.heading('#2', text='Item Name')
transaction_display.heading('#3', text='Quantity')
transaction_display.heading('#4', text='Date')
transaction_display.pack(side='left', fill='y')

transaction_scrollbar = ttk.Scrollbar(transaction_frame, orient='vertical', command=transaction_display.yview)
transaction_scrollbar.pack(side='right', fill='y')
transaction_display.configure(yscrollcommand=transaction_scrollbar.set)

tk.Button(root, text="Display Transactions", command=display_transactions).pack()

# Add Customer Section
tk.Label(root, text="Add Customer").pack()
tk.Label(root, text="Name:").pack()
customer_name_entry = tk.Entry(root)
customer_name_entry.pack()

tk.Label(root, text="Email:").pack()
customer_email_entry = tk.Entry(root)
customer_email_entry.pack()

tk.Label(root, text="Phone:").pack()
customer_phone_entry = tk.Entry(root)
customer_phone_entry.pack()

tk.Button(root, text="Add Customer", command=add_customer_click).pack()

root.mainloop()
