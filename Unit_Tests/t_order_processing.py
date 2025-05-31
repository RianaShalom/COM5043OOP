import sys
import unittest
from unittest.mock import MagicMock, patch
from datetime import date

sys.modules['data_storage'] = MagicMock() # Mock data_storage module and mock inventory-manager so inventory import works
mock_inventory_manager_class = MagicMock()
sys.modules['inventory'] = MagicMock(InventoryManager=mock_inventory_manager_class)

from Backend.order_processing import Customer, CustomerOrder, OrderProcessor

class TestCustomer(unittest.TestCase):
    def test_customer_to_dict_and_from_dict(self): # Testing serialisation and deserialisation to ensure no attributes are lost or changed
        c = Customer("cust123", "John Doe", "john@example.com", "1234567890")
        data = c.to_dict()
        c2 = Customer.from_dict(data)
        self.assertEqual(c.customer_id, c2.customer_id)
        self.assertEqual(c.name, c2.name)
        self.assertEqual(c.email, c2.email)
        self.assertEqual(c.phone, c2.phone)

    def test_customer_str(self): # Test representation of Customer
        c = Customer("cust123", "John Doe", "john@example.com", "1234567890")
        s = str(c)
        self.assertIn("John Doe", s)
        self.assertIn("john@example.com", s)

class TestCustomerOrder(unittest.TestCase):
    def setUp(self):
        self.customer = Customer("cust1", "Jane Smith", "jane@example.com", "0987654321")
        self.order = CustomerOrder("order1", self.customer, date(2025, 5, 30))

    def test_add_item_accumulates_quantity_and_price(self): # Adding items updates quantities and total price
        self.order.add_item("item_ID1", 2, 5.0)
        self.assertEqual(self.order.items["item_ID1"], 2)
        self.assertEqual(self.order.total_price, 10.0)

        self.order.add_item("item_ID1", 3, 5.0)
        self.assertEqual(self.order.items["item_ID1"], 5)
        self.assertEqual(self.order.total_price, 25.0)

    def test_order_to_dict_and_from_dict(self): # Testing serialisation and deserialisation to ensure no attributes are lost or changed
        self.order.add_item("item_ID1", 2, 5.0)
        data = self.order.to_dict()

        order2 = CustomerOrder.from_dict(data, self.customer)
        self.assertEqual(order2.order_id, self.order.order_id)
        self.assertEqual(order2.customer, self.customer)
        self.assertEqual(order2.order_date, self.order.order_date)
        self.assertEqual(order2.items, self.order.items)
        self.assertEqual(order2.total_price, self.order.total_price)

class TestOrderProcessor(unittest.TestCase):
    def setUp(self):
        self.mock_inventory_manager = MagicMock() # Create a MagicMock InventoryManager instance with required methods to isolate and inject for testing purposes
        self.processor = OrderProcessor(self.mock_inventory_manager)

        self.customer = Customer("cust123", "John Customer", "cust@example.com", "555-1234") # Adds a sample customer for order tests
        self.processor.add_customer(self.customer)

    def test_add_customer_success(self): # Test adding a new customer succeeds
        new_customer = Customer("cust456", "New Customer", "new@example.com", "555-6789")
        result = self.processor.add_customer(new_customer)
        self.assertTrue(result)
        self.assertIn(new_customer.customer_id, self.processor.customers)

    def test_create_order_successful_stock_deduction(self): # Test creating an order when stock is sufficient
        items = {"item_ID1": 2, "item_ID2": 3}
        product1 = MagicMock(quantity=5, price=10.0)# Setup mock inventory products with sufficient stock and prices
        product2 = MagicMock(quantity=10, price=20.0)

        def get_product_side_effect(item_ID):
            return product1 if item_ID == "item_ID1" else product2 if item_ID == "item_ID2" else None

        self.mock_inventory_manager.get_product.side_effect = get_product_side_effect # Calls inventory_manager.get_product for each item_ID
        self.mock_inventory_manager.update_stock.return_value = True # Calls update_stock to deduct quantities

        result = self.processor.create_order("order1", self.customer.customer_id, date.today(), items)
        self.assertTrue(result)
        self.assertIn("order1", self.processor.orders)

        expected_calls = [unittest.mock.call("item_ID1"), unittest.mock.call("item_ID2")] # Check calls to get_product
        self.mock_inventory_manager.get_product.assert_has_calls(expected_calls, any_order=True)

        self.mock_inventory_manager.update_stock.assert_any_call("item_ID1", -2) # Check calls to update_stock with negative quantity
        self.mock_inventory_manager.update_stock.assert_any_call("item_ID2", -3)

    def test_create_order_insufficient_stock_fails(self): # Test creating order fails if any product has insufficient stock
        items = {"item_ID1": 2, "item_ID2": 3}

        product1 = MagicMock(quantity=1, price=10.0) # Insufficient quantity for item_ID1
        product2 = MagicMock(quantity=10, price=20.0)

        def get_product_side_effect(item_ID):
            return product1 if item_ID == "item_ID1" else product2 if item_ID == "item_ID2" else None

        self.mock_inventory_manager.get_product.side_effect = get_product_side_effect

        result = self.processor.create_order("order2", self.customer.customer_id, date.today(), items)
        self.assertFalse(result)
        self.assertNotIn("order2", self.processor.orders)
        self.mock_inventory_manager.update_stock.assert_not_called()

    def test_get_order_and_list_orders(self): # Test retrieving a specific order and listing all orders
        order = CustomerOrder("order1", self.customer, date.today())
        self.processor.orders[order.order_id] = order

        retrieved = self.processor.get_order(order.order_id)
        self.assertEqual(retrieved, order)

        all_orders = self.processor.list_orders()
        self.assertIn(order, all_orders)

if __name__ == "__main__":
    unittest.main()