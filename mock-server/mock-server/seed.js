// Sinh db.json: chay "node seed.js" (server.js tu goi neu chua co db.json)
const fs = require("fs");
const path = require("path");
// Neu co anh that trong thu muc ./images (jpg/png/webp) thi dung, khong thi dung anh SVG tam
const imgDir = path.join(__dirname, "images");
const photos = fs.existsSync(imgDir)
  ? fs.readdirSync(imgDir).filter((f) => /\.(jpe?g|png|webp)$/i.test(f)).sort()
  : [];
const PORT = process.env.PORT || 3001;
const colors = ["black", "red", "white", "blue"];
const shoeNames = ["Air Runner", "Court Classic", "Street Flex", "Trail Pro", "Speed Lite", "Urban Walker", "Pulse Max", "Cloud Step"];
const clothNames = ["Dry-Fit Tee", "Training Shorts", "Zip Hoodie", "Track Jacket", "Compression Tights", "Sport Tank"];
const shoeSizes = ["6", "7", "8", "9", "10"];
const clothSizes = ["small", "medium", "large"];
const products = [];
let id = 1;
const make = (name, category, gender, sizes) => {
  const color = colors[id % colors.length];
  const price = 1500 + ((id * 373) % 4500);
  products.push({
    id,
    key: id,
    name: `${name} ${gender === "MEN" ? "M" : "W"}`,
    category,
    gender,
    color,
    colortype: color,
    sizes,
    rating: Number((3 + ((id * 7) % 20) / 10).toFixed(1)),
    reviews: 10 + ((id * 13) % 90),
    strike_price: price + 500,
    final_price: price,
    images: [0, 1, 2, 3, 4].map((n) =>
      photos.length
        ? `http://localhost:${PORT}/photos/${encodeURIComponent(photos[(id + n) % photos.length])}`
        : `http://localhost:${PORT}/img/${encodeURIComponent(name)}-${id}-${n}.svg`
    ),
  });
  id++;
};
for (const g of ["MEN", "WOMEN"]) {
  shoeNames.forEach((n) => make(n, "shoes", g, shoeSizes));
  clothNames.forEach((n) => make(n, "clothes", g, clothSizes));
}
const db = {
  allproducts: products,
  Homepage: products.slice(0, 8),
  users: [
    { id: 1, name: "Test User", username: "testuser", email: "test@example.com", password: "123456", mobile: "0900000000", description: "Tai khoan mau" },
  ],
};
fs.writeFileSync(__dirname + "/db.json", JSON.stringify(db, null, 2));
console.log(`Da tao db.json (${products.length} san pham, ${photos.length} anh that)`);
