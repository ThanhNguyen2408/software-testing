"""TC_DangKy – tên hàm bắt buộc dạng test_REG_01_... để script export map về Excel."""
import pytest
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from helpers import *

VALID = dict(name="Nguyen", username="nguyen01", email="nguyen01@example.com",
             password="Abc#1234", mobile="0912345678")


def open_register(d):
    goto(d, "/register")
    wait(d).until(EC.visibility_of_element_located((By.CSS_SELECTOR, "#Name")))


def submit(d, **override):
    open_register(d)
    fill_register(d, **{**VALID, **override})
    click_button(d, "Sign up")


def test_REG_01_dang_ky_hop_le(driver):
    import time
    email = f"nguyen{int(time.time())}@example.com"      # email mới mỗi lần chạy
    submit(driver, email=email)
    assert wait_toast(driver, "Registered Successful")
    wait(driver).until(EC.url_contains("/login"))


def test_REG_02_de_trong_tat_ca(driver):
    open_register(driver)
    click_button(driver, "Sign up")
    assert wait_toast(driver, "Please fill all the details")


@pytest.mark.parametrize("field", ["name", "username", "email", "password", "mobile"])
def test_REG_03_de_trong_tung_truong(driver, field):
    submit(driver, **{field: ""})
    assert wait_toast(driver, "Please fill all the details")


def test_REG_04_ten_khong_viet_hoa(driver):
    submit(driver, name="nguyen")
    assert wait_toast(driver, "First latter should be Capital")


def test_REG_05_email_thieu_a_cong(driver):
    # type="email" của ô input có thể chặn submit ở mức HTML5 -> kiểm tra cả 2 khả năng
    submit(driver, email="nguyen01example.com")
    assert wait_toast(driver, "valid email")


def test_REG_06_email_thieu_ten_mien(driver):
    submit(driver, email="nguyen01@example")
    assert wait_toast(driver, "valid email")


def test_REG_07_mat_khau_ngan(driver):
    submit(driver, password="Ab#1")
    assert wait_toast(driver, "at least 6 characters")


def test_REG_08_mat_khau_dai(driver):
    submit(driver, password="Abcdefgh#12345678")
    assert wait_toast(driver, "not more than 16 characters")


def test_REG_09_mat_khau_thieu_chu_hoa(driver):
    submit(driver, password="abc#1234")
    assert wait_toast(driver, "upper case"), "Kỳ vọng báo lỗi chữ hoa (nghi vấn BUG-01)"


@pytest.mark.parametrize("pw,msg", [("Abcdef#g", "number"), ("Abcd1234", "special character")])
def test_REG_10_mat_khau_thieu_so_hoac_ky_tu_dac_biet(driver, pw, msg):
    submit(driver, password=pw)
    assert wait_toast(driver, msg)


def test_REG_11_sdt_thieu_chu_so(driver):
    submit(driver, mobile="091234567")
    assert wait_toast(driver, "10 digit")


def test_REG_12_sdt_chua_chu_cai(driver):
    # ô type="number" của trình duyệt có thể không cho gõ chữ -> gõ 'e' vẫn lọt
    submit(driver, mobile="09123abcde")
    assert not ls(driver, "token") and "/login" not in driver.current_url, \
        "SĐT chứa chữ không được phép đăng ký (nghi vấn BUG-14)"


def test_REG_13_email_da_ton_tai(driver):
    submit(driver, email="test@example.com")
    assert wait_toast(driver, "User already exists")
    assert "/register" in driver.current_url


def test_REG_14_hien_an_mat_khau(driver):
    open_register(driver)
    type_into(driver, "#password", "Abc#1234")
    eye = driver.find_element(By.CSS_SELECTOR, ".chakra-input__right-element button")
    pw = driver.find_element(By.CSS_SELECTOR, "#password")
    assert pw.get_attribute("type") == "password"
    eye.click();  assert pw.get_attribute("type") == "text"
    eye.click();  assert pw.get_attribute("type") == "password"
