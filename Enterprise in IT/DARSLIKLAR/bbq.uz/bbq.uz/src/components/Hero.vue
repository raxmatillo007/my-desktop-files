<template>
  <section id="content" class="hero">
    <div class="container hero-inner">
      <div class="hero-text">
        <span class="eyebrow">Eng zo‘r gril taomlari</span>
        <h2 class="heading-xl">Issiq va mazali taomlarni bizdan oling 🍖🔥</h2>
        <p class="lead">
          Whogrill sizga eng sifatli go‘sht va eng zamonaviy taqdimot bilan xizmat qiladi. 
          Endi buyurtma bering va farqni his qiling!
        </p>
        <div class="hero-actions">
          <button type="button" class="btn">Buyurtma berish</button>
          <button type="button" class="btn ghost">Menu ko‘rish</button>
        </div>
      </div>

      <div class="hero-image">
        <img src="/hero.png" alt="Grill taomlari" />
      </div>
    </div>
  </section>
</template>

<script setup>
</script>

<style scoped>
.hero {
    width: 100%;

  display: flex;
  align-items: center;
  background: var(--bg);
}
.hero-inner {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 3rem;
  max-width: 1200px;
  margin: 0 auto;
  flex-wrap: wrap; /* mobilda stack bo‘lishi uchun */
}
.hero-text {
  flex: 1;
  min-width: 300px;
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
}
.hero-actions {
  display: flex;
  gap: 1rem;
  margin-top: 1.5rem;
  flex-wrap: wrap;
}
.hero-image {
  flex: 1;
  min-width: 300px;
  display: flex;
  justify-content: center;
}
.hero-image img {
  width: 100%;
  max-width: 500px;
  border-radius: var(--radius-xl);
  box-shadow: var(--shadow-2);
}
.eyebrow {
  color: var(--brand-2);
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 2px;
}
.heading-xl {
  font-size: clamp(2rem, 5vw, 3rem);
  font-weight: 800;
  line-height: 1.1;
}
.lead {
  color: var(--muted);
  font-size: 1.1rem;
  line-height: 1.6;
}
.btn {
  background: var(--brand);
  color: #000;
  padding: 0.8rem 1.2rem;
  border-radius: 10px;
  font-weight: 600;
  border: none;
  cursor: pointer;
  transition: all 0.2s ease-in-out;
}
.btn:hover {
  background: var(--brand-2);
}
.btn.ghost {
  background: transparent;
  border: 1px solid var(--brand);
  color: var(--brand);
}
.btn.ghost:hover {
  border-color: var(--brand-2);
  color: var(--brand-2);
}

/* Responsive for mobile */
@media (max-width: 768px) {
  .hero-inner {
    flex-direction: column;
    text-align: center;
    gap: 2rem;
  }
  .hero-actions {
    justify-content: center;
  }
  .hero-image {
    justify-content: center;
  }
}
</style>
