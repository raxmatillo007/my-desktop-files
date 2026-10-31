import express from "express"; // Expressni yuklash
import { dirname } from "path";// papka manzili uchun model
import { fileURLToPath } from "url";// URL manziliga utkazish

const __dirname = dirname(fileURLToPath(import.meta.url));// loyiha turgan papkani aniqlash

const app = express(); // ilova yasash
const port = 3000;// prot raqam

app.get("/", (req, res) => {
  
  res.sendFile(__dirname + "/public/index.html");// asosiy sahifaga kirganda HTMLni chiqarish 
});

app.listen(port, () => {
  console.log(`Listening on port ${port}`);// Serverni ishga tushurish     
});
