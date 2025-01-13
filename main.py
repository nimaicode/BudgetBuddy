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
    QInputDialog,
    QDialog,
    QHeaderView,
    QMessageBox,
    QTabWidget
)
from PyQt5.QtCore import QDate, Qt, QSettings
from PyQt5.QtGui import QIcon, QFont
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
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

class FinanceTracker(QWidget):
    def __init__(self):
        super().__init__()
        # Initialize data with default columns
        self.data = pd.DataFrame(columns=["Date", "Type", "Account", "Amount", "Source/Category", "Notes"])
        self.setWindowTitle("PhD Finance Tracker Pro")
        self.setWindowIcon(QIcon('finance_icon.png'))
        self.layout = QVBoxLayout()
        self.init_ui()
        
        # Load data empty
        self.load_data()

        self.settings = QSettings("MyCompany", "FinanceTracker")

    def init_ui(self):
        # Input Fields
        self.date_edit = QDateEdit()
        self.date_edit.setDate(QDate.currentDate())
        self.type_combo = QComboBox()
        self.type_combo.addItems(["Income", "Expense"])
        self.account_combo = QComboBox()
        self.account_combo.addItems(["Checking", "Savings", "Credit Card"])
        self.amount_edit = QLineEdit()
        self.source_category_edit = QLineEdit()
        self.notes_edit = QLineEdit()
        self.add_button = QPushButton("Add Transaction")
        self.add_button.clicked.connect(self.add_transaction)

        # Input Layout
        input_layout = QHBoxLayout()
        input_layout.addWidget(QLabel("Date:"))
        input_layout.addWidget(self.date_edit)
        input_layout.addWidget(QLabel("Type:"))
        input_layout.addWidget(self.type_combo)
        input_layout.addWidget(QLabel("Account:"))
        input_layout.addWidget(self.account_combo)
        input_layout.addWidget(QLabel("Amount:"))
        input_layout.addWidget(self.amount_edit)
        input_layout.addWidget(QLabel("Source/Category:"))
        input_layout.addWidget(self.source_category_edit)
        input_layout.addWidget(QLabel("Notes:"))
        input_layout.addWidget(self.notes_edit)
        input_layout.addWidget(self.add_button)

        # Table
        self.table = QTableWidget()
        self.table.setColumnCount(6)
        self.table.setHorizontalHeaderLabels(["Date", "Type", "Account", "Amount", "Source/Category", "Notes"])
        self.table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.table.doubleClicked.connect(self.edit_transaction)
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)

        # Search/Filter
        self.search_bar = QLineEdit()
        self.search_bar.setPlaceholderText("Search...")
        self.search_bar.textChanged.connect(self.filter_table)

        self.type_filter_combo = QComboBox()
        self.type_filter_combo.addItems(["All", "Income", "Expense"])
        self.type_filter_combo.currentIndexChanged.connect(self.filter_table)

        filter_layout = QHBoxLayout()
        filter_layout.addWidget(QLabel("Search:"))
        filter_layout.addWidget(self.search_bar)
        filter_layout.addWidget(QLabel("Type:"))
        filter_layout.addWidget(self.type_filter_combo)

        # Analysis Tab
        self.analysis_tab = QWidget()
        self.analysis_layout = QVBoxLayout()
        self.analysis_tab.setLayout(self.analysis_layout)
        self.create_analysis_tab()

        # Tab Widget
        self.tabs = QTabWidget()
        self.tabs.addTab(self, "Transactions")
        self.tabs.addTab(self.analysis_tab, "Analysis")

        # Layout
        self.layout.addLayout(filter_layout)
        self.layout.addWidget(self.tabs)
        self.setLayout(self.layout)

        # Load Data
        self.update_table()
        self.load_settings()

    def create_analysis_tab(self):
        # Monthly Spending Chart
        self.monthly_spending_figure = Figure()
        self.monthly_spending_canvas = FigureCanvas(self.monthly_spending_figure)
        self.analysis_layout.addWidget(self.monthly_spending_canvas)

        # Category Pie Chart
        self.category_pie_figure = Figure()
        self.category_pie_canvas = FigureCanvas(self.category_pie_figure)
        self.analysis_layout.addWidget(self.category_pie_canvas)

        self.update_analysis_charts()

    def add_transaction(self):
        date = self.date_edit.date().toString("yyyy-MM-dd")
        _type = self.type_combo.currentText()
        account = self.account_combo.currentText()
        amount = float(self.amount_edit.text())
        source_category = self.source_category_edit.text()
        notes = self.notes_edit.text()

        new_row = pd.Series([date, _type, account, amount, source_category, notes], index=self.data.columns)
        self.data = self.data.append(new_row, ignore_index=True)
        self.save_data()
        self.update_table()
        self.update_analysis_charts()  # Update charts after adding transaction
        self.clear_input_fields()

    def edit_transaction(self, index):
        row = index.row()
        selected_row = self.data.iloc[row]

        # Create a dialog for editing
        edit_dialog = EditTransactionDialog(selected_row)
        if edit_dialog.exec_() == QDialog.Accepted:
            self.data.iloc[row] = edit_dialog.get_updated_data()
            self.save_data()
            self.update_table()
            self.update_analysis_charts()  # Update charts after editing transaction

    def delete_transaction(self):
        selected_rows = sorted(set(index.row() for index in self.table.selectedIndexes()))
        if not selected_rows:
            QMessageBox.warning(self, "Warning", "No transaction selected.")
            return

        confirm = QMessageBox.question(self, "Confirm Deletion", "Are you sure you want to delete the selected transactions?", QMessageBox.Yes | QMessageBox.No)
        if confirm == QMessageBox.Yes:
            self.data.drop(selected_rows, inplace=True)
            self.data.reset_index(drop=True, inplace=True)
            self.save_data()
            self.update_table()
            self.update_analysis_charts()  # Update charts after deleting transaction

    def update_table(self, data=None):
        if data is None:
            data = self.data
        self.table.setRowCount(len(data))
        for i, row in data.iterrows():
            self.table.setItem(i, 0, QTableWidgetItem(row["Date"]))
            self.table.setItem(i, 1, QTableWidgetItem(row["Type"]))
            self.table.setItem(i, 2, QTableWidgetItem(row["Account"]))
            self.table.setItem(i, 3, QTableWidgetItem(f"{row['Amount']:.2f}"))
            self.table.setItem(i, 4, QTableWidgetItem(row["Source/Category"]))
            self.table.setItem(i, 5, QTableWidgetItem(row["Notes"]))
        self.table.resizeColumnsToContents()

    def filter_table(self):
        search_text = self.search_bar.text().lower()
        selected_type = self.type_filter_combo.currentText()
        filtered_data = self.data.copy()

        if search_text:
            filtered_data = filtered_data[filtered_data.apply(lambda row: row.astype(str).str.lower().str.contains(search_text).any(), axis=1)]

        if selected_type != "All":
            filtered_data = filtered_data[filtered_data["Type"] == selected_type]

        self.update_table(filtered_data)

    def update_analysis_charts(self):
        # Convert Date column to datetime for easier date-based analysis
        self.data["Date"] = pd.to_datetime(self.data["Date"], errors='coerce')

        # Ensure Amount column is numeric
        self.data["Amount"] = pd.to_numeric(self.data["Amount"], errors='coerce')

        # Drop rows with NaN in Amount after conversion
        valid_data = self.data.dropna(subset=["Amount"])  
        
        # Check if there is any valid data to plot
        reply = QMessageBox.question(self, "No Data to Plot", 
                                     "No data available for analysis. Would you like to add transactions now?", 
                                     QMessageBox.Yes | QMessageBox.No)
        if reply == QMessageBox.Yes:
            self.add_transaction_interactively()  # Trigger the add transaction process
        return
          
        # Monthly Spending Chart
        self.monthly_spending_figure.clear()
        ax = self.monthly_spending_figure.add_subplot(111)
        monthly_spending = self.data[self.data["Type"] == "Expense"].groupby(pd.Grouper(key="Date", freq="M"))["Amount"].sum()
        monthly_spending.plot(kind="bar", ax=ax)
        ax.set_title("Monthly Spending")
        ax.set_xlabel("Month")
        ax.set_ylabel("Amount")
        self.monthly_spending_canvas.draw()

        # Category Pie Chart
        self.category_pie_figure.clear()
        ax = self.category_pie_figure.add_subplot(111)
        category_spending = self.data[self.data["Type"] == "Expense"].groupby("Source/Category")["Amount"].sum()
        category_spending.plot(kind="pie", ax=ax, autopct='%1.1f%%', startangle=90)
        ax.set_title("Expense Categories")
        self.category_pie_canvas.draw()

    def save_data(self):
        self.data.to_csv("transactions.csv", index=False)
    '''
    def load_data(self):
        try:
            self.data = pd.read_csv("transactions.csv")
            print(seft.data.head())
        except FileNotFoundError:
            self.data = pd.DataFrame(columns=["Date", "Type", "Account", "Amount", "Source/Category", "Notes"])
    '''
    def load_data(self):
        try:
            self.data = pd.read_csv("./transactions.csv")
            print(self.data.head())
            if self.data.empty:
                QMessageBox.information(self, "No Data", "No transactions found. Please add your first transaction.")
                self.add_transaction_interactively()
        except FileNotFoundError:
            self.data = pd.DataFrame(columns=["Date", "Type", "Account", "Amount", "Source/Category", "Notes"])
            QMessageBox.information(self, "No Data File", "No transactions file found. Please add your first transaction.")
            self.add_transaction_from_dialog()

    def add_transaction_interactively(self):
        dialog = QDialog(self)
        dialog.setWindowTitle("Add New Transaction")

        layout = QVBoxLayout()

        # Input Fields
        date_edit = QDateEdit()
        date_edit.setDate(QDate.currentDate())
        type_combo = QComboBox()
        type_combo.addItems(["Income", "Expense"])
        account_combo = QComboBox()
        account_combo.addItems(["Checking", "Savings", "Credit Card"])
        amount_edit = QLineEdit()
        source_category_edit = QLineEdit()
        notes_edit = QLineEdit()

        layout.addWidget(QLabel("Date:"))
        layout.addWidget(date_edit)
        layout.addWidget(QLabel("Type:"))
        layout.addWidget(type_combo)
        layout.addWidget(QLabel("Account:"))
        layout.addWidget(account_combo)
        layout.addWidget(QLabel("Amount:"))
        layout.addWidget(amount_edit)
        layout.addWidget(QLabel("Source/Category:"))
        layout.addWidget(source_category_edit)
        layout.addWidget(QLabel("Notes:"))
        layout.addWidget(notes_edit)

        # Add Button
        add_button = QPushButton("Add")
        add_button.clicked.connect(lambda: self.add_transaction_from_dialog(dialog, date_edit, type_combo, account_combo, amount_edit, source_category_edit, notes_edit))
        layout.addWidget(add_button)

        dialog.setLayout(layout)
        dialog.exec_()

    def add_transaction_from_dialog(self, dialog, date_edit, type_combo, account_combo, amount_edit, source_category_edit, notes_edit):
        date = date_edit.date().toString("yyyy-MM-dd")
        _type = type_combo.currentText()
        account = account_combo.currentText()
        amount = amount_edit.text()
        source_category = source_category_edit.text()
        notes = notes_edit.text()

        # Validate and Add Transaction
        if amount:
            try:
                amount = float(amount)
                new_row = pd.Series([date, _type, account, amount, source_category, notes], index=self.data.columns)
                self.data = self.data_.append(new_row, ignore_index=True)
                self.save_data()
                self.update_table()
                dialog.accept()
            except ValueError:
                QMessageBox.warning(self, "Invalid Input", "Amount must be a valid number.")
        else:
            QMessageBox.warning(self, "Missing Input", "Please enter an amount.")

    def clear_input_fields(self):
        self.date_edit.setDate(QDate.currentDate())
        self.type_combo.setCurrentIndex(0)
        self.account_combo.setCurrentIndex(0)
        self.amount_edit.clear()
        self.source_category_edit.clear()
        self.notes_edit.clear()

    def load_settings(self):
        window_geometry = self.settings.value("windowGeometry")
        if window_geometry:
            self.restoreGeometry(window_geometry)

    def closeEvent(self, event):
        self.settings.setValue("windowGeometry", self.saveGeometry())
        event.accept()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    finance_tracker = FinanceTracker()
    finance_tracker.show()
    sys.exit(app.exec_())