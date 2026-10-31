// 1 dan 6 gacha bolgan tasodidiy sonlarni tanlab olib son yaratish
let randomSon1 = Math.floor(Math.random() * 6) + 1;

// Tasodifiy saonlar oqali rasm manziliga murojat qilish 
let randomDiceImage = "images/dice" + randomSon1 + ".png";

// birinchi <img> tegini olish uchun va unning rasm manzili(src) yangilash
document.querySelectorAll("img")[0].setAttribute("src",randomDiceImage)


// 1 dan 6 gacha bolgan tasodidiy sonlarni tanlab olib son yaratish
let randomSon2 = Math.floor(Math.random() * 6) + 1;

// Tasodifiy saonlar oqali rasm manziliga murojat qilish 
let randomDiceImage2 = "images/dice" + randomSon2 + ".png";

// birinchi <img> tegini olish uchun va unning rasm manzili(src) yangilash
document.querySelectorAll("img")[1].setAttribute("src",randomDiceImage2)


// Agar 1-oyinchi yutsa
if ( randomSon1 > randomSon2){
    document.querySelector("h1").innerHTML = "1-Player yutdi"
}
// Agar 2-oyinchi yutsa
 else if ( randomSon2 > randomSon1){
    document.querySelector("h1").innerHTML = "2-Player yutdi"
}
else {
    document.querySelector("h1").innerHTML = " Durrang"
}