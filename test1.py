from PyQt5.QtWidgets import (
    QApplication,
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QDateEdit,
    QComboBox,
    QPushButton,
    QTableWidget,
    QTableWidgetItem,
    QFileDialog,
    QDialog,
    QHeaderView,
    QMessageBox,
    QTabWidget
)
from PyQt5.QtCore import QDate, Qt, QSettings
from PyQt5.QtGui import QIcon
import pandas as pd
import sys


class EditTransactionDialog(QDialog):
    def __init__(self, row):
        super().__init__()
        self.setWindowTitle("Edit Transaction")
        self.layout = QVBoxLayout()

        self.date_edit = QDateEdit()
        self.date_edit.setDate(QDate.fromString(row["Date"], "yyyy-MM-dd"))
        self.type_combo = QComboBox()
        self.type_combo.addItems(["Income", "Expense"])
        self.type_combo.setCurrentText(row["Type"])
        self.account_combo = QComboBox()
        self.account_combo.addItems(["Checking", "Savings", "Credit Card"])
        self.account_combo.setCurrentText(row["Account"])
        self.amount_edit = QLineEdit(str(row["Amount"]))
        self.source_category_edit = QLineEdit(row["Source/Category"])
        self.notes_edit = QLineEdit(row["Notes"])
        self.save_button = QPushButton("Save")
        self.save_button.clicked.connect(self.accept)

        self.layout.addWidget(QLabel("Date:"))
        self.layout.addWidget(self.date_edit)
        self.layout.addWidget(QLabel("Type:"))
        self.layout.addWidget(self.type_combo)
        self.layout.addWidget(QLabel("Account:"))
        self.layout.addWidget(self.account_combo)
        self.layout.addWidget(QLabel("Amount:"))
        self.layout.addWidget(self.amount_edit)
        self.layout.addWidget(QLabel("Source/Category:"))
        self.layout.addWidget(self.source_category_edit)
        self.layout.addWidget(QLabel("Notes:"))
        self.layout.addWidget(self.notes_edit)
        self.layout.addWidget(self.save_button)

        self.setLayout(self.layout)

    def get_updated_data(self):
        return {
            "Date": self.date_edit.date().toString("yyyy-MM-dd"),
            "Type": self.type_combo.currentText(),
            "Account": self.account_combo.currentText(),
            "Amount": float(self.amount_edit.text()),
            "Source/Category": self.source_category_edit.text(),
            "Notes": self.notes_edit.text()
        }


class AddTransactionDialog(QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Add New Transaction")
        self.layout = QVBoxLayout()

        self.date_edit = QDateEdit()
        self.date_edit.setDate(QDate.currentDate())
        self.type_combo = QComboBox()
        self.type_combo.addItems(["Income", "Expense"])
        self.account_combo = QComboBox()
        self.account_combo.addItems(["Checking", "Savings", "Credit Card"])
        self.amount_edit = QLineEdit()
        self.source_category_edit = QLineEdit()
        self.notes_edit = QLineEdit()
        self.save_button = QPushButton("Save")
        self.save_button.clicked.connect(self.accept)

        self.layout.addWidget(QLabel("Date:"))
        self.layout.addWidget(self.date_edit)
        self.layout.addWidget(QLabel("Type:"))
        self.layout.addWidget(self.type_combo)
        self.layout.addWidget(QLabel("Account:"))
        self.layout.addWidget(self.account_combo)
        self.layout.addWidget(QLabel("Amount:"))
        self.layout.addWidget(self.amount_edit)
        self.layout.addWidget(QLabel("Source/Category:"))
        self.layout.addWidget(self.source_category_edit)
        self.layout.addWidget(QLabel("Notes:"))
        self.layout.addWidget(self.notes_edit)
        self.layout.addWidget(self.save_button)

        self.setLayout(self.layout)

    def get_transaction_data(self):
        return {
            "Date": self.date_edit.date().toString("yyyy-MM-dd"),
            "Type": self.type_combo.currentText(),
            "Account": self.account_combo.currentText(),
            "Amount": float(self.amount_edit.text()),
            "Source/Category": self.source_category_edit.text(),
            "Notes": self.notes_edit.text()
        }


class FinanceTracker(QWidget):
    def __init__(self):
        super().__init__()
        self.data = pd.DataFrame(columns=["Date", "Type", "Account", "Amount", "Source/Category", "Notes"])
        self.setWindowTitle("PhD Finance Tracker Pro")
        self.setWindowIcon(QIcon('finance_icon.png'))
        self.layout = QVBoxLayout()
        self.init_ui()

        self.settings = QSettings("MyCompany", "FinanceTracker")

    def init_ui(self):
        # Input Fields for Adding a New Transaction
        self.add_button = QPushButton("Add Transaction")
        self.add_button.clicked.connect(self.add_transaction)

        # Table to Display Transactions
        self.table = QTableWidget()
        self.table.setColumnCount(6)
        self.table.setHorizontalHeaderLabels(["Date", "Type", "Account", "Amount", "Source/Category", "Notes"])
        self.table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.table.doubleClicked.connect(self.edit_transaction)
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)

        # Layout for the Main Window
        self.layout.addWidget(self.add_button)
        self.layout.addWidget(self.table)
        self.setLayout(self.layout)

        # Load Data
        self.load_data()
        self.update_table()

    def add_transaction(self):
        add_dialog = AddTransactionDialog()
        if add_dialog.exec_() == QDialog.Accepted:
            new_transaction_data = add_dialog.get_transaction_data()
            # Add the new transaction data to the DataFrame
            new_row = pd.Series(new_transaction_data, index=self.data.columns)
            self.data = self.data.append(new_row, ignore_index=True)
            self.save_data()
            self.update_table()

    def edit_transaction(self, index):
        row = index.row()
        selected_row = self.data.iloc[row]

        # Create a dialog for editing
        edit_dialog = EditTransactionDialog(selected_row)
        if edit_dialog.exec_() == QDialog.Accepted:
            self.data.iloc[row] = edit_dialog.get_updated_data()
            self.save_data()
            self.update_table()

    def update_table(self):
        self.table.setRowCount(len(self.data))
        for i, row in self.data.iterrows():
            self.table.setItem(i, 0, QTableWidgetItem(row["Date"]))
            self.table.setItem(i, 1, QTableWidgetItem(row["Type"]))
            self.table.setItem(i, 2, QTableWidgetItem(row["Account"]))
            self.table.setItem(i, 3, QTableWidgetItem(f"{row['Amount']:.2f}"))
            self.table.setItem(i, 4, QTableWidgetItem(row["Source/Category"]))
            self.table.setItem(i, 5, QTableWidgetItem(row["Notes"]))
        self.table.resizeColumnsToContents()

    def save_data(self):
        self.data.to_csv("transactions.csv", index=False)

    def load_data(self):
        try:
            self.data = pd.read_csv("transactions.csv")
        except FileNotFoundError:
            self.data = pd.DataFrame(columns=["Date", "Type", "Account", "Amount", "Source/Category", "Notes"])

if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    finance_tracker = FinanceTracker()
    finance_tracker.show()
    sys.exit(app.exec_())
