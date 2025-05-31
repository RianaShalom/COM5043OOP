# inventory.py

from typing import Dict, List
from data_storage import save_data, load_data

class Product: # Representing a product in the WMSBNUIS LTD warehouse
    def __init__(self, item_ID: str, name: str, price: float, quantity: int, low_stock_threshold: int = 10):
        self.item_ID = item_ID  # Stock Keeping Unit, unique ID
        self.name = name
        self.price = price
        self.quantity = quantity
        self.low_stock_threshold = low_stock_threshold

    def is_low_stock(self) -> bool: # Check if the product is below the low stock threshold
        return self.quantity <= self.low_stock_threshold

    def __str__(self):
        status = "LOW STOCK!" if self.is_low_stock() else "In Stock"
        return f"{self.name} (item_ID: {self.item_ID}) - Qty: {self.quantity} - {status}"
    
    def to_dict(self) -> dict: # Serialise product to dictionary
        return {
            "item_ID": self.item_ID,
            "name": self.name,
            "price": self.price,
            "quantity": self.quantity,
            "low_stock_threshold": self.low_stock_threshold
        }

    @classmethod
    def from_dict(cls, data: dict):
        """Deserialize product from dictionary."""
        return cls(
            item_ID=data["item_ID"],
            name=data["name"],
            price=data["price"],
            quantity=data["quantity"],
            low_stock_threshold=data.get("low_stock_threshold", 10)
        )

class InventoryManager: # Manages all product stock in the warehouse, with persistent storage in the /Data/ folder
    DATA_FILENAME = "products.json"

    def __init__(self):
        self.products: Dict[str, Product] = {}
        self.load_products()

    def load_products(self): # Load products from JSON file into memory
        loaded_products = load_data(self.DATA_FILENAME, Product.from_dict)
        self.products = {p.item_ID: p for p in loaded_products}

    def save_products(self): # Save current products to JSON file
        save_data(list(self.products.values()), self.DATA_FILENAME, lambda p: p.to_dict())

    def add_product(self, product: Product) -> bool: # Adding a product and saving it
        if product.item_ID in self.products:
            return False
        self.products[product.item_ID] = product
        self.save_products()
        return True

    def remove_product(self, item_ID: str) -> bool: # Removing a product and saving it
        if item_ID not in self.products:
            return False
        del self.products[item_ID]
        self.save_products()
        return True

    def update_stock(self, item_ID: str, quantity_change: int) -> bool: # UPdating a product and saving it
        product = self.products.get(item_ID)
        if not product or product.quantity + quantity_change < 0:
            return False
        product.quantity += quantity_change
        self.save_products()
        return True

    def get_product(self, item_ID: str) -> Product: # Fetching product by ID provided
        return self.products.get(item_ID)

    def list_low_stock_products(self) -> List[Product]: # List low stock products variant on threshhold
        return [product for product in self.products.values() if product.is_low_stock()]