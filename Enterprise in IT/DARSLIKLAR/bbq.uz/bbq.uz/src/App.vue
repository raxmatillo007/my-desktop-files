<template>
  <main class="page">
    <a class="skip" href="#content">Skip to content</a>
    <Header />
    <Hero />
    <Features />
    <MenuGrid />
    <Promo />
    <Testimonials />
    <CTA />
    <Footer />
  </main>
</template>

<script setup>
import Header from "./components/Header.vue"
import Hero from "./components/Hero.vue"
import Features from "./components/Features.vue"
import MenuGrid from "./components/MenuGrid.vue"
import Promo from "./components/Promo.vue"
import Testimonials from "./components/Testimonials.vue"
import CTA from "./components/CTA.vue"
import Footer from "./components/Footer.vue"
</script>

<style>
:root {
  --bg: #ffffff;        /* Oq fon */
  --panel: #f9f9f9;     /* Kartochka foni */
  --muted: #666666;     /* Ikkilamchi matn */
  --text: #111111;      /* Asosiy qora matn */
  --brand: #ff6b2c;     /* Brend apelsin */
  --brand-2: #ffd166;   /* Brend sariq */
  --ring: #ffb997;
  --radius: 16px;
  --radius-xl: 28px;
  --shadow-1: 0 6px 24px rgba(0,0,0,.08);
  --shadow-2: 0 14px 44px rgba(0,0,0,.12);
  --grid-max: 1200px;
}

.page {
  color: var(--text);
  background: #fff;
  height: 100vh;
}

.container {
  max-width: 1200px;
  width: 100%;
  padding: 0 1rem;
}

.btn {
  display: inline-flex;
  align-items: center;
  gap: .6rem;
  padding: .9rem 1.2rem;
  border-radius: 14px;
  background: var(--brand);
  color: #fff;
  font-weight: 700;
  letter-spacing: .2px;
  border: none;
  box-shadow: inset 0 -2px 0 rgba(0,0,0,.1), var(--shadow-1);
  transition: transform .15s ease, filter .15s ease;
}

.btn:hover {
  transform: translateY(-1px);
  filter: brightness(1.05);
}

.btn.ghost {
  background: transparent;
  color: var(--text);
  border: 1px solid #ccc;
}

.badge {
  font-size: .8rem;
  padding: .3rem .6rem;
  border-radius: 999px;
  background: rgba(255,107,44,.15);
  color: var(--brand);
  border: 1px solid rgba(255,107,44,.35);
}

.eyebrow {
  color: var(--brand-2);
  font-weight: 700;
  letter-spacing: .26em;
  text-transform: uppercase;
  font-size: .8rem;
}

.heading-xl {
  font-size: clamp(2.2rem, 5vw, 3.8rem);
  line-height: 1.08;
  font-weight: 900;
}

.lead {
  color: var(--muted);
  font-size: clamp(1rem, 2.2vw, 1.125rem);
}

.card {
  background: #fff;
  border: 1px solid #eee;
  border-radius: var(--radius-xl);
  box-shadow: var(--shadow-1);
}

.row {
  display: grid;
  gap: 1.2rem;
}

.grid-3 {
  grid-template-columns: repeat(3, minmax(0,1fr));
}

.grid-2 {
  grid-template-columns: repeat(2, minmax(0,1fr));
}

.skip {
  position: absolute;
  left: -9999px;
  top: -9999px;
}

.skip:focus {
  left: 16px;
  top: 16px;
  z-index: 9999;
  background: var(--brand);
  color: #fff;
  padding: .5rem .75rem;
  border-radius: 8px;
}

.icon {
  width: 28px;
  height: 28px;
  stroke-width: 2.2;
  color: var(--text);
}
.icon:hover {
  color: var(--brand);
}

/* Responsive grid */
@media (max-width: 920px) {
  .grid-3 {
    grid-template-columns: 1fr 1fr;
  }
}

@media (max-width: 640px) {
  .grid-3,
  .grid-2 {
    grid-template-columns: 1fr;
  }
}

/* Header responsive adjustments */
header .header-inner {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

/* Desktop nav */
header .nav.desktop-nav {
  display: flex;
  gap: 1rem;
}

/* Mobile nav */
header .mobile-nav,
header .mobile-btn {
  display: none;
}

/* Show mobile menu on small screens */
@media (max-width: 768px) {
  header .nav.desktop-nav {
    display: none;
  }
  header .mobile-btn {
    display: block;
  }
  header .mobile-nav {
    display: flex;
    flex-direction: column;
    gap: 1rem;
    padding: 1rem 0;
  }
}
</style>
