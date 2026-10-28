"""TC_LocSapXep. Số lượng mong đợi lấy từ db.json (28 sản phẩm)."""
import requests, pytest
from selenium.webdriver.common.by import By
from helpers import *
from config import API_URL


def open_section(d, title):
    """Accordion của Chakra mặc định đóng -> mở mục (Category/Color/Gender/Rating)."""
    btn = d.find_element(By.XPATH, f"//button[contains(@class,'chakra-accordion__button')][contains(.,'{title}')]")
    if btn.get_attribute("aria-expanded") != "true":
        btn.click()


def _click_when_ready(d, section, xpath):
    """Mở mục, ĐỢI animation mở xong (phần tử clickable) rồi mới click -> hết lỗi 'not interactable'."""
    import time
    from selenium.webdriver.support import expected_conditions as EC
    open_section(d, section)
    el = wait(d).until(EC.element_to_be_clickable((By.XPATH, xpath)))
    el.click()
    time.sleep(1.0)          # đợi trang gọi API + render lại danh sách


def tick(d, section, value):
    _click_when_ready(d, section,
        f"//label[contains(@class,'chakra-checkbox')][.//input[@value='{value}']]")


def untick(d, section, value):
    tick(d, section, value)   # click lần nữa = bỏ chọn


def count_after(d, expected=None, t=8):
    """Đợi danh sách ổn định rồi trả về số thẻ."""
    import time; time.sleep(1.2)
    return len(product_cards(d))


def test_FIL_01_hien_thi_tat_ca(driver):
    goto(driver, "/allproducts"); wait_products(driver)
    assert count_after(driver) == 28


@pytest.mark.parametrize("path,n,key", [("/men", 14, "MEN"), ("/women", 14, "WOMEN"), ("/shoes", 16, None)])
def test_FIL_02_03_04_trang_theo_nhom(driver, path, n, key):
    goto(driver, path); wait_products(driver)
    assert count_after(driver) == n
    if key:
        genders = [e.text for e in driver.find_elements(By.XPATH, f"//p[.='MEN' or .='WOMEN']")]
        assert all(g == key for g in genders)


def test_FIL_05_loc_category(driver):
    goto(driver, "/allproducts"); wait_products(driver)
    tick(driver, "Category", "clothes");  assert count_after(driver) == 12
    untick(driver, "Category", "clothes")
    tick(driver, "Category", "shoes");    assert count_after(driver) == 16
    tick(driver, "Category", "clothes");  assert count_after(driver) == 28


def test_FIL_06_loc_mau_black_khop_API(driver):
    goto(driver, "/allproducts"); wait_products(driver)
    tick(driver, "Color", "black")
    api = len(requests.get(f"{API_URL}/allproducts", params={"colortype": "black"}).json())
    assert count_after(driver) == api == 7


def test_FIL_07_hai_mau(driver):
    goto(driver, "/allproducts"); wait_products(driver)
    tick(driver, "Color", "red"); tick(driver, "Color", "blue")
    assert count_after(driver) == 14


def test_FIL_08_ket_hop(driver):
    goto(driver, "/allproducts"); wait_products(driver)
    tick(driver, "Category", "shoes"); tick(driver, "Gender", "MEN")
    assert count_after(driver) == 8
    untick(driver, "Gender", "MEN"); tick(driver, "Gender", "WOMEN"); tick(driver, "Color", "white")
    assert count_after(driver) == 2


def test_FIL_09_size_small(driver):
    pytest.skip("Bộ lọc Size đã bị comment trong FilterData.jsx -> chức năng chưa có trên giao diện")


def test_FIL_10_sap_xep_rating(driver):
    goto(driver, "/allproducts"); wait_products(driver)

    def ratings():
        import re
        return [float(re.search(r":\s*([\d.]+)", e.text).group(1)) for e in
                driver.find_elements(By.XPATH, "//div[contains(@class,'chakra-text') and starts-with(normalize-space(.),':')]")]

    _click_when_ready(driver, "Rating", "//label[contains(@class,'chakra-radio')][.//input[@value='ASC']]")
    asc = ratings()
    assert asc == sorted(asc)
    _click_when_ready(driver, "Rating", "//label[contains(@class,'chakra-radio')][.//input[@value='DESC']]")
    desc = ratings()
    assert desc == sorted(desc, reverse=True) and len(asc) == len(desc)


def test_FIL_12_ket_qua_rong(driver):
    pytest.skip("Dữ liệu db.json có đủ mọi tổ hợp Category×Gender×Color -> không tạo được kết quả rỗng qua UI; test thủ công bằng URL")


def test_FIL_13_giu_bo_loc_khi_F5(driver):
    goto(driver, "/allproducts"); wait_products(driver)
    tick(driver, "Category", "shoes"); tick(driver, "Color", "red")
    n1 = count_after(driver); url = driver.current_url
    driver.refresh(); wait_products(driver)
    assert count_after(driver) == n1
    open_section(driver, "Category"); import time; time.sleep(0.8)
    assert driver.find_element(By.CSS_SELECTOR, "input[value='shoes']").is_selected()
