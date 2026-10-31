import express from "express";
import bodyParser from "body-parser";
import axios from "axios";

const app = express();
const port = 3000;

app.use(express.static("public"));
app.use(bodyParser.urlencoded({ extended: true }));

// 1-qadam: Foydalanuvchi bosh sahifaga kirganida,
//   tasodifiy faoliyat ko'rsatilishini ta'minlang. Siz
//   response.data dan kelgan JSON ma'lumotlar formatini tekshirib,
//   index.ejs faylini shunga mos ravishda tahrirlashingiz kerak.
app.get("/", async (req, res) => {
  try {
    const response = await axios.get("https://bored-api.appbrewery.com/random");
    const result = response.data;
    res.render("index.ejs", { data: result });
  } catch (error) {
    console.error("So'rov yuborishda xatolik yuz berdi:", error.message);
    res.render("index.ejs", {
      error: error.message,
    });
  }
});

app.post("/", async (req, res) => {
  try {
    console.log(req.body);
    // 2-qadam: Ochiladigan ro'yxatlar bilan o'ynab ko'ring va nima qayd etilishini kuzating.
    const type = req.body.type;
    const participants = req.body.participants;
    // Axios yordamida /filter manziliga API so'rovi yuboring. 
    // type va participants so'rov parametrlarini to'g'ri uzatayotganingizga ishonch hosil qiling.
    const response = await axios.get(`https://bored-api.appbrewery.com/filter?type=${type}&participants=${participants}`);

    const result = response.data
    console.log(result);

    res.render("index.ejs", {
      data: result[Math.floor(Math.random() * result.length)],
    });
  }
  catch (error) {
    console.error("So'rov yuborishda xatolik yuzaga keldi", error.message);

    res.render("index,ejs",{
      error: "Sizning mezonlaringizga mos faoliyat topilmadi", }); 
  } 
});

app.listen(port, () => {
  console.log(`Server ${port} portida ishlamoqda`);
});


 // API so'rovidan qaytgan *tasodifiy* bitta faoliyat bilan index.ejs faylini render qiling.
  // 3-qadam: Agar API so'rovidan 404 xatosi (resurs topilmadi) kelsa,
  // Foydalanuvchiga quyidagi xabarni ko'rsating:
  // "Sizning mezonlaringizga mos faoliyat topilmadi."