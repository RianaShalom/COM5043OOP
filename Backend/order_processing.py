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
