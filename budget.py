# Budget is the class that asks and saves your budget like "foor budget", 'edu budget'
class Budget:
    # This is the constuctor holds name of the budget and its amount
    def __init__(self, name, amount):
        self.name = name
        self.amount = amount


    # This method returns a dict of items (keys : values) 
    # keys is "name", "amount"
    # values is (self.name), (self.amount)
    def to_dict(self):
        return {"name": self.name, "amount": self.amount}



    @staticmethod
    def from_dict(data):
        return Budget(data["name"], data["amount"])


    # This method returns the values
    def __str__(self):
        return f"{self.name} | {self.amount:.2f}"
