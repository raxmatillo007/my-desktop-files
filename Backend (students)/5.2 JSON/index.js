import express from "express"; // Expressni yuklash
import bodyParser from "body-parser";

const app = express(); // Ilova yasash
const port = 3000;  // Port raqamo

const recipeJSON =
'[{"id": "0001","type": "taco","name": "Tovuqli Taco","price": 2.99,"ingredients": {"protein": {"name": "Tovuq","preparation": "Grillda pishirilgan"},  "salsa": {"name": "Pomidor Salsasi","spiciness": "Oʻrta"},  "toppings": [{"name": "Salat",  "quantity": "1 stakan",  "ingredients": ["Muzli Salat"]  },      {"name": "Pishloq",  "quantity": "1/2 stakan",  "ingredients": ["Cheddar Pishloq", "Monterey Jack Pishloq"]  },      {"name": "Gvakamole",  "quantity": "2 osh qoshiq",  "ingredients": ["Avokado", "Limon Sharbati", "Tuz", "Piyoz", "Kinza"]  },      {"name": "Smetana",  "quantity": "2 osh qoshiq",  "ingredients": ["Smetana"]  }      ]    }  },{"id": "0002","type": "taco","name": "Goʻshtli Taco","price": 3.49,"ingredients": {"protein": {"name": "Goʻsht","preparation": "Ziravorlab grillda pishirilgan"},  "salsa": {"name": "Yashil Salsa","spiciness": "Achchiq"},  "toppings": [{"name": "Piyoz",  "quantity": "1/4 stakan",  "ingredients": ["Oq Piyoz", "Qizil Piyoz"]  },      {"name": "Kinza",  "quantity": "2 osh qoshiq",  "ingredients": ["Yangi Kinza"]  },      {"name": "Queso Fresco",  "quantity": "1/4 stakan",  "ingredients": ["Queso Fresco"]  }      ]    }  },{"id": "0003","type": "taco","name": "Baliqli Taco","price": 4.99,"ingredients": {"protein": {"name": "Baliq","preparation": "Xamirda qovurilgan"},  "salsa": {"name": "Chipotle Mayonez","spiciness": "Kam Achchiq"},  "toppings": [{"name": "Karam Salati",  "quantity": "1 stakan",  "ingredients": ["Maydalangan Karam","Sabzi","Mayonez","Limon Sharbati","Tuz"]  },      {"name": "Piko de Galyo",  "quantity": "1/2 stakan",  "ingredients": ["Pomidor", "Piyoz", "Kinza", "Limon Sharbati", "Tuz"]  },      {"name": "Limonli Krema",  "quantity": "2 osh qoshiq",  "ingredients": ["Smetana", "Limon Sharbati", "Tuz"]  }      ]    }  }]';

app.use(bodyParser.urlencoded({ extended: true }));

app.use(express.static("public"));

let data 

app.get("/", (req, res) => {
    res.render("index.ejs", { recipe:data });
});

app.post("/recipe", (req, res) => {
    switch (req.body.choice) {
        case "tovuq":
            data = JSON.parse(recipeJSON)[0];
            break;
        case "qosht":
            data = JSON.parse(recipeJSON)[1];
            break;
        case "baliq":
            data = JSON.parse(recipeJSON)[2];
            break;

        default:
            break;
    }
    res.redirect("/")
})

app.listen(port, () => {
    console.log(`Listening on port ${port}`);
});