import express from "express";
const app = express();
const port = 3000;

// *********************
// Keling, Postman’dan foydalanishni mashq qilamiz. Serveringiz nodemon orqali yoniq turganiga ishonch hosil qiling.
// Keyin quyidagi 5 ta marshrutni (route) Postman’da tekshirib ko'ring. Har bir so'rov uchun alohida tab oching.
// Har bitta marshrut uchun serverdan to'g'ri status code kelayotganini tekshiring.
// 404 yoki 500 xatolik kodlari chiqmasligi kerak.
// *********************
//1.
app.get("/", (req, res) => {
  res.send("<h1>Home Page</h1>");
});
//2.
app.post("/register", (req, res) => {
  // Ma'lumotlar ustida biror amal bajaring

  res.sendStatus(201);
});
//3.
app.put("/user/raxmatillo", (req, res) => {
  res.sendStatus(200);
});
//4.
app.patch("/user/raxmatillo", (req, res) => {
  res.sendStatus(200);
});
//5.
app.delete("/user/raxmatillo", (req, res) => {
  // O'chirish...
  res.sendStatus(200);
});
//6.
app.listen(port, () => {
  console.log(`Server ${port}-portda ishga tushdi`);
});
