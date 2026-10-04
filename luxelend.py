"""
luxelend.py
LuxeLend Rental Studio — core logic.

Every function here maps 1:1 to a row in the Design Doc's "Function Signatures"
table (Section 4), and its steps follow the matching "Function-Level Algorithm"
(Section 5). Comments reference the PRD's FR/EC numbers where relevant.
"""

import math

DIVIDER = "-" * 32  # PRD Output Format: "A divider is always exactly 32 dashes"

ALLOWED_CONDITIONS = {"good", "stained", "torn", "incomplete"}

DAMAGE_PERCENT = {
    "good": 0.00,
    "stained": 0.30,
    "torn": 0.60,
    "incomplete": 1.00,
}


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def round_half_up(value):
    """
    True half-up rounding.

    NOTE: Python's built-in round() uses banker's rounding (round-half-to-even),
    e.g. round(2.5) == 2, not 3. The PRD/Design Doc specify half-up rounding for
    every Rs formula, so we implement it explicitly instead of relying on round().
    Safe for our use since every value here (money, days) is non-negative.
    """
    return math.floor(value + 0.5)


def build_inventory():
    """The studio's fixed catalog of 10 items. Never added to or removed from
    at runtime — only each item's 'status' field changes (Design Doc, Section 2)."""
    return {
        "B01": {"brand": "Louis Vuitton", "category": "Bag", "rate": 800, "deposit": 8000, "status": "Available"},
        "B02": {"brand": "Chanel", "category": "Bag", "rate": 900, "deposit": 9000, "status": "Available"},
        "C01": {"brand": "Coach", "category": "Bag", "rate": 300, "deposit": 3000, "status": "Available"},
        "CT01": {"brand": "Cartier", "category": "Jewelry", "rate": 1200, "deposit": 12000, "status": "Available"},
        "D01": {"brand": "Dior", "category": "Outfit", "rate": 600, "deposit": 6000, "status": "Available"},
        "F01": {"brand": "Fendi", "category": "Bag", "rate": 650, "deposit": 6500, "status": "Available"},
        "H01": {"brand": "Hermes", "category": "Bag", "rate": 1500, "deposit": 15000, "status": "Available"},
        "P01": {"brand": "Prada", "category": "Bag", "rate": 700, "deposit": 7000, "status": "Available"},
        "R01": {"brand": "Rolex", "category": "Watch", "rate": 2000, "deposit": 20000, "status": "Available"},
        "Y01": {"brand": "YSL", "category": "Outfit", "rate": 500, "deposit": 5000, "status": "Available"},
    }


# ---------------------------------------------------------------------------
# Menu
# ---------------------------------------------------------------------------

def display_menu(inventory):
    """Prints the divider, title, current inventory in Item ID order, and the
    three menu options. All items are listed regardless of status (PRD, Main menu)."""
    print(DIVIDER)
    print("      LUXELEND RENTAL STUDIO")
    print(DIVIDER)
    print()
    print("Inventory:")
    for item_id in sorted(inventory.keys()):  # "in Item ID order" (lexicographic)
        item = inventory[item_id]
        print(
            f"  {item_id}  {item['brand']}  {item['category']}  "
            f"Rs{item['rate']}/day  Deposit Rs{item['deposit']}   {item['status']}"
        )
    print()
    print("1. Rent Item")
    print("2. Return Item")
    print("3. Exit")


def is_valid_menu_choice(raw):
    """FR1: only exactly '1', '2', or '3' — no decimals, signs, leading zeros, text."""
    return raw in ("1", "2", "3")


def get_menu_choice():
    """Prompts 'Enter choice: ', re-prompting on invalid input (FR1 / EC1)."""
    while True:
        raw = input("Enter choice: ")
        if is_valid_menu_choice(raw):
            return int(raw)
        print("Invalid choice.")


# ---------------------------------------------------------------------------
# Generic input getters
# ---------------------------------------------------------------------------

def get_id(prompt):
    """FR5: Customer ID / Item ID are free-form strings, accepted with no
    format validation."""
    return input(prompt)


def get_membership(prompt):
    """Design Doc 'Membership answer': only a stripped, lower-cased 'y' counts
    as member. Anything else (including 'n', blank, or a typo) is non-member,
    with no error printed."""
    raw = input(prompt)
    return raw.strip().lower() == "y"


def is_valid_rental_days(raw):
    """FR8: whole integer from 1 to 30 inclusive. No decimals, signs, or text."""
    if not raw.isdigit():
        return False
    value = int(raw)
    return 1 <= value <= 30


def get_rental_days(prompt):
    """Returns None on invalid input — caller aborts the transaction (FR8 / EC3)."""
    raw = input(prompt)
    if not is_valid_rental_days(raw):
        print("Rental days must be a whole number from 1 to 30.")
        return None
    return int(raw)


def is_valid_days_late(raw):
    """FR8: whole integer from 0 to 365 inclusive."""
    if not raw.isdigit():
        return False
    value = int(raw)
    return 0 <= value <= 365


def get_days_late(prompt):
    """Returns None on invalid input — caller aborts the transaction (FR8 / EC4)."""
    raw = input(prompt)
    if not is_valid_days_late(raw):
        print("Days late must be a whole number from 0 to 365.")
        return None
    return int(raw)


def is_valid_condition(raw):
    """FR8: case-insensitively one of good/stained/torn/incomplete."""
    return raw.strip().lower() in ALLOWED_CONDITIONS


def get_condition(prompt):
    """Returns None on invalid input — caller aborts the transaction (FR8 / EC5)."""
    raw = input(prompt)
    if not is_valid_condition(raw):
        print("Invalid condition.")
        return None
    return raw.strip().lower()


# ---------------------------------------------------------------------------
# Pure computation functions
# ---------------------------------------------------------------------------

def compute_rental_fee(rate, days):
    """FR2: rental_fee = rate * days."""
    return rate * days


def compute_discount(price, is_member):
    """FR6: 20% off, half-up, if the customer is a member; else 0.
    The deposit is never discounted — this is applied to price (the fee) only."""
    if is_member:
        return round_half_up(0.20 * price)
    return 0


def compute_late_fee(deposit, days_late):
    """FR3: 10% of the deposit per day late, half-up."""
    return round_half_up(0.10 * deposit * days_late)


def compute_damage_fee(deposit, condition):
    """FR3: percentage of deposit based on condition, half-up."""
    pct = DAMAGE_PERCENT[condition]
    return round_half_up(pct * deposit)


# ---------------------------------------------------------------------------
# Incident tracking & suspension (FR7)
# ---------------------------------------------------------------------------

def is_suspended(customer_id, customer_incidents):
    """True once a Customer ID has 3 or more incidents this run."""
    return customer_incidents.get(customer_id, 0) >= 3


def record_incident(customer_id, customer_incidents):
    """Increments the incident count for customer_id, creating the entry if absent."""
    customer_incidents[customer_id] = customer_incidents.get(customer_id, 0) + 1


# ---------------------------------------------------------------------------
# Bill / receipt formatting
# ---------------------------------------------------------------------------

def format_rental_bill(customer_id, item_id, brand, category, days, fee, discount, deposit, total):
    lines = [
        DIVIDER,
        "          RENTAL BILL",
        DIVIDER,
        f"Customer ID: {customer_id}",
        f"Item ID:     {item_id}",
        f"Brand:       {brand}",
        f"Category:    {category}",
        "",
        f"Rental days:      {days}",
        f"Rental fee:       Rs {fee}",
        f"Member discount:  Rs {discount}",
        f"Security deposit: Rs {deposit}",
        DIVIDER,
        f"TOTAL DUE:        Rs {total}",
        DIVIDER,
        "Press Enter to return to menu.",
    ]
    return "\n".join(lines)


def format_return_receipt(customer_id, item_id, condition, days_late, late_fee, damage_fee, deposit, refund):
    lines = [
        DIVIDER,
        "         RETURN RECEIPT",
        DIVIDER,
        f"Customer ID: {customer_id}",
        f"Item ID:     {item_id}",
        f"Condition:   {condition}",
        "",
        f"Days late:        {days_late}",
        f"Late fee:         Rs {late_fee}",
        f"Damage fee:       Rs {damage_fee}",
        f"Deposit held:     Rs {deposit}",
        DIVIDER,
        f"DEPOSIT REFUNDED: Rs {refund}",
        DIVIDER,
        "Press Enter to return to menu.",
    ]
    return "\n".join(lines)


# ---------------------------------------------------------------------------
# Transactions
# ---------------------------------------------------------------------------

def rent_item(inventory, customer_incidents):
    """FR2 + FR4 + FR7: runs the Rent Item prompts, validates input, checks
    suspension and availability, computes fee/discount/deposit, prints the
    bill, and updates inventory."""
    customer_id = get_id("Customer ID: ")

    if is_suspended(customer_id, customer_incidents):
        print("Customer is suspended due to repeated incidents.")
        return

    is_member = get_membership("Are you a member? (y/n): ")
    item_id = get_id("Item ID: ")

    if item_id not in inventory:
        print("Invalid ID.")
        return

    if inventory[item_id]["status"] != "Available":
        print("That item is not currently available.")
        return

    days = get_rental_days("Rental days: ")
    if days is None:
        return

    rate = inventory[item_id]["rate"]
    deposit = inventory[item_id]["deposit"]

    fee = compute_rental_fee(rate, days)
    discount = compute_discount(fee, is_member)
    total = fee - discount + deposit

    inventory[item_id]["status"] = "Rented"

    print(format_rental_bill(
        customer_id, item_id, inventory[item_id]["brand"], inventory[item_id]["category"],
        days, fee, discount, deposit, total,
    ))


def return_item(inventory, customer_incidents):
    """FR3 + FR7: runs the Return Item prompts, validates input, computes
    late/damage fees and refund, updates inventory status and
    customer_incidents, and prints the receipt."""
    customer_id = get_id("Customer ID: ")
    item_id = get_id("Item ID: ")

    if item_id not in inventory or inventory[item_id]["status"] != "Rented":
        print("Invalid ID.")
        return

    days_late = get_days_late("Days late (0 if on time): ")
    if days_late is None:
        return

    condition = get_condition("Condition (good/stained/torn/incomplete): ")
    if condition is None:
        return

    deposit = inventory[item_id]["deposit"]
    late_fee = compute_late_fee(deposit, days_late)
    damage_fee = compute_damage_fee(deposit, condition)
    refund = max(0, deposit - late_fee - damage_fee)

    if days_late > 0 or condition != "good":
        record_incident(customer_id, customer_incidents)

    if days_late == 0 and condition == "good":
        inventory[item_id]["status"] = "Available"
    else:
        inventory[item_id]["status"] = "Cleaning"

    print(format_return_receipt(
        customer_id, item_id, condition, days_late, late_fee, damage_fee, deposit, refund,
    ))


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

def main():
    """Initializes state and runs the menu loop until the user exits (Program Flow)."""
    inventory = build_inventory()
    customer_incidents = {}

    while True:
        display_menu(inventory)
        choice = get_menu_choice()

        if choice == 1:
            rent_item(inventory, customer_incidents)
            input()
        elif choice == 2:
            return_item(inventory, customer_incidents)
            input()
        elif choice == 3:
            print("Goodbye!")
            break
