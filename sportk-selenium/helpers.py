"""Hàm dùng chung. App KHÔNG có data-testid nên selector dựa vào id, placeholder, text."""
import re
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from config import BASE_URL, TIMEOUT, USER


def wait(d, t=TIMEOUT):
    return WebDriverWait(d, t)


def goto(d, path):
    """Tải lại toàn bộ trang (F5). Redux store bị reset -> GIỎ HÀNG MẤT (xem BUG-09)."""
    d.get(BASE_URL + path)


def spa_goto(d, path):
    """Điều hướng trong SPA, KHÔNG reload -> giữ giỏ hàng trong Redux."""
    d.execute_script(
        "window.history.pushState({}, '', arguments[0]);"
        "window.dispatchEvent(new PopStateEvent('popstate'));", path)


def clear_session(d):
    d.get(BASE_URL + "/")
    d.execute_script("localStorage.clear(); sessionStorage.clear();")
    d.get(BASE_URL + "/")


def ls(d, key):
    return d.execute_script("return localStorage.getItem(arguments[0]);", key)


# ---------- toast (Chakra) ----------
def toasts(d):
    """Đọc textContent (không phụ thuộc opacity) – .text của Selenium trả về rỗng khi toast đang mờ."""
    return d.execute_script(
        "return [...document.querySelectorAll('.chakra-alert')].map(e => e.textContent.trim()).filter(Boolean);")


def wait_toast(d, text, t=TIMEOUT):
    """Chờ có toast chứa `text` (không phân biệt hoa thường). Poll 0.1s vì toast chỉ hiện ~2s."""
    try:
        WebDriverWait(d, t, poll_frequency=0.1).until(
            lambda x: any(text.lower() in s.lower() for s in toasts(x)))
        return True
    except Exception:
        return False


# ---------- form ----------
def type_into(d, css, value):
    el = wait(d).until(EC.visibility_of_element_located((By.CSS_SELECTOR, css)))
    el.clear()
    # clear() không kích hoạt onChange của React ở mọi trường hợp -> xoá bằng phím
    el.send_keys("\u0001", "\ue003")   # Ctrl+A, Backspace
    if value:
        el.send_keys(value)


def click_button(d, text):
    wait(d).until(EC.element_to_be_clickable(
        (By.XPATH, f"//button[normalize-space()='{text}']"))).click()


def fill_register(d, name="", username="", email="", password="", mobile=""):
    for css, v in (("#Name", name), ("#username", username), ("#email", email),
                   ("#password", password), ("#mobile", mobile)):
        type_into(d, css, v)


def login_ui(d, email=USER["email"], password=USER["password"]):
    goto(d, "/login")
    type_into(d, "#username", email)     # ô Email có id="username"
    type_into(d, "#password", password)
    click_button(d, "Sign in")


def login_and_wait(d):
    login_ui(d)
    wait(d).until(lambda x: ls(x, "token"))


# ---------- sản phẩm / giỏ ----------
def product_cards(d):
    return d.find_elements(By.CSS_SELECTOR, "img.imageAnimation")


def wait_products(d, minimum=1):
    wait(d).until(lambda x: len(product_cards(x)) >= minimum)


def add_to_cart(d, product_id, size):
    """Mở /description/<id> bằng SPA-nav, chọn size, bấm ADD TO BAG."""
    spa_goto(d, f"/description/{product_id}")
    wait(d).until(EC.element_to_be_clickable(
        (By.XPATH, f"//button[normalize-space()='{size}']"))).click()
    click_button(d, "ADD TO BAG")


def badges(d):
    """[wishlist, cart] – hai ô số tròn trên Navbar."""
    els = d.find_elements(
        By.XPATH, "//div[contains(@class,'Navbar')]//p[normalize-space()!='' "
                  "and translate(normalize-space(.),'0123456789','')='']")
    return [int(e.text) for e in els]


def vnd_to_int(text):
    """'1.798.000 ₫' -> 1798000"""
    return int(re.sub(r"[^\d]", "", text))


def summary_value(d, label):
    """Đọc giá trị (số nguyên VNĐ) cạnh nhãn trong ORDER SUMMARY: ORIGINAL PRICE / DISCOUNT / TOTAL.
    Cấu trúc app: một Stack chứa các nhãn, Stack kế bên chứa giá trị cùng thứ tự."""
    lab = d.find_element(By.XPATH, f"//p[normalize-space()='{label}']")
    idx = len(lab.find_elements(By.XPATH, "preceding-sibling::*")) + 1
    val = lab.find_element(By.XPATH, f"../following-sibling::*[1]/*[{idx}]")
    return vnd_to_int(val.text) if re.search(r"\d", val.text) else 0
