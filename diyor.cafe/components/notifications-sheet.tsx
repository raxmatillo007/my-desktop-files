"use client"

import { X, Tag, Truck, Sparkles } from "lucide-react"

type Notif = {
  id: string
  icon: typeof Tag
  title: string
  body: string
  time: string
  tone: "amber" | "brand"
}

const notifications: Notif[] = [
  {
    id: "n1",
    icon: Tag,
    title: "Kombo taomlarga 25% chegirma!",
    body: "Bugun barcha kombo to'plamlar arzon narxda.",
    time: "5 daqiqa oldin",
    tone: "amber",
  },
  {
    id: "n2",
    icon: Truck,
    title: "Bepul yetkazib berish",
    body: "50 000 so'mdan yuqori buyurtmalarga bepul.",
    time: "1 soat oldin",
    tone: "brand",
  },
  {
    id: "n3",
    icon: Sparkles,
    title: "Yangi taom qo'shildi",
    body: "Pishloqli Lavash endi menyuda mavjud.",
    time: "Kecha",
    tone: "brand",
  },
]

export function NotificationsSheet({
  open,
  onClose,
}: {
  open: boolean
  onClose: () => void
}) {
  return (
    <div
      className={[
        "fixed inset-0 z-[60] flex justify-center transition-opacity duration-300",
        open ? "opacity-100" : "pointer-events-none opacity-0",
      ].join(" ")}
    >
      <button aria-label="Yopish" onClick={onClose} className="absolute inset-0 bg-[#1c0c38]/50 backdrop-blur-sm" />

      <div className="pointer-events-none absolute inset-x-0 bottom-0 flex justify-center">
        <div
          className={[
            "pointer-events-auto w-full max-w-md rounded-t-[32px] bg-[#fbf7f0] pb-8 shadow-[0_-20px_50px_-12px_rgba(28,12,56,0.4)] transition-transform duration-300 ease-out",
            open ? "translate-y-0" : "translate-y-full",
          ].join(" ")}
        >
          <div className="mx-auto mt-3 h-1.5 w-12 rounded-full bg-[#e4dccf]" />
          <div className="flex items-center justify-between px-6 pt-5">
            <h3 className="font-display text-[20px] font-extrabold tracking-tight text-[#14100c]">Bildirishnomalar</h3>
            <button
              onClick={onClose}
              aria-label="Yopish"
              className="flex h-9 w-9 items-center justify-center rounded-full bg-white text-[#2a0e57] ring-1 ring-black/5 transition active:scale-90"
            >
              <X className="h-4.5 w-4.5" strokeWidth={2.4} />
            </button>
          </div>

          <div className="mt-4 space-y-3 px-6">
            {notifications.map((n) => {
              const Icon = n.icon
              return (
                <div
                  key={n.id}
                  className="flex items-start gap-3 rounded-[20px] bg-white p-4 shadow-[0_10px_28px_-22px_rgba(43,16,87,0.5)] ring-1 ring-black/5"
                >
                  <span
                    className={[
                      "flex h-10 w-10 shrink-0 items-center justify-center rounded-full",
                      n.tone === "amber" ? "bg-amber/15 text-[#b45309]" : "bg-[#5b2a86]/12 text-[#5b2a86]",
                    ].join(" ")}
                  >
                    <Icon className="h-5 w-5" strokeWidth={2.2} />
                  </span>
                  <div className="min-w-0 flex-1">
                    <h4 className="font-display text-[14px] font-bold leading-tight text-[#14100c]">{n.title}</h4>
                    <p className="mt-1 text-[13px] leading-snug text-[#8a8175]">{n.body}</p>
                    <p className="mt-1.5 text-[11px] font-medium text-[#a49a8d]">{n.time}</p>
                  </div>
                </div>
              )
            })}
          </div>
        </div>
      </div>
    </div>
  )
}
