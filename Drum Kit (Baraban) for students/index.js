// // DOM ga ulash 
// document.querySelector("button").addEventListener("click", tugmaBosilganda);

// // 1-> funksiya yozamiz
// function tugmaBosilganda() {
//     alert("Meni bosishdi!")
// }

// 4 -> Hamma knopka ishlashi uchun (w,a,s,d,j,k,l)

let barabanTugmalariSoni = document.querySelectorAll(".drum").length;

// for (loop - tsikl ) yozamiz
for (let i = 0; i < barabanTugmalariSoni; i++) {
    document.querySelectorAll(".drum")[i].addEventListener("click", function () {
        let buttoninnerHTML = this.innerHTML
        makeSound(buttoninnerHTML)

        // Animatsa (tugma bosganda)
        buttonAnimatsiya(buttoninnerHTML)
    });
}

// KEYBORDNI BOSGANDA ISHLAVOTI
document.addEventListener("keypress", function (event) {
makeSound(event.key)
// animatsiya (klaviatura bosganda)
buttonAnimatsiya(event.key)

});

function makeSound(key) {
    switch (key) {
        case "w":
            // Audio qoshish
            let tom1 = new Audio("sounds/tom-1.mp3")
            tom1.play();
            break;
        case "a":
            // Audio qoshish
            let tom2 = new Audio("sounds/tom-2.mp3")
            tom2.play();
            break;
        case "s":
            // Audio qoshish
            let tom3 = new Audio("sounds/tom-3.mp3")
            tom3.play();
            break;
        case "d":
            // Audio qoshish
            let tom4 = new Audio("sounds/tom-4.mp3")
            tom4.play();
            break;
        case "j":
            // Audio qoshish
            let snare = new Audio("sounds/snare.mp3")
            snare.play();
            break;
        case "k":
            // Audio qoshish
            let crash = new Audio("sounds/crash.mp3")
            crash.play();
            break;
        case "l":
            // Audio qoshish
            let kick = new Audio("sounds/kick-bass.mp3")
            kick.play();
            break;

        default: console.log(buttoninnerHTML);

            break;
    }
}

// Knopkaga animatsiya qoshish
function buttonAnimatsiya(hozirgiKey){
let activeButton = document.querySelector("." + hozirgiKey);
activeButton.classList.add("pressed")

// knopka orqaga qaytishi uchun animatsiya (remove)
setTimeout(function(){
    activeButton.classList.remove("pressed")
},100)
}