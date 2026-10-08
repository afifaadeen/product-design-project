"""
test_luxelend.py - unit tests for every function in luxelend.py.
Run with:  python -m unittest test_luxelend -v
"""

import unittest
import luxelend as ll


class TestRounding(unittest.TestCase):
    def test_half_goes_up(self):
        self.assertEqual(ll.round_half_up(2.5), 3)   # built-in round gives 2

    def test_below_half_goes_down(self):
        self.assertEqual(ll.round_half_up(2.4), 2)

    def test_whole_number(self):
        self.assertEqual(ll.round_half_up(5.0), 5)


class TestBuildInventory(unittest.TestCase):
    def test_has_10_items_all_available(self):
        inv = ll.build_inventory()
        self.assertEqual(len(inv), 10)
        self.assertTrue(all(i["status"] == "Available" for i in inv.values()))

    def test_coach_values(self):
        c01 = ll.build_inventory()["C01"]
        self.assertEqual((c01["brand"], c01["rate"], c01["deposit"]), ("Coach", 300, 3000))

    def test_returns_fresh_copy_each_time(self):
        a = ll.build_inventory()
        a["C01"]["status"] = "Rented"
        self.assertEqual(ll.build_inventory()["C01"]["status"], "Available")


class TestMenuChoice(unittest.TestCase):
    def test_valid(self):
        for raw in ("1", "2", "3"):
            self.assertTrue(ll.is_valid_menu_choice(raw))

    def test_invalid_EC1(self):
        for raw in ("abc", "0", "4", "-1", "2.0", "01", "", " 1", "1 "):
            self.assertFalse(ll.is_valid_menu_choice(raw), raw)


class TestRentalDays(unittest.TestCase):
    def test_valid(self):
        for raw in ("1", "15", "30"):
            self.assertTrue(ll.is_valid_rental_days(raw))

    def test_invalid_EC3(self):
        for raw in ("0", "31", "45", "-3", "2.5", "abc", "", "²"):
            self.assertFalse(ll.is_valid_rental_days(raw), raw)


class TestDaysLate(unittest.TestCase):
    def test_valid(self):
        for raw in ("0", "7", "365"):
            self.assertTrue(ll.is_valid_days_late(raw))

    def test_invalid_EC4(self):
        for raw in ("-1", "366", "1.5", "abc", "", "²"):
            self.assertFalse(ll.is_valid_days_late(raw), raw)


class TestCondition(unittest.TestCase):
    def test_valid_any_case(self):
        for raw in ("good", "STAINED", " Torn ", "Incomplete"):
            self.assertTrue(ll.is_valid_condition(raw))

    def test_invalid_EC5(self):
        for raw in ("ripped", "", "goood"):
            self.assertFalse(ll.is_valid_condition(raw))

    def test_normalize(self):
        self.assertEqual(ll.normalize_condition("  STAINED "), "stained")


class TestMembership(unittest.TestCase):
    def test_yes(self):
        for raw in ("y", "Y", " y "):
            self.assertTrue(ll.parse_membership(raw))

    def test_everything_else_is_no(self):
        for raw in ("n", "", "yes", "maybe"):
            self.assertFalse(ll.parse_membership(raw))


class TestInventoryChecks(unittest.TestCase):
    def setUp(self):
        self.inv = ll.build_inventory()
        self.inv["D01"]["status"] = "Rented"
        self.inv["Y01"]["status"] = "Cleaning"

    def test_item_exists(self):
        self.assertTrue(ll.item_exists(self.inv, "C01"))
        self.assertFalse(ll.item_exists(self.inv, "Z99"))   # EC6

    def test_is_item_available(self):
        self.assertTrue(ll.is_item_available(self.inv, "C01"))
        self.assertFalse(ll.is_item_available(self.inv, "D01"))   # EC7
        self.assertFalse(ll.is_item_available(self.inv, "Y01"))   # Cleaning
        self.assertFalse(ll.is_item_available(self.inv, "Z99"))

    def test_is_item_rented(self):
        self.assertTrue(ll.is_item_rented(self.inv, "D01"))
        self.assertFalse(ll.is_item_rented(self.inv, "C01"))      # EC8
        self.assertFalse(ll.is_item_rented(self.inv, "Z99"))

    def test_set_item_status_changes_copy_only(self):
        new = ll.set_item_status(self.inv, "C01", "Rented")
        self.assertEqual(new["C01"]["status"], "Rented")
        self.assertEqual(self.inv["C01"]["status"], "Available")  # original untouched


class TestCalculations(unittest.TestCase):
    def test_rental_fee_FR2(self):
        self.assertEqual(ll.compute_rental_fee(300, 4), 1200)

    def test_discount_member_FR6(self):
        self.assertEqual(ll.compute_discount(1800, True), 360)

    def test_discount_non_member(self):
        self.assertEqual(ll.compute_discount(1800, False), 0)

    def test_discount_rounds_half_up(self):
        self.assertEqual(ll.compute_discount(12, True), 2)   # 2.4 -> 2
        self.assertEqual(ll.compute_discount(2, True), 0)    # 0.4 -> 0

    def test_total_due(self):
        self.assertEqual(ll.compute_total_due(1800, 360, 6000), 7440)
        self.assertEqual(ll.compute_total_due(1200, 0, 3000), 4200)

    def test_late_fee_FR3(self):
        self.assertEqual(ll.compute_late_fee(6000, 2), 1200)
        self.assertEqual(ll.compute_late_fee(6000, 0), 0)

    def test_damage_fee_FR3(self):
        self.assertEqual(ll.compute_damage_fee(6000, "good"), 0)
        self.assertEqual(ll.compute_damage_fee(6000, "stained"), 1800)
        self.assertEqual(ll.compute_damage_fee(6000, "torn"), 3600)
        self.assertEqual(ll.compute_damage_fee(6000, "incomplete"), 6000)

    def test_refund_normal(self):
        self.assertEqual(ll.compute_refund(6000, 1200, 1800), 3000)

    def test_refund_full_EC10(self):
        self.assertEqual(ll.compute_refund(5000, 0, 0), 5000)

    def test_refund_never_negative(self):
        self.assertEqual(ll.compute_refund(5000, 4000, 5000), 0)

    def test_status_after_return(self):
        self.assertEqual(ll.status_after_return(0, "good"), "Available")
        self.assertEqual(ll.status_after_return(1, "good"), "Cleaning")
        self.assertEqual(ll.status_after_return(0, "stained"), "Cleaning")


class TestIncidents(unittest.TestCase):
    def test_is_incident(self):
        self.assertFalse(ll.is_incident(0, "good"))
        self.assertTrue(ll.is_incident(1, "good"))
        self.assertTrue(ll.is_incident(0, "torn"))

    def test_is_suspended_FR7(self):
        self.assertFalse(ll.is_suspended("A", {}))
        self.assertFalse(ll.is_suspended("A", {"A": 2}))
        self.assertTrue(ll.is_suspended("A", {"A": 3}))
        self.assertTrue(ll.is_suspended("A", {"A": 5}))
        self.assertFalse(ll.is_suspended("B", {"A": 3}))

    def test_record_incident_new_customer(self):
        self.assertEqual(ll.record_incident("A", {}), {"A": 1})

    def test_record_incident_existing_customer(self):
        self.assertEqual(ll.record_incident("A", {"A": 2}), {"A": 3})

    def test_record_incident_does_not_mutate(self):
        original = {"A": 1}
        ll.record_incident("A", original)
        self.assertEqual(original, {"A": 1})


class TestFormatting(unittest.TestCase):
    def test_inventory_row(self):
        row = ll.format_inventory_row("C01", ll.build_inventory()["C01"])
        self.assertEqual(row, "  C01  Coach  Bag  Rs300/day  Deposit Rs3000   Available")

    def test_menu_is_sorted_and_complete(self):
        menu = ll.format_menu(ll.build_inventory())
        self.assertTrue(menu.startswith("-" * 32 + "\n      LUXELEND RENTAL STUDIO"))
        self.assertTrue(menu.endswith("1. Rent Item\n2. Return Item\n3. Exit"))
        self.assertLess(menu.index("B01"), menu.index("CT01"))
        self.assertLess(menu.index("C01"), menu.index("CT01"))

    def test_rental_bill(self):
        bill = ll.format_rental_bill("CU100", "C01", "Coach", "Bag", 4, 1200, 0, 3000, 4200)
        self.assertIn("Rental fee:       Rs 1200", bill)
        self.assertIn("TOTAL DUE:        Rs 4200", bill)
        self.assertTrue(bill.endswith("Press Enter to return to menu."))

    def test_return_receipt(self):
        r = ll.format_return_receipt("CU101", "D01", "stained", 2, 1200, 1800, 6000, 3000)
        self.assertIn("Late fee:         Rs 1200", r)
        self.assertIn("DEPOSIT REFUNDED: Rs 3000", r)


if __name__ == "__main__":
    unittest.main()
