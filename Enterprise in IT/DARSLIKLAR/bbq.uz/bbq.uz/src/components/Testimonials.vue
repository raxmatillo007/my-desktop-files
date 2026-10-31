<template>
  <section class="testimonials">
    <div class="container">
      <h2 class="heading" v-motion-fade-visible>Mijozlar fikrlari</h2>

      <div class="testimonials-grid">
        <div class="testimonial" v-for="t in testimonials" :key="t.name" v-motion-slide-visible-up>
          <p class="quote">“{{ t.text }}”</p>
          <h4 class="author">- {{ t.name }}</h4>
        </div>
      </div>
    </div>
  </section>
</template>

<script setup>
const testimonials = [
  { name: "Dilshod", text: "Eng mazali grill taomlarni shu yerdan topdim!" },
  { name: "Madina", text: "Xizmat sifati juda zo‘r. Yana buyurtma qilaman!" },
  { name: "Javohir", text: "Narxlar ham qulay, juda xursand bo‘ldim." },
]
</script>
