const fs = require("fs");
const path = require("path");
const jsonServer = require("json-server");
const PORT = process.env.PORT || 3001;
const dbFile = path.join(__dirname, "db.json");
if (!fs.existsSync(dbFile)) require("./seed");

const server = jsonServer.create();
const router = jsonServer.router(dbFile);
server.use(jsonServer.defaults({ noCors: false }));
server.use(jsonServer.bodyParser);

server.use("/photos", require("express").static(path.join(__dirname, "images")));

// Anh san pham dang SVG (khong can Internet)
server.get("/img/:name.svg", (req, res) => {
  const label = decodeURIComponent(req.params.name).replace(/-\d+-(\d)$/, " #$1");
  const hue = (req.params.name.length * 47) % 360;
  res.type("image/svg+xml").send(
    `<svg xmlns="http://www.w3.org/2000/svg" width="600" height="600"><rect width="600" height="600" fill="hsl(${hue},45%,80%)"/><text x="300" y="310" font-size="34" text-anchor="middle" font-family="Arial" fill="#222">${label}</text></svg>`
  );
});

const users = () => router.db.get("users");
const makeToken = (u) => Buffer.from(`${u.email}:${Date.now()}`).toString("base64");

server.post("/auth/signup", (req, res) => {
  const { name, username, email, password, mobile, description } = req.body || {};
  if (!name || !email || !password) return res.status(400).json({ msg: "Please fill name, email and password" });
  if (users().find({ email }).value()) return res.status(409).json({ msg: "User already exists" });
  const id = Date.now();
  users().push({ id, name, username, email, password, mobile, description }).write();
  res.status(201).json({ msg: "signup successfully" });
});

server.post("/auth/login", (req, res) => {
  const { email, password } = req.body || {};
  const u = users().find({ email }).value();
  if (!u || u.password !== password) return res.status(401).json({ msg: "Wrong email or password" });
  res.json({ msg: "login successfully", token: makeToken(u) });
});

server.get("/auth/:email", (req, res) => {
  const u = users().find({ email: req.params.email }).value();
  if (!u) return res.status(404).json({ msg: "User not found" });
  const { password, ...safe } = u;
  res.json(safe);
});

// Loc san pham (json-server khong loc duoc truong mang "sizes" nen tu viet)
server.get("/allproducts", (req, res) => {
  const toArr = (v) => (v === undefined ? [] : Array.isArray(v) ? v : [v]);
  const { category, gender, colortype, sizes, _sort, _order } = req.query;
  let list = router.db.get("allproducts").value().slice();
  const eq = (field, vals) => {
    vals = toArr(vals).filter((v) => v !== "");
    if (vals.length) list = list.filter((p) => vals.map(String).includes(String(p[field])));
  };
  eq("category", category);
  eq("gender", gender);
  eq("colortype", colortype);
  const sz = toArr(sizes).filter((v) => v !== "");
  if (sz.length) list = list.filter((p) => p.sizes.some((x) => sz.includes(String(x))));
  if (_sort) {
    const dir = String(_order).toLowerCase() === "desc" ? -1 : 1;
    list.sort((a, b) => (a[_sort] > b[_sort] ? 1 : a[_sort] < b[_sort] ? -1 : 0) * dir);
  }
  res.json(list);
});

server.use(router);
server.listen(PORT, () => console.log(`Mock API chay tai http://localhost:${PORT}`));
