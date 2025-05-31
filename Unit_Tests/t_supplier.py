import sys
import unittest
from unittest.mock import patch, MagicMock
from datetime import date

sys.modules['data_storage'] = MagicMock() # Mock data_storage before importing supplier module

from Backend.supplier import Supplier, PurchaseOrder, SupplierManager, OrderStatus

class TestSupplier(unittest.TestCase):
    def test_str_and_to_dict(self): # Testing serialisation and deserialisation to ensure no attributes are lost or changed
        s = Supplier("sup1", "Supplier Inc", "Alice", "1234567890", "alice@example.com", "123 Street")
        self.assertIn("Supplier Inc", str(s))
        d = s.to_dict()
        self.assertEqual(d["supplier_id"], "sup1")
        self.assertEqual(d["name"], "Supplier Inc")

    def test_from_dict(self):  # Testing deserialisation to ensure no attributes are lost or changed
        data = {
            "supplier_id": "sup2",
            "name": "Best Supplier",
            "contact_name": "Bob",
            "phone": "0987654321",
            "email": "bob@example.com",
            "address": "456 Avenue"
        }
        s = Supplier.from_dict(data)
        self.assertEqual(s.supplier_id, "sup2")
        self.assertEqual(s.contact_name, "Bob")

    def test_add_order(self): # Test adding a purchase order to supplier's history
        supplier = Supplier("sup3", "Supplier", "Eve", "5555555555", "eve@example.com", "789 Blvd")
        po = MagicMock()
        supplier.add_order(po)
        self.assertIn(po, supplier.order_history)

class TestPurchaseOrder(unittest.TestCase):
    def setUp(self):
        self.supplier = Supplier("sup4", "Supplier4", "Dan", "2223334444", "dan@example.com", "101 Road")
        self.po = PurchaseOrder("po1", self.supplier, date(2024, 1, 1), date(2024, 1, 15))

    def test_add_item(self): # Add or update items in purchase order
        self.po.add_item("item_ID1", 5)
        self.assertEqual(self.po.items["item_ID1"], 5)
        self.po.add_item("item_ID1", 3)
        self.assertEqual(self.po.items["item_ID1"], 8)

    def test_update_status(self): # Update the status of the purchase order
        self.po.update_status(OrderStatus.DELIVERED)
        self.assertEqual(self.po.status, OrderStatus.DELIVERED)

    def test_str_and_to_dict(self): # Test representation and serialisation
        self.po.add_item("item_ID2", 2)
        s = str(self.po)
        self.assertIn("PO po1", s)
        d = self.po.to_dict()
        self.assertEqual(d["po_id"], "po1")
        self.assertEqual(d["supplier_id"], self.supplier.supplier_id)
        self.assertEqual(d["status"], self.po.status.name)
        self.assertEqual(d["items"]["item_ID2"], 2)

class TestSupplierManager(unittest.TestCase):
    def setUp(self):
        patcher_load = patch('Backend.supplier.load_data')
        patcher_save = patch('Backend.supplier.save_data')
        self.mock_load = patcher_load.start()
        self.mock_save = patcher_save.start()
        self.addCleanup(patcher_load.stop)
        self.addCleanup(patcher_save.stop)

        # Default mocks to return empty lists (no saved data)
        self.mock_load.side_effect = [[], []]  # suppliers, purchase orders

        self.manager = SupplierManager()

    def test_load_called_on_init(self): # Verify load_data called twice on initialisation
        self.assertEqual(self.mock_load.call_count, 2)
        self.assertEqual(self.manager.suppliers, {})
        self.assertEqual(self.manager.purchase_orders, {})

    def test_add_supplier_success(self): # Testiong to add supplier successfully and check save called
        supplier = Supplier("sup5", "New Supplier", "Cathy", "1231231234", "cathy@example.com", "12 Lane")
        result = self.manager.add_supplier(supplier)
        self.assertTrue(result)
        self.assertIn(supplier.supplier_id, self.manager.suppliers)
        self.mock_save.assert_called_once()

    def test_add_supplier_duplicate_fails(self): # Testing to add supplier with existing ID returns False - no dupes
        supplier = Supplier("sup6", "Dup Supplier", "Dan", "1112223333", "dan@example.com", "34 Blvd")
        self.manager.suppliers[supplier.supplier_id] = supplier
        result = self.manager.add_supplier(supplier)
        self.assertFalse(result)
        self.mock_save.assert_not_called()

    def test_update_supplier_success(self): # Testing to update supplier attributes and save
        supplier = Supplier("sup7", "Old Name", "Eve", "9998887777", "eve@example.com", "56 Road")
        self.manager.suppliers[supplier.supplier_id] = supplier
        result = self.manager.update_supplier(supplier.supplier_id, name="New Name", phone="0001112222")
        self.assertTrue(result)
        self.assertEqual(supplier.name, "New Name")
        self.assertEqual(supplier.phone, "0001112222")
        self.mock_save.assert_called_once()

    def test_delete_supplier_success(self): # Delete existing supplier
        supplier = Supplier("sup8", "DeleteMe", "Fay", "5555555555", "fay@example.com", "789 Lane")
        self.manager.suppliers[supplier.supplier_id] = supplier
        result = self.manager.delete_supplier(supplier.supplier_id)
        self.assertTrue(result)
        self.assertNotIn(supplier.supplier_id, self.manager.suppliers)
        self.mock_save.assert_called_once()

    def test_delete_supplier_fail(self): # Deleting non-existent supplier returns False
        result = self.manager.delete_supplier("no_id")
        self.assertFalse(result)
        self.mock_save.assert_not_called()

    def test_create_purchase_order_success(self): # Create a new purchase order and verify it is linked to supplier
        supplier = Supplier("sup9", "PO Supplier", "Greg", "7777777777", "greg@example.com", "1010 Road")
        self.manager.suppliers[supplier.supplier_id] = supplier
        po = self.manager.create_purchase_order("po100", supplier.supplier_id, date(2024, 3, 1), date(2024, 3, 15))
        self.assertIsNotNone(po)
        self.assertEqual(po.po_id, "po100")
        self.assertIn(po.po_id, self.manager.purchase_orders)
        self.assertIn(po, supplier.order_history)
        self.assertEqual(self.mock_save.call_count, 2)  # purchase orders + suppliers saved

    def test_get_supplier_and_purchase_order(self): # Retrieve supplier and purchase order by id
        supplier = Supplier("sup11", "Supplier11", "Ivy", "6666666666", "ivy@example.com", "1414 Way")
        po = PurchaseOrder("po400", supplier, date.today(), date.today())
        self.manager.suppliers[supplier.supplier_id] = supplier
        self.manager.purchase_orders[po.po_id] = po

        self.assertEqual(self.manager.get_supplier(supplier.supplier_id), supplier)
        self.assertEqual(self.manager.get_purchase_order(po.po_id), po)

        self.assertIsNone(self.manager.get_supplier("no_id"))
        self.assertIsNone(self.manager.get_purchase_order("no_po"))

if __name__ == "__main__":
    unittest.main()