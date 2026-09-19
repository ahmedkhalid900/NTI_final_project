from datetime import date, timedelta

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QGridLayout

from qfluentwidgets import FluentIcon, CardWidget, StrongBodyLabel, CaptionLabel, ScrollArea

from . import theme
from .components import SectionHeader, StatCard, EmptyState, BudgetProgressCard, apply_soft_shadow
from .charts import Sparkline


class DashboardPage(QWidget):
    def __init__(self, expense_manager, budget_manager, parent=None):
        super().__init__(parent)
        self.expense_manager = expense_manager
        self.budget_manager = budget_manager
        self.settings = theme.load_settings()

        outer = QVBoxLayout(self)
        outer.setContentsMargins(0, 0, 0, 0)

        scroll = ScrollArea(self)
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("QScrollArea{background: transparent; border: none;}")
        outer.addWidget(scroll)

        content = QWidget()
        content.setStyleSheet("background: transparent;")
        scroll.setWidget(content)

        self.layout_ = QVBoxLayout(content)
        self.layout_.setContentsMargins(32, 28, 32, 32)
        self.layout_.setSpacing(theme.SPACE_LG)

        self.layout_.addWidget(SectionHeader("Dashboard", "A quick look at where your money's going"))

        # --- hero stat row ---
        self.stats_row = QHBoxLayout()
        self.stats_row.setSpacing(theme.SPACE_MD)
        self.total_card = StatCard("Total spent (all time)", "$0.00", FluentIcon.MARKET, theme.COLOR_INFO)
        self.month_card = StatCard("Spent this month", "$0.00", FluentIcon.CALENDAR, theme.COLOR_WARNING)
        self.remaining_card = StatCard("Left across budgets", "$0.00", FluentIcon.PIE_SINGLE, theme.COLOR_SUCCESS)
        self.stats_row.addWidget(self.total_card, 1)
        self.stats_row.addWidget(self.month_card, 1)
        self.stats_row.addWidget(self.remaining_card, 1)
        self.layout_.addLayout(self.stats_row)

        # --- trend card ---
        self.trend_card = CardWidget()
        self.trend_card.setBorderRadius(theme.RADIUS_MD)
        apply_soft_shadow(self.trend_card, blur=18, y_offset=4, alpha=26)
        trend_layout = QVBoxLayout(self.trend_card)
        trend_layout.setContentsMargins(20, 16, 20, 16)
        trend_header = QHBoxLayout()
        trend_title = StrongBodyLabel("Last 14 days")
        trend_header.addWidget(trend_title)
        trend_header.addStretch(1)
        self.trend_caption = CaptionLabel("")
        trend_header.addWidget(self.trend_caption)
        trend_layout.addLayout(trend_header)
        self.sparkline = Sparkline()
        trend_layout.addWidget(self.sparkline)
        self.layout_.addWidget(self.trend_card)

        # --- budgets section ---
        budgets_header = QHBoxLayout()
        budgets_header.addWidget(StrongBodyLabel("Budgets"))
        self.layout_.addLayout(budgets_header)

        self.budgets_grid_holder = QVBoxLayout()
        self.layout_.addLayout(self.budgets_grid_holder)
        self.layout_.addStretch(1)

        self.refresh()

    # ------------------------------------------------------------
    def refresh(self):
        self.settings = theme.load_settings()
        currency = self.settings.get("currency", "$")

        total = self.expense_manager.total_spent()
        self.total_card.set_value(f"{currency}{total:,.2f}")

        today = date.today()
        month_total = sum(
            e.amount for e in self.expense_manager.expenses
            if e.date_str[:7] == today.strftime("%Y-%m")
        )
        self.month_card.set_value(f"{currency}{month_total:,.2f}")

        if self.budget_manager.budgets:
            remaining_total = sum(self.budget_manager.remaining_amounts(self.expense_manager).values())
            self.remaining_card.set_value(f"{currency}{remaining_total:,.2f}")
        else:
            self.remaining_card.set_value("--")

        self._refresh_sparkline()
        self._refresh_budgets(currency)

    def _refresh_sparkline(self):
        today = date.today()
        days = [today - timedelta(days=i) for i in range(13, -1, -1)]
        totals_by_day = {}
        for expense in self.expense_manager.expenses:
            totals_by_day[expense.date_str] = totals_by_day.get(expense.date_str, 0) + expense.amount
        values = [totals_by_day.get(d.strftime("%Y-%m-%d"), 0) for d in days]
        self.sparkline.set_values(values, theme.COLOR_INFO)
        last_total = sum(values)
        currency = self.settings.get("currency", "$")
        self.trend_caption.setText(f"{currency}{last_total:,.2f} over 14 days")

    def _refresh_budgets(self, currency):
        # clear old widgets
        while self.budgets_grid_holder.count():
            item = self.budgets_grid_holder.takeAt(0)
            widget = item.widget()
            if widget:
                widget.deleteLater()
            elif item.layout():
                self._clear_layout(item.layout())

        if not self.budget_manager.budgets:
            self.budgets_grid_holder.addWidget(
                EmptyState(FluentIcon.PIE_SINGLE, "No budgets yet",
                           "Head over to the Budgets tab to set your first spending limit.")
            )
            return

        spent_by_category = self.expense_manager.total_by_category()
        grid = QGridLayout()
        grid.setSpacing(theme.SPACE_MD)
        columns = 3
        for i, budget in enumerate(self.budget_manager.budgets):
            spent = spent_by_category.get(budget.name, 0)
            card = BudgetProgressCard(budget.name, spent, budget.amount, currency)
            grid.addWidget(card, i // columns, i % columns)
        self.budgets_grid_holder.addLayout(grid)

    @staticmethod
    def _clear_layout(layout):
        while layout.count():
            item = layout.takeAt(0)
            widget = item.widget()
            if widget:
                widget.deleteLater()
