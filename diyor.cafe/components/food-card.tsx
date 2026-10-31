"use client"

import Image from "next/image"
import { Heart, Plus, Star } from "lucide-react"
import { formatSom, type FoodItem } from "@/lib/menu-data"

export function FoodCard({
  item,
  quantity = 0,
  isFavorite,
  onToggleFavorite,
  onAdd,
}: {
  item: FoodItem
  quantity?: number
  isFavorite: boolean
  onToggleFavorite: (id: string) => void
  onAdd: (id: string) => void
}) {
  return (
    <div className="food-card-3d group relative flex flex-col overflow-hidden rounded-[24px] bg-white p-3 shadow-[0_14px_34px_-22px_rgba(43,16,87,0.5)] ring-1 ring-black/5">
      {/* image area */}
      <div className="relative overflow-hidden rounded-[18px] bg-[#f3ede3]">
        <div className="relative aspect-[4/3] w-full">
          <Image
            src={item.image || "/placeholder.svg"}
            alt={item.title}
            fill
            sizes="(max-width: 480px) 45vw, 200px"
            className="object-contain p-2 transition-transform duration-300 group-active:scale-95"
          />
        </div>

        {item.badge && (
          <span
            className={[
              "absolute left-2 top-2 rounded-full px-2.5 py-1 text-[10px] font-bold uppercase tracking-wide shadow-sm",
              item.badge.tone === "amber"
                ? "bg-amber text-[#2a0e57]"
                : "bg-[#5b2a86] text-white",
            ].join(" ")}
          >
            {item.badge.label}
          </span>
        )}

        <button
          aria-label="Sevimlilarga qo'shish"
          onClick={() => onToggleFavorite(item.id)}
          className="absolute right-2 top-2 flex h-8 w-8 items-center justify-center rounded-full bg-white/90 backdrop-blur transition active:scale-90"
        >
          <Heart
            className={isFavorite ? "h-4 w-4 fill-rose-500 text-rose-500" : "h-4 w-4 text-[#a49a8d]"}
            strokeWidth={2.4}
          />
        </button>
      </div>

      {/* content */}
      <div className="flex flex-1 flex-col px-1 pt-3">
        <div className="flex items-center gap-1">
          <Star className="h-3.5 w-3.5 fill-amber text-amber" strokeWidth={0} />
          <span className="text-[12px] font-semibold text-[#14100c]">{item.rating}</span>
          <span className="text-[11px] text-[#a49a8d]">({item.reviews})</span>
        </div>

        <h4 className="mt-1.5 font-display text-[15px] font-bold leading-tight tracking-tight text-[#14100c]">
          {item.title}
        </h4>
        <p className="mt-1 line-clamp-2 text-[12px] leading-snug text-[#8a8175]">{item.description}</p>

        <div className="mt-auto flex items-center justify-between pt-3">
          <div className="leading-none">
            <span className="font-display text-[15px] font-extrabold text-[#5b2a86]">
              {formatSom(item.price)}
            </span>
          </div>
          <button
            aria-label={`${item.title} savatga qo'shish`}
            onClick={() => onAdd(item.id)}
            className="relative flex h-10 w-10 items-center justify-center rounded-full bg-amber text-[#2a0e57] shadow-[0_8px_18px_-8px_rgba(245,158,11,0.9)] transition active:scale-90"
          >
            {quantity > 0 && (
              <span className="absolute -right-1 -top-1 flex h-5 min-w-5 items-center justify-center rounded-full bg-[#5b2a86] px-1 text-[10px] font-bold text-white ring-2 ring-white">
                {quantity}
              </span>
            )}
            <Plus className="h-5 w-5" strokeWidth={2.8} />
          </button>
        </div>
      </div>
    </div>
  )
}
