import type { LucideIcon } from "lucide-react"
import { LayoutGrid, Popcorn, Sandwich, Utensils } from "lucide-react"
import { createElement, type SVGProps } from "react"

const BurgerIcon: LucideIcon = (props: SVGProps<SVGSVGElement>) =>
  createElement(
    "svg",
    {
      viewBox: "0 0 100 100",
      fill: "currentColor",
      xmlns: "http://www.w3.org/2000/svg",
      ...props,
    },
    createElement("path", {
      d: "M16 56c0-19 14-34 32-34s32 15 32 34v4H16v-4Zm10 13h48a8 8 0 0 1 8 8v7H18v-7a8 8 0 0 1 8-8Zm-8 17h64a8 8 0 0 1 8 8v4H8v-4a8 8 0 0 1 8-8ZM30 20h40l-3 8H33l-3-8Zm-9-6 5 8-5 6-5-6 5-8Zm64 0 5 8-5 6-5-6 5-8ZM33 35h9v9h-9Zm16 0h9v9h-9Zm16 0h9v9h-9Z",
    }),
  )

const KfcIcon: LucideIcon = (props: SVGProps<SVGSVGElement>) =>
  createElement(
    "svg",
    {
      viewBox: "0 0 100 100",
      fill: "currentColor",
      xmlns: "http://www.w3.org/2000/svg",
      ...props,
    },
    createElement("path", {
      d: "M30 81h40c5 0 9-4 9-9V35c0-4-3-8-8-8H29c-5 0-9 4-9 8v37c0 5 4 9 9 9Zm-5-54h50l-7-9H32l-7 9Zm13 11h24l-6 13H44l-6-13Zm-12 18h48l-5 17H38l-5-17Zm18-38h12l-3 9H48l-3-9Zm-3 20 3-7h12l3 7H43Zm-5 12h26l-2 7H40l-2-7Z",
    }),
  )

export type Category = {
  id: string
  label: string
  icon: LucideIcon
}

export const categories: Category[] = [
  { id: "all", label: "Hammasi", icon: LayoutGrid },
  { id: "lavash", label: "Lavashlar", icon: Sandwich },
  { id: "doner", label: "Doner", icon: Sandwich },
  { id: "burger", label: "Burgerlar", icon: BurgerIcon },
  { id: "hotdog", label: "Hot-doglar", icon: Utensils },
  { id: "kfc", label: "KFC", icon: KfcIcon },
  { id: "fri", label: "Fri & Souslar", icon: Popcorn },
]

export type FoodItem = {
  id: string
  title: string
  description: string
  price: number
  rating: number
  reviews: string
  image: string
  badge?: { label: string; tone: "amber" | "brand" }
  category: string
}

const menuItem = (
  id: string,
  title: string,
  price: number,
  category: string,
  image: string,
  description = "Yangi va mazali Diyor's Doner taomi",
): FoodItem => ({
  id,
  title,
  description,
  price,
  rating: 4.8,
  reviews: "100+",
  image,
  category,
})

export const popularItems: FoodItem[] = [
  menuItem("lavash-standard", "Lavash Standard", 28000, "lavash", "/images/lavash-standard.png"),
  menuItem("lavash-achchiq", "Lavash (Achchiq)", 30000, "lavash", "/images/lavash-achchiq.png"),
  menuItem("lavash-sirli", "Lavash Sirli", 32000, "lavash", "/images/lavash-sirli.png"),
  menuItem("doner", "Doner", 27000, "doner", "/images/hero-doner.png"),
  menuItem("hotdog", "Hot-Dog", 10000, "hotdog", "/images/hotdog-klassik.png"),
  menuItem("gamburger", "Gamburger", 25000, "burger", "/images/gamburger-max.png"),
  menuItem("chizburger", "Chizburger", 28000, "burger", "/images/chizburger.png"),
  menuItem("kfc-achchiq", "KFC (Achchiq)", 30000, "kfc", "/images/kfc-sershira.png"),
  menuItem("fri", "Fri", 15000, "fri", "/images/fri-kartoshka.png"),
]

export function getItemById(id: string): FoodItem | undefined {
  return popularItems.find((item) => item.id === id)
}

export function formatSom(price: number) {
  return `${price.toLocaleString("ru-RU").replace(/,/g, " ")} so'm`
}
