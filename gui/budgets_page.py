from PySide6.QtCore import Signal
from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QGridLayout

from qfluentwidgets import (
    CardWidget, LineEdit, PrimaryPushButton, TransparentToolButton,
    FluentIcon, InfoBar, InfoBarPosition, StrongBodyLabel, MessageBox,
)

from . import theme
from .components import SectionHeader, EmptyState, BudgetProgressCard, apply_soft_shadow, EditDialog


class BudgetsPage(QWidget):
    data_changed = Signal()

    def __init__(self, budget_manager, expense_manager, parent=None):
        super().__init__(parent)
        self.budget_manager = budget_manager
        self.expense_manager = expense_manager

        layout = QVBoxLayout(self)
        layout.setContentsMargins(32, 28, 32, 32)
        layout.setSpacing(theme.SPACE_LG)

        layout.addWidget(SectionHeader("Budgets", "Set a spending limit per category and track it"))

        # --- add form ---
        form_card = CardWidget()
        form_card.setBorderRadius(theme.RADIUS_MD)
        apply_soft_shadow(form_card, blur=18, y_offset=4, alpha=26)
        form_layout = QHBoxLayout(form_card)
        form_layout.setContentsMargins(20, 18, 20, 18)
        form_layout.setSpacing(12)

        self.name_input = LineEdit()
        self.name_input.setPlaceholderText("Category name (e.g. Food)")

        self.amount_input = LineEdit()
        self.amount_input.setPlaceholderText("Budget amount")
        self.amount_input.setFixedWidth(160)

        self.add_button = PrimaryPushButton(FluentIcon.ADD, "Add budget")
        self.add_button.clicked.connect(self._on_add)

        form_layout.addWidget(self.name_input, 1)
        form_layout.addWidget(self.amount_input)
        form_layout.addWidget(self.add_button)
        layout.addWidget(form_card)

        # --- list ---
        self.list_holder = QVBoxLayout()
        layout.addLayout(self.list_holder)
        layout.addStretch(1)

        self.refresh()

    def _on_add(self):
        name = self.name_input.text().strip()
        amount_text = self.amount_input.text().strip()

        if not name:
            InfoBar.error("Missing name", "Enter a category name for this budget.",
                          position=InfoBarPosition.TOP, parent=self)
            return
        try:
            amount = float(amount_text)
            if amount <= 0:
                raise ValueError
        except ValueError:
            InfoBar.error("Invalid amount", "Enter a positive number for the budget.",
                          position=InfoBarPosition.TOP, parent=self)
            return

        if name in self.budget_manager.get_budget_names():
            InfoBar.warning("Already exists", f"A budget named '{name}' already exists.",
                             position=InfoBarPosition.TOP, parent=self)
            return

        self.budget_manager.add_budget(name, amount)
        self.name_input.clear()
        self.amount_input.clear()

        InfoBar.success("Budget added", f"'{name}' set to {amount:.2f}.",
                         position=InfoBarPosition.TOP, duration=2000, parent=self)

        self.refresh()
        self.data_changed.emit()

    def _on_delete(self, index):
        box = MessageBox("Delete this budget?", "Your expenses in this category stay untouched.", self)
        if box.exec():
            self.budget_manager.delete_budget(index)
            self.refresh()
            self.data_changed.emit()

    def _on_edit(self, index):
        budget = self.budget_manager.budgets[index]

        dialog = EditDialog(
            "Edit budget",
            fields=[
                ("name", "Category name", budget.name),
                ("amount", "Budget amount", budget.amount),
            ],
            parent=self,
        )
        if not dialog.exec():
            return

        values = dialog.values()
        new_name = values["name"]

        if not new_name:
            InfoBar.error("Missing name", "Enter a category name for this budget.",
                          position=InfoBarPosition.TOP, parent=self)
            return

        try:
            new_amount = float(values["amount"])
            if new_amount <= 0:
                raise ValueError
        except ValueError:
            InfoBar.error("Invalid amount", "Enter a positive number for the budget.",
                          position=InfoBarPosition.TOP, parent=self)
            return

        # block renaming to a name that collides with a DIFFERENT budget
        other_names = [b.name for i, b in enumerate(self.budget_manager.budgets) if i != index]
        if new_name in other_names:
            InfoBar.warning("Already exists", f"A budget named '{new_name}' already exists.",
                             position=InfoBarPosition.TOP, parent=self)
            return

        self.budget_manager.update_budget(index, name=new_name, amount=new_amount)

        InfoBar.success("Updated", f"'{new_name}' saved.",
                         position=InfoBarPosition.TOP, duration=2000, parent=self)

        self.refresh()
        self.data_changed.emit()

    def refresh(self):
        while self.list_holder.count():
            item = self.list_holder.takeAt(0)
            widget = item.widget()
            if widget:
                widget.deleteLater()
            elif item.layout():
                self._clear_layout(item.layout())

        if not self.budget_manager.budgets:
            self.list_holder.addWidget(
                EmptyState(FluentIcon.PIE_SINGLE, "No budgets yet",
                           "Add a category and a limit above - e.g. 'Food', 300.")
            )
            return

        currency = theme.load_settings().get("currency", "$")
        spent_by_category = self.expense_manager.total_by_category()

        grid = QGridLayout()
        grid.setSpacing(theme.SPACE_MD)
        columns = 2
        for i, budget in enumerate(self.budget_manager.budgets):
            spent = spent_by_category.get(budget.name, 0)
            row_widget = QWidget()
            row_layout = QHBoxLayout(row_widget)
            row_layout.setContentsMargins(0, 0, 0, 0)
            row_layout.setSpacing(6)

            card = BudgetProgressCard(budget.name, spent, budget.amount, currency)
            row_layout.addWidget(card, 1)

            edit_btn = TransparentToolButton(FluentIcon.EDIT)
            edit_btn.setFixedSize(32, 32)
            edit_btn.clicked.connect(lambda _, idx=i: self._on_edit(idx))
            row_layout.addWidget(edit_btn)

            delete_btn = TransparentToolButton(FluentIcon.DELETE)
            delete_btn.setFixedSize(32, 32)
            delete_btn.clicked.connect(lambda _, idx=i: self._on_delete(idx))
            row_layout.addWidget(delete_btn)

            grid.addWidget(row_widget, i // columns, i % columns)

        self.list_holder.addLayout(grid)

    @staticmethod
    def _clear_layout(layout):
        while layout.count():
            item = layout.takeAt(0)
            widget = item.widget()
            if widget:
                widget.deleteLater()
