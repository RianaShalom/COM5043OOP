import unittest, sys, os
from datetime import datetime
from Backend.order import Order, PurchaseOrder, SalesOrder

class TestOrderBase(unittest.TestCase):
    def setUp(self):
        self.order_id = "ORD001"
        self.date = datetime(2025, 1, 15)
        self.items = {"itemA": 3, "itemB": 2}
        self.total_cost = 150.00

    def test_purchase_order_properties(self):
        po = PurchaseOrder(self.order_id, self.date, self.items, self.total_cost, "SUP123")
        self.assertEqual(po.order_id, self.order_id)
        self.assertEqual(po.date, self.date)
        self.assertEqual(po.items, self.items)
        self.assertEqual(po.total_cost, self.total_cost)
        self.assertEqual(po.supplier_id, "SUP123")
        self.assertEqual(po.order_type(), "Purchase")
        self.assertIn("Purchase Order", str(po))
        self.assertIn("Supplier ID: SUP123", str(po))
        print("test - test_purchase_order_properties: successful")

    def test_sales_order_properties(self): # Testing the oder has all necessary properties
        so = SalesOrder(self.order_id, self.date, self.items, self.total_cost, "Alice")
        self.assertEqual(so.order_id, self.order_id)
        self.assertEqual(so.date, self.date)
        self.assertEqual(so.items, self.items)
        self.assertEqual(so.total_cost, self.total_cost)
        self.assertEqual(so.customer_name, "Alice")
        self.assertEqual(so.order_type(), "Sales")
        self.assertIn("Sales Order", str(so))
        self.assertIn("Customer: Alice", str(so))
        print("test - test_sales_order_properties: successful")

    def test_order_abstract_instantiation(self): # Testing you cannot instantiate Order directly
        with self.assertRaises(TypeError):
            Order(self.order_id, self.date, self.items, self.total_cost)
        print("test - test_order_abstract_instantiation: successful")

if __name__ == "__main__":
    unittest.main()