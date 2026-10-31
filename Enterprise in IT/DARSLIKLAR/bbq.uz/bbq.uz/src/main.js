import { createApp } from "vue"
import App from "./App.vue"
import router from "./router"           // Router qo‘shilgan bo‘lsa
import { MotionPlugin } from "@vueuse/motion"

// Global style (agar yozib qo‘ygan bo‘lsang)
import "./assets/main.css"

const app = createApp(App)

// app.use(router)     
app.use(MotionPlugin)    // Animatsiyalar uchun

app.mount("#app")
