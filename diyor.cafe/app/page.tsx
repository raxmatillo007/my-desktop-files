"use client"

import { useMemo, useState } from "react"
import { AppHeader } from "@/components/app-header"
import { SearchBar } from "@/components/search-bar"
import { HeroBanner } from "@/components/hero-banner"
import { CategoryScroller } from "@/components/category-scroller"
import { PopularSection } from "@/components/popular-section"
import { FooterInfo } from "@/components/footer-info"
import { BottomNav } from "@/components/bottom-nav"
import { CartSheet } from "@/components/cart-sheet"
import { MenuDrawer } from "@/components/menu-drawer"
import { NotificationsSheet } from "@/components/notifications-sheet"
import { popularItems } from "@/lib/menu-data"

export default function Page() {
  const [activeCategory, setActiveCategory] = useState("all")
  const [activeNav, setActiveNav] = useState("home")
  const [query, setQuery] = useState("")
  const [favorites, setFavorites] = useState<Set<string>>(new Set(["gamburger-max"]))
  const [cart, setCart] = useState<Record<string, number>>({})

  const [cartOpen, setCartOpen] = useState(false)
  const [menuOpen, setMenuOpen] = useState(false)
  const [notifOpen, setNotifOpen] = useState(false)

  const cartCount = useMemo(() => Object.values(cart).reduce((a, b) => a + b, 0), [cart])

  const visibleItems = useMemo(() => {
    const q = query.trim().toLowerCase()
    return popularItems.filter((item) => {
      const matchesCategory = activeCategory === "all" || item.category === activeCategory
      const matchesQuery =
        q === "" ||
        item.title.toLowerCase().includes(q) ||
        item.description.toLowerCase().includes(q)
      return matchesCategory && matchesQuery
    })
  }, [activeCategory, query])

  const toggleFavorite = (id: string) => {
    setFavorites((prev) => {
      const next = new Set(prev)
      next.has(id) ? next.delete(id) : next.add(id)
      return next
    })
  }

  const addToCart = (id: string) => setCart((prev) => ({ ...prev, [id]: (prev[id] ?? 0) + 1 }))

  const decFromCart = (id: string) =>
    setCart((prev) => {
      const next = { ...prev }
      const current = next[id] ?? 0
      if (current <= 1) delete next[id]
      else next[id] = current - 1
      return next
    })

  const removeFromCart = (id: string) =>
    setCart((prev) => {
      const next = { ...prev }
      delete next[id]
      return next
    })

  const handleNav = (id: string) => {
    setActiveNav(id)
    if (id === "cart") setCartOpen(true)
  }

  const showHomeContent = activeNav === "home"
  const showMenuContent = activeNav === "menu"

  const handleDrawerNavigate = (id: string) => {
    setMenuOpen(false)
    if (id === "menu") setActiveNav("menu")
    else setActiveNav("home")
  }

  return (
    <div className="relative mx-auto min-h-dvh w-full max-w-7xl">
      <div className="pb-28">
        <AppHeader
          cartCount={cartCount}
          notifCount={3}
          onOpenMenu={() => setMenuOpen(true)}
          onOpenNotifications={() => setNotifOpen(true)}
          onOpenCart={() => setCartOpen(true)}
        />
        <>
            {showHomeContent && <HeroBanner onOrder={() => setCartOpen(true)} />}
            <section className={showMenuContent ? "px-5 pb-3 pt-6" : ""} aria-labelledby={showMenuContent ? "menu-title" : undefined}>
              {showMenuContent && <><p className="text-xs font-bold uppercase tracking-[0.18em] text-brand">Diyor&apos;s Doner House</p><h1 id="menu-title" className="mt-2 font-display text-3xl font-black text-ink">To&apos;liq menyu</h1><p className="mt-2 text-sm font-medium text-ink/60">O&apos;zingizga yoqqan taomni tanlang.</p></>}
              <SearchBar value={query} onChange={setQuery} />
              <CategoryScroller active={activeCategory} onSelect={setActiveCategory} />
              <PopularSection
                items={visibleItems}
                favorites={favorites}
                cart={cart}
                onToggleFavorite={toggleFavorite}
                onAdd={addToCart}
                onShowAll={() => { setActiveCategory("all"); setQuery("") }}
              />
            </section>
            {showHomeContent && <FooterInfo />}
          </>
      </div>

      <BottomNav active={activeNav} onSelect={handleNav} cartCount={cartCount} />

      <CartSheet
        open={cartOpen}
        onClose={() => setCartOpen(false)}
        cart={cart}
        onInc={addToCart}
        onDec={decFromCart}
        onRemove={removeFromCart}
      />
      <MenuDrawer open={menuOpen} onClose={() => setMenuOpen(false)} onNavigate={handleDrawerNavigate} />
      <NotificationsSheet open={notifOpen} onClose={() => setNotifOpen(false)} />
    </div>
  )
}
