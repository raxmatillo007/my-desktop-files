"use client"

import { Menu, Bell, ShoppingBag, HandMetal } from "lucide-react"

export function AppHeader({
  cartCount,
  notifCount,
  onOpenMenu,
  onOpenNotifications,
  onOpenCart,
}: {
  cartCount: number
  notifCount: number
  onOpenMenu: () => void
  onOpenNotifications: () => void
  onOpenCart: () => void
}) {
  return (
    <header className="px-5 pt-6 pb-2">
      <div className="flex items-center justify-between">
        <button
          onClick={onOpenMenu}
          aria-label="Menyuni ochish"
          className="flex h-11 w-11 items-center justify-center rounded-2xl bg-white text-[#2a0e57] shadow-[0_6px_20px_-8px_rgba(43,16,87,0.35)] ring-1 ring-black/5 transition active:scale-95"
        >
          <Menu className="h-5 w-5" strokeWidth={2.4} />
        </button>

        <div className="flex items-center gap-3">
          <button
            onClick={onOpenNotifications}
            aria-label="Bildirishnomalar"
            className="relative flex h-11 w-11 items-center justify-center rounded-2xl bg-white text-[#2a0e57] shadow-[0_6px_20px_-8px_rgba(43,16,87,0.35)] ring-1 ring-black/5 transition active:scale-95"
          >
            <Bell className="h-5 w-5" strokeWidth={2.2} />
            {notifCount > 0 && (
              <span className="absolute right-2.5 top-2.5 h-2 w-2 rounded-full bg-amber ring-2 ring-white" />
            )}
          </button>
          <button
            onClick={onOpenCart}
            aria-label="Savat"
            className="relative flex h-11 w-11 items-center justify-center rounded-2xl bg-gradient-to-br from-[#5b2a86] to-[#2a0e57] text-white shadow-[0_10px_24px_-8px_rgba(91,42,134,0.7)] transition active:scale-95"
          >
            <ShoppingBag className="h-5 w-5" strokeWidth={2.2} />
            {cartCount > 0 && (
              <span className="absolute -right-1 -top-1 flex h-5 min-w-5 items-center justify-center rounded-full bg-amber px-1 text-[11px] font-bold text-[#2a0e57] ring-2 ring-[#fbf7f0]">
                {cartCount}
              </span>
            )}
          </button>
        </div>
      </div>

      <div className="mt-6">
        <p className="flex items-center gap-1.5 text-[15px] font-medium text-[#7a7167]">
          Salom, Taom Ishqibozi!
          <HandMetal className="h-4 w-4 text-amber" strokeWidth={2.2} />
        </p>
        <h1 className="mt-1 font-display text-[26px] font-extrabold leading-tight tracking-tight text-[#14100c]">
          DIYOR&apos;S DONER <span className="text-[#5b2a86]">HOUSE</span>
        </h1>
      </div>
    </header>
  )
}
