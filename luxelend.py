"""
luxelend.py
LuxeLend Rental Studio - core logic ONLY.

Rules for this file (from the project instructions):
  * no print()   * no input()
  * no changing global variables
  * never mutating the arguments it receives (we return NEW values instead)
"""

import math

DIVIDER = "-" * 32

SUSPENSION_THRESHOLD = 3
ALLOWED_CONDITIONS = {"good", "stained", "torn", "incomplete"}
DAMAGE_PERCENT = {"good": 0.00, "stained": 0.30, "torn": 0.60, "incomplete": 1.00}


# ---------------------------------------------------------------- helpers
def round_half_up(value):
    """Python's round() rounds 2.5 -> 2 (banker's rounding). PRD wants half-up."""
    return math.floor(value + 0.5)


def build_inventory():
    """Returns a brand-new catalog of 10 items (all Available)."""
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


# ------------------------------------------------------------- validation
def is_valid_menu_choice(raw):
    """FR1: exactly '1', '2' or '3'."""
    return raw in ("1", "2", "3")


def _is_whole_number_in_range(raw, low, high):
    # isascii() stops odd characters like '²' that isdigit() accepts
    # but int() cannot convert.
    if not (raw.isascii() and raw.isdigit()):
        return False
    return low <= int(raw) <= high


def is_valid_rental_days(raw):
    """FR8: whole number 1 to 30."""
    return _is_whole_number_in_range(raw, 1, 30)


def is_valid_days_late(raw):
    """FR8: whole number 0 to 365."""
    return _is_whole_number_in_range(raw, 0, 365)


def is_valid_condition(raw):
    """FR8: good/stained/torn/incomplete, any capitalisation."""
    return raw.strip().lower() in ALLOWED_CONDITIONS


def normalize_condition(raw):
    """'  STAINED ' -> 'stained'."""
    return raw.strip().lower()


def parse_membership(raw):
    """Only 'y' (any case, spaces ignored) means member. Anything else = no."""
    return raw.strip().lower() == "y"


# ------------------------------------------------------- inventory checks
def item_exists(inventory, item_id):
    return item_id in inventory


def is_item_available(inventory, item_id):
    return item_id in inventory and inventory[item_id]["status"] == "Available"


def is_item_rented(inventory, item_id):
    return item_id in inventory and inventory[item_id]["status"] == "Rented"


def set_item_status(inventory, item_id, new_status):
    """Returns a COPY of inventory with one item's status changed.
    The original inventory is left untouched."""
    new_inventory = {key: dict(value) for key, value in inventory.items()}
    new_inventory[item_id]["status"] = new_status
    return new_inventory


# ----------------------------------------------------------- calculations
def compute_rental_fee(rate, days):
    """FR2."""
    return rate * days


def compute_discount(price, is_member):
    """FR6: 20% of the rental fee for members (deposit is never discounted)."""
    if is_member:
        return round_half_up(0.20 * price)
    return 0


def compute_total_due(fee, discount, deposit):
    return fee - discount + deposit


def compute_late_fee(deposit, days_late):
    """FR3: 10% of deposit per late day."""
    return round_half_up(0.10 * deposit * days_late)


def compute_damage_fee(deposit, condition):
    """FR3: percentage of deposit depending on condition."""
    return round_half_up(DAMAGE_PERCENT[condition] * deposit)


def compute_refund(deposit, late_fee, damage_fee):
    """FR3: never below zero."""
    return max(0, deposit - late_fee - damage_fee)


def status_after_return(days_late, condition):
    """Available only if on time AND good, else Cleaning."""
    if days_late == 0 and condition == "good":
        return "Available"
    return "Cleaning"


# -------------------------------------------------- incidents (FR7 / EC9)
def is_incident(days_late, condition):
    """A return is an incident if late OR not in good condition."""
    return days_late > 0 or condition != "good"


def is_suspended(customer_id, customer_incidents):
    return customer_incidents.get(customer_id, 0) >= SUSPENSION_THRESHOLD


def record_incident(customer_id, customer_incidents):
    """Returns a NEW dict with this customer's count + 1."""
    updated = dict(customer_incidents)
    updated[customer_id] = updated.get(customer_id, 0) + 1
    return updated


# -------------------------------------------------------------- formatting
def format_inventory_row(item_id, item):
    return (
        f"  {item_id}  {item['brand']}  {item['category']}  "
        f"Rs{item['rate']}/day  Deposit Rs{item['deposit']}   {item['status']}"
    )


def format_menu(inventory):
    """Builds the whole menu text (inventory in Item ID order)."""
    lines = [DIVIDER, "      LUXELEND RENTAL STUDIO", DIVIDER, "", "Inventory:"]
    for item_id in sorted(inventory.keys()):
        lines.append(format_inventory_row(item_id, inventory[item_id]))
    lines += ["", "1. Rent Item", "2. Return Item", "3. Exit"]
    return "\n".join(lines)


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
