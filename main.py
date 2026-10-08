"""
main.py
LuxeLend Rental Studio - the menu and ALL input()/print().
All calculations and checks live in luxelend.py.

Run with:  python main.py
"""

import luxelend as ll


# ------------------------------------------------ input helpers (re-prompt)
def ask_menu_choice():
    while True:
        raw = input("Enter choice: ")
        if ll.is_valid_menu_choice(raw):
            return int(raw)
        print("Invalid choice.")


def ask_rental_days():
    while True:
        raw = input("Rental days: ")
        if ll.is_valid_rental_days(raw):
            return int(raw)
        print("Rental days must be a whole number from 1 to 30.")


def ask_days_late():
    while True:
        raw = input("Days late (0 if on time): ")
        if ll.is_valid_days_late(raw):
            return int(raw)
        print("Days late must be a whole number from 0 to 365.")


def ask_condition():
    while True:
        raw = input("Condition (good/stained/torn/incomplete): ")
        if ll.is_valid_condition(raw):
            return ll.normalize_condition(raw)
        print("Invalid condition.")


# ------------------------------------------------------------ transactions
def rent_item(inventory, customer_incidents):
    """Returns the (possibly updated) inventory."""
    customer_id = input("Customer ID: ")

    if ll.is_suspended(customer_id, customer_incidents):
        print("Customer is suspended due to repeated incidents.")
        return inventory

    is_member = ll.parse_membership(input("Are you a member? (y/n): "))
    item_id = input("Item ID: ")

    if not ll.item_exists(inventory, item_id):
        print("Invalid ID.")
        return inventory
    if not ll.is_item_available(inventory, item_id):
        print("That item is not currently available.")
        return inventory

    days = ask_rental_days()

    item = inventory[item_id]
    fee = ll.compute_rental_fee(item["rate"], days)
    discount = ll.compute_discount(fee, is_member)
    total = ll.compute_total_due(fee, discount, item["deposit"])

    inventory = ll.set_item_status(inventory, item_id, "Rented")

    print(ll.format_rental_bill(
        customer_id, item_id, item["brand"], item["category"],
        days, fee, discount, item["deposit"], total))
    return inventory


def return_item(inventory, customer_incidents):
    """Returns the (inventory, customer_incidents) pair after the return."""
    customer_id = input("Customer ID: ")
    item_id = input("Item ID: ")

    if not ll.is_item_rented(inventory, item_id):
        print("Invalid ID.")
        return inventory, customer_incidents

    days_late = ask_days_late()
    condition = ask_condition()

    deposit = inventory[item_id]["deposit"]
    late_fee = ll.compute_late_fee(deposit, days_late)
    damage_fee = ll.compute_damage_fee(deposit, condition)
    refund = ll.compute_refund(deposit, late_fee, damage_fee)

    if ll.is_incident(days_late, condition):
        customer_incidents = ll.record_incident(customer_id, customer_incidents)

    new_status = ll.status_after_return(days_late, condition)
    inventory = ll.set_item_status(inventory, item_id, new_status)

    print(ll.format_return_receipt(
        customer_id, item_id, condition, days_late, late_fee, damage_fee, deposit, refund))
    return inventory, customer_incidents


# -------------------------------------------------------------------- main
def main():
    inventory = ll.build_inventory()
    customer_incidents = {}

    while True:
        print(ll.format_menu(inventory))
        choice = ask_menu_choice()

        if choice == 1:
            inventory = rent_item(inventory, customer_incidents)
            input()
        elif choice == 2:
            inventory, customer_incidents = return_item(inventory, customer_incidents)
            input()
        else:
            print("Goodbye!")
            break


if __name__ == "__main__":
    main()
