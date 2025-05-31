import uuid
from inventory import InventoryManager, Product
from order_processing import OrderProcessor, Customer
from supplier import SupplierManager, Supplier, OrderStatus
from financial import FinancialManager
from datetime import date

inventory_manager = InventoryManager() # Initialises the managers
order_processor = OrderProcessor(inventory_manager)
supplier_manager = SupplierManager()
financial_manager = FinancialManager()

def inventory_menu():
    while True:
        print("\n--- Inventory Management ---") # Nav menu for inventory management
        print("1. Add Product")
        print("2. Remove Product")
        print("3. List All Products")
        print("4. List Low Stock Products")
        print("5. Back")
        choice = input("Choose option: ")

        if choice == "1":
            item_ID = input("Enter Item ID: ")
            name = input("Enter name: ")
            price = float(input("Enter price: "))
            qty = int(input("Enter quantity: "))
            product = Product(item_ID, name, price, qty) # Bundles all this information into a product which is then added
            if inventory_manager.add_product(product):
                print("Product added.")
            else:
                print("That Item ID already exists.")
        elif choice == "2":
            item_ID = input("Enter Item ID to remove: ")
            if inventory_manager.remove_product(item_ID):
                print("Removed.")
            else:
                print("Product not found.")
        elif choice == "3":
            print("\nProducts:")
            for p in inventory_manager.list_all_products():
                print(p)
        elif choice == "4":
            print("\nLow Stock Products:")
            for p in inventory_manager.list_low_stock_products():
                print(p)
        elif choice == "5":
            break

def main_menu():
    while True:
        print("\n====== Warehouse System ======")
        print("1. Manage Inventory")
        print("2. Customer Orders")
        print("3. Supplier Orders")
        print("4. Financial Report")
        print("5. Exit")
        choice = input("Choose option: ")

        if choice == "1":
            inventory_menu()
        elif choice == "2":
            customer_order_menu()
        elif choice == "3":
            supplier_menu()
        elif choice == "4":
            finance_menu()
        elif choice == "5":
            print("Goodbye!")
            break
        else:
            print("Invalid choice.")

if __name__ == "__main__":
    main_menu()
