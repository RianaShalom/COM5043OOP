from abc import ABC, abstractmethod
from datetime import datetime
from typing import Dict

class Order(ABC): # Abstract base class representing a generic order
    def __init__(self, order_id: str, date: datetime, items: Dict[str, int], total_cost: float):
        self._order_id = order_id  # Unique identifier for the order
        self._date = date  # Date the order was created
        self._items = items  # Dictionary of item IDs and their quantities
        self._total_cost = total_cost  # Total monetary value of the order

    @property # To get the order
    def order_id(self) -> str:
        return self._order_id
    
    @property # To get the date
    def date(self) -> datetime:
        return self._date
    
    @property # To get the items
    def items(self) -> Dict[str, int]:
        return self._items
    
    @property # To get the cost
    def total_cost(self) -> float:
        return self._total_cost
    
    @abstractmethod # Abstract method to return the type of the order
    def order_type(self) -> str:
        pass

    def __str__(self) -> str:
        return f"{self.order_type()} Order | ID: {self.order_id} | Date: {self.date.strftime('%Y-%m-%d')} | Total: ${self.total_cost:.2f}"

class PurchaseOrder(Order): # Class representing a purchase order from a supplier
    def __init__(self, order_id: str, date: datetime, items: Dict[str, int], total_cost: float, supplier_id: str):
        super().__init__(order_id, date, items, total_cost)
        self._supplier_id = supplier_id  # ID of the supplier the order is from

    @property # To get the supplier ID
    def supplier_id(self) -> str:
        return self._supplier_id

    def order_type(self) -> str: # Returns the type of the order
        return "Purchase"

    def __str__(self) -> str: # String representation including supplier ID
        return super().__str__() + f" | Supplier ID: {self.supplier_id}"

class SalesOrder(Order): # Class representing a sales order to a customer
    def __init__(self, order_id: str, date: datetime, items: Dict[str, int], total_cost: float, customer_name: str):
        super().__init__(order_id, date, items, total_cost)
        self._customer_name = customer_name  # Name of the customer

    @property # Property to get the customer name
    def customer_name(self) -> str:
        return self._customer_name

    def order_type(self) -> str: # Returns the type of the order
        return "Sales"

    def __str__(self) -> str: # String representation including customer name
        return super().__str__() + f" | Customer: {self.customer_name}"
