import math


def display_menu(inventory: dict) -> None:
    """Prints the divider, title, current inventory in Item ID order, and menu options."""
    print("==================================================")
    print("            LUXELEND RENTAL STUDIO               ")
    print("==================================================")
    print("Current Catalog:")
    print(f"{'ID':<6} {'Brand':<18} {'Category':<10} {'Rate':<8} {'Deposit':<10} {'Status':<10}")
    print("-" * 65)
    
    # Iterate in sorted Item ID order
    for item_id in sorted(inventory.keys()):
        item = inventory[item_id]
        print(
            f"{item_id:<6} {item['brand']:<18} {item['category']:<10} "
            f"Rs {item['rate']:<5} Rs {item['deposit']:<7} {item['status']:<10}"
        )
    
    print("-" * 65)
    print("1. Rent Item")
    print("2. Return Item")
    print("3. Exit")
    print("==================================================")


def is_valid_menu_choice(raw: str) -> bool:
    """Returns True only if raw is exactly '1', '2', or '3'."""
    return raw in ("1", "2", "3")


def get_menu_choice() -> int:
    """Prompts 'Enter choice: ', re-prompting on invalid input, and returns choice as int."""
    while True:
        raw = input("Enter choice: ")
        if is_valid_menu_choice(raw):
            return int(raw)
        print("Invalid choice.")


def get_id(prompt: str) -> str:
    """Prompts for a Customer ID or Item ID and returns raw string, unvalidated."""
    return input(prompt)


def get_membership(prompt: str) -> bool:
    """Prompts for membership and returns True only if stripped, lower-cased input is 'y'."""
    raw = input(prompt)
    return raw.strip().lower() == "y"


def is_valid_rental_days(raw: str) -> bool:
    """Returns True only if raw is a whole integer string from 1 to 30 inclusive."""
    if not raw.isdigit():
        return False
    val = int(raw)
    return 1 <= val <= 30


def get_rental_days(prompt: str) -> int | None:
    """Prompts for rental days, printing error and returning None on invalid input."""
    raw = input(prompt)
    if not is_valid_rental_days(raw):
        print("Rental days must be a whole number from 1 to 30.")
        return None
    return int(raw)


def is_valid_days_late(raw: str) -> bool:
    """Returns True only if raw is a whole integer string from 0 to 365 inclusive."""
    if not raw.isdigit():
        return False
    val = int(raw)
    return 0 <= val <= 365


def get_days_late(prompt: str) -> int | None:
    """Prompts for days late, printing error and returning None on invalid input."""
    raw = input(prompt)
    if not is_valid_days_late(raw):
        print("Days late must be a whole number from 0 to 365.")
        return None
    return int(raw)


def is_valid_condition(raw: str) -> bool:
    """Returns True if raw case-insensitively is good, stained, torn, or incomplete."""
    return raw.strip().lower() in {"good", "stained", "torn", "incomplete"}


def get_condition(prompt: str) -> str | None:
    """Prompts for condition, printing error and returning None on invalid input."""
    raw = input(prompt)
    if not is_valid_condition(raw):
        print("Invalid condition.")
        return None
    return raw.strip().lower()


def round_half_up(n: float) -> int:
    """Utility function to round half-up as required by the spec."""
    return math.floor(n + 0.5)


def compute_rental_fee(rate: int, days: int) -> int:
    """Returns Rs rental fee: rate * days."""
    return rate * days


def compute_discount(price: int, is_member: bool) -> int:
    """Returns 20% of price (rounded half-up) if is_member, else 0."""
    if is_member:
        return round_half_up(0.20 * price)
    return 0


def compute_late_fee(deposit: int, days_late: int) -> int:
    """Returns Rs late fee: round_half_up(0.10 * deposit * days_late)."""
    return round_half_up(0.10 * deposit * days_late)


def compute_damage_fee(deposit: int, condition: str) -> int:
    """Returns Rs damage fee for condition, rounded half-up."""
    pct_map = {
        "good": 0.00,
        "stained": 0.30,
        "torn": 0.60,
        "incomplete": 1.00
    }
    damage_pct = pct_map.get(condition, 0.0)
    return round_half_up(damage_pct * deposit)


def is_suspended(customer_id: str, customer_incidents: dict) -> bool:
    """Returns True if customer_incidents holds 3 or more incidents for customer_id."""
    return customer_incidents.get(customer_id, 0) >= 3


def record_incident(customer_id: str, customer_incidents: dict) -> None:
    """Increments the incident count for customer_id."""
    customer_incidents[customer_id] = customer_incidents.get(customer_id, 0) + 1


def format_rental_bill(customer_id: str, item_id: str, brand: str, category: str,
                       rate: int, days: int, rental_fee: int, discount: int,
                       deposit: int, total_due: int) -> str:
    """Builds the exact RENTAL BILL text block."""
    return (
        "\n----------------------------------------\n"
        "             RENTAL BILL                \n"
        "----------------------------------------\n"
        f"Customer ID : {customer_id}\n"
        f"Item ID     : {item_id} ({brand} {category})\n"
        f"Rate        : Rs {rate}/day\n"
        f"Days        : {days}\n"
        f"Rental Fee  : Rs {rental_fee}\n"
        f"Discount    : Rs {discount}\n"
        f"Deposit     : Rs {deposit}\n"
        "----------------------------------------\n"
        f"TOTAL DUE   : Rs {total_due}\n"
        "----------------------------------------"
    )


def format_return_receipt(customer_id: str, item_id: str, brand: str, category: str,
                         deposit: int, days_late: int, late_fee: int,
                         condition: str, damage_fee: int, refund: int) -> str:
    """Builds the exact RETURN RECEIPT text block."""
    return (
        "\n----------------------------------------\n"
        "            RETURN RECEIPT              \n"
        "----------------------------------------\n"
        f"Customer ID     : {customer_id}\n"
        f"Item ID         : {item_id} ({brand} {category})\n"
        f"Deposit Held    : Rs {deposit}\n"
        f"Days Late       : {days_late}\n"
        f"Late Fee        : Rs {late_fee}\n"
        f"Condition       : {condition}\n"
        f"Damage Fee      : Rs {damage_fee}\n"
        "----------------------------------------\n"
        f"DEPOSIT REFUNDED: Rs {refund}\n"
        "----------------------------------------"
    )


def rent_item(inventory: dict, customer_incidents: dict) -> None:
    """Runs the Rent Item flow."""
    customer_id = get_id("Customer ID: ")
    
    # Check suspension
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
    brand = inventory[item_id]["brand"]
    category = inventory[item_id]["category"]

    fee = compute_rental_fee(rate, days)
    discount = compute_discount(fee, is_member)
    total = fee - discount + deposit

    # Update state
    inventory[item_id]["status"] = "Rented"

    # Output receipt
    bill = format_rental_bill(
        customer_id, item_id, brand, category, rate, days, fee, discount, deposit, total
    )
    print(bill)


def return_item(inventory: dict, customer_incidents: dict) -> None:
    """Runs the Return Item flow."""
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
    brand = inventory[item_id]["brand"]
    category = inventory[item_id]["category"]

    late_fee = compute_late_fee(deposit, days_late)
    damage_fee = compute_damage_fee(deposit, condition)
    refund = max(0, deposit - late_fee - damage_fee)

    # Track incident
    if days_late > 0 or condition != "good":
        record_incident(customer_id, customer_incidents)

    # Update item state
    if days_late == 0 and condition == "good":
        inventory[item_id]["status"] = "Available"
    else:
        inventory[item_id]["status"] = "Cleaning"

    # Output receipt
    receipt = format_return_receipt(
        customer_id, item_id, brand, category, deposit, days_late, late_fee, condition, damage_fee, refund
    )
    print(receipt)


def main() -> None:
    """Initializes catalog and runs menu loop until exit."""
    inventory: dict[str, dict] = {
        "B01": {"brand": "Louis Vuitton", "category": "Bag", "rate": 800, "deposit": 8000, "status": "Available"},
        "B02": {"brand": "Chanel", "category": "Bag", "rate": 900, "deposit": 9000, "status": "Available"},
        "B03": {"brand": "Gucci", "category": "Bag", "rate": 750, "deposit": 7500, "status": "Available"},
        "D01": {"brand": "Dior", "category": "Dress", "rate": 1200, "deposit": 12000, "status": "Available"},
        "D02": {"brand": "Prada", "category": "Dress", "rate": 1100, "deposit": 11000, "status": "Available"},
        "D03": {"brand": "Versace", "category": "Dress", "rate": 1300, "deposit": 13000, "status": "Available"},
        "W01": {"brand": "Rolex", "category": "Watch", "rate": 2000, "deposit": 20000, "status": "Available"},
        "W02": {"brand": "Cartier", "category": "Watch", "rate": 1800, "deposit": 18000, "status": "Available"},
        "J01": {"brand": "Tiffany & Co.", "category": "Jewelry", "rate": 1500, "deposit": 15000, "status": "Available"},
        "J02": {"brand": "Bvlgari", "category": "Jewelry", "rate": 1600, "deposit": 16000, "status": "Available"},
    }

    customer_incidents: dict[str, int] = {}

    while True:
        display_menu(inventory)
        choice = get_menu_choice()

        if choice == 1:
            rent_item(inventory, customer_incidents)
        elif choice == 2:
            return_item(inventory, customer_incidents)
        elif choice == 3:
            print("Goodbye!")
            break

        input("\nPress Enter to continue...")


if __name__ == "__main__":
    main()