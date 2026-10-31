# Sports-K: Kiểm thử và đánh giá chất lượng website thương mại điện tử

Dự án kiểm thử website bán giày và trang phục thể thao **Sports-K** bằng **Selenium**, **Postman**, **SonarQube**. Kết quả gồm bộ test case, báo cáo lỗi và đánh giá chất lượng hệ thống.

## 1. Hệ thống được kiểm thử

| Thành phần | Công nghệ | Cổng |
|---|---|---|
| Frontend | ReactJS 18, Redux, Chakra UI, React Router | 3000 |
| Backend giả lập | JSON Server (REST API, dữ liệu trong `db.json`) | 3001 |
| Thanh toán | Razorpay (sandbox) | - |

Dữ liệu mẫu có 28 sản phẩm (16 giày, 12 quần áo).

## 2. Phạm vi kiểm thử

1. **Giao diện chức năng (Selenium):** đăng ký, đăng nhập, lọc và sắp xếp, chi tiết sản phẩm, giỏ hàng, danh sách yêu thích, mã giảm giá, form thanh toán, quản trị sản phẩm, một số kiểm tra giao diện (responsive, ảnh, điều hướng).
2. **API (Postman):** các endpoint xác thực và sản phẩm, kèm kiểm tra bảo mật cơ bản.
3. **Phân tích mã nguồn (SonarQube) và unit test (Jest).**
4. **Kiểm thử thủ công:** popup Razorpay, dark mode, tương thích trình duyệt.

Ngoài phạm vi: thanh toán thật, kiểm thử tải lớn, kiểm thử xâm nhập chuyên sâu, SEO.

## 3. Cấu trúc thư mục

```
shoe-testing/
├── e-commerce-master/e-commerce-master/   Mã nguồn frontend (React)
│   └── src/components/Other/CheckProperty.test.js   Unit test Jest
├── mock-server/mock-server/               API giả lập (JSON Server)
├── sportk-selenium/                       Bộ kiểm thử Selenium (Python + pytest)
│   ├── config.py                          URL, trình duyệt, tài khoản test
│   ├── helpers.py                         Hàm dùng chung (chờ, toast, giỏ hàng...)
│   ├── conftest.py                        Khởi tạo trình duyệt, tự chụp ảnh khi lỗi
│   ├── export_results.py                  Ghi kết quả pytest vào file Excel
│   ├── pytest.ini
│   ├── requirements.txt
│   └── tests/
│       ├── test_01_register.py
│       ├── test_02_login.py
│       ├── test_03_filter_sort.py
│       ├── test_04_detail_cart.py
│       ├── test_05_wishlist_coupon_checkout.py
│       └── test_06_admin_ui.py
├── postman/                               Collection Postman (thêm file export vào đây)
└── SportsK_TestCases_updated_ketqua.xlsx  Test plan, test case, kết quả, báo cáo lỗi
```

File Excel gồm các sheet: `Test_Plan`, `Tong_Hop`, `TC_*` theo từng module, `TC_API` và `Bug_Report`.

## 4. Cài đặt và chạy ứng dụng

Yêu cầu: Node.js, Python 3.10 trở lên, Google Chrome.

```bash
# Terminal 1: API giả lập
cd mock-server/mock-server
copy db.json db.backup.json        # sao lưu trước khi test (Windows)
npm install && npm start           # http://localhost:3001

# Terminal 2: Frontend
cd e-commerce-master/e-commerce-master
npm install && npm start           # http://localhost:3000
```

## 5. Chạy kiểm thử Selenium

```bash
cd sportk-selenium
python -m pip install -r requirements.txt

python -m pytest                          # chạy toàn bộ (khoảng 6 phút)
python -m pytest tests/test_02_login.py   # một module
python -m pytest -k "REG_09 or LOG_02"    # một vài test case
set HEADLESS=1 && python -m pytest        # chạy ngầm (Windows)
set BROWSER=firefox && python -m pytest   # đổi trình duyệt
```

Kết quả nằm trong `results/`: `report.html`, `junit.xml` và ảnh chụp lỗi `screenshots/<ID>.png`.

Ghi kết quả vào Excel:

```bash
python export_results.py ../SportsK_TestCases_updated.xlsx
```

**Quy ước:** hàm test đặt tên `test_<ID>_mota` (ví dụ `test_REG_09_...`) để script map về đúng dòng trong Excel. Test được viết theo **kết quả mong đợi** trong test case, nên test **Fail nghĩa là phát hiện lỗi**.

### Lưu ý khi chạy

- Test Admin (ADM-04) **sửa dữ liệu trong `db.json`** và test đăng ký tạo thêm user. Hãy khôi phục `db.json` từ bản sao lưu sau khi chạy.
- Chạy từng file sẽ ghi đè `results/report.html`. Muốn có báo cáo đầy đủ, chạy `python -m pytest` một lần cho toàn bộ.

## 6. Kết quả

### 6.1. Selenium (tự động)

| Tổng test | Pass | Fail (lỗi thật của web) | Skip |
|---|---|---|---|
| 97 | 85 | 10 | 2 |

Hai test Skip: **FIL-09** (bộ lọc Size không có trên giao diện) và **FIL-12** (dữ liệu có đủ mọi tổ hợp lọc nên không tạo được kết quả rỗng qua giao diện).

### 6.2. Tổng hợp toàn bộ test case

| Module | Tổng | Pass | Fail | Blocked | Not Run |
|---|---|---|---|---|---|
| Đăng ký | 14 | 13 | 1 | 0 | 0 |
| Đăng nhập | 12 | 9 | 1 | 0 | 2 |
| Lọc / Sắp xếp | 15 | 10 | 1 | 1 | 3 |
| Chi tiết sản phẩm | 8 | 6 | 0 | 0 | 2 |
| Giỏ hàng | 12 | 10 | 1 | 0 | 1 |
| Wishlist | 6 | 2 | 1 | 0 | 3 |
| Mã giảm giá | 9 | 3 | 3 | 0 | 3 |
| Checkout / Thanh toán | 18 | 6 | 0 | 0 | 12 |
| Quản trị | 10 | 3 | 1 | 0 | 6 |
| Giao diện | 11 | 4 | 2 | 0 | 5 |
| API (Postman) | 30 | 23 | 7 | 0 | 0 |
| **Tổng** | **145** | **89** | **18** | **1** | **37** |

Các test "Not Run" chủ yếu là phần kiểm thử thủ công (Razorpay, dark mode, nhiều trình duyệt). Số liệu trong sheet `Tong_Hop` là công thức nên tự cập nhật khi bạn đổi trạng thái.

### 6.3. Báo cáo lỗi

Sheet `Bug_Report` ghi 27 mục: 4 Critical, 8 Major, 14 Minor, 1 Trivial. Một số mục đang ở trạng thái "Nghi vấn" hoặc "Không phải lỗi" nên không phải mục nào cũng là lỗi đã xác nhận.

Các lỗi nổi bật (đã xác nhận):

| Bug | Mô tả | Nguồn phát hiện |
|---|---|---|
| BUG-01 | Mật khẩu không có chữ hoa vẫn được chấp nhận (regex `/[A-Z]/i` có cờ `i`) | Selenium REG-09 |
| BUG-04 | Người dùng thường vào được `/admin` (route không kiểm tra vai trò) | Selenium ADM-02 |
| BUG-09 | Giỏ hàng và wishlist mất khi tải lại trang (chỉ lưu trong Redux) | Selenium CART-09, WL-06 |
| BUG-11 | URL không tồn tại hiện trang trắng, không có trang 404 | Selenium UI-10 |
| BUG-12 | Bấm Sign in khi để trống không có phản hồi | Selenium LOG-04 |
| BUG-19 | Bộ lọc Size không hiển thị trên giao diện (khối mã bị comment) | Selenium FIL-09 |
| BUG-25 | Nhập mã giảm giá sai không có thông báo | Selenium CPN-03 |
| BUG-26 | Mã giảm giá phân biệt hoa thường và không bỏ khoảng trắng | Selenium CPN-04, CPN-05 |
| BUG-27 | Trang `/cart` bị cuộn ngang ở màn 1920×1080 | Selenium UI-01 |
| BUG-02, 03, 05, 17, 20 | Lỗi bảo mật và validate ở API (lộ mật khẩu plaintext, thiếu xác thực, token dễ đoán...) | Postman |
| BUG-21 đến 24 | Regex dễ bị backtracking, promise không xử lý lỗi, điều kiện thừa, đặt tên trùng `Error` | SonarQube |

## 7. Ghi chú kỹ thuật khi viết Selenium cho dự án này

- **Không có `data-testid`**: selector dựa vào `id` (ví dụ `#username`, `#password`), `placeholder` và text hiển thị.
- **Giỏ hàng chỉ nằm trong Redux**: `driver.get()` tương đương F5 và làm mất giỏ. Hàm `spa_goto()` điều hướng trong SPA mà không tải lại trang để giữ giỏ khi dựng dữ liệu test.
- **Chakra UI**: checkbox và radio thật bị ẩn nên phải click vào thẻ `label`. Các mục lọc là accordion mặc định đóng, và phải chờ animation mở xong mới click được.
- **Toast chỉ hiển thị khoảng 2 giây** và mờ dần, nên đọc bằng `textContent` và kiểm tra mỗi 0,1 giây để tránh bỏ sót.
- **Ô `type="number"`** (SĐT, Pin Code) tự bỏ chữ cái trong trình duyệt, nên cách kiểm tra "nhập chữ" phải đọc lại giá trị thực của ô.
- **Phân loại test Fail**: mỗi test Fail đều được đối chiếu với mã nguồn và làm lại bằng tay để tách lỗi thật của web khỏi lỗi script hoặc lỗi do thời gian chờ.

## 8. Hạn chế

- Popup Razorpay (CO-12 đến CO-17), dark mode và so sánh trình duyệt làm thủ công, chưa tự động hóa.
- Kiểm thử chạy trên môi trường giả lập (JSON Server), không đại diện cho hệ thống production.
- Dữ liệu `db.json` bị thay đổi sau mỗi lần chạy các test ghi dữ liệu; cần khôi phục trước khi chạy lại.

## 9. Thông tin nhóm
- Người thực hiện: Nguyễn Trường Thành
- Giảng viên hướng dẫn: Trịnh Thanh Bình

## 10.Video thuyết trình
https://drive.google.com/file/d/17oz1XlDT09VWKFNns37-q2tuuWKzM_5q/view?usp=drive_link
