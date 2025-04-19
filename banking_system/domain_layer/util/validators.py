"""
This file holds the validator class that holds methods, all predicates for common validation issues that cut accross the account and transaction classes
"""


#to keep things simple, use validator function for now
#TODO when multiple functions are created, use one class to simplify imports 

def float_greater_than_zero(value:float) -> bool :
    print(f"Validating if {value} is greater than zero.")
    if value > 0:
        print("Validation passed.")
        return True
    else:
        print("Validation failed.")
        return False

