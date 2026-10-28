"""TC_ChiTiet + TC_GioHang. Chú ý: giỏ chỉ nằm trong Redux -> dùng spa_goto, KHÔNG dùng goto."""
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from helpers import *


def open_detail(d, pid=1):
    goto(d, f"/description/{pid}")
    wait(d).until(EC.visibility_of_element_located((By.TAG_NAME, "h2")))


def cart_lines(d):
    return d.find_elements(By.XPATH, "//p[starts-with(normalize-space(.),'SIZE :')]")


def qty_buttons(d, row=0):
    row_el = cart_lines(d)[row].find_element(By.XPATH, "./ancestor::div[.//button][3]")
    b = row_el.find_elements(By.TAG_NAME, "button")
    return b[0], b[1]      # [−, +]


# ---------------- Chi tiết ----------------
def test_DET_01_thong_tin_chi_tiet(driver):
    goto(driver, "/allproducts"); wait_products(driver)
    driver.find_element(By.CSS_SELECTOR, "img[alt='Air Runner M']").click()
    wait(driver).until(EC.url_contains("/description/1"))
    body = driver.find_element(By.TAG_NAME, "body").text
    assert "Air Runner M" in body and "712.000" in body and "562.000" in body


def test_DET_02_chua_chon_size(driver):
    open_detail(driver)
    btn = driver.find_element(By.XPATH, "//button[contains(.,'Please Select A Size')]")
    assert not btn.is_enabled() or btn.get_attribute("disabled") is not None


def test_DET_03_chon_size_them_gio(driver):
    open_detail(driver)
    driver.find_element(By.XPATH, "//button[normalize-space()='6']").click()
    click_button(driver, "ADD TO BAG")
    assert wait_toast(driver, "Item added to your bag")
    assert badges(driver)[-1] == 1


def test_DET_04_them_yeu_thich(logged_in):
    d = logged_in
    spa_goto(d, "/description/1"); wait(d).until(EC.visibility_of_element_located((By.TAG_NAME, "h2")))
    before = badges(d)[0]
    d.find_element(By.XPATH, "//button[contains(.,'ADD TO FAVOURITE')]").click()
    wait(d).until(lambda x: badges(x)[0] == before + 1)


def test_DET_07_anh_san_pham_khong_vo(driver):
    open_detail(driver)
    import time; time.sleep(1)
    bad = driver.execute_script(
        "return [...document.images].filter(i=>!i.complete||i.naturalWidth===0).map(i=>i.src)")
    assert bad == []


def test_DET_08_quy_doi_vnd(driver):
    exp = {1: ("712.000", "562.000"), 2: ("824.000", "674.000")}
    for pid, (orig, final) in exp.items():
        open_detail(driver, pid)
        body = driver.find_element(By.TAG_NAME, "body").text
        assert orig in body and final in body, f"id={pid}"


# ---------------- Giỏ hàng ----------------
def test_CART_01_gio_trong(driver):
    goto(driver, "/cart")
    wait(driver).until(EC.visibility_of_element_located((By.TAG_NAME, "h2")))
    assert not driver.find_elements(By.XPATH, "//button[normalize-space()='CHECKOUT']")


def test_CART_02_them_mot_san_pham(driver):
    goto(driver, "/"); add_to_cart(driver, 1, 6)
    spa_goto(driver, "/cart")
    wait(driver).until(lambda d: len(cart_lines(d)) == 1)
    assert "TOTAL [1 items]" in driver.find_element(By.TAG_NAME, "body").text
    assert badges(driver)[-1] == 1


def test_CART_03_cung_san_pham_cung_size(driver):
    goto(driver, "/"); add_to_cart(driver, 1, 6); add_to_cart(driver, 1, 6)
    spa_goto(driver, "/cart")
    wait(driver).until(lambda d: len(cart_lines(d)) >= 1)
    assert len(cart_lines(driver)) == 1
    assert "TOTAL [2 items]" in driver.find_element(By.TAG_NAME, "body").text


def test_CART_04_cung_san_pham_khac_size(driver):
    goto(driver, "/"); add_to_cart(driver, 1, 6); add_to_cart(driver, 1, 7)
    spa_goto(driver, "/cart")
    wait(driver).until(lambda d: len(cart_lines(d)) >= 1)
    assert len(cart_lines(driver)) == 2


def test_CART_05_06_07_tang_giam_so_luong(driver):
    goto(driver, "/"); add_to_cart(driver, 1, 6); spa_goto(driver, "/cart")
    wait(driver).until(lambda d: len(cart_lines(d)) == 1)
    minus, plus = qty_buttons(driver)
    plus.click()
    wait(driver).until(lambda d: "TOTAL [2 items]" in d.find_element(By.TAG_NAME, "body").text)
    minus, plus = qty_buttons(driver); minus.click()
    wait(driver).until(lambda d: "TOTAL [1 items]" in d.find_element(By.TAG_NAME, "body").text)
    minus, plus = qty_buttons(driver); minus.click()          # SL=1 -> xoá dòng
    wait(driver).until(lambda d: len(cart_lines(d)) == 0)


def test_CART_08_tinh_tong_tien(driver):
    goto(driver, "/")
    add_to_cart(driver, 1, 6); add_to_cart(driver, 1, 6); add_to_cart(driver, 2, 6)
    spa_goto(driver, "/cart")
    wait(driver).until(lambda d: len(cart_lines(d)) == 2)
    body = driver.find_element(By.TAG_NAME, "body").text
    assert "TOTAL [3 items]" in body
    assert "2.248.000" in body and "1.798.000" in body


def test_CART_09_giu_gio_sau_F5(driver):
    goto(driver, "/"); add_to_cart(driver, 1, 6); spa_goto(driver, "/cart")
    wait(driver).until(lambda d: len(cart_lines(d)) == 1)
    driver.refresh()
    import time; time.sleep(1.5)
    assert len(cart_lines(driver)) == 1, "Giỏ hàng mất sau F5 (nghi vấn BUG-09)"


def test_CART_10_badge_navbar(driver):
    goto(driver, "/")
    add_to_cart(driver, 1, 6); add_to_cart(driver, 1, 6); add_to_cart(driver, 2, 6)
    assert badges(driver)[-1] == 3


def test_CART_11_chua_dang_nhap_bam_checkout(driver):
    goto(driver, "/"); add_to_cart(driver, 1, 6); spa_goto(driver, "/cart")
    wait(driver).until(lambda d: len(cart_lines(d)) == 1)
    click_button(driver, "CHECKOUT")
    wait(driver).until(EC.url_contains("/login"))
