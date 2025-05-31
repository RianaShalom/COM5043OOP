from typing import List
from datetime import datetime

class Transaction: # All transactions come through here, defined as either sales or purchases
    def __init__(self, transaction_type: str, amount: float, description: str):
        self.date = datetime.now()
        self.transaction_type = transaction_type  # Being either 'purchase' or 'sale'
        self.amount = amount
        self.description = description

    def __str__(self):
        return f"[{self.date.strftime('%Y-%m-%d %H:%M')}] {self.transaction_type.upper()} - £{self.amount:.2f} - {self.description}"
    
    def to_dict(self):
        return {
            "date": self.date.isoformat(),
            "transaction_type": self.transaction_type,
            "amount": self.amount,
            "description": self.description
        }

    @classmethod # Reading from the saved data
    def from_dict(cls, data):
        obj = cls(
            transaction_type=data["transaction_type"],
            amount=data["amount"],
            description=data["description"]
        )
        obj.date = datetime.fromisoformat(data["date"])
        return obj

class FinancialManager: # Used for generating financial reports and logging purchases
    def __init__(self):
        self.transactions: List[Transaction] = []

    def record_purchase(self, amount: float, description: str): # Purchasing stock
        if amount <= 0:
            raise ValueError("Purchase amount must be positive.")
        self.transactions.append(Transaction("purchase", amount, description))

    def record_sale(self, amount: float, description: str): # Recording sale
        if amount <= 0:
            raise ValueError("Sale amount must be positive.")
        self.transactions.append(Transaction("sale", amount, description))

    def total_purchases(self) -> float: # Financial report total purchases calculated
        return sum(t.amount for t in self.transactions if t.transaction_type == "purchase")

    def total_sales(self) -> float: # Financial report total sales calculated
        return sum(t.amount for t in self.transactions if t.transaction_type == "sale")

    def net_income(self) -> float: # Financial report net income calculated (profit vs loss)
        return self.total_sales() - self.total_purchases()

    def generate_report(self) -> str:
        """Generate a summary report of finances."""
        report = "\n--- Financial Report ---\n"
        report += f"Total Sales: £{self.total_sales():.2f}\n"
        report += f"Total Purchases: £{self.total_purchases():.2f}\n"
        report += f"Net Income: £{self.net_income():.2f} {'(Profit)' if self.net_income() >= 0 else '(Loss)'}\n"
        report += "\nTransactions:\n"
        for t in self.transactions:
            report += str(t) + "\n"
        return report