import os, pathlib, pytest
from selenium import webdriver
from config import BROWSER, HEADLESS, BASE_URL
from helpers import clear_session

SHOTS = pathlib.Path("results/screenshots")
SHOTS.mkdir(parents=True, exist_ok=True)


def _make_driver():
    if BROWSER == "firefox":
        o = webdriver.FirefoxOptions()
        if HEADLESS: o.add_argument("-headless")
        d = webdriver.Firefox(options=o)
    elif BROWSER == "edge":
        o = webdriver.EdgeOptions()
        if HEADLESS: o.add_argument("--headless=new")
        d = webdriver.Edge(options=o)
    else:
        o = webdriver.ChromeOptions()
        if HEADLESS: o.add_argument("--headless=new")
        o.add_argument("--window-size=1920,1080")
        d = webdriver.Chrome(options=o)       # Selenium Manager tự tải driver
    d.set_window_size(1920, 1080)
    return d


@pytest.fixture(scope="session")
def _browser():
    d = _make_driver()
    yield d
    d.quit()


@pytest.fixture
def driver(_browser):
    """Mỗi test bắt đầu ở trạng thái sạch: chưa đăng nhập, giỏ rỗng."""
    _browser.set_window_size(1920, 1080)
    clear_session(_browser)
    return _browser


@pytest.fixture
def logged_in(driver):
    from helpers import login_and_wait
    login_and_wait(driver)
    return driver


@pytest.hookimpl(hookwrapper=True)
def pytest_runtest_makereport(item, call):
    """Tự chụp ảnh khi test Fail -> dùng làm bằng chứng trong Bug_Report."""
    out = yield
    rep = out.get_result()
    if rep.when == "call" and rep.failed and "driver" in item.fixturenames:
        d = item.funcargs["driver"]
        name = item.name.split("_")[1:3]
        tcid = "-".join(name) if len(name) == 2 else item.name
        d.save_screenshot(str(SHOTS / f"{tcid}.png"))
