# LuxeLend Rental Studio

A command-line app for a designer rental studio. It manages an inventory of luxury bags, outfits, jewelry and watches (Louis Vuitton, Chanel, Dior, Prada, Fendi, Coach, Hermes, Cartier, Rolex, YSL) and handles the two customer transactions: **renting** an item and **returning** it.

## Features

- **Live inventory:** each item is `Available`, `Rented` or `Cleaning`, and its status updates after every transaction.
- **Rental pricing:** fee = daily rate x days, plus a refundable security deposit.
- **Membership discount:** members get 20% off the rental fee (the deposit is never discounted).
- **Return settlement:** late fees and damage fees are taken from the deposit, and the remainder is refunded.
- **Suspension system:** a customer with 3 or more late or damaged returns is blocked from renting for the rest of the session.
- **Input validation:** invalid menu choices, rental days, days late, conditions and item IDs print an exact error message and ask again.
- **Exact output format:** the menu, rental bill and return receipt follow the PRD character for character.

## Project structure

| File | Role |
|---|---|
| `main.py` | The menu and **all** `input()` / `print()`. Run this file. |
| `luxelend.py` | Core logic as **pure functions** (validation, calculations, rules, text formatting). No printing, no input, no global changes, no mutated arguments. |
| `test_luxelend.py` | 41 unit tests covering every logic function. |

## Requirements

- Python 3.8 or newer
- No external libraries (standard library only)

## How to run

1. Put the three files in the same folder.
2. Open a terminal in that folder.
3. Start the app:

```
python main.py
```

(On Mac/Linux use `python3 main.py`.)

## How to run the tests

```
python -m unittest test_luxelend -v
```

All 41 tests should pass and the last line should read `OK`. You can also run a single test class:

```
python -m unittest test_luxelend.TestCalculations -v
```

## Example session

```
--------------------------------
      LUXELEND RENTAL STUDIO
--------------------------------

Inventory:
  B01  Louis Vuitton  Bag  Rs800/day  Deposit Rs8000   Available
  ...

1. Rent Item
2. Return Item
3. Exit
Enter choice: 1
Customer ID: CU100
Are you a member? (y/n): n
Item ID: C01
Rental days: 4
--------------------------------
          RENTAL BILL
--------------------------------
Customer ID: CU100
Item ID:     C01
Brand:       Coach
Category:    Bag

Rental days:      4
Rental fee:       Rs 1200
Member discount:  Rs 0
Security deposit: Rs 3000
--------------------------------
TOTAL DUE:        Rs 4200
--------------------------------
Press Enter to return to menu.
```

## Formulas

All amounts are whole rupees. Percentages use **half-up rounding** (`floor(x + 0.5)`), because Python's built-in `round()` rounds 2.5 down to 2.

| Value | Formula |
|---|---|
| Rental fee | `rate x days` |
| Member discount | `round_half_up(0.20 x rental_fee)` for members, otherwise `0` |
| Total due | `rental_fee - discount + deposit` |
| Late fee | `round_half_up(0.10 x deposit x days_late)` |
| Damage fee | `round_half_up(damage_pct x deposit)` |
| Refund | `max(0, deposit - late_fee - damage_fee)` |

Damage percentages: `good` 0%, `stained` 30%, `torn` 60%, `incomplete` 100%.

### Rules

- A return is an **incident** if `days_late > 0` or the condition is not `good`.
- After a return, the item becomes `Available` only if it was on time **and** good. Otherwise it becomes `Cleaning`.
- Rental days must be a whole number from 1 to 30. Days late must be a whole number from 0 to 365.

## Design notes

- **Two-file split:** `main.py` handles everything the user sees and types, and `luxelend.py` handles everything that can be calculated or checked. This makes the logic easy to test without typing any input.
- **Pure functions:** functions that "change" data (`set_item_status`, `record_incident`) copy it, change the copy and return it. `main()` replaces its old variable with the new one.
- **Data structures:** a `dict` for the inventory and for customer incident counts (fast lookup by ID), and a `set` for the allowed conditions (fast membership test).

## Limitations

- Inventory and incident history live in memory only, so they reset every time the program restarts.
- The incident threshold (3) and the damage and discount percentages are assumptions from the PRD, pending confirmation with the studio.

## Authors

Add your team members' names here.
