import unittest, time
from datetime import datetime
from Backend.financial import Transaction, FinancialManager

class TestTransaction(unittest.TestCase):
    def test_transaction_creation(self): # Testing the creation of transaction objects
        t = Transaction("sale", 100.0, "Test sale")
        self.assertEqual(t.transaction_type, "sale")
        self.assertEqual(t.amount, 100.0)
        self.assertEqual(t.description, "Test sale")
        self.assertIsInstance(t.date, datetime)
    
    def test_transaction_str_format(self): # Testong the transaction has all relevant fields of detail
        t = Transaction("purchase", 50.5, "Test purchase")
        s = str(t)
        self.assertIn("PURCHASE", s)
        self.assertIn("£50.50", s)
        self.assertIn("Test purchase", s)
        self.assertRegex(s, r"\[\d{4}-\d{2}-\d{2} \d{2}:\d{2}\] PURCHASE - £50\.50 - Test purchase")

    def test_to_dict_and_from_dict(self): # Testing serialisation and deserialisation to ensure no attributes are lost or changed
        t1 = Transaction("sale", 75.0, "Dict test")
        d = t1.to_dict()
        t2 = Transaction.from_dict(d)
        self.assertEqual(t1.transaction_type, t2.transaction_type)
        self.assertEqual(t1.amount, t2.amount)
        self.assertEqual(t1.description, t2.description)
        self.assertEqual(t1.date, t2.date)

class TestFinancialManager(unittest.TestCase):
    def setUp(self):
        self.fm = FinancialManager() # Initialising FinancialManager for the testing

    def test_record_purchase_and_sale(self): # Testing recording purchases and sales adds correct transactions
        self.fm.record_purchase(100.0, "Bought stock")
        self.fm.record_sale(150.0, "Sold item")
        self.assertEqual(len(self.fm.transactions), 2)
        self.assertEqual(self.fm.transactions[0].transaction_type, "purchase")
        self.assertEqual(self.fm.transactions[1].transaction_type, "sale")

    def test_record_purchase_invalid_amount(self): # Testing user input/edge cases of non-positive value
        with self.assertRaises(ValueError):
            self.fm.record_purchase(0, "Zero amount")
        with self.assertRaises(ValueError):
            self.fm.record_purchase(-10, "Negative amount")

    def test_record_sale_invalid_amount(self): # Testing sale records input/edge cases of non-positive value
        with self.assertRaises(ValueError):
            self.fm.record_sale(0, "Zero sale")
        with self.assertRaises(ValueError):
            self.fm.record_sale(-5, "Negative sale")

    def test_total_purchases_and_sales(self): # Testing sales calculator by injecting purchases and values
        self.fm.record_purchase(100.0, "Stock A")
        self.fm.record_purchase(200.0, "Stock B")
        self.fm.record_sale(500.0, "Sale A")
        self.fm.record_sale(300.0, "Sale B")
        self.assertEqual(self.fm.total_purchases(), 300.0)
        self.assertEqual(self.fm.total_sales(), 800.0)

    def test_generate_report_content(self): # Test that the generated report string contains key summary info and transaction details
        self.fm.record_purchase(100.0, "Purchase 1")
        self.fm.record_sale(150.0, "Sale 1")
        report = self.fm.generate_report()
        self.assertIn("Total Sales: £150.00", report)
        self.assertIn("Total Purchases: £100.00", report)
        self.assertIn("Net Income: £50.00 (Profit)", report)
        self.assertIn("PURCHASE", report)
        self.assertIn("SALE", report)
        self.assertIn("Purchase 1", report)
        self.assertIn("Sale 1", report)

if __name__ == "__main__":
    unittest.main()