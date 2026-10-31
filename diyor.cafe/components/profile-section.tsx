"use client"

import { Gift, History, Phone, ShieldCheck, Sparkles, Trophy } from "lucide-react"

const phoneNumber = "+998 90 123 45 67"

export function ProfileSection({ orderCount, totalSpent }: { orderCount: number; totalSpent: number }) {
  const completedMilestones = Math.floor(totalSpent / 500000)
  const bonusGoal = 500000 * 2 ** completedMilestones
  const previousGoal = completedMilestones === 0 ? 0 : 500000 * 2 ** (completedMilestones - 1)
  const progress = Math.min(((totalSpent - previousGoal) / (bonusGoal - previousGoal)) * 100, 100)
  const remaining = Math.max(bonusGoal - totalSpent, 0)

  return (
    <section className="px-5 pb-8 pt-3" aria-labelledby="profile-title">
      <div className="relative overflow-hidden rounded-[30px] bg-gradient-to-br from-[#2a0e57] via-[#4d1d78] to-[#8b5cf6] p-5 text-white shadow-[0_24px_55px_-25px_rgba(42,14,87,.75)] [transform:perspective(900px)_rotateX(1deg)]">
        <div className="pointer-events-none absolute -right-8 -top-10 h-36 w-36 rounded-full bg-amber/30 blur-2xl" />
        <div className="relative flex items-start justify-between">
          <div>
            <p className="text-xs font-semibold uppercase tracking-[0.18em] text-white/65">Diyor&apos;s Doner House</p>
            <h1 id="profile-title" className="mt-2 font-display text-2xl font-black">Mening profilim</h1>
            <p className="mt-1 text-sm text-white/75">Buyurtmalaringiz va bonuslaringiz bir joyda</p>
          </div>
          <div className="grid h-14 w-14 place-items-center rounded-2xl bg-white/15 ring-1 ring-white/20 shadow-inner">
            <Sparkles className="h-7 w-7 text-amber" aria-hidden="true" />
          </div>
        </div>
        <a href={`tel:${phoneNumber.replaceAll(" ", "")}`} className="mt-6 flex items-center justify-between rounded-2xl bg-white/10 px-4 py-3 text-sm font-bold ring-1 ring-white/15 transition hover:bg-white/15">
          <span>Buyurtma berish uchun qo&apos;ng&apos;iroq</span>
          <Phone className="h-4 w-4 text-amber" aria-hidden="true" />
        </a>
      </div>

      <div className="mt-4 grid grid-cols-2 gap-3">
        <div className="rounded-3xl border border-[#eadfce] bg-white/75 p-4 shadow-sm">
          <History className="h-5 w-5 text-brand" aria-hidden="true" />
          <p className="mt-3 text-2xl font-black text-ink">{orderCount}</p>
          <p className="text-xs font-semibold text-ink/55">Jami buyurtma</p>
        </div>
        <div className="rounded-3xl border border-[#eadfce] bg-white/75 p-4 shadow-sm">
          <Trophy className="h-5 w-5 text-amber-500" aria-hidden="true" />
          <p className="mt-3 text-2xl font-black text-ink">{totalSpent.toLocaleString("uz-UZ")}</p>
          <p className="text-xs font-semibold text-ink/55">So&apos;m sarflandi</p>
        </div>
      </div>

      <div className="mt-4 rounded-3xl border border-[#eadfce] bg-white/80 p-5 shadow-sm">
        <div className="flex items-center justify-between gap-3">
          <div className="flex items-center gap-3">
            <span className="grid h-11 w-11 place-items-center rounded-2xl bg-amber/15 text-amber-600"><Gift className="h-5 w-5" aria-hidden="true" /></span>
            <div><h2 className="font-display font-extrabold text-ink">Bonus dasturi</h2><p className="text-xs font-medium text-ink/55">Keyingi bonus: {bonusGoal.toLocaleString("uz-UZ")} so&apos;m</p></div>
          </div>
          <span className="text-sm font-black text-brand">{Math.round(progress)}%</span>
        </div>
        <div className="mt-5 h-3 overflow-hidden rounded-full bg-[#efe7da]" role="progressbar" aria-valuenow={Math.round(progress)} aria-valuemin={0} aria-valuemax={100} aria-label="Bonus progressi">
          <div className="h-full rounded-full bg-gradient-to-r from-amber-400 to-amber-600 transition-all" style={{ width: `${progress}%` }} />
        </div>
        <p className="mt-3 text-sm font-semibold text-ink/65">{remaining > 0 ? `${remaining.toLocaleString("uz-UZ")} so'm qoldi — bonusga yaqin!` : "Tabriklaymiz, bonusga ega bo'ldingiz!"}</p>
      </div>

      <div className="mt-4 flex items-center gap-3 rounded-2xl bg-[#efe7da]/70 px-4 py-3 text-xs font-semibold text-ink/60">
        <ShieldCheck className="h-5 w-5 shrink-0 text-brand" aria-hidden="true" />
        Ma&apos;lumotlaringiz xavfsiz saqlanadi.
      </div>
    </section>
  )
}
