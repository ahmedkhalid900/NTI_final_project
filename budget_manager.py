import json
import os
# This import the class that we made in file(budget.py).
from budget import Budget

# This class is made for mangging the user's budget.
class BudgetManager:
    def __init__(self, filepath="budgets.json"):
        self.filepath = filepath
        self.budgets = []
        self.load_budgets()

    # This method makes a new budget, save it in the (self.budgets) list, then return new_budget.
    def add_budget(self, name, amount):
        new_budget = Budget(name, amount)
        self.budgets.append(new_budget)
        self.save_budgets()
        return new_budget

    # This method is used to delete a budget that we added by a condition 
    # the condition makes sure that the expense is in the list, if true, it will 
    # delete it and then we save the update we did . 
    def delete_budget(self, index):
        if 0 <= index < len(self.budgets):
            del self.budgets[index]
            self.save_budgets()

    # this method returns a list of all the budgets names.
    def get_budget_names(self):
        return [budget.name for budget in self.budgets]

    
    def remaining_amounts(self, expense_manager):
        spent_by_category = expense_manager.total_by_category()

        remaining = {}
        for budget in self.budgets:
            spent_so_far = spent_by_category.get(budget.name, 0)
            remaining[budget.name] = budget.amount - spent_so_far

        return remaining


    # This method edit or change in the budget if there is something wrong or want to be edited from the user if he want to edit it.
    def update_budget(self, index, name=None, amount=None):
        # this checks if the index that was sent is in the list or not.
        if 0 <= index < len(self.budgets):
            # This gets the real object not a copy to edit on it.
            budget = self.budgets[index]
            # THis if codition works if the user sent a budget name it will change it, if not, it will keep it as it was.
            if name is not None:
                budget.name = name
            # Same thing but in amount of money.
            if amount is not None:
                budget.amount = amount

            # this method changes the code into a dict to save it in a JSOn file to read it and save it .
            self.save_budgets()
            return budget
        return None


    
    # This method saves the budgets in the JSON file
    def save_budgets(self):
        # (data) variable transefers the budgets objects to a list of dictionaries by using 
        # to_dict() to make JSON file read it correctly. 
        data = [budget.to_dict() for budget in self.budgets]

        # opens the file to write using "w" and "utf-8" and (json.dumb()) writes 
        # the data into the file and (indent=2) makes the reading of the file much
        # easier by making 2 spaces before each line .
        with open(self.filepath, "w", encoding="utf-8") as file:
            json.dump(data, file, indent=2)


    # This method checks if the filepath is existing, if not, like if we just started the
    # programe it makes the (self.budgets) an empty list and return it.
    def load_budgets(self):
        if not os.path.exists(self.filepath):
            self.budgets = []
            return

        # If the filepath is already existing then we open the file to read it "r" using "utf-8"
        # and we transefer the included data in the file to JSON using json.load(file)
        try:
            with open(self.filepath, "r", encoding="utf-8") as file:
                data = json.load(file)
                self.budgets = [Budget.from_dict(item) for item in data]

        # if there is an error in reading files or an osError we make the list
        # empty to avoid programe crashing
        except (json.JSONDecodeError, OSError):
            self.budgets = []
