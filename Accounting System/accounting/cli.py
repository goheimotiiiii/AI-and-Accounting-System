from __future__ import annotations

import argparse
import uuid
from datetime import date
from typing import Iterable, List

from .models import Ledger, Transaction, TransactionItem, normalize_date, parse_decimal
from .storage import load_ledger, save_ledger


def parse_entry(value: str) -> TransactionItem:
    if ":" not in value:
        raise argparse.ArgumentTypeError("エントリは 'Account:Amount' の形式で指定してください。")
    account, amount = value.split(":", 1)
    return TransactionItem(account=account.strip(), amount=parse_decimal(amount.strip()))


def format_money(amount: float) -> str:
    return f"{amount:,.2f}"


def print_transaction(transaction: Transaction) -> None:
    print(f"ID: {transaction.id}")
    print(f"日付: {transaction.date}")
    print(f"説明: {transaction.description}")
    for entry in transaction.entries:
        print(f"  {entry.account}: {entry.amount:+.2f}")
    print("-")


def add_command(args: argparse.Namespace) -> None:
    ledger = load_ledger(args.file)
    transaction = Transaction(
        id=str(uuid.uuid4()),
        date=normalize_date(args.date),
        description=args.description,
        entries=[parse_entry(entry) for entry in args.entry],
    )
    ledger.add_transaction(transaction)
    save_ledger(ledger, args.file)
    print("仕訳を保存しました。")


def list_command(args: argparse.Namespace) -> None:
    ledger = load_ledger(args.file)
    if not ledger.transactions:
        print("仕訳がありません。")
        return
    for transaction in sorted(ledger.transactions, key=lambda tx: tx.date):
        print_transaction(transaction)


def balance_command(args: argparse.Namespace) -> None:
    ledger = load_ledger(args.file)
    balances = ledger.balance_by_account()
    if args.account:
        amount = balances.get(args.account, 0)
        print(f"{args.account} の残高: {amount:.2f}")
        return
    for account, amount in sorted(balances.items()):
        print(f"{account}: {amount:.2f}")


def main() -> None:
    parent_parser = argparse.ArgumentParser(add_help=False)
    parent_parser.add_argument("--file", default="ledger.json", help="仕訳を保存するJSONファイル")

    parser = argparse.ArgumentParser(description="シンプルな会計システム")
    parser.add_argument("--file", default="ledger.json", help="仕訳を保存するJSONファイル")

    subparsers = parser.add_subparsers(dest="command", required=True)

    add_parser = subparsers.add_parser("add", parents=[parent_parser], help="仕訳を追加する")
    add_parser.add_argument("--date", required=True, help="取引日 (YYYY-MM-DD)")
    add_parser.add_argument("--description", required=True, help="取引の説明")
    add_parser.add_argument("--entry", required=True, action="append", help="仕訳のエントリ。例: Cash:100.00")

    list_parser = subparsers.add_parser("list", parents=[parent_parser], help="仕訳一覧を表示する")

    balance_parser = subparsers.add_parser("balance", parents=[parent_parser], help="残高を表示する")
    balance_parser.add_argument("--account", help="特定の勘定科目の残高を表示する")

    gui_parser = subparsers.add_parser("gui", parents=[parent_parser], help="GUIを起動する")

    args = parser.parse_args()
    if args.command == "add":
        add_command(args)
    elif args.command == "list":
        list_command(args)
    elif args.command == "balance":
        balance_command(args)
    elif args.command == "gui":
        from .gui import run_gui
        run_gui()
