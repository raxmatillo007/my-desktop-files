// Yakuniy veb-sayt qanday ishlashini ko‘rish
// Barcha kerakli kutubxonalar o‘rnatilganiga ishonch hosil qilish uchun "npm i" ni ishga tushiring.
// Parol: ILoveProgramming

import express from "express";
import bodyParser from "body-parser";
import { dirname} from "path";// Papka manzili uchun modul
import { fileURLToPath} from "url";// URL ni manzilga utkazish
import { log } from "console";

const __dirname = dirname(fileURLToPath(import.meta.url));

const app = express();
const port = 3000;

let userTasdiqlasa = false

app.use(bodyParser.urlencoded({extended: true}));

function passwordCheeck(req, res, next){
        const password = req.body["password"];
        if (password === "ILoveProgramming"){
            userTasdiqlasa = true;
        }
        next()
}

app.use(passwordCheeck);

app.get("/", (req, res) =>{
 res.sendFile(__dirname + "/public/index.html");
});

app.post("/check", (req, res) => {
    if (userTasdiqlasa){
 res.sendFile(__dirname + "/public/secret.html");
} else {
    res.sendFile(__dirname + "/public/index.html");
}
});

app.listen(port, () => {
  console.log(`Listening on port ${port}`);
});
