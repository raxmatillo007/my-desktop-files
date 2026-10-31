<script setup>
import { ref } from "vue";
import { Menu, X } from "lucide-vue-next";

const isOpen = ref(false);
const toggleMenu = () => {
  isOpen.value = !isOpen.value;
};
</script>

<template>
  <header class="header">
    <div class="container header-inner">
      <h1 class="logo">Whogrill</h1>

      <!-- Desktop nav -->
      <nav class="nav desktop-nav">
        <a href="#">Bosh sahifa</a>
        <a href="#">Menu</a>
        <a href="#">Aloqa</a>
      </nav>

      <!-- Mobile menu button -->
      <button class="menu-btn mobile-btn" @click="toggleMenu">
        <Menu v-if="!isOpen" class="icon" />
        <X v-else class="icon" />
      </button>
    </div>

    <!-- Mobile nav -->
    <nav v-if="isOpen" class="nav mobile-nav">
      <a href="#">Bosh sahifa</a>
      <a href="#">Menu</a>
      <a href="#">Aloqa</a>
    </nav>
  </header>
</template>

<style scoped>
.header {

  width: 89vw;
  padding: 1rem 0;        
  background: #fff;
  border-bottom: 1px solid #ddd;
  position: relative;
  z-index: 1000;
}

.header-inner {
  display: flex;
  justify-content: space-between;
  align-items: center;
  max-width: 1200px;       
  margin: 0 auto;
}

/* Logo */
.logo {
  font-size: 1.8rem;
  font-weight: bold;
}

/* Nav links */
.nav a {
  color: black;
  margin-left: 2rem;           /* desktopda kengroq */
  text-decoration: none;
  font-weight: 500;
  transition: color 0.3s;
}
.nav a:hover {
  color: var(--brand);
}

/* Icons */
.icon {
  width: 28px;
  height: 28px;
  stroke-width: 2.2;
  color: #000;
}
.icon:hover {
  color: var(--brand);
}

/* Desktop nav only */
.desktop-nav {
  display: flex;
  gap: 2rem;                  /* linklar orasini kengaytirish */
}

/* Mobile nav hidden on desktop */
.mobile-nav,
.mobile-btn {
  display: none;
}

/* Responsive for mobile */
@media (max-width: 768px) {
  .desktop-nav {
    display: none;
  }
  .mobile-btn {
    display: block;
  }
  .mobile-nav {
    display: flex;
    flex-direction: column;
    gap: 1rem;
    padding: 1rem 0;
  }
}
</style>
