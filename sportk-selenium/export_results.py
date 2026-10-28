"""Đọc results/junit.xml và ghi Pass/Fail vào file Excel test case.
Cách dùng:  python export_results.py ../SportsK_TestCases_updated.xlsx
Tên hàm test_REG_09_... -> ID 'REG-09' -> tìm dòng có ID đó ở mọi sheet TC_*.
Test dùng parametrize (nhiều case/1 ID) -> gộp: chỉ Pass khi tất cả Pass."""
import os, re, sys, shutil, xml.etree.ElementTree as ET
from collections import defaultdict
import openpyxl

xlsx = sys.argv[1]
os.makedirs("results", exist_ok=True)
out = os.path.join("results", os.path.basename(xlsx).replace(".xlsx", "_ketqua.xlsx"))
shutil.copy(xlsx, out)

res = defaultdict(list)          # id -> [(status, message)]
for tc in ET.parse("results/junit.xml").getroot().iter("testcase"):
    m = re.match(r"test_([A-Z]+)((?:_\d{2})+)", tc.get("name"))   # test_FIL_02_03_04_... -> FIL-02,03,04
    if not m:
        continue
    ids = [f"{m.group(1)}-{n}" for n in re.findall(r"\d{2}", m.group(2))]
    fail = tc.find("failure"); err = tc.find("error"); skip = tc.find("skipped")
    if fail is not None or err is not None:
        node = fail if fail is not None else err
        st, msg = "Fail", (node.get("message") or "").split("\n")[0][:200]
    elif skip is not None:
        st, msg = "Blocked", (skip.get("message") or "")[:200]
    else:
        st, msg = "Pass", ""
    for i in set(ids):
        res[i].append((st, msg))

wb = openpyxl.load_workbook(out)
filled = 0
for ws in wb:
    if not ws.title.startswith("TC_") or ws.title == "TC_API":
        continue
    for row in ws.iter_rows(min_row=2):
        tid = row[0].value
        if tid in res:
            sts = [s for s, _ in res[tid]]
            status = "Fail" if "Fail" in sts else ("Blocked" if "Blocked" in sts else "Pass")
            msgs = "; ".join(m for s, m in res[tid] if m)
            row[6].value = "Đúng như mong đợi" if status == "Pass" else (msgs or "Xem results/report.html")
            row[7].value = status
            if status == "Fail" and not row[10].value:
                row[10].value = f"Ảnh: results/screenshots/{tid}.png"
            filled += 1
wb.save(out)
print(f"Đã ghi {filled} test case vào {out}")
