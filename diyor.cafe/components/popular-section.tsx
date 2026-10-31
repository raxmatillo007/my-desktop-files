"use client"

import { FoodCard } from "@/components/food-card"
import type { FoodItem } from "@/lib/menu-data"

export function PopularSection({
  items,
  favorites,
  cart,
  onToggleFavorite,
  onAdd,
  onShowAll,
}: {
  items: FoodItem[]
  favorites: Set<string>
  cart: Record<string, number>
  onToggleFavorite: (id: string) => void
  onAdd: (id: string) => void
  onShowAll: () => void
}) {
  return (
    <section className="px-5 pt-8 sm:px-8 lg:px-12">
      <div className="flex items-end justify-between">
        <div>
          <h3 className="font-display text-[20px] font-extrabold tracking-tight text-[#14100c]">
            Ommabop Taomlar
          </h3>
          <p className="mt-0.5 text-[13px] text-[#8a8175]">Eng ko&apos;p buyurtma qilinganlar</p>
        </div>
        <button
          type="button"
          onClick={onShowAll}
          className="rounded-full px-3 py-1.5 text-[13px] font-semibold text-[#5b2a86] transition hover:bg-[#f3ede3] active:scale-95"
        >
          Barchasi
        </button>
      </div>

      {items.length === 0 ? (
        <p className="mt-8 text-center text-[14px] text-[#8a8175]">
          Bu kategoriyada hozircha taom yo&apos;q.
        </p>
      ) : (
        <div className="mt-4 grid grid-cols-2 gap-4 sm:grid-cols-3 lg:grid-cols-4 xl:grid-cols-5">
          {items.map((item) => (
            <FoodCard
              key={item.id}
              item={item}
              quantity={cart[item.id] ?? 0}
              isFavorite={favorites.has(item.id)}
              onToggleFavorite={onToggleFavorite}
              onAdd={onAdd}
            />
          ))}
        </div>
      )}
    </section>
  )
}
