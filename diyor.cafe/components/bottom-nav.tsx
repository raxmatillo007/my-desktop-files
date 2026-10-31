"use client"

import { Home, UtensilsCrossed, ShoppingBag } from "lucide-react"

const items = [
  { id: "home", label: "Asosiy", icon: Home },
  { id: "menu", label: "Menyu", icon: UtensilsCrossed },
  { id: "cart", label: "Savat", icon: ShoppingBag },
]

export function BottomNav({
  active,
  onSelect,
  cartCount,
}: {
  active: string
  onSelect: (id: string) => void
  cartCount: number
}) {
  return (
    <div className="pointer-events-none fixed inset-x-0 bottom-0 z-50 flex justify-center px-3 pb-3 sm:px-5 sm:pb-5">
      <nav
        className="pointer-events-auto flex w-full max-w-xl items-center justify-between bg-[#1c0c38]/95 px-3 py-2.5 shadow-[0_20px_44px_-16px_rgba(28,12,56,0.9)] backdrop-blur-xl sm:px-6"
        style={{ borderRadius: 12, overflow: 'hidden' }}
      >
        {items.map((item) => {
          const Icon = item.icon
          const isActive = active === item.id
          return (
            <button
              key={item.id}
              onClick={() => onSelect(item.id)}
              className={[
                "relative flex flex-col items-center gap-1 rounded-2xl px-3 py-2 transition-all",
                isActive ? "bg-white/10" : "",
              ].join(" ")}
            >
              <span className="relative">
                <Icon
                  className={isActive ? "h-[22px] w-[22px] text-amber" : "h-[22px] w-[22px] text-white/60"}
                  strokeWidth={2.2}
                />
                {item.id === "cart" && cartCount > 0 && (
                  <span className="absolute -right-2 -top-1.5 flex h-4 min-w-4 items-center justify-center rounded-full bg-amber px-1 text-[9px] font-bold text-[#2a0e57]">
                    {cartCount}
                  </span>
                )}
              </span>
              <span
                className={[
                  "text-[10px] font-semibold",
                  isActive ? "text-white" : "text-white/50",
                ].join(" ")}
              >
                {item.label}
              </span>
            </button>
          )
        })}
      </nav>
    </div>
  )
}
