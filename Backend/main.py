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

def customer_order_menu():
    while True:
        print("\n--- Customer Orders ---")
        print("1. Add Customer")
        print("2. Create Order")
        print("3. View Orders")
        print("4. Back")
        choice = input("Choose option: ")

        if choice == "1":
            cid = input("Customer ID: ")
            name = input("Name: ")
            email = input("Email: ")
            phone = input("Phone: ")
            c = Customer(cid, name, email, phone) # Bundles all this information into a customer which is then added
            if order_processor.add_customer(c):
                print("Customer added.")
            else:
                print("Already exists.")
        elif choice == "2":
            cid = input("Customer ID: ")
            order_id = str(uuid.uuid4())[:8]
            order_items = {}

            print("Enter items (Item ID and Quantity). Leave Item ID blank to finish.")
            while True:
                item_ID = input("Item ID: ")
                if not item_ID:
                    break
                qty = int(input("Qty: "))
                order_items[item_ID] = qty

            if order_processor.create_order(order_id, cid, date.today(), order_items):
                # Calculate total for financial record
                total = sum(inventory_manager.get_product(item_ID).price * qty for item_ID, qty in order_items.items())
                financial_manager.record_sale(total, f"Customer order {order_id}")
                print(f"Order {order_id} created.")
            else:
                print("Failed. Check customer and stock levels.")
        elif choice == "3":
            print("\nAll Orders:")
            for order in order_processor.list_orders():
                print(order)
        elif choice == "4":
            break


def supplier_menu():
    while True:
        print("\n--- Supplier Management ---")
        print("1. Add Supplier")
        print("2. Create Purchase Order")
        print("3. Receive Delivery (Mark Delivered + Update Stock)")
        print("4. View Suppliers")
        print("5. View Purchase Orders")
        print("6. Back")
        choice = input("Choose option: ")

        if choice == "1":
            sid = input("Supplier ID: ")
            name = input("Name: ")
            contact = input("Contact Name: ")
            phone = input("Phone: ")
            email = input("Email: ")
            addr = input("Address: ")
            s = Supplier(sid, name, contact, phone, email, addr)
            if supplier_manager.add_supplier(s):
                print("Added.")
            else:
                print("Already exists.")
        elif choice == "2":
            sid = input("Supplier ID: ")
            po_id = str(uuid.uuid4())[:8]
            order_date = date.today()
            expected = date.fromisoformat(input("Expected Delivery (YYYY-MM-DD): "))
            po = supplier_manager.create_purchase_order(po_id, sid, order_date, expected)

            if not po:
                print("Failed. Check supplier ID.")
                continue

            print("Add items (Item ID and Quantity). Leave Item ID blank to finish.")
            while True:
                item_ID = input("Item ID: ")
                if not item_ID:
                    break
                qty = int(input("Qty: "))
                po.add_item(item_ID, qty)

            po.update_status(OrderStatus.ORDERED)
            print(f"PO {po_id} created.")
        elif choice == "3":
            po_id = input("PO ID to mark delivered: ")
            po = supplier_manager.get_purchase_order(po_id)
            if not po:
                print("Not found.")
                continue

            for item_ID, qty in po.items.items():
                inventory_manager.update_stock(item_ID, qty)
            po.update_status(OrderStatus.DELIVERED)

            # Assume we calculate total cost from product price
            total_cost = sum(inventory_manager.get_product(item_ID).price * qty for item_ID, qty in po.items.items())
            financial_manager.record_purchase(total_cost, f"PO {po_id} from {po.supplier.name}")
            print(f"PO {po_id} marked as delivered and inventory updated.")
        elif choice == "4":
            print("\nSuppliers:")
            for s in supplier_manager.list_suppliers():
                print(s)
        elif choice == "5":
            print("\nPurchase Orders:")
            for po in supplier_manager.list_purchase_orders():
                print(po)
        elif choice == "6":
            break


def finance_menu():
    print("\n--- Financial Report ---")
    print(financial_manager.generate_report())

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
