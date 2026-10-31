# 1. Yetkazib berish buyutmasini tekshirish
# order_total = 85000
# product_available = True
# inside_city = False

# if product_available == False:
#     print("Buyurtma rad etildi.")
# elif order_total <= 0:
#     print("Buyurtma rad etildi.")
# else:
#     print("Buyurtma qabul qilindi")

# if order_total >= 100000:
#     yetkazib_berish = 0
# else:
#     if inside_city == True:
#         yetkazib_berish = 15000
#     else:
#         yetkazib_berish = 25000
# jami = order_total + yetkazib_berish
# print(f"Yetkazib berish: {yetkazib_berish} sum")
# print(f"Jami: {jami} sum")        

# 2. Mehmonxonada xona band qilish
age = 17
has_adult_companion = True
room_available = True
nights = 4
price_per_night = 200000

if nights <= 0:
    print("Bron rad etiladi.")
elif room_available == False:
    print("Bron rad etiladi")
elif age < 18 and has_adult_companion == False:
    print("Bron rad etiladi.")
else:
    print("Bron qabul qilidi.")
    if nights > 3:
        chegirma = 0.10
    else:
        chegirma = 0

    umumiy_narx = nights * price_per_night
    chegirma_summasi = umumiy_narx * chegirma
    jami = umumiy_narx - chegirma_summasi
print(f"Jami: {int(jami)} so'm")

