<script setup>
import { Timer, Beef, Wallet } from "lucide-vue-next"
</script>

<template>
  <section class="features">
    <div class="container">
      <h2 class="heading" v-motion-fade-visible>
        Nega aynan <span class="brand">Whogrill?</span>
      </h2>

      <div class="features-grid">
        <div class="feature card" v-motion-slide-visible-left>
          <Timer class="icon" />
          <h3>Tezkor xizmat</h3>
          <p>Buyurtmangiz qisqa vaqtda tayyor bo‘ladi. Vaqtingiz biz uchun qimmat!</p>
        </div>

        <div class="feature card" v-motion-fade-visible>
          <Beef class="icon" />
          <h3>Sifatli go‘sht</h3>
          <p>Faqat yangi va sinovdan o‘tgan mahsulotlardan foydalanamiz.</p>
        </div>

        <div class="feature card" v-motion-slide-visible-right>
          <Wallet class="icon" />
          <h3>Qulay narx</h3>
          <p>Eng yuqori sifat – eng maqbul narxlarda. Har bir mijozni qadrlaymiz.</p>
        </div>
      </div>
    </div>
  </section>
</template>
