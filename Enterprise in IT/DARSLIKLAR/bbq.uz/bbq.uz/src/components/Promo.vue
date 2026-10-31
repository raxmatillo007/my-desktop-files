<template>
  <section id="promo" class="promo">
    <div class="promo-overlay"></div>
    <div class="container promo-inner" v-motion-fade-visible>
      <h2 class="promo-title">🔥 Haftalik maxsus aksiya!</h2>
      <p class="promo-text">
        Har payshanba kuni barcha <strong>BBQ taomlariga 20% chegirma</strong>.
      </p>
      <button class="btn big">Hozir buyurtma berish</button>
    </div>
  </section>
</template>

<script setup>
</script>

<style scoped>
.promo {
  position: relative;
  padding: 5rem 1rem;
  background: url("/promo/promo-bg.jpg") center/cover no-repeat;
  border-radius: var(--radius-xl);
  margin: 3rem auto;
  overflow: hidden;
  text-align: center;
}
.promo-overlay {
  position: absolute;
  inset: 0;
  background: rgba(0,0,0,0.55);
}
.promo-inner {
  position: relative;
  z-index: 1;
  color: #fff;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 1rem;
}
.promo-title {
  font-size: clamp(1.8rem, 4vw, 2.5rem);
  font-weight: 800;
}
.promo-text {
  font-size: 1.2rem;
  color: #ddd;
  max-width: 600px;
}
.btn.big {
  padding: 1rem 1.6rem;
  font-size: 1.1rem;
  border-radius: 12px;
  font-weight: 700;
}
</style>
