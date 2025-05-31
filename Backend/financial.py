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

