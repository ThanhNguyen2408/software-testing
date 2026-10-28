"""TC_DangNhap"""
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from helpers import *
from config import USER


def test_LOG_01_dang_nhap_thanh_cong(driver):
    login_ui(driver)
    assert wait_toast(driver, "Login Success")
    wait(driver).until(lambda d: d.current_url.rstrip("/").endswith("3000"))
    assert ls(driver, "token") and ls(driver, "userInfo")


def test_LOG_02_sai_mat_khau(driver):
    login_ui(driver, password="Sai#1234")
    assert wait_toast(driver, "Wrong email or password")
    # BUG-13 nghi vấn: toast hiện 2 lần -> đếm toast trùng nội dung
    import time; time.sleep(1)
    n = sum("wrong email" in t.lower() for t in toasts(driver))
    assert n == 1, f"Có {n} toast lỗi cùng lúc (kỳ vọng 1)"
    assert "/login" in driver.current_url and not ls(driver, "token")


def test_LOG_03_email_khong_ton_tai(driver):
    login_ui(driver, email="khongco@example.com")
    assert wait_toast(driver, "Wrong email or password")
    assert "/login" in driver.current_url


def test_LOG_04_de_trong(driver):
    goto(driver, "/login")
    type_into(driver, "#username", "")
    type_into(driver, "#password", "")
    click_button(driver, "Sign in")
    assert toasts(driver) or wait_toast(driver, "fill", 3), \
        "Không có thông báo khi để trống (nghi vấn BUG-12)"


def test_LOG_05_hien_an_mat_khau(driver):
    goto(driver, "/login")
    type_into(driver, "#password", "123456")
    pw = driver.find_element(By.CSS_SELECTOR, "#password")
    eye = driver.find_element(By.CSS_SELECTOR, ".chakra-input__right-element button")
    eye.click(); assert pw.get_attribute("type") == "text"
    eye.click(); assert pw.get_attribute("type") == "password"


def test_LOG_06_checkout_chua_dang_nhap_roi_quay_lai(driver):
    goto(driver, "/checkout")
    wait(driver).until(EC.url_contains("/login"))
    type_into(driver, "#username", USER["email"])
    type_into(driver, "#password", USER["password"])
    click_button(driver, "Sign in")
    wait(driver).until(EC.url_contains("/checkout"))


def test_LOG_07_wishlist_chua_dang_nhap(driver):
    goto(driver, "/wishlist")
    wait(driver).until(EC.url_contains("/login"))


def test_LOG_08_giu_phien_sau_F5(logged_in):
    d = logged_in
    d.refresh()
    goto(d, "/wishlist")
    assert "/login" not in d.current_url


def test_LOG_09_dang_xuat(logged_in):
    d = logged_in
    goto(d, "/")
    wait(d).until(EC.element_to_be_clickable((By.CSS_SELECTOR, ".Navbar button.chakra-menu__menu-button"))).click()
    wait(d).until(EC.element_to_be_clickable((By.XPATH, "//button[@role='menuitem' and contains(.,'Logout')]"))).click()
    wait(d).until(lambda x: ls(x, "token") is None)
    assert ls(d, "userInfo") is None
    goto(d, "/wishlist")
    wait(d).until(lambda x: "/login" in x.current_url or x.current_url.rstrip("/").endswith("3000"))


def test_LOG_11_sql_injection(driver):
    login_ui(driver, email="' OR '1'='1", password="' OR '1'='1")
    assert wait_toast(driver, "Wrong email or password")
    assert not ls(driver, "token")
