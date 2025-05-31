import sys
import unittest
from unittest.mock import patch, MagicMock
sys.modules['data_storage'] = MagicMock() # Mock 'data_storage' module will prevent ImportError during testing, and allows for mock injections
from Backend.inventory import Product, InventoryManager

class TestProduct(unittest.TestCase): 
    def test_is_low_stock_true(self): # Test is_low_stock returns True when quantity <= threshold
        p = Product("item_ID1", "Widget", 10.0, 5, low_stock_threshold=10)
        self.assertTrue(p.is_low_stock())

    def test_is_low_stock_false(self): # Test is_low_stock returns False when quantity > threshold
        p = Product("item_ID2", "Gadget", 10.0, 15, low_stock_threshold=10)
        self.assertFalse(p.is_low_stock())

    def test_to_dict_and_from_dict(self): # Testing serialisation and deserialisation to ensure no attributes are lost or changed
        """."""
        original = Product("item_ID3", "Thing", 12.5, 7, low_stock_threshold=3)
        data = original.to_dict()
        recreated = Product.from_dict(data)
        self.assertEqual(original.item_ID, recreated.item_ID)
        self.assertEqual(original.name, recreated.name)
        self.assertEqual(original.price, recreated.price)
        self.assertEqual(original.quantity, recreated.quantity)
        self.assertEqual(original.low_stock_threshold, recreated.low_stock_threshold)

class TestInventoryManager(unittest.TestCase):
    def setUp(self): # Patch load_data and save_data to only affect mock files (this won't affect the actual data when running tests - very important!)
        patcher_load = patch('Backend.inventory.load_data')
        patcher_save = patch('Backend.inventory.save_data')
        self.mock_load = patcher_load.start()
        self.mock_save = patcher_save.start()
        self.addCleanup(patcher_load.stop)
        self.addCleanup(patcher_save.stop)

        self.mock_load.return_value = [] # Brand new mock env
        self.inv = InventoryManager()

    def test_load_products_called_on_init(self): # Test load_products calls load_data and sets products dict
        self.mock_load.assert_called_once_with(InventoryManager.DATA_FILENAME, Product.from_dict)
        self.assertEqual(self.inv.products, {})

    def test_add_product_success(self): # Add a new product successfully and check save
        product = Product("item_ID5", "New Product", 20.0, 30)
        result = self.inv.add_product(product)
        self.assertTrue(result)
        self.assertIn(product.item_ID, self.inv.products)
        self.mock_save.assert_called_once()

    def test_add_product_duplicate_fails(self): # Adding a product with existing item_ID to ensure this doesn't save or overwrite
        product = Product("item_ID6", "Existing", 15.0, 10)
        self.inv.products[product.item_ID] = product
        result = self.inv.add_product(product)
        self.assertFalse(result)
        # save_products should NOT be called again after duplicate add attempt
        self.mock_save.assert_not_called()

    def test_remove_product_success(self): # Remove an existing product by item_ID and check save
        product = Product("item_ID7", "To Remove", 5.0, 12)
        self.inv.products[product.item_ID] = product
        result = self.inv.remove_product(product.item_ID)
        self.assertTrue(result)
        self.assertNotIn(product.item_ID, self.inv.products)
        self.mock_save.assert_called_once()

    def test_update_stock_success(self): # Testing to update stock quantity
        product = Product("item_ID8", "Stock Update", 7.0, 10)
        self.inv.products[product.item_ID] = product

        result_inc = self.inv.update_stock(product.item_ID, 5)
        self.assertTrue(result_inc)
        self.assertEqual(self.inv.products[product.item_ID].quantity, 15)

        result_dec = self.inv.update_stock(product.item_ID, -3)
        self.assertTrue(result_dec)
        self.assertEqual(self.inv.products[product.item_ID].quantity, 12)

        self.assertEqual(self.mock_save.call_count, 2)

    def test_update_stock_nonexistent_product(self): # Updating stock for a non-existent product returns False
        result = self.inv.update_stock("missing_item_ID", 5)
        self.assertFalse(result)
        self.mock_save.assert_not_called()

    def test_get_product(self): # Retrieve a product by item_ID, returns None if missing
        product = Product("item_ID10", "Get Product", 8.0, 9)
        self.inv.products[product.item_ID] = product
        found = self.inv.get_product(product.item_ID)
        self.assertEqual(found, product)

        missing = self.inv.get_product("no_item_ID")
        self.assertIsNone(missing)

    def test_list_low_stock_products(self): # List only products that are low stock
        products = [
            Product("item_ID13", "LowStock1", 1.0, 3, low_stock_threshold=5),
            Product("item_ID14", "OkStock", 2.0, 10, low_stock_threshold=5),
            Product("item_ID15", "LowStock2", 3.0, 5, low_stock_threshold=5),
        ]
        for p in products:
            self.inv.products[p.item_ID] = p

        low_stock = self.inv.list_low_stock_products() # This should only contain item_ID13 and item_ID15
        expected = [products[0], products[2]]
        self.assertCountEqual(low_stock, expected)

if __name__ == '__main__':
    unittest.main()