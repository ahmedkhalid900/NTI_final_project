Expense Tracker - Windows 11 Fluent GUI
========================================

1) Install the two libraries needed for the GUI (one-time):

   py -m pip install PySide6 PySide6-Fluent-Widgets

2) Run the app from inside this folder:

   py main.py

Turning it into a real Desktop app (one .exe, double-click to open)
--------------------------------------------------------------------
1) Double-click build.bat inside this folder (or run it from a
   terminal). It installs PyInstaller if needed and builds the app -
   this takes a few minutes the first time.
2) When it finishes, you'll find dist\ExpenseTracker.exe.
3) Right-click ExpenseTracker.exe -> Send to -> Desktop (create
   shortcut). That's it - double-clicking the shortcut opens the app
   directly, no Python, no terminal, nothing else needed.
4) Keep expenses.json / budgets.json / settings.json wherever
   ExpenseTracker.exe itself lives (they're created automatically
   next to it the first time you use the app) - don't move the .exe
   to a different folder afterwards without moving those with it if
   you want to keep your data.

Files
-----
expense.py             - Expense model (unchanged backend)
expense_manager.py     - ExpenseManager (unchanged backend)
budget.py              - Budget model (unchanged backend)
budget_manager.py      - BudgetManager (unchanged backend)
main.py                - App entry point
gui/theme.py           - Design system: spacing, colors, category color
                          hashing, and settings.json (accent/theme/currency)
gui/components.py      - Reusable styled widgets: StatCard, BudgetProgressCard,
                          EmptyState, SectionHeader, IconBadge, CategoryDot
gui/charts.py           - Hand-drawn donut chart + sparkline (no external
                          chart library needed)
gui/main_window.py      - App shell: Fluent navigation rail + Mica backdrop
gui/dashboard_page.py   - Hero stats (total / this month / left across
                          budgets), 14-day spending sparkline, budget
                          progress cards
gui/expenses_page.py    - Add / filter / list / delete expenses
gui/budgets_page.py     - Add / list / delete budgets, each with a
                          color-coded progress bar
gui/settings_page.py    - Personalization: theme (Light/Dark/Auto),
                          accent color, currency symbol

Notes
-----
- expenses.json and budgets.json are created automatically next to
  main.py the first time you add something - same as before, nothing
  changed in how the backend saves or loads data.
- settings.json is new and purely cosmetic (theme/accent/currency).
  Deleting it just resets appearance back to defaults; it never
  touches your expenses or budgets.
- The GUI only calls methods that already existed on ExpenseManager and
  BudgetManager (add_expense, delete_expense, total_by_category,
  total_spent, filter_by_category, add_budget, delete_budget,
  remaining_amounts, get_budget_names) - no backend logic was changed,
  duplicated, or added.
