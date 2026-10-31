// Express kutubxonasi import qilamiz
import express from 'express'

// Express ilovasi yasaymiz
const ilova = express()

//Prot raqami belgilash
const port = 3000;

//Serverni ishga tushurish
ilova.listen(port, () => {
    console.log(`Server ${port} portda ishlayapdi`);
    
});