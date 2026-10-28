"""TC_Admin + TC_GiaoDien (phần Selenium được). Trước khi chạy ADM-04/05: sao lưu mock-server/db.json!"""
import pytest
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from helpers import *


# ---------------- Admin ----------------
def test_ADM_01_chua_dang_nhap(driver):
    goto(driver, "/admin"); wait(driver).until(EC.url_contains("/login"))


def test_ADM_02_user_thuong_vao_admin(logged_in):
    goto(logged_in, "/admin")
    import time; time.sleep(1.5)
    assert "/admin" not in logged_in.current_url, "User thường vào được /admin (nghi vấn BUG-04)"


def test_ADM_03_danh_sach_admin(logged_in):
    goto(logged_in, "/admin")
    wait(logged_in).until(lambda d: len(d.find_elements(By.CSS_SELECTOR, "img[alt]")) >= 28)


def test_ADM_04_sua_ten(logged_in):
    """LƯU Ý: test này SỬA db.json -> khôi phục từ db.backup.json sau khi chạy."""
    d = logged_in; goto(d, "/admin")
    wait(d).until(lambda x: len(x.find_elements(By.CSS_SELECTOR, "img[alt]")) >= 28)
    # Dòng sản phẩm = tổ tiên gần nhất của ảnh có đúng 2 nút: [1]=Xoá, [2]=Sửa. (AdminNavbar cũng có nút svg nên KHÔNG lấy theo svg toàn trang)
    edit = d.find_element(By.XPATH,
        "(//img[@alt='Air Runner M']/ancestor::div[count(.//button)=2][1]//button)[2]")
    edit.click()
    name = wait(d).until(EC.visibility_of_element_located((By.CSS_SELECTOR, "input[placeholder='Name']")))
    name.send_keys("\u0001", "\ue003"); name.send_keys("Air Runner M EDIT")
    d.find_element(By.CSS_SELECTOR, ".chakra-modal__body form button").click()
    wait(d).until(lambda x: "Air Runner M EDIT" in x.find_element(By.TAG_NAME, "body").text)


# ---------------- Giao diện ----------------
@pytest.mark.parametrize("path", ["/", "/allproducts", "/cart"])
def test_UI_01_desktop_1920(driver, path):
    goto(driver, path)
    import time; time.sleep(1)
    overflow = driver.execute_script("return document.documentElement.scrollWidth > window.innerWidth")
    assert not overflow, "Có cuộn ngang ở 1920×1080"


@pytest.mark.parametrize("w,h", [(768, 1024), (375, 667)])
@pytest.mark.parametrize("path", ["/", "/allproducts", "/login"])
def test_UI_02_03_responsive(driver, w, h, path):
    driver.set_window_size(w, h)
    goto(driver, path)
    import time; time.sleep(1)
    overflow = driver.execute_script("return document.documentElement.scrollWidth > window.innerWidth")
    assert not overflow, f"Cuộn ngang ở {w}×{h} tại {path}"


def test_UI_06_dieu_huong_navbar(driver):
    goto(driver, "/")
    for text, url in [("AllProducts", "/allproducts"), ("Men", "/men"), ("Women", "/women"),
                      ("Shoes", "/shoes"), ("Home", "/")]:
        driver.find_element(By.XPATH, f"//div[contains(@class,'Navbar')]//a[.//p[normalize-space()='{text}']]").click()
        wait(driver).until(lambda d, u=url: d.current_url.rstrip("/").endswith(u.rstrip("/")) or u == "/")


def test_UI_07_anh_khong_vo(driver):
    for path in ["/allproducts", "/men", "/shoes"]:
        goto(driver, path); wait_products(driver)
        import time; time.sleep(1.5)
        bad = driver.execute_script("return [...document.images].filter(i=>!i.complete||i.naturalWidth===0).length")
        assert bad == 0, f"{bad} ảnh vỡ ở {path}"


def test_UI_10_url_khong_ton_tai(driver):
    goto(driver, "/abc")
    import time; time.sleep(1)
    body = driver.find_element(By.TAG_NAME, "body").text.lower()
    assert "404" in body or "not found" in body or driver.current_url.rstrip("/").endswith("3000"), \
        "Trang trắng khi vào URL không tồn tại (nghi vấn BUG-11)"
