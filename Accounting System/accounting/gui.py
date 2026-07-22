from __future__ import annotations

import tkinter as tk
from tkinter import messagebox, ttk
from datetime import date
import uuid

from .models import Ledger, Transaction, TransactionItem, normalize_date, parse_decimal
from .storage import load_ledger, save_ledger


class AccountingApp(ttk.Frame):
    def __init__(self, master: tk.Tk) -> None:
        super().__init__(master, padding=10)
        master.title("会計システム")
        master.rowconfigure(0, weight=1)
        master.columnconfigure(0, weight=1)
        self.grid(sticky="nsew")

        self.ledger_file_var = tk.StringVar(value="ledger.json")
        self.date_var = tk.StringVar(value=date.today().isoformat())
        self.description_var = tk.StringVar()
        self.debit_account_var = tk.StringVar()
        self.debit_amount_var = tk.StringVar()
        self.credit_account_var = tk.StringVar()
        self.credit_amount_var = tk.StringVar()

        self.ledger = Ledger()
        self.create_widgets()
        self.refresh_display()

    def create_widgets(self) -> None:
        file_frame = ttk.Frame(self)
        file_frame.grid(row=0, column=0, columnspan=2, sticky="ew", pady=(0, 10))
        file_frame.columnconfigure(1, weight=1)

        ttk.Label(file_frame, text="仕訳ファイル:").grid(row=0, column=0, sticky="w")
        ttk.Entry(file_frame, textvariable=self.ledger_file_var, width=40).grid(row=0, column=1, sticky="ew", padx=(5, 5))
        ttk.Button(file_frame, text="読み込み", command=self.load_ledger).grid(row=0, column=2)

        entry_frame = ttk.LabelFrame(self, text="仕訳を追加")
        entry_frame.grid(row=1, column=0, sticky="nsew", padx=(0, 10), pady=(0, 10))
        entry_frame.columnconfigure(1, weight=1)

        ttk.Label(entry_frame, text="日付:").grid(row=0, column=0, sticky="w", pady=2)
        ttk.Entry(entry_frame, textvariable=self.date_var).grid(row=0, column=1, sticky="ew", pady=2)

        ttk.Label(entry_frame, text="説明:").grid(row=1, column=0, sticky="w", pady=2)
        ttk.Entry(entry_frame, textvariable=self.description_var).grid(row=1, column=1, sticky="ew", pady=2)

        ttk.Label(entry_frame, text="借方科目:").grid(row=2, column=0, sticky="w", pady=2)
        ttk.Entry(entry_frame, textvariable=self.debit_account_var).grid(row=2, column=1, sticky="ew", pady=2)

        ttk.Label(entry_frame, text="借方金額:").grid(row=3, column=0, sticky="w", pady=2)
        ttk.Entry(entry_frame, textvariable=self.debit_amount_var).grid(row=3, column=1, sticky="ew", pady=2)

        ttk.Label(entry_frame, text="貸方科目:").grid(row=4, column=0, sticky="w", pady=2)
        ttk.Entry(entry_frame, textvariable=self.credit_account_var).grid(row=4, column=1, sticky="ew", pady=2)

        ttk.Label(entry_frame, text="貸方金額:").grid(row=5, column=0, sticky="w", pady=2)
        ttk.Entry(entry_frame, textvariable=self.credit_amount_var).grid(row=5, column=1, sticky="ew", pady=2)

        ttk.Button(entry_frame, text="追加", command=self.add_transaction).grid(row=6, column=0, columnspan=2, pady=(10, 0))

        self.transaction_text = tk.Text(self, width=60, height=16, wrap="none")
        self.transaction_text.grid(row=1, column=1, sticky="nsew", pady=(0, 10))
        self.transaction_text.configure(state="disabled")

        balance_frame = ttk.LabelFrame(self, text="残高")
        balance_frame.grid(row=2, column=0, columnspan=2, sticky="nsew")
        balance_frame.columnconfigure(0, weight=1)

        self.balance_text = tk.Text(balance_frame, width=80, height=10, wrap="none")
        self.balance_text.grid(row=0, column=0, sticky="nsew")
        self.balance_text.configure(state="disabled")

    def load_ledger(self) -> None:
        try:
            self.ledger = load_ledger(self.ledger_file_var.get())
            self.refresh_display()
        except Exception as exc:
            messagebox.showerror("読み込みエラー", str(exc))

    def refresh_display(self) -> None:
        self.transaction_text.configure(state="normal")
        self.transaction_text.delete("1.0", tk.END)
        if not self.ledger.transactions:
            self.transaction_text.insert(tk.END, "仕訳がありません。\n")
        else:
            for transaction in sorted(self.ledger.transactions, key=lambda tx: tx.date):
                self.transaction_text.insert(tk.END, f"ID: {transaction.id}\n")
                self.transaction_text.insert(tk.END, f"日付: {transaction.date}\n")
                self.transaction_text.insert(tk.END, f"説明: {transaction.description}\n")
                for entry in transaction.entries:
                    self.transaction_text.insert(tk.END, f"  {entry.account}: {entry.amount:+.2f}\n")
                self.transaction_text.insert(tk.END, "-\n")
        self.transaction_text.configure(state="disabled")
        self.update_balance_text()

    def update_balance_text(self) -> None:
        balances = self.ledger.balance_by_account()
        self.balance_text.configure(state="normal")
        self.balance_text.delete("1.0", tk.END)
        if not balances:
            self.balance_text.insert(tk.END, "残高データがありません。\n")
        else:
            for account, amount in sorted(balances.items()):
                self.balance_text.insert(tk.END, f"{account}: {amount:.2f}\n")
        self.balance_text.configure(state="disabled")

    def add_transaction(self) -> None:
        try:
            transaction = Transaction(
                id=str(uuid.uuid4()),
                date=normalize_date(self.date_var.get()),
                description=self.description_var.get().strip(),
                entries=[
                    TransactionItem(account=self.debit_account_var.get().strip(), amount=parse_decimal(self.debit_amount_var.get())),
                    TransactionItem(account=self.credit_account_var.get().strip(), amount=-parse_decimal(self.credit_amount_var.get())),
                ],
            )
            if not transaction.description:
                raise ValueError("説明を入力してください。")
            if not transaction.entries[0].account or not transaction.entries[1].account:
                raise ValueError("勘定科目を入力してください。")
            self.ledger.add_transaction(transaction)
            save_ledger(self.ledger, self.ledger_file_var.get())
            messagebox.showinfo("保存", "仕訳を保存しました。")
            self.refresh_display()
            self.description_var.set("")
            self.debit_account_var.set("")
            self.debit_amount_var.set("")
            self.credit_account_var.set("")
            self.credit_amount_var.set("")
        except Exception as exc:
            messagebox.showerror("エラー", str(exc))


def run_gui() -> None:
    root = tk.Tk()
    root.geometry("900x700")
    AccountingApp(root)
    root.mainloop()
