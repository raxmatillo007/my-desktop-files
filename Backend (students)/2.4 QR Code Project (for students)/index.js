// 1. inquirer npm package bilan foydalanuvchi input oling.
import inquirer from 'inquirer';

// 2. qr-image npm package bilan URL’ni QR kodga aylantiring.
import qr from 'qr-image'
import fs from 'fs'

inquirer
    .prompt([
        {
            message: "Linkni kiriting: ",
            name: "URL"
        }
    ])
    .then((answers) => {
        const url = answers.URL;
        var qr_svg = qr.image(url);
        qr_svg.pipe(fs.createWriteStream('qr_img.png'));

        // 3.fs Node.js module bilan `.txt` faylga saqlang.
        fs.writeFile('URL.txt', url, (err) => {
            if (err) throw err;
            console.log('Fayl saqlandi!');
        });
    })
    .catch((error) => {
        if (error.isTtyError) {
            // Prompt couldn't be rendered in the current environment
        } else {
            // Something else went wrong
        }
    });










