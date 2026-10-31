"use client"

import { X, Home, UtensilsCrossed, Tag, Phone, MapPin, ChevronRight } from "lucide-react"

const links = [
  { id: "home", label: "Asosiy", icon: Home },
  { id: "menu", label: "Menyu", icon: UtensilsCrossed },
]

export function MenuDrawer({
  open,
  onClose,
  onNavigate,
}: {
  open: boolean
  onClose: () => void
  onNavigate: (id: string) => void
}) {
  return (
    <div
      className={[
        "fixed inset-0 z-[60] flex justify-center transition-opacity duration-300",
        open ? "opacity-100" : "pointer-events-none opacity-0",
      ].join(" ")}
    >
      <button aria-label="Yopish" onClick={onClose} className="absolute inset-0 bg-[#1c0c38]/50 backdrop-blur-sm" />

      <div className="pointer-events-none absolute inset-y-0 left-0 flex w-full max-w-md">
        <div
          className={[
            "pointer-events-auto flex w-[88%] max-w-[350px] flex-col rounded-r-[30px] bg-[#fffaf3] px-5 pb-6 pt-5 shadow-[20px_0_60px_-28px_rgba(28,12,56,0.45)] transition-transform duration-300 ease-out",
            open ? "translate-x-0" : "-translate-x-full",
          ].join(" ")}
        >
          <div className="flex items-center justify-between">
            <div>
              <p className="font-display text-[18px] font-extrabold leading-tight text-[#2a0e57]">
                DIYOR&apos;S DONER
              </p>
              <p className="text-[12px] font-semibold text-[#c46a1b]">House</p>
            </div>
            <button
              onClick={onClose}
              aria-label="Yopish"
              className="flex h-9 w-9 items-center justify-center rounded-full bg-[#2a0e57]/10 text-[#2a0e57] transition active:scale-90"
            >
              <X className="h-4.5 w-4.5" strokeWidth={2.4} />
            </button>
          </div>

          <nav className="mt-8 flex flex-col gap-1">
            {links.map((link) => {
              const Icon = link.icon
              return (
                <button
                  key={link.id}
                  onClick={() => onNavigate(link.id)}
                  className="flex items-center gap-3 rounded-2xl px-3 py-3.5 text-left transition hover:bg-[#2a0e57]/5 active:bg-[#2a0e57]/10"
                >
                  <span className="flex h-10 w-10 items-center justify-center rounded-xl bg-[#2a0e57]/10 text-[#c46a1b]">
                    <Icon className="h-5 w-5" strokeWidth={2.2} />
                  </span>
                  <span className="flex-1 text-[15px] font-bold text-[#24152f]">{link.label}</span>
                  <ChevronRight className="h-4 w-4 text-[#2a0e57]/35" strokeWidth={2.4} />
                </button>
              )
            })}
          </nav>

          <div className="mt-auto space-y-3 rounded-[22px] bg-[#2a0e57] p-4">
            <a href="tel:+998333004001" className="flex items-center gap-3">
              <span className="flex h-9 w-9 items-center justify-center rounded-full bg-amber text-[#2a0e57]">
                <Phone className="h-4 w-4" strokeWidth={2.2} />
              </span>
              <div>
                <p className="text-[11px] text-white/50">Yetkazib berish</p>
                <p className="text-[14px] font-bold text-white">+998 33 300 40 01</p>
              </div>
            </a>
            <div className="flex items-start gap-3">
              <span className="flex h-9 w-9 shrink-0 items-center justify-center rounded-full bg-white/10 text-amber">
                <MapPin className="h-4 w-4" strokeWidth={2.2} />
              </span>
              <p className="text-[12px] leading-snug text-white/70">
                Uychi tumani, Katta masjid orqa eshigi ro&apos;parasida
              </p>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}
