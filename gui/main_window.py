from qfluentwidgets import (
    FluentWindow, NavigationItemPosition, FluentIcon, setTheme, Theme,
    setThemeColor,
)

from expense_manager import ExpenseManager
from budget_manager import BudgetManager

from . import theme
from .dashboard_page import DashboardPage
from .expenses_page import ExpensesPage
from .budgets_page import BudgetsPage
from .settings_page import SettingsPage


class MainWindow(FluentWindow):
    """App shell: left navigation rail + Mica backdrop + one page per
    section. Every page shares the same ExpenseManager/BudgetManager
    instances so an action on one page (e.g. adding an expense) is
    reflected everywhere else the moment you switch tabs."""

    def __init__(self):
        super().__init__()

        settings = theme.load_settings()
        self._apply_theme_mode(settings["theme_mode"])
        setThemeColor(settings["accent"])

        # Shared backend objects - the SAME instances are handed to
        # every page, so there is exactly one source of truth.
        self.expense_manager = ExpenseManager()
        self.budget_manager = BudgetManager()

        self.setWindowTitle("Expense Tracker")
        self.resize(1180, 760)
        self.setMinimumSize(980, 640)

        # Mica backdrop (Windows 11's signature translucent material).
        # Silently no-ops on non-Windows platforms.
        try:
            self.setMicaEffectEnabled(True)
        except Exception:
            pass

        self._build_pages()

    def _apply_theme_mode(self, mode: str):
        mode = (mode or "Auto").lower()
        if mode == "light":
            setTheme(Theme.LIGHT)
        elif mode == "dark":
            setTheme(Theme.DARK)
        else:
            setTheme(Theme.AUTO)

    def _build_pages(self):
        self.dashboard_page = DashboardPage(self.expense_manager, self.budget_manager, self)
        self.expenses_page = ExpensesPage(self.expense_manager, self.budget_manager, self)
        self.budgets_page = BudgetsPage(self.budget_manager, self.expense_manager, self)
        self.settings_page = SettingsPage(self)

        self.dashboard_page.setObjectName("dashboardPage")
        self.expenses_page.setObjectName("expensesPage")
        self.budgets_page.setObjectName("budgetsPage")
        self.settings_page.setObjectName("settingsPage")

        self.addSubInterface(self.dashboard_page, FluentIcon.HOME, "Dashboard")
        self.addSubInterface(self.expenses_page, FluentIcon.SHOPPING_CART, "Expenses")
        self.addSubInterface(self.budgets_page, FluentIcon.PIE_SINGLE, "Budgets")
        self.addSubInterface(self.settings_page, FluentIcon.SETTING, "Settings",
                              NavigationItemPosition.BOTTOM)

        # Cross-page refresh wiring: any change anywhere refreshes the
        # dashboard, since it's a read-only summary of the same data.
        self.expenses_page.data_changed.connect(self.refresh_summaries)
        self.budgets_page.data_changed.connect(self.refresh_summaries)
        self.settings_page.currency_changed.connect(lambda _: self._refresh_all())

        self.refresh_summaries()

    def refresh_summaries(self):
        self.dashboard_page.refresh()

    def _refresh_all(self):
        self.dashboard_page.refresh()
        self.expenses_page.refresh()
        self.budgets_page.refresh()
