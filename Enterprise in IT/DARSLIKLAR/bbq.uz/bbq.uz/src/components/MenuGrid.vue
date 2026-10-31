<template>
  <section class="menu">
    <div class="container">
      <h2 class="heading" v-motion-fade-visible>Bizning Menu</h2>

      <div class="menu-grid">
        <div class="menu-card" v-motion-slide-visible-up v-for="item in items" :key="item.title">
          <img :src="item.image" :alt="item.title" />
          <h3>{{ item.title }}</h3>
          <p>{{ item.desc }}</p>
          <span class="price">{{ item.price }}</span>
        </div>
      </div>
    </div>
  </section>
</template>

<script setup>
const items = [
  {
    title: "Kabob",
    desc: "Yangi va mazali kabob",
    price: "35 000 so‘m",
    image: "/menu-kabob.jpg", // public/ ichiga qo‘y
  },
  {
    title: "Burger",
    desc: "Grill burger maxsus sous bilan",
    price: "45 000 so‘m",
    image: "/menu-burger.jpg",
  },
  {
    title: "Steak",
    desc: "Premium darajadagi steyk",
    price: "75 000 so‘m",
    image: "/menu-steak.jpg",
  },
]
</script>
