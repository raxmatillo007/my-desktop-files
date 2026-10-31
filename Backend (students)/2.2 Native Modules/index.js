const fs = require("fs")

// fs.writeFile("xabar.txt","Salom, 214-guruh",(err) => {
//   if (err) throw err;
//   console.log('Fayl saqlandi!');
// }); 


// CHALLENGE -> readFile

fs.readFile('xabar.txt', 'utf8', (err, data) => {
  if (err) throw err;
  console.log(data);
});   


// const fs = require('fs');

// // fs.writeFile('xabar.txt', "Salom Node.js", (err) => {
// //   if (err) throw err;
// //   console.log('Fayl saqlandi!');
// // });


// // CHALLENGE - > "fs.readFile" dan foydalanib faylni (xabar) ichidagi tekstini terminlandan chiqarib bering
// fs.readFile("xabar.txt", "utf8" ,(err, data) => {
//   if (err) throw err;
//   console.log(data);
// });