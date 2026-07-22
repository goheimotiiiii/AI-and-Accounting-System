from __future__ import annotations

import json
from dataclasses import dataclass, field, asdict
from datetime import date, datetime
from decimal import Decimal, InvalidOperation
from typing import Any, Dict, List


def parse_decimal(value: str) -> Decimal:
    try:
        number = Decimal(value)
    except (InvalidOperation, ValueError) as exc:
        raise ValueError(f"無効な金額です: {value}") from exc
    return number.quantize(Decimal("0.01"))


@dataclass
class TransactionItem:
    account: str
    amount: Decimal
    memo: str = ""

    def to_dict(self) -> Dict[str, Any]:
        return {
            "account": self.account,
            "amount": str(self.amount),
            "memo": self.memo,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "TransactionItem":
        return cls(
            account=data["account"],
            amount=parse_decimal(str(data["amount"])),
            memo=data.get("memo", ""),
        )


@dataclass
class Transaction:
    id: str
    date: str
    description: str
    entries: List[TransactionItem] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "date": self.date,
            "description": self.description,
            "entries": [entry.to_dict() for entry in self.entries],
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Transaction":
        return cls(
            id=data["id"],
            date=data["date"],
            description=data["description"],
            entries=[TransactionItem.from_dict(entry) for entry in data.get("entries", [])],
        )


@dataclass
class Ledger:
    transactions: List[Transaction] = field(default_factory=list)

    def add_transaction(self, transaction: Transaction) -> None:
        total = sum(entry.amount for entry in transaction.entries)
        if total != Decimal("0.00"):
            raise ValueError("借方と貸方の合計が一致していません。")
        self.transactions.append(transaction)

    def balance_by_account(self) -> Dict[str, Decimal]:
        balances: Dict[str, Decimal] = {}
        for transaction in self.transactions:
            for entry in transaction.entries:
                balances.setdefault(entry.account, Decimal("0.00"))
                balances[entry.account] += entry.amount
        return balances

    def to_dict(self) -> Dict[str, Any]:
        return {
            "transactions": [transaction.to_dict() for transaction in self.transactions],
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Ledger":
        return cls(
            transactions=[Transaction.from_dict(item) for item in data.get("transactions", [])],
        )


def normalize_date(value: str) -> str:
    try:
        parsed = datetime.fromisoformat(value).date()
    except ValueError as exc:
        raise ValueError(f"無効な日付形式です: {value}") from exc
    return parsed.isoformat()
