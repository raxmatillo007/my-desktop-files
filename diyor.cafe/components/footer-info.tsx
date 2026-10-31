"use client"

import { Phone, MapPin } from "lucide-react"

export function FooterInfo() {
  return (
    <footer className="px-5 pt-8">
      <div className="rounded-[26px] bg-white p-5 shadow-[0_14px_34px_-24px_rgba(43,16,87,0.5)] ring-1 ring-black/5">
        <h4 className="font-display text-[16px] font-extrabold tracking-tight text-[#14100c]">
          Diyor&apos;s Doner House
        </h4>
        <p className="mt-1 text-[12px] text-[#8a8175]">Yetkazib berish har kuni 09:00 - 21:00</p>

        <div className="mt-4 space-y-3">
          <a
            href="tel:+998333004001"
            className="flex items-center gap-3 rounded-2xl bg-[#f6f1e8] px-4 py-3 transition active:scale-[0.99]"
          >
            <span className="flex h-10 w-10 items-center justify-center rounded-full bg-gradient-to-br from-[#5b2a86] to-[#2a0e57] text-white">
              <Phone className="h-4.5 w-4.5" strokeWidth={2.2} />
            </span>
            <div>
              <p className="text-[11px] font-medium text-[#8a8175]">Yetkazib berish</p>
              <p className="text-[15px] font-bold text-[#14100c]">+998 33 300 40 01</p>
            </div>
          </a>

          <a
            href="tel:+998947236272"
            className="flex items-center gap-3 rounded-2xl bg-[#f6f1e8] px-4 py-3 transition active:scale-[0.99]"
          >
            <span className="flex h-10 w-10 items-center justify-center rounded-full bg-gradient-to-br from-[#5b2a86] to-[#2a0e57] text-white">
              <Phone className="h-4.5 w-4.5" strokeWidth={2.2} />
            </span>
            <div>
              <p className="text-[11px] font-medium text-[#8a8175]">Yetkazib berish</p>
              <p className="text-[15px] font-bold text-[#14100c]">+998 94 723 62 72</p>
            </div>
          </a>

          <div className="flex items-center gap-3 rounded-2xl bg-[#f6f1e8] px-4 py-3">
            <span className="flex h-10 w-10 shrink-0 items-center justify-center rounded-full bg-gradient-to-br from-[#5b2a86] to-[#2a0e57] text-white">
              <MapPin className="h-4.5 w-4.5" strokeWidth={2.2} />
            </span>
            <div>
              <p className="text-[11px] font-medium text-[#8a8175]">Monjal</p>
              <p className="text-[13px] font-semibold leading-snug text-[#14100c]">
                Uychi tumani, Katta masjid orqa eshigi ro&apos;parasida
              </p>
            </div>
          </div>
        </div>
      </div>

      <p className="mt-5 text-center text-[11px] text-[#a49a8d]">
        © 2026 Diyor&apos;s Doner House · Barcha huquqlar himoyalangan
      </p>
    </footer>
  )
}
