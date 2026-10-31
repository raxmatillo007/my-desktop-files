<script setup>
import { computed, onMounted, ref } from "vue";

const currentLang = ref("uz");

const languages = [
  { code: "uz", label: "UZ" },
  { code: "ru", label: "RU" },
  { code: "en", label: "EN" },
];

const sharedProjects = [
  {
    title: "TechHouse",
    meta: "Vue / UI",
  },
  {
    title: "Zen Focus",
    meta: "UI / UX",
  },
  {
    title: "MMI",
    meta: "Front-end / Design",
  },
];

const content = {
  uz: {
    profile: {
      name: "Abdulloxonov Raxmatillo",
      role: "Web Developer",
      tagline: "Tezkor, toza va ishonchli web interfeyslar yarataman.",
      description:
        "Men zamonaviy portfolio, landing page va biznes saytlar uchun aniq struktura, kuchli vizual uslub va responsive front-end yechimlar tayyorlayman.",
    },
    navItems: [
      { label: "Men haqimda", href: "#about" },
      { label: "Skills", href: "#skills" },
      { label: "Loyihalar", href: "#projects" },
      { label: "Aloqa", href: "#contact" },
    ],
    cta: {
      header: "Bog'lanish",
      projects: "Loyihalarni ko'rish",
      about: "Qisqacha men haqimda",
    },
    heroBadges: ["Freelance uchun ochiq", "Portfolio / Landing Page / Business Site"],
    stats: [
      { value: "2+", label: "Yillik tajriba" },
      { value: "3+", label: "Yakunlangan ishlar" },
      { value: "100%", label: "Responsive yondashuv" },
    ],
    about: {
      eyebrow: "Men haqimda",
      title: "Professional ko'rinishga ega, aniq va zamonaviy saytlar ustida ishlayman.",
      cards: [
        {
          title: "Yondashuv",
          text: "Har bir sayt chiroyli ko'rinish bilan cheklanmasligi kerak. Men dizayn, tezlik va qulay foydalanishni birgalikda qurishga e'tibor beraman.",
        },
        {
          title: "Yo'nalish",
          text: "Personal portfolio, startup landing page va xizmat ko'rsatish saytlarini zamonaviy front-end asosida ishlab chiqaman.",
        },
        {
          title: "Natija",
          text: "Natijada foydalanuvchi uchun tushunarli, buyurtmachi uchun esa professional ko'rinadigan web sahifa hosil bo'ladi.",
        },
      ],
    },
    skills: {
      eyebrow: "Ko'nikmalar",
      title: "Ish jarayonimdagi asosiy texnologiyalar",
      items: ["HTML", "CSS", "JavaScript", "Vue", "Responsive UI", "Landing Pages", "Motion Design", "Figma to Code"],
    },
    projects: {
      eyebrow: "Loyihalar",
      title: "Tanlangan ishlanmalar",
      items: [
        {
          type: "Web Project",
          text: "Texnologiya yo'nalishidagi loyiha uchun zamonaviy bloklar, aniq tipografiya va responsive interfeys bilan tayyorlangan sahifa.",
        },
        {
          type: "Landing Page",
          text: "Minimal dizayn, kuchli vizual balans va foydalanuvchini kerakli nuqtaga olib boradigan tartibli landing page.",
        },
        {
          type: "Corporate Site",
          text: "Korporativ uslubdagi loyiha uchun ishonch beradigan tuzilma, xizmat bloklari va professional taqdimot bilan tayyorlangan sayt.",
        },
      ],
    },
    contact: {
      eyebrow: "Aloqa",
      title: "Loyiha yoki hamkorlik uchun bog'laning.",
      text: "Agar sizga zamonaviy portfolio, landing page yoki biznes sayt kerak bo'lsa, men bilan bog'lanishingiz mumkin.",
      items: [
        {
          label: "Email",
          href: "mailto:abdulloxonovraxmatillo@gmail.com",
          text: "abdulloxonovraxmatillo@gmail.com",
        },
        {
          label: "Telegram",
          href: "https://t.me/User_polo",
          text: "@User_polo",
        },
      ],
    },
  },
  ru: {
    profile: {
      name: "Abdulloxonov Raxmatillo",
      role: "Веб-разработчик",
      tagline: "Создаю быстрые, аккуратные и надежные веб-интерфейсы.",
      description:
        "Разрабатываю современные портфолио, landing page и бизнес-сайты с четкой структурой, сильной визуальной подачей и адаптивным front-end.",
    },
    navItems: [
      { label: "Обо мне", href: "#about" },
      { label: "Навыки", href: "#skills" },
      { label: "Проекты", href: "#projects" },
      { label: "Контакты", href: "#contact" },
    ],
    cta: {
      header: "Связаться",
      projects: "Смотреть проекты",
      about: "Кратко обо мне",
    },
    heroBadges: ["Открыт для фриланса", "Portfolio / Landing Page / Business Site"],
    stats: [
      { value: "2+", label: "Года опыта" },
      { value: "3+", label: "Завершенных работ" },
      { value: "100%", label: "Адаптивный подход" },
    ],
    about: {
      eyebrow: "Обо мне",
      title: "Работаю над современными сайтами с четкой структурой и профессиональным видом.",
      cards: [
        {
          title: "Подход",
          text: "Сайт не должен быть просто красивым. Я соединяю дизайн, скорость и удобство использования в одном решении.",
        },
        {
          title: "Направление",
          text: "Разрабатываю personal portfolio, startup landing page и сайты услуг на современном front-end.",
        },
        {
          title: "Результат",
          text: "В итоге получается понятный для пользователя и профессионально выглядящий сайт для заказчика.",
        },
      ],
    },
    skills: {
      eyebrow: "Навыки",
      title: "Основные технологии в моей работе",
      items: ["HTML", "CSS", "JavaScript", "Vue", "Responsive UI", "Landing Pages", "Motion Design", "Figma to Code"],
    },
    projects: {
      eyebrow: "Проекты",
      title: "Избранные работы",
      items: [
        {
          type: "Веб-проект",
          text: "Страница для технологического проекта с современными блоками, четкой типографикой и адаптивным интерфейсом.",
        },
        {
          type: "Landing Page",
          text: "Минималистичный landing page с сильным визуальным балансом и продуманным потоком контента.",
        },
        {
          type: "Корпоративный сайт",
          text: "Сайт с корпоративной структурой, блоками услуг и профессиональной подачей, вызывающей доверие.",
        },
      ],
    },
    contact: {
      eyebrow: "Контакты",
      title: "Свяжитесь со мной для проекта или сотрудничества.",
      text: "Если вам нужен современный portfolio, landing page или бизнес-сайт, вы можете связаться со мной.",
      items: [
        {
          label: "Email",
          href: "mailto:abdulloxonovraxmatillo@gmail.com",
          text: "abdulloxonovraxmatillo@gmail.com",
        },
        {
          label: "Telegram",
          href: "https://t.me/User_polo",
          text: "@User_polo",
        },
      ],
    },
  },
  en: {
    profile: {
      name: "Abdulloxonov Raxmatillo",
      role: "Web Developer",
      tagline: "I build fast, clean, and reliable web interfaces.",
      description:
        "I create modern portfolio websites, landing pages, and business sites with clear structure, strong visual style, and responsive front-end implementation.",
    },
    navItems: [
      { label: "About", href: "#about" },
      { label: "Skills", href: "#skills" },
      { label: "Projects", href: "#projects" },
      { label: "Contact", href: "#contact" },
    ],
    cta: {
      header: "Contact",
      projects: "View Projects",
      about: "About Me",
    },
    heroBadges: ["Available for freelance work", "Portfolio / Landing Page / Business Site"],
    stats: [
      { value: "2+", label: "Years of experience" },
      { value: "3+", label: "Completed projects" },
      { value: "100%", label: "Responsive approach" },
    ],
    about: {
      eyebrow: "About",
      title: "I work on modern websites with clear structure and a professional look.",
      cards: [
        {
          title: "Approach",
          text: "A website should be more than visually attractive. I focus on combining design, speed, and usability into one polished solution.",
        },
        {
          title: "Direction",
          text: "I build personal portfolio sites, startup landing pages, and service websites with a modern front-end approach.",
        },
        {
          title: "Result",
          text: "The result is a website that feels clear for users and professional for clients.",
        },
      ],
    },
    skills: {
      eyebrow: "Skills",
      title: "Core technologies in my workflow",
      items: ["HTML", "CSS", "JavaScript", "Vue", "Responsive UI", "Landing Pages", "Motion Design", "Figma to Code"],
    },
    projects: {
      eyebrow: "Projects",
      title: "Selected Work",
      items: [
        {
          type: "Web Project",
          text: "A technology-focused project page with modern sections, clear typography, and a responsive interface.",
        },
        {
          type: "Landing Page",
          text: "A minimal landing page with strong visual balance and a clear content flow that guides the visitor.",
        },
        {
          type: "Corporate Site",
          text: "A corporate-style website with a trust-building structure, service blocks, and a professional presentation.",
        },
      ],
    },
    contact: {
      eyebrow: "Contact",
      title: "Get in touch for a project or collaboration.",
      text: "If you need a modern portfolio, landing page, or business website, feel free to contact me.",
      items: [
        {
          label: "Email",
          href: "mailto:abdulloxonovraxmatillo@gmail.com",
          text: "abdulloxonovraxmatillo@gmail.com",
        },
        {
          label: "Telegram",
          href: "https://t.me/User_polo",
          text: "@User_polo",
        },
      ],
    },
  },
};

const currentContent = computed(() => content[currentLang.value]);

const localizedProjects = computed(() =>
  currentContent.value.projects.items.map((project, index) => ({
    ...sharedProjects[index],
    ...project,
  }))
);

onMounted(() => {
  const revealItems = document.querySelectorAll(".reveal");
  const observer = new IntersectionObserver(
    (entries) => {
      entries.forEach((entry) => {
        if (!entry.isIntersecting) {
          return;
        }

        entry.target.classList.add("is-visible");
        observer.unobserve(entry.target);
      });
    },
    { threshold: 0.18 }
  );

  revealItems.forEach((item, index) => {
    item.style.transitionDelay = `${index * 80}ms`;
    observer.observe(item);
  });
});
</script>

<template>
  <div class="page-shell">
    <header class="site-header">
      <a class="brand" href="#top">{{ currentContent.profile.name }}</a>
      <nav class="site-nav">
        <a v-for="item in currentContent.navItems" :key="item.href" :href="item.href">{{ item.label }}</a>
      </nav>
      <div class="header-actions">
        <div class="lang-switch">
          <button
            v-for="lang in languages"
            :key="lang.code"
            type="button"
            class="lang-button"
            :class="{ active: currentLang === lang.code }"
            @click="currentLang = lang.code"
          >
            {{ lang.label }}
          </button>
        </div>
        <a class="header-cta" href="#contact">{{ currentContent.cta.header }}</a>
      </div>
    </header>

    <main id="top">
      <section class="hero">
        <div class="hero-copy reveal">
          <p class="eyebrow">{{ currentContent.profile.name }} / {{ currentContent.profile.role }}</p>
          <h1>{{ currentContent.profile.tagline }}</h1>
          <p class="hero-text">{{ currentContent.profile.description }}</p>
          <div class="hero-note">
            <span v-for="badge in currentContent.heroBadges" :key="badge">{{ badge }}</span>
          </div>
          <div class="hero-actions">
            <a class="button button-primary" href="#projects">{{ currentContent.cta.projects }}</a>
            <a class="button button-secondary" href="#about">{{ currentContent.cta.about }}</a>
          </div>
        </div>

        <aside class="hero-card reveal">
          <div v-for="stat in currentContent.stats" :key="stat.label" class="stat">
            <span>{{ stat.value }}</span>
            <p>{{ stat.label }}</p>
          </div>
        </aside>
      </section>

      <section id="about" class="about section">
        <div class="section-heading reveal">
          <p class="eyebrow">{{ currentContent.about.eyebrow }}</p>
          <h2>{{ currentContent.about.title }}</h2>
        </div>
        <div class="about-grid">
          <article v-for="card in currentContent.about.cards" :key="card.title" class="about-card reveal">
            <h3>{{ card.title }}</h3>
            <p>{{ card.text }}</p>
          </article>
        </div>
      </section>

      <section id="skills" class="skills section">
        <div class="section-heading reveal">
          <p class="eyebrow">{{ currentContent.skills.eyebrow }}</p>
          <h2>{{ currentContent.skills.title }}</h2>
        </div>
        <div class="skills-grid">
          <div v-for="skill in currentContent.skills.items" :key="skill" class="skill-pill reveal">{{ skill }}</div>
        </div>
      </section>

      <section id="projects" class="projects section">
        <div class="section-heading reveal">
          <p class="eyebrow">{{ currentContent.projects.eyebrow }}</p>
          <h2>{{ currentContent.projects.title }}</h2>
        </div>
        <div class="project-list">
          <article v-for="project in localizedProjects" :key="project.title" class="project-card reveal">
            <div>
              <p class="project-type">{{ project.type }}</p>
              <h3>{{ project.title }}</h3>
              <p>{{ project.text }}</p>
            </div>
            <span>{{ project.meta }}</span>
          </article>
        </div>
      </section>

      <section id="contact" class="contact section">
        <div class="contact-panel reveal">
          <div>
            <p class="eyebrow">{{ currentContent.contact.eyebrow }}</p>
            <h2>{{ currentContent.contact.title }}</h2>
            <p>{{ currentContent.contact.text }}</p>
          </div>
          <div class="contact-links">
            <a
              v-for="contact in currentContent.contact.items"
              :key="contact.label"
              :href="contact.href"
              :target="contact.label === 'Telegram' ? '_blank' : null"
              :rel="contact.label === 'Telegram' ? 'noreferrer' : null"
              class="contact-item"
            >
              <span class="contact-label">{{ contact.label }}:</span>
              <span class="contact-value">{{ contact.text }}</span>
            </a>
          </div>
        </div>
      </section>
    </main>
  </div>
</template>
