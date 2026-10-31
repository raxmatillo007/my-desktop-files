import express from 'express';
import { log } from 'node:console';

const ilova = express();
const port = 3000;

ilova.get('/', (req, res) => {
    // console.log(req.rawHeaders);
    res.send("<h1>Hello Word!</h1>")
})
ilova.get('/about', (req, res) => {
    // console.log(req.rawHeaders);
    res.send("<h1>Hello </h1>")
})
ilova.get('/contact', (req, res) => {
    // console.log(req.rawHeaders);
    res.send("<h1>tel : 11111 </h1>")
})

ilova.get('/talents', (req, res) => {
    // console.log(req.rawHeaders);
    res.send("<h1>Talents: </h1> <ul><li>JavaScript</li><li>Node.js</li><li>Express.js</li></ul>")
})



ilova.listen(port, () => {
    console.log(`Server ${port} portda ishlayapdi`)
    
});