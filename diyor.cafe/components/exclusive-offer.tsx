"use client"

import Image from "next/image"
import { ArrowRight } from "lucide-react"

export function ExclusiveOffer({ onOrder }: { onOrder: () => void }) {
  return (
    <section className="px-5 pt-8">
      <div className="flex items-center justify-between">
        <h3 className="font-display text-[20px] font-extrabold tracking-tight text-[#14100c]">
          Maxsus Taklif
        </h3>
      </div>

      <div className="relative mt-4 overflow-hidden rounded-[26px] bg-gradient-to-br from-[#2a0e57] via-[#3f1a6b] to-[#5b2a86] p-5 shadow-[0_22px_46px_-20px_rgba(42,14,87,0.7)]">
        <div className="pointer-events-none absolute -right-6 top-1/2 h-40 w-40 -translate-y-1/2 rounded-full bg-amber/20 blur-2xl" />

        <div className="relative flex items-center gap-4">
          <div className="flex-1">
            <span className="inline-flex rounded-full bg-amber px-3 py-1 text-[11px] font-extrabold uppercase tracking-wide text-[#2a0e57]">
              25% gacha
            </span>
            <h4 className="mt-3 font-display text-[18px] font-extrabold leading-tight text-white text-balance">
              Kombo taomlarga 25% gacha chegirma
            </h4>
            <button
              onClick={onOrder}
              className="mt-4 inline-flex items-center gap-2 rounded-full bg-white px-4 py-2 text-[13px] font-bold text-[#2a0e57] transition active:scale-95"
            >
              Order Now
              <ArrowRight className="h-4 w-4" strokeWidth={2.6} />
            </button>
          </div>

          <div className="relative h-32 w-32 shrink-0 sm:h-36 sm:w-36">
            <Image
              src="/images/combo-offer.png"
              alt="Kombo taom to'plami"
              fill
              className="object-contain drop-shadow-2xl"
            />
          </div>
        </div>
      </div>
    </section>
  )
}
