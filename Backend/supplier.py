from typing import List, Dict, Optional
from enum import Enum, auto
from datetime import date
from data_storage import save_data, load_data

class OrderStatus(Enum): # Enum to represent the status of a purchase order
    PENDING = auto()
    ORDERED = auto()
    DELIVERED = auto()
    CANCELLED = auto()

class Supplier: # Represents a supplier with contact info and order history
    def __init__(self, supplier_id: str, name: str, contact_name: str, phone: str, email: str, address: str):
        self.supplier_id = supplier_id
        self.name = name
        self.contact_name = contact_name
        self.phone = phone
        self.email = email
        self.address = address
        self.order_history: List['PurchaseOrder'] = []

    def add_order(self, order: 'PurchaseOrder') -> None: # Add a purchase order to the supplier's order history
        self.order_history.append(order)
    
    def __str__(self):
        return f"ID: {self.supplier_id} - {self.name} (Contact: {self.contact_name}, Phone: {self.phone})"

    def to_dict(self) -> Dict:
        return {
            "supplier_id": self.supplier_id,
            "name": self.name,
            "contact_name": self.contact_name,
            "phone": self.phone,
            "email": self.email,
            "address": self.address
        }

    @classmethod
    def from_dict(cls, data: Dict) -> 'Supplier':
        return cls(
            supplier_id=data["supplier_id"],
            name=data["name"],
            contact_name=data["contact_name"],
            phone=data["phone"],
            email=data["email"],
            address=data["address"]
        )

class PurchaseOrder: # Represents a purchase order made to a supplier
    def __init__(self, po_id: str, supplier: Supplier, order_date: date, expected_delivery: date):
        self.po_id = po_id
        self.supplier = supplier
        self.order_date = order_date
        self.expected_delivery = expected_delivery
        self.status = OrderStatus.PENDING
        self.items: Dict[str, int] = {}  # item_ID -> quantity ordered

    def add_item(self, item_ID: str, quantity: int) -> None: # Ard or update the quantity of a product in this orde
        if item_ID in self.items:
            self.items[item_ID] += quantity
        else:
            self.items[item_ID] = quantity

    def update_status(self, new_status: OrderStatus) -> None: # Update the status of the purchase order
        self.status = new_status

    def __str__(self):
        return f"PO {self.po_id} to {self.supplier.name} on {self.order_date}, Status: {self.status.name}"
    
    def to_dict(self) -> Dict:
        return {
            "po_id": self.po_id,
            "supplier_id": self.supplier.supplier_id,
            "order_date": self.order_date.isoformat(),
            "expected_delivery": self.expected_delivery.isoformat(),
            "status": self.status.name,
            "items": self.items
        }

    @classmethod
    def from_dict(cls, data: Dict, supplier: Supplier) -> 'PurchaseOrder':
        order = cls(
            po_id=data["po_id"],
            supplier=supplier,
            order_date=date.fromisoformat(data["order_date"]),
            expected_delivery=date.fromisoformat(data["expected_delivery"])
        )
        order.status = OrderStatus[data["status"]]
        order.items = data["items"]
        return order


class SupplierManager:
    SUPPLIERS_FILE = "suppliers.json"
    PURCHASE_ORDERS_FILE = "purchase_orders.json"

    def __init__(self):
        self.suppliers: Dict[str, Supplier] = {}
        self.purchase_orders: Dict[str, PurchaseOrder] = {}
        self.load_suppliers()
        self.load_purchase_orders()

    def save_suppliers(self):
        save_data(list(self.suppliers.values()), self.SUPPLIERS_FILE, lambda s: s.to_dict())

    def load_suppliers(self):
        loaded_suppliers = load_data(self.SUPPLIERS_FILE, Supplier.from_dict)
        self.suppliers = {s.supplier_id: s for s in loaded_suppliers}

    def save_purchase_orders(self):
        save_data(list(self.purchase_orders.values()), self.PURCHASE_ORDERS_FILE, lambda po: po.to_dict())

    def load_purchase_orders(self):
        loaded_orders_data = load_data(self.PURCHASE_ORDERS_FILE, lambda d: d)  # just raw dicts
        for order_data in loaded_orders_data:
            supplier_id = order_data["supplier_id"]
            supplier = self.suppliers.get(supplier_id)
            if supplier:
                po = PurchaseOrder.from_dict(order_data, supplier)
                self.purchase_orders[po.po_id] = po
                # Also add order to supplier's history if not already there
                if po not in supplier.order_history:
                    supplier.order_history.append(po)

    def add_supplier(self, supplier: Supplier) -> bool:
        if supplier.supplier_id in self.suppliers:
            return False
        self.suppliers[supplier.supplier_id] = supplier
        self.save_suppliers()
        return True

    def update_supplier(self, supplier_id: str, **kwargs) -> bool:
        supplier = self.suppliers.get(supplier_id)
        if not supplier:
            return False
        for key, value in kwargs.items():
            if hasattr(supplier, key):
                setattr(supplier, key, value)
        self.save_suppliers()
        return True

    def delete_supplier(self, supplier_id: str) -> bool:
        if supplier_id in self.suppliers:
            del self.suppliers[supplier_id]
            self.save_suppliers()
            return True
        return False

    def create_purchase_order(self, po_id: str, supplier_id: str, order_date: date, expected_delivery: date) -> Optional[PurchaseOrder]:
        if po_id in self.purchase_orders or supplier_id not in self.suppliers:
            return None
        supplier = self.suppliers[supplier_id]
        po = PurchaseOrder(po_id, supplier, order_date, expected_delivery)
        self.purchase_orders[po_id] = po
        supplier.add_order(po)
        self.save_purchase_orders()
        self.save_suppliers()  # Save suppliers too because order history changed
        return po

    def get_supplier(self, supplier_id: str) -> Optional[Supplier]:  # Get supplier by ID
        return self.suppliers.get(supplier_id)

    def get_purchase_order(self, po_id: str) -> Optional[PurchaseOrder]: # Get purchase order by ID
        return self.purchase_orders.get(po_id)

    def list_suppliers(self) -> List[Supplier]: # Return all suppliers
        return list(self.suppliers.values())

    def list_purchase_orders(self) -> List[PurchaseOrder]: # Return all purchase orders
        return list(self.purchase_orders.values())