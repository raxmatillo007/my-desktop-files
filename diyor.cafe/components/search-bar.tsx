"use client"

import { Search, X } from "lucide-react"

export function SearchBar({
  value,
  onChange,
}: {
  value: string
  onChange: (v: string) => void
}) {
  return (
    <div className="px-5 pt-4">
      <div className="flex items-center gap-3">
        <div className="flex flex-1 items-center gap-3 rounded-2xl bg-white px-4 py-3.5 shadow-[0_8px_24px_-14px_rgba(43,16,87,0.3)] ring-1 ring-black/5 focus-within:ring-2 focus-within:ring-[#5b2a86]/40">
          <Search className="h-5 w-5 shrink-0 text-[#a49a8d]" strokeWidth={2.2} />
          <input
            type="text"
            value={value}
            onChange={(e) => onChange(e.target.value)}
            enterKeyHint="search"
            placeholder="Sevimli taomingizni qidiring..."
            className="w-full bg-transparent text-[15px] text-[#14100c] placeholder:text-[#a49a8d] focus:outline-none"
          />
          {value && (
            <button
              onClick={() => onChange("")}
              aria-label="Tozalash"
              className="flex h-6 w-6 shrink-0 items-center justify-center rounded-full bg-[#f0e9dd] text-[#7a7167] transition active:scale-90"
            >
              <X className="h-3.5 w-3.5" strokeWidth={2.6} />
            </button>
          )}
        </div>
      </div>
    </div>
  )
}
