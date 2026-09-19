# Date time is a module or lib that is used for dates like (yy,mm,dd)
# date is the class that holds this date data .
# If the user didnt enter a date, it gets the date automaticlly.
from datetime import date

# Expense is the class that holds the expenses for every buying operation.
class Expense:
    # This is the constructor of the class.
    def __init__(self, amount, category, note, date_str=None):
        # Those are some variables used in to get attributes.
        self.amount = amount
        self.category = category
        self.note = note
        # This is the variable that takes the date automaticlly if the user didnt
        # enter it.
        self.date_str = date_str if date_str else date.today().strftime("%Y-%m-%d")


    # This is the func that coverts the object to a dict
    # because the json files doesnt understand python classes, but dict.
    def to_dict(self):
        return {
            "amount": self.amount,
            "category": self.category,
            "note": self.note,
            "date": self.date_str,
        }

    
    @staticmethod
    def from_dict(data):
        return Expense(data["amount"], data["category"], data["note"], data["date"])

    # This function return the values of the class 
    # (.2f) means it will make the number be printed with two digits after the dot 
    # ex. (25.55), (99.45)
    def __str__(self):
        return f"{self.date_str} | {self.category} | {self.amount:.2f} | {self.note}"
