"use client"

import { categories } from "@/lib/menu-data"

export function CategoryScroller({
  active,
  onSelect,
}: {
  active: string
  onSelect: (id: string) => void
}) {
  return (
    <section className="pt-7">
      <div className="flex items-center justify-between px-5">
        <h3 className="font-display text-[18px] font-bold tracking-tight text-[#14100c]">Kategoriyalar</h3>
      </div>

      <div className="no-scrollbar mt-4 grid grid-cols-3 gap-3 px-5 pb-1 sm:grid-cols-4 md:grid-cols-7 md:gap-4">
        {categories.map((cat) => {
          const Icon = cat.icon
          const isActive = active === cat.id
          return (
            <button
              key={cat.id}
              onClick={() => onSelect(cat.id)}
              aria-pressed={isActive}
              className="flex min-w-0 flex-col items-center gap-2 rounded-2xl p-1 outline-none transition-transform hover:-translate-y-0.5 focus-visible:ring-2 focus-visible:ring-[#5b2a86]/40"
            >
              <span
                className={[
                  "flex h-14 w-14 items-center justify-center rounded-[20px] transition-all duration-200 sm:h-16 sm:w-16",
                  isActive
                    ? "bg-gradient-to-br from-[#5b2a86] to-[#2a0e57] text-white shadow-[0_12px_26px_-10px_rgba(91,42,134,0.8)] scale-105"
                    : "bg-white text-[#5b2a86] shadow-[0_8px_20px_-14px_rgba(43,16,87,0.4)] ring-1 ring-black/5",
                ].join(" ")}
              >
                <Icon className="h-7 w-7" strokeWidth={2} />
              </span>
              <span
                className={[
                  "text-[12px] font-semibold transition-colors",
                  isActive ? "text-[#5b2a86]" : "text-[#7a7167]",
                ].join(" ")}
              >
                {cat.label}
              </span>
            </button>
          )
        })}
      </div>
    </section>
  )
}
