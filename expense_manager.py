# json is the module that is made for reading (JSON files) and save it.
import json
# os is made for interacting with the operating system, like creating files 
# and directories, management of files and directories and process management. 
import os
# This import the class that we made in file(expense.py)
from expense import Expense

# This class is made for mangging all the expenses of the user.
class ExpenseManager:
    # This is the constructor that takes the file path that we will save in it
    # the expense objects by using an empty list and saving expense obj in it.
    # (self.load_expenses()) is made for that if there was data that is already
    # saved before, it will load it when the object is made.
    def __init__(self, filepath="expenses.json"):
        self.filepath = filepath
        self.expenses = []
        self.load_expenses()

    # This method is used to make a new expense or add a new expense and appends
    # it to the (self.expenses) list and saves it and returns the new expense 
    def add_expense(self, amount, category, note):
        new_expense = Expense(amount, category, note)
        self.expenses.append(new_expense)
        self.save_expenses()
        return new_expense

    # This method is used to delete a expense that we added by a condition 
    # the condition makes sure that the expense is in the list, if true, it will 
    # delete it and then we save the update we did . 
    def delete_expense(self, index):
        if 0 <= index < len(self.expenses):
            del self.expenses[index]
            self.save_expenses()

    # Total amount spent across every expense.
    def total_spent(self):
        return sum(expense.amount for expense in self.expenses)


    # This method edit or change in the expense if there is something wrong or want to be edited from the user.
    def update_expense(self, index, amount=None, category=None, note=None, date=None):
        # this checks if the index that was sent is in the list or not.
        if 0 <= index < len(self.expenses):
            # This gets the real object not a copy to edit on it.
            expense = self.expenses[index]

            # THis if codition works if the user sent a budget amount it will change it, if not, it will keep it as it was.
            if amount is not None:
                expense.amount = amount
            # THis if codition works if the user sent a budget category it will change it, if not, it will keep it as it was.
            if category is not None:
                expense.category = category
            # THis if codition works if the user sent a budget note it will change it, if not, it will keep it as it was.
            if note is not None:
                expense.note = note
            # THis if codition works if the user sent a budget date it will change it, if not, it will keep it as it was.
            if date is not None:
                expense.date = date

            # this method changes the code into a dict to save it in a JSON file to read it and save it .
            self.save_expenses()
            return expense
        return None


    # Returns a dictionary like {"Food": 120.0, "Transport": 45.0, ...}
    def total_by_category(self):
        totals = {}
        for expense in self.expenses:
            totals[expense.category] = totals.get(expense.category, 0) + expense.amount
        return totals

    # Returns only the expenses matching a given category.
    def filter_by_category(self, category):
        return [expense for expense in self.expenses if expense.category == category]

    # This method saves the expenses in the JSON file
    def save_expenses(self):
        # (data) varianle transefers the expenses objects to a list of dictionaries by using 
        # to_dict() to make JSON file read it correctly. 
        data = [expense.to_dict() for expense in self.expenses]

        # opens the file to write using "w" and "utf-8" and (json.dumb()) writes 
        # the data into the file and (indent=2) makes the reading of the file much
        # easier by making 2 spaces before each line .
        with open(self.filepath, "w", encoding="utf-8") as file:
            json.dump(data, file, indent=2)


    # This method checks if the filepath is existing, if not, like if we just started the
    # programe it makes the (self.expenses) an empty list and return it.
    def load_expenses(self):
        if not os.path.exists(self.filepath):
            self.expenses = []
            return

        
        # If the filepath is already existing then we open the file to read it "r" using "utf-8"
        # and we transefer the included data in the file to JSON using json.load(file)

        try:
            with open(self.filepath, "r", encoding="utf-8") as file:
                data = json.load(file)
                self.expenses = [Expense.from_dict(item) for item in data]

        # if there is an error in reading files or an osError we make the list
        # empty to avoid programe crashing
        except (json.JSONDecodeError, OSError):
            self.expenses = []
