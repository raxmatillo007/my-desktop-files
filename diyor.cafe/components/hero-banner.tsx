"use client"

import Image from "next/image"
import { ArrowRight } from "lucide-react"

export function HeroBanner({ onOrder }: { onOrder: () => void }) {
  return (
    <div className="px-5 pt-6">
      <div className="relative overflow-hidden rounded-[28px] bg-gradient-to-br from-[#5b2a86] via-[#3f1a6b] to-[#2a0e57] p-6 shadow-[0_24px_50px_-20px_rgba(42,14,87,0.7)]">
        {/* decorative glow */}
        <div className="pointer-events-none absolute -right-10 -top-10 h-40 w-40 rounded-full bg-[#8b5cf6]/30 blur-3xl" />
        <div className="pointer-events-none absolute -bottom-12 left-4 h-36 w-36 rounded-full bg-amber/20 blur-3xl" />

        <div className="relative flex items-center justify-between gap-3">
          <div className="max-w-[60%]">
            <span className="inline-flex items-center rounded-full bg-white/15 px-3 py-1 text-[11px] font-semibold uppercase tracking-wide text-amber-soft backdrop-blur">
              Yangi mavsum
            </span>
            <h2 className="mt-3 font-display text-[22px] font-extrabold leading-[1.08] tracking-tight text-white text-balance">
              MUKAMMAL TA&apos;MLAR, DOIMIY SIFAT
            </h2>
            <button
              onClick={onOrder}
              className="mt-5 inline-flex items-center gap-2 rounded-full bg-amber px-4 py-2 text-[13px] font-bold text-[#2a0e57] shadow-lg shadow-black/20 transition active:scale-95"
            >
              Hozir Buyurtma Berish
              <ArrowRight className="h-4 w-4" strokeWidth={2.6} />
            </button>
          </div>

          <div className="relative h-36 w-36 shrink-0 sm:h-40 sm:w-40">
            <div className="absolute inset-0 rounded-full bg-white/10 blur-md" />
            <Image
              src="/images/hero-doner.png"
              alt="Mazali doner lavash"
              fill
              className="animate-float-slow object-contain drop-shadow-2xl"
              priority
            />
          </div>
        </div>
      </div>
    </div>
  )
}
