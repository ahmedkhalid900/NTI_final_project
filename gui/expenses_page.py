from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QHeaderView, QTableWidgetItem, QAbstractItemView,
)

from qfluentwidgets import (
    CardWidget, LineEdit, EditableComboBox, PrimaryPushButton, TransparentToolButton,
    TableWidget, FluentIcon, InfoBar, InfoBarPosition, StrongBodyLabel, ComboBox,
    MessageBox,
)

from . import theme
from .components import SectionHeader, EmptyState, apply_soft_shadow, CategoryDot, EditDialog


class ExpensesPage(QWidget):
    data_changed = Signal()

    def __init__(self, expense_manager, budget_manager, parent=None):
        super().__init__(parent)
        self.expense_manager = expense_manager
        self.budget_manager = budget_manager
        self._active_filter = "All categories"

        layout = QVBoxLayout(self)
        layout.setContentsMargins(32, 28, 32, 32)
        layout.setSpacing(theme.SPACE_LG)

        layout.addWidget(SectionHeader("Expenses", "Log a purchase, filter, and review your history"))

        # --- add form card ---
        form_card = CardWidget()
        form_card.setBorderRadius(theme.RADIUS_MD)
        apply_soft_shadow(form_card, blur=18, y_offset=4, alpha=26)
        form_layout = QHBoxLayout(form_card)
        form_layout.setContentsMargins(20, 18, 20, 18)
        form_layout.setSpacing(12)

        self.amount_input = LineEdit()
        self.amount_input.setPlaceholderText("Amount")
        self.amount_input.setFixedWidth(120)

        self.category_input = EditableComboBox()
        self.category_input.setPlaceholderText("Category")
        self.category_input.setFixedWidth(160)

        self.note_input = LineEdit()
        self.note_input.setPlaceholderText("What was it for?")

        self.add_button = PrimaryPushButton(FluentIcon.ADD, "Add expense")
        self.add_button.clicked.connect(self._on_add)

        form_layout.addWidget(self.amount_input)
        form_layout.addWidget(self.category_input)
        form_layout.addWidget(self.note_input, 1)
        form_layout.addWidget(self.add_button)
        layout.addWidget(form_card)

        # --- filter row ---
        filter_row = QHBoxLayout()
        filter_row.addWidget(StrongBodyLabel("Filter:"))
        self.filter_combo = ComboBox()
        self.filter_combo.addItem("All categories")
        self.filter_combo.setFixedWidth(200)
        self.filter_combo.currentTextChanged.connect(self._on_filter_changed)
        filter_row.addWidget(self.filter_combo)
        filter_row.addStretch(1)
        self.count_label = StrongBodyLabel("")
        filter_row.addWidget(self.count_label)
        layout.addLayout(filter_row)

        # --- table card ---
        self.table_card = CardWidget()
        self.table_card.setBorderRadius(theme.RADIUS_MD)
        apply_soft_shadow(self.table_card, blur=18, y_offset=4, alpha=26)
        table_layout = QVBoxLayout(self.table_card)
        table_layout.setContentsMargins(4, 4, 4, 4)

        self.table = TableWidget()
        self.table.setBorderVisible(False)
        self.table.setBorderRadius(theme.RADIUS_MD)
        self.table.setWordWrap(False)
        self.table.setColumnCount(6)
        self.table.setHorizontalHeaderLabels(["Date", "Category", "Note", "Amount", "", ""])
        self.table.horizontalHeader().setSectionResizeMode(2, QHeaderView.Stretch)
        self.table.verticalHeader().hide()
        self.table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        table_layout.addWidget(self.table)

        self.empty_state = EmptyState(
            FluentIcon.SHOPPING_CART, "No expenses yet",
            "Add your first expense above to start tracking your spending."
        )
        table_layout.addWidget(self.empty_state)

        layout.addWidget(self.table_card, 1)

        self.refresh()

    # ------------------------------------------------------------
    def _on_add(self):
        amount_text = self.amount_input.text().strip()
        category = self.category_input.text().strip()
        note = self.note_input.text().strip()

        try:
            amount = float(amount_text)
            if amount <= 0:
                raise ValueError
        except ValueError:
            InfoBar.error("Invalid amount", "Enter a positive number for the amount.",
                          position=InfoBarPosition.TOP, parent=self)
            return

        if not category:
            InfoBar.error("Missing category", "Enter a category for this expense.",
                          position=InfoBarPosition.TOP, parent=self)
            return

        self.expense_manager.add_expense(amount, category, note)

        self.amount_input.clear()
        self.note_input.clear()

        InfoBar.success("Added", f"Logged {amount:.2f} in '{category}'.",
                         position=InfoBarPosition.TOP, duration=2000, parent=self)

        self.refresh()
        self.data_changed.emit()

    def _on_filter_changed(self, text):
        self._active_filter = text
        self._render_table()

    def _on_delete(self, real_index):
        box = MessageBox("Delete expense?", "This can't be undone.", self)
        if box.exec():
            self.expense_manager.delete_expense(real_index)
            self.refresh()
            self.data_changed.emit()

    def _on_edit(self, real_index):
        expense = self.expense_manager.expenses[real_index]

        dialog = EditDialog(
            "Edit expense",
            fields=[
                ("amount", "Amount", expense.amount),
                ("category", "Category", expense.category),
                ("note", "Note", expense.note),
                ("date", "Date (YYYY-MM-DD)", expense.date_str),
            ],
            parent=self,
        )
        if not dialog.exec():
            return

        values = dialog.values()

        try:
            new_amount = float(values["amount"])
            if new_amount <= 0:
                raise ValueError
        except ValueError:
            InfoBar.error("Invalid amount", "Enter a positive number for the amount.",
                          position=InfoBarPosition.TOP, parent=self)
            return

        new_category = values["category"]
        if not new_category:
            InfoBar.error("Missing category", "Enter a category for this expense.",
                          position=InfoBarPosition.TOP, parent=self)
            return

        new_date = values["date"] or expense.date_str

        self.expense_manager.update_expense(
            real_index,
            amount=new_amount,
            category=new_category,
            note=values["note"],
            date=new_date,
        )

        InfoBar.success("Updated", "Expense saved.",
                         position=InfoBarPosition.TOP, duration=2000, parent=self)

        self.refresh()
        self.data_changed.emit()

    # ------------------------------------------------------------
    def refresh(self):
        self._refresh_category_filter()
        self._render_table()

    def _refresh_category_filter(self):
        categories = sorted({e.category for e in self.expense_manager.expenses}
                             | set(self.budget_manager.get_budget_names()))
        current = self.filter_combo.currentText() or "All categories"
        self.filter_combo.blockSignals(True)
        self.filter_combo.clear()
        self.filter_combo.addItem("All categories")
        self.filter_combo.addItems(categories)
        self.category_input.clear()
        self.category_input.addItems(categories)
        idx = self.filter_combo.findText(current)
        self.filter_combo.setCurrentIndex(idx if idx >= 0 else 0)
        self.filter_combo.blockSignals(False)
        self._active_filter = self.filter_combo.currentText()

    def _render_table(self):
        currency = theme.load_settings().get("currency", "$")
        expenses = self.expense_manager.expenses
        # keep (real_index, expense) pairs so delete targets the right row
        indexed = list(enumerate(expenses))
        if self._active_filter and self._active_filter != "All categories":
            indexed = [(i, e) for i, e in indexed if e.category == self._active_filter]
        # newest first
        indexed.sort(key=lambda pair: pair[1].date_str, reverse=True)

        self.count_label.setText(f"{len(indexed)} expense(s)")

        if not indexed:
            self.table.hide()
            self.empty_state.show()
            return
        self.empty_state.hide()
        self.table.show()

        self.table.setRowCount(len(indexed))
        for row, (real_index, expense) in enumerate(indexed):
            self.table.setItem(row, 0, QTableWidgetItem(expense.date_str))

            cat_item = QTableWidgetItem("  " + expense.category)
            cat_item.setForeground(Qt.GlobalColor.transparent)  # color handled by dot widget below
            self.table.setItem(row, 1, QTableWidgetItem(expense.category))

            self.table.setItem(row, 2, QTableWidgetItem(expense.note or "-"))
            amount_item = QTableWidgetItem(f"{currency}{expense.amount:,.2f}")
            amount_item.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
            self.table.setItem(row, 3, amount_item)

            edit_btn = TransparentToolButton(FluentIcon.EDIT)
            edit_btn.clicked.connect(lambda _, i=real_index: self._on_edit(i))
            self.table.setCellWidget(row, 4, edit_btn)

            delete_btn = TransparentToolButton(FluentIcon.DELETE)
            delete_btn.clicked.connect(lambda _, i=real_index: self._on_delete(i))
            self.table.setCellWidget(row, 5, delete_btn)

        self.table.resizeColumnsToContents()
        self.table.horizontalHeader().setSectionResizeMode(2, QHeaderView.Stretch)
        self.table.setColumnWidth(4, 44)
        self.table.setColumnWidth(5, 44)
