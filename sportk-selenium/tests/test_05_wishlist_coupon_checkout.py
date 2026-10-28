"""TC_Wishlist + TC_MaGiamGia + TC_Checkout (phần Selenium được – KHÔNG tự động hoá popup Razorpay)."""
import pytest
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from helpers import *


def wl_items(d):
    return d.find_elements(By.CSS_SELECTOR, "img[alt]:not([alt='logo'])")


def fav(d, pid):
    spa_goto(d, f"/description/{pid}")
    wait(d).until(EC.element_to_be_clickable((By.XPATH, "//button[contains(.,'ADD TO FAVOURITE')]"))).click()


# ---------------- Wishlist ----------------
def test_WL_01_them_vao_wishlist(logged_in):
    d = logged_in; fav(d, 1)
    wait(d).until(lambda x: badges(x)[0] >= 1)
    spa_goto(d, "/wishlist")
    wait(d).until(lambda x: "Air Runner M" in x.find_element(By.TAG_NAME, "body").text)


def test_WL_02_them_trung(logged_in):
    d = logged_in; fav(d, 1); import time; time.sleep(1); fav(d, 1); time.sleep(1)
    assert badges(d)[0] == 1


def test_WL_06_giu_wishlist_sau_F5(logged_in):
    d = logged_in; fav(d, 1)
    wait(d).until(lambda x: badges(x)[0] >= 1)
    goto(d, "/wishlist"); d.refresh()
    wait(d).until(lambda x: "Air Runner M" in x.find_element(By.TAG_NAME, "body").text)


# ---------------- Checkout helpers ----------------
def prepare_cart_and_checkout(d):
    add_to_cart(d, 1, 6); add_to_cart(d, 1, 6); add_to_cart(d, 2, 6)
    spa_goto(d, "/checkout")
    wait(d).until(EC.visibility_of_element_located((By.CSS_SELECTOR, "input[placeholder='First Name*']")))


FORM = {"First Name*": "An", "Last Name*": "Nguyen", "Address Line 1*": "12 Le Loi",
        "Town/City*": "Bac Giang", "Pin Code*": "220000", "State/Territory*": "BG",
        "Country*": "VN", "Email*": "an@example.com", "Mobile*": "0912345678"}


def fill_checkout(d, **override):
    data = {**FORM, **override}
    for ph, v in data.items():
        el = d.find_element(By.CSS_SELECTOR, f"input[placeholder='{ph}']")
        el.send_keys("\u0001", "\ue003")
        if v: el.send_keys(v)


def press_order(d):
    d.find_element(By.CSS_SELECTOR, "button[type='submit']").click()


# ---------------- Mã giảm giá ----------------
def coupon_box(d):
    return d.find_element(By.CSS_SELECTOR, "input[placeholder='Enter Your Promo Code']")


def apply_coupon(d, code):
    coupon_box(d).send_keys(code)
    d.find_element(By.CSS_SELECTOR, ".chakra-input__right-element button").click()


@pytest.fixture
def at_checkout(logged_in):
    prepare_cart_and_checkout(logged_in)
    return logged_in


@pytest.mark.parametrize("code,pct", [("family5", 5), ("family10", 10), ("family15", 15),
                                      ("family20", 20), ("family25", 25), ("family30", 30)])
def test_CPN_01_ap_tung_ma(at_checkout, code, pct):
    d = at_checkout
    apply_coupon(d, code)
    assert wait_toast(d, "Coupon Applied")
    total_before = 1798000                       # giá bán của giỏ mẫu (xem CART-08)
    discount = summary_value(d, "DISCOUNT")
    assert abs(discount - total_before * pct / 100) <= total_before * 0.005, \
        f"{code}: DISCOUNT={discount}, kỳ vọng ≈ {total_before * pct / 100:.0f}"


def test_CPN_03_ma_khong_hop_le(at_checkout):
    apply_coupon(at_checkout, "abc123")
    assert wait_toast(at_checkout, "invalid") or wait_toast(at_checkout, "not valid", 2)


def test_CPN_04_ma_viet_hoa(at_checkout):
    apply_coupon(at_checkout, "FAMILY10")
    assert wait_toast(at_checkout, "Coupon Applied", 4), "Mã viết hoa không được chấp nhận (code so sánh ===)"


def test_CPN_05_ma_co_khoang_trang(at_checkout):
    apply_coupon(at_checkout, "family10 ")
    assert wait_toast(at_checkout, "Coupon Applied", 4)


def test_CPN_07_go_ma(at_checkout):
    d = at_checkout; apply_coupon(d, "family10")
    wait_toast(d, "Coupon Applied")
    d.find_element(By.CSS_SELECTOR, ".chakra-input__right-element button").click()
    assert wait_toast(d, "Coupon Removed")


def test_CPN_08_khong_cong_don_ma(at_checkout):
    d = at_checkout; apply_coupon(d, "family10"); wait_toast(d, "Coupon Applied")
    assert not coupon_box(d).is_enabled()


# ---------------- Checkout ----------------
def test_CO_01_chua_dang_nhap(driver):
    goto(driver, "/checkout"); wait(driver).until(EC.url_contains("/login"))


def test_CO_03_order_summary(at_checkout):
    body = at_checkout.find_element(By.TAG_NAME, "body").text
    assert "2.248.000" in body and "1.798.000" in body and "3" in body


def test_CO_04_de_trong_tat_ca(at_checkout):
    press_order(at_checkout)
    assert wait_toast(at_checkout, "Please fill the mandatory details")


@pytest.mark.parametrize("ph,val,msg", [
    ("Town/City*", "", "Please fill the mandatory details"),
    ("First Name*", "an", "First latter should be Capital"),
    ("Last Name*", "nguyen", "First latter should be Capital"),
    ("Email*", "an@example", "valid email"),
    ("Pin Code*", "12345", "6 digit"),
    ("Mobile*", "091234567", "10 digit"),
])
def test_CO_05_to_10_validate_form(at_checkout, ph, val, msg):
    fill_checkout(at_checkout, **{ph: val}); press_order(at_checkout)
    assert wait_toast(at_checkout, msg)


def test_CO_09_pincode_co_chu(at_checkout):
    """Ô Pin Code là type=number: trình duyệt tự bỏ chữ cái ('12ab56' -> '1256') rồi form báo thiếu chữ số."""
    d = at_checkout
    fill_checkout(d, **{"Pin Code*": "12ab56"})
    value = d.find_element(By.CSS_SELECTOR, "input[placeholder='Pin Code*']").get_attribute("value")
    assert not any(c.isalpha() for c in value), f"Pin Code chứa chữ: {value}"
    press_order(d)
    assert wait_toast(d, "6 digit")


def test_CO_18_back_to_cart(at_checkout):
    click_button(at_checkout, "BACK TO CART")
    wait(at_checkout).until(EC.url_contains("/cart"))
