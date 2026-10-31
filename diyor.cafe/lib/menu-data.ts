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
 M18.9,67.6V70c0,4.2,3.4,7.7,7.7,7.7h46.2c4.2,0,7.7-3.4,7.7-7.7v-2.8c-1.8,1.3-4.5,2-7.5,2c-3.7,0-7.1-1.2-8.8-3.2c-0.3-0.4-0.9-0.6-1.6-0.6h-2.4c-0.6,0-1.2,0.2-1.6,0.6c-1.7,2-5.1,3.2-8.8,3.2c-3.7,0-7.1-1.2-8.8-3.2c-0.3-0.4-0.9-0.6-1.6-0.6h-2.9c-0.6,0-1.2,0.2-1.6,0.6c-1.7,2-5.1,3.2-8.8,3.2C23.2,69.3,20.8,68.7,18.9,67.6z M80.3,57.5H19.9c-3.9,0-7.1-3.3-7.1-7.4c0-2,0.7-3.8,2-5.2c1.4-1.4,3.1-2.2,5-2.2h41c0.5,0,1,0.3,1.3,0.7l2.1,3.5l4.6-3.9c0.3-0.2,0.6-0.4,1-0.4h10.5c3.9,0,7.1,3.3,7.1,7.4c0,2-0.7,3.8-2,5.2C84,56.7,82.2,57.5,80.3,57.5z M19.9,45.6c-1.1,0-2.1,0.4-2.9,1.3c-0.8,0.8-1.2,2-1.2,3.2c0,2.4,1.8,4.4,4.1,4.4h60.4c1.1,0,2.1-0.4,2.9-1.3c0.8-0.8,1.2-2,1.2-3.2c0-2.4-1.8-4.4-4.1-4.4h-9.9l-5.5,4.7c-0.3,0.3-0.8,0.4-1.2,0.3c-0.4-0.1-0.8-0.3-1-0.7L60,45.6H19.9z M63.9,50.7c-0.1,0-0.2,0-0.2,0c-0.4-0.1-0.8-0.3-1-0.7L60,45.6H20.1c-0.8,0-1.5-0.7-1.5-1.5v-6.8c0-0.8,0.7-1.5,1.5-1.5h59.3c0.8,0,1.5,0.7,1.5,1.5v6.8c0,0.8-0.7,1.5-1.5,1.5h-9l-5.5,4.7C64.6,50.6,64.3,50.7,63.9,50.7z M21.6,42.6h39.2c0.5,0,1,0.3,1.3,0.7l2.1,3.5l4.6-3.9c0.3-0.2,0.6-0.4,1-0.4h8v-3.8H21.6V42.6z M73,69.3c-4.2,0-7.8-1.5-9.3-3.8H59c-1.5,2.3-5.1,3.8-9.3,3.8c-4.2,0-7.8-1.5-9.3-3.8h-5.2c-1.5,2.3-5.1,3.8-9.3,3.8c-4.4,0-8.1-1.6-9.4-4c-2.3-0.7-3.9-2.8-3.9-5.2c0-2.5,1.8-4.7,4.2-5.3c0.2-0.1,0.4-0.1,0.6-0.1H82c3,0,5.4,2.4,5.4,5.4c0,2.9-2.3,5.3-5.1,5.4C80.8,67.8,77.2,69.3,73,69.3z M58.1,62.5h6.5c0.6,0,1.2,0.4,1.4,1c0.4,1.3,3.2,2.8,7,2.8c3.7,0,6.5-1.4,6.9-2.8c0.2-0.6,0.8-1,1.4-1H82c1.3,0,2.4-1.1,2.4-2.4c0-1.3-1.1-2.4-2.4-2.4H17.8c-0.1,0-0.1,0-0.2,0c-1.2,0.2-2.1,1.2-2.1,2.4s0.9,2.2,2.1,2.4c0.2,0,0.3,0.1,0.4,0.1c0.4,0.2,0.8,0.5,0.9,0.9c0.4,1.3,3.2,2.8,7,2.8c3.7,0,6.5-1.4,6.9-2.8c0.2-0.6,0.8-1,1.4-1h7c0.6,0,1.2,0.4,1.4,1c0.4,1.3,3.2,2.8,6.9,2.8c3.7,0,6.5-1.4,6.9-2.8C56.9,62.9,57.4,62.5,58.1,62.5z M82,38.9H17.4c-0.8,0-1.5-0.7-1.5-1.5v-1.8c0-9,7.3-16.3,16.3-16.3h34.9c9,0,16.3,7.3,16.3,16.3v1.8C83.5,38.2,82.8,38.9,82,38.9z M18.9,35.9h61.6v-0.3c0-7.3-6-13.3-13.3-13.3H32.3c-7.3,0-13.3,6-13.3,13.3V35.9z M31.6,31.4l3.8-3.8c0.6-0.6,0.6-1.5,0-2.1c-0.6-0.6-1.5-0.6-2.1,0l-3.8,3.8c-0.6,0.6-0.6,1.5,0,2.1c0.3,0.3,0.7,0.4,1.1,0.4C30.9,31.8,31.3,31.6,31.6,31.4z M48.9,31.4l3.8-3.8c0.6-0.6,0.6-1.5,0-2.1c-0.6-0.6-1.5-0.6-2.1,0l-3.8,3.8c-0.6,0.6-0.6,1.5,0,2.1c0.3,0.3,0.7,0.4,1.1,0.4C48.2,31.8,48.6,31.6,48.9,31.4z M65.6,31.4l3.8-3.8c0.6-0.6,0.6-1.5,0-2.1c-0.6-0.6-1.5-0.6-2.1,0l-3.8,3.8c-0.6,0.6-0.6,1.5,0,2.1c0.3,0.3,0.7,0.4,1.1,0.4C64.9,31.8,65.3,31.6,65.6,31.4z"/>
    </svg>
  )
}

export type Category = {
  id: string
  label: string
  icon: LucideIcon
}

function KfcIcon(props: React.ComponentPropsWithoutRef<"svg">) {
  return (
    <svg
      viewBox="0 0 100 100"
      fill="currentColor"
      xmlns="http://www.w3.org/2000/svg"
      {...props}
    >
      <path d="M59.3,88.2H39.7c-0.8,0-1.4-0.6-1.5-1.4l-4.7-49.4c0-0.4,0.1-0.8,0.4-1.2s0.7-0.5,1.1-0.5h29.1c0.4,0,0.8,0.2,1.1,0.5s0.4,0.7,0.4,1.2l-4.7,49.4C60.8,87.6,60.1,88.2,59.3,88.2z M41.1,85.2H58l4.4-46.4H36.7L41.1,85.2z M69.3,88.2h-10c-0.4,0-0.8-0.2-1.1-0.5s-0.4-0.7-0.4-1.2l4.7-49.4c0.1-0.8,0.7-1.4,1.5-1.4h10c0.4,0,0.8,0.2,1.1,0.5s0.4,0.7,0.4,1.2l-4.7,49.4C70.8,87.6,70.1,88.2,69.3,88.2z M61,85.2h7l4.4-46.4h-7L61,85.2z M59.3,88.2H39.7c-0.8,0-1.4-0.6-1.5-1.4l-4.7-49.4c0-0.4,0.1-0.8,0.4-1.2s0.7-0.5,1.1-0.5h29.1c0.4,0,0.8,0.2,1.1,0.5s0.4,0.7,0.4,1.2l-4.7,49.4C60.8,87.6,60.1,88.2,59.3,88.2z M41.1,85.2H58l4.4-46.4H36.7L41.1,85.2z M39.7,88.2h-10c-0.8,0-1.4-0.6-1.5-1.4l-4.7-49.4c0-0.4,0.1-0.8,0.4-1.2s0.7-0.5,1.1-0.5h10c0.8,0,1.4,0.6,1.5,1.4l4.7,49.4c0,0.4-0.1,0.8-0.4,1.2S40.2,88.2,39.7,88.2z M31.1,85.2h7l-4.4-46.4h-7L31.1,85.2z M59.3,88.2H39.7c-0.8,0-1.4-0.6-1.5-1.4l-4.7-49.4c0-0.4,0.1-0.8,0.4-1.2s0.7-0.5,1.1-0.5h29.1c0.4,0,0.8,0.2,1.1,0.5s0.4,0.7,0.4,1.2l-4.7,49.4C60.8,87.6,60.1,88.2,59.3,88.2z M41.1,85.2H58l4.4-46.4H36.7L41.1,85.2z M71.4,38.8H27.7c-3.1,0-5.6-2.5-5.6-5.6c0-1.7,0.8-3.3,2.1-4.3c-0.7-1.3-1-2.7-1-4.2c0-4.9,3.9-8.9,8.7-9.1c2.2-3.7,6.1-5.9,10.4-5.9c2.7,0,5.3,0.9,7.4,2.5c2.1-1.7,4.7-2.5,7.4-2.5c4.3,0,8.3,2.3,10.4,6c4.6,0.5,8.2,4.4,8.2,9.1c0,1.5-0.3,2.9-1,4.2c1.3,1,2.1,2.6,2.1,4.3C76.9,36.3,74.4,38.8,71.4,38.8z M32.4,18.6c-3.4,0-6.2,2.8-6.2,6.2c0,1.4,0.4,2.7,1.3,3.8c0.3,0.4,0.4,0.9,0.3,1.3c-0.1,0.5-0.5,0.8-0.9,1c-1,0.4-1.7,1.3-1.7,2.4c0,1.4,1.2,2.6,2.6,2.6h43.7c1.4,0,2.6-1.2,2.6-2.6c0-1.1-0.7-2-1.7-2.4c-0.5-0.2-0.8-0.5-0.9-1c-0.1-0.5,0-1,0.3-1.3c0.8-1.1,1.3-2.4,1.3-3.8c0-3.4-2.8-6.2-6.2-6.2c-0.6,0-1.1-0.3-1.4-0.8c-1.6-3.1-4.7-5.1-8.2-5.1c-2.4,0-4.7,0.9-6.4,2.6c-0.6,0.6-1.5,0.6-2.1,0c-1.7-1.7-4-2.6-6.4-2.6c-3.5,0-6.6,2-8.2,5.1c-0.3,0.5-0.8,0.9-1.4,0.8l-0.1,0C32.5,18.6,32.4,18.6,32.4,18.6z M43.8,29.3c0.6-0.6,0.6-1.5,0-2.1c-1.9-2-4-2.9-6.1-2.8c-3.3,0.1-5.5,2.8-5.6,2.9c-0.5,0.6-0.4,1.6,0.2,2.1c0.6,0.5,1.6,0.4,2.1-0.2c0,0,1.5-1.7,3.4-1.8c1.3,0,2.6,0.6,3.8,1.9c0.3,0.3,0.7,0.5,1.1,0.5C43.2,29.7,43.5,29.5,43.8,29.3z M66.1,29.3c0.6-0.6,0.6-1.5,0-2.1c-1.9-2-4-2.9-6.1-2.8c-3.3,0.1-5.5,2.8-5.6,2.9c-0.5,0.6-0.4,1.6,0.2,2.1c0.6,0.5,1.6,0.4,2.1-0.2c0,0,1.5-1.7,3.4-1.8c1.3,0,2.6,0.6,3.8,1.9c0.3,0.3,0.7,0.5,1.1,0.5C65.4,29.7,65.8,29.5,66.1,29.3z M49.4,73.2c-7.6,0-13.8-6.1-13.8-13.6S41.8,46,49.4,46c7.6,0,13.8,6.1,13.8,13.6S57,73.2,49.4,73.2z M49.4,49c-5.9,0-10.8,4.8-10.8,10.6s4.8,10.6,10.8,10.6c5.9,0,10.8-4.8,10.8-10.6S55.3,49,49.4,49z" />
    </svg>
  )
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


