# order_processing.py

from typing import List, Dict
from datetime import date
from inventory import InventoryManager  # Make sure to have inventory.py ready

class Customer: # Represents a customer who can place orders
    def __init__(self, customer_id: str, name: str, email: str, phone: str):
        self.customer_id = customer_id
        self.name = name
        self.email = email
        self.phone = phone

    def __str__(self):
        return f"{self.name} (Email: {self.email}, Phone: {self.phone})"
    
    def to_dict(self):
        return {
            "customer_id": self.customer_id,
            "name": self.name,
            "email": self.email,
            "phone": self.phone
        }

    @classmethod
    def from_dict(cls, data):
        return cls(
            customer_id=data["customer_id"],
            name=data["name"],
            email=data["email"],
            phone=data["phone"]
        )

class CustomerOrder: # Represents a customer order with items and their quantities
    def __init__(self, order_id: str, customer: Customer, order_date: date):
        self.order_id = order_id
        self.customer = customer
        self.order_date = order_date
        self.items: Dict[str, int] = {}  # item_ID -> quantity
        self.total_price: float = 0.0

    def add_item(self, item_ID: str, quantity: int, price_per_unit: float): # Add item to the order
        if item_ID in self.items:
            self.items[item_ID] += quantity
        else:
            self.items[item_ID] = quantity
        self.total_price += quantity * price_per_unit

    def __str__(self):
        return f"Order {self.order_id} by {self.customer.name} - Total: ${self.total_price:.2f}"
    
    def to_dict(self):
        return {
            "order_id": self.order_id,
            "customer_id": self.customer.customer_id,
            "order_date": self.order_date.isoformat(),
            "items": self.items,
            "total_price": self.total_price
        }

    @classmethod
    def from_dict(cls, data, customer: Customer):
        order = cls(
            order_id=data["order_id"],
            customer=customer,
            order_date=date.fromisoformat(data["order_date"])
        )
        order.items = data["items"]
        order.total_price = data["total_price"]
        return order

class OrderProcessor: #Handles order creation and stock deduction
    def __init__(self, inventory_manager: InventoryManager):
        self.inventory_manager = inventory_manager
        self.customers: Dict[str, Customer] = {}
        self.orders: Dict[str, CustomerOrder] = {}

    def add_customer(self, customer: Customer) -> bool: # Adding a new customer (customers can't have the same ID)
        if customer.customer_id in self.customers:
            return False
        self.customers[customer.customer_id] = customer
        return True

    def create_order(self, order_id: str, customer_id: str, order_date: date, items: Dict[str, int]) -> bool: # Attempt to create a customer order with given item_IDs and quantities
        if order_id in self.orders or customer_id not in self.customers:
            return False

        for item_ID, quantity in items.items():
            product = self.inventory_manager.get_product(item_ID)
            if not product or product.quantity < quantity:
                return False # Stock is insufficient

        customer = self.customers[customer_id]
        order = CustomerOrder(order_id, customer, order_date)

        for item_ID, quantity in items.items():
            product = self.inventory_manager.get_product(item_ID)
            order.add_item(item_ID, quantity, product.price)
            self.inventory_manager.update_stock(item_ID, -quantity) # Stock is being removed

        self.orders[order_id] = order
        return True

    def get_order(self, order_id: str) -> CustomerOrder: # Retrieve an order by ID
        return self.orders.get(order_id)

    def list_orders(self) -> List[CustomerOrder]: # View all current orders
        return list(self.orders.values())