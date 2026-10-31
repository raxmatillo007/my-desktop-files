"use client"

import Image from "next/image"
import { X, Minus, Plus, Trash2, ShoppingBag, Phone } from "lucide-react"
import { getItemById, formatSom } from "@/lib/menu-data"

export function CartSheet({
  open,
  onClose,
  cart,
  onInc,
  onDec,
  onRemove,
}: {
  open: boolean
  onClose: () => void
  cart: Record<string, number>
  onInc: (id: string) => void
  onDec: (id: string) => void
  onRemove: (id: string) => void
}) {
  const lines = Object.entries(cart)
    .map(([id, qty]) => ({ item: getItemById(id), qty }))
    .filter((l): l is { item: NonNullable<ReturnType<typeof getItemById>>; qty: number } => Boolean(l.item))

  const total = lines.reduce((sum, { item, qty }) => sum + item.price * qty, 0)
  const count = lines.reduce((sum, { qty }) => sum + qty, 0)

  return (
    <Overlay open={open} onClose={onClose}>
      <div className="flex items-center justify-between px-6 pt-5">
        <div className="flex items-center gap-2">
          <h3 className="font-display text-[20px] font-extrabold tracking-tight text-[#14100c]">Savat</h3>
          {count > 0 && (
            <span className="flex h-6 min-w-6 items-center justify-center rounded-full bg-[#5b2a86] px-1.5 text-[12px] font-bold text-white">
              {count}
            </span>
          )}
        </div>
        <CloseButton onClose={onClose} />
      </div>

      {lines.length === 0 ? (
        <div className="flex flex-col items-center justify-center px-6 py-16 text-center">
          <span className="flex h-16 w-16 items-center justify-center rounded-full bg-[#f3ede3] text-[#a49a8d]">
            <ShoppingBag className="h-7 w-7" strokeWidth={2} />
          </span>
          <p className="mt-4 font-display text-[16px] font-bold text-[#14100c]">Savat bo&apos;sh</p>
          <p className="mt-1 text-[13px] text-[#8a8175]">Menyudan sevimli taomingizni qo&apos;shing</p>
        </div>
      ) : (
        <>
          <div className="no-scrollbar mt-4 max-h-[46vh] space-y-3 overflow-y-auto px-6">
            {lines.map(({ item, qty }) => (
              <div
                key={item.id}
                className="flex items-center gap-3 rounded-[20px] bg-[#f8f4ec] p-2.5 ring-1 ring-black/5"
              >
                <div className="relative h-16 w-16 shrink-0 overflow-hidden rounded-[14px] bg-[#f3ede3]">
                  <Image src={item.image || "/placeholder.svg"} alt={item.title} fill sizes="64px" className="object-cover" />
                </div>
                <div className="min-w-0 flex-1">
                  <h4 className="truncate font-display text-[14px] font-bold text-[#14100c]">{item.title}</h4>
                  <p className="mt-0.5 text-[13px] font-extrabold text-[#5b2a86]">{formatSom(item.price)}</p>
                </div>
                <div className="flex flex-col items-end gap-2">
                  <button
                    onClick={() => onRemove(item.id)}
                    aria-label={`${item.title} o'chirish`}
                    className="text-[#c4bbae] transition active:scale-90"
                  >
                    <Trash2 className="h-4 w-4" strokeWidth={2.2} />
                  </button>
                  <div className="flex items-center gap-2 rounded-full bg-white p-1 ring-1 ring-black/5">
                    <button
                      onClick={() => onDec(item.id)}
                      aria-label="Kamaytirish"
                      className="flex h-7 w-7 items-center justify-center rounded-full bg-[#f3ede3] text-[#2a0e57] transition active:scale-90"
                    >
                      <Minus className="h-3.5 w-3.5" strokeWidth={2.8} />
                    </button>
                    <span className="w-5 text-center text-[13px] font-bold text-[#14100c]">{qty}</span>
                    <button
                      onClick={() => onInc(item.id)}
                      aria-label="Ko'paytirish"
                      className="flex h-7 w-7 items-center justify-center rounded-full bg-amber text-[#2a0e57] transition active:scale-90"
                    >
                      <Plus className="h-3.5 w-3.5" strokeWidth={2.8} />
                    </button>
                  </div>
                </div>
              </div>
            ))}
          </div>

          <div className="mt-5 border-t border-black/5 px-6 pb-2 pt-4">
            <div className="flex items-center justify-between">
              <span className="text-[14px] font-medium text-[#8a8175]">Jami</span>
              <span className="font-display text-[20px] font-extrabold text-[#14100c]">{formatSom(total)}</span>
            </div>
            <a
              href="tel:+998333004001"
              className="mt-4 flex w-full items-center justify-center gap-2 rounded-full bg-gradient-to-br from-[#5b2a86] to-[#2a0e57] py-4 font-display text-[15px] font-bold text-white shadow-[0_16px_30px_-12px_rgba(91,42,134,0.8)] transition active:scale-[0.98]"
            >
              <Phone className="h-4 w-4" strokeWidth={2.4} />
              Buyurtma berish
            </a>
          </div>
        </>
      )}
    </Overlay>
  )
}

function Overlay({
  open,
  onClose,
  children,
}: {
  open: boolean
  onClose: () => void
  children: React.ReactNode
}) {
  return (
    <div
      className={[
        "fixed inset-0 z-[60] flex justify-center transition-opacity duration-300",
        open ? "opacity-100" : "pointer-events-none opacity-0",
      ].join(" ")}
    >
      <button
        aria-label="Yopish"
        onClick={onClose}
        className="absolute inset-0 bg-[#1c0c38]/50 backdrop-blur-sm"
      />
      <div className="pointer-events-none absolute inset-0 flex items-end justify-center sm:items-center sm:p-6">
        <div
          className={[
            "pointer-events-auto w-full max-w-xl rounded-t-[32px] bg-[#fbf7f0] pb-[calc(1.5rem+env(safe-area-inset-bottom))] shadow-[0_-20px_50px_-12px_rgba(28,12,56,0.4)] transition-transform duration-300 ease-out sm:rounded-[32px] sm:shadow-[0_24px_70px_-18px_rgba(28,12,56,0.55)]",
            open ? "translate-y-0" : "translate-y-full",
          ].join(" ")}
        >
          <div className="mx-auto mt-3 h-1.5 w-12 rounded-full bg-[#e4dccf]" />
          {children}
        </div>
      </div>
    </div>
  )
}

function CloseButton({ onClose }: { onClose: () => void }) {
  return (
    <button
      onClick={onClose}
      aria-label="Yopish"
      className="flex h-9 w-9 items-center justify-center rounded-full bg-white text-[#2a0e57] ring-1 ring-black/5 transition active:scale-90"
    >
      <X className="h-4.5 w-4.5" strokeWidth={2.4} />
    </button>
  )
}
