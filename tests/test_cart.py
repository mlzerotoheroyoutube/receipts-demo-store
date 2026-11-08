import pytest

from store import Cart, CouponError, Item


def mug():
    return Item("MUG", "Mug", 1200)


def tee():
    return Item("TEE", "T-shirt", 2500)


def test_subtotal_sums_lines():
    cart = Cart()
    cart.add(mug())
    cart.add(tee())
    assert cart.subtotal_cents() == 3700


def test_adding_same_sku_merges_qty():
    cart = Cart()
    cart.add(mug())
    cart.add(mug())
    assert len(cart.items) == 1
    assert cart.items[0].qty == 2


def test_remove_line():
    cart = Cart()
    cart.add(mug())
    cart.add(mug())
    cart.add(tee())
    cart.remove("MUG")
    assert cart.subtotal_cents() == 2500


def test_percent_coupon_single_item():
    cart = Cart()
    cart.add(tee())
    cart.apply_coupon("SAVE10")
    assert cart.discount_cents() == 250


def test_percent_coupon_applies_to_every_line():
    cart = Cart()
    cart.add(mug())
    cart.add(tee())
    cart.apply_coupon("SAVE10")
    assert cart.discount_cents() == 370


def test_percent_coupon_includes_quantities():
    cart = Cart()
    cart.add(Item("MUG", "Mug", 1200, qty=2))
    cart.add(tee())
    cart.apply_coupon("SAVE10")
    # Subtotal is 4900, so 10% off the whole subtotal is 490.
    assert cart.discount_cents() == 490


def test_percent_coupon_rounds_down():
    cart = Cart()
    cart.add(Item("ODD", "Odd priced", 1005))
    cart.apply_coupon("SAVE10")
    # 10% of 1005 is 100.5, rounded down to the cent.
    assert cart.discount_cents() == 100


def test_second_coupon_rejected():
    cart = Cart()
    cart.add(tee())
    cart.apply_coupon("SAVE10")
    with pytest.raises(CouponError):
        cart.apply_coupon("FIVEOFF")


def test_fixed_coupon_needs_minimum():
    cart = Cart()
    cart.add(mug())
    cart.apply_coupon("FIVEOFF")
    assert cart.discount_cents() == 0


def test_shipping_charged_on_small_order():
    cart = Cart()
    cart.add(mug())
    assert cart.shipping_cents() == 599


def test_free_shipping_on_big_order():
    cart = Cart()
    cart.add(Item("JKT", "Jacket", 8000))
    assert cart.shipping_cents() == 0


def test_free_shipping_at_exact_threshold():
    cart = Cart()
    cart.add(Item("BOX", "Box", 5000))
    assert cart.shipping_cents() == 0


def test_tax_rounds_half_up():
    cart = Cart()
    cart.add(Item("PEN", "Pen", 1006))  # 8% of 1006 = 80.48 -> 80
    assert cart.tax_cents() == 80


def test_total():
    cart = Cart()
    cart.add(mug())
    # 1200 + 599 shipping + 96 tax
    assert cart.total_cents() == 1895
