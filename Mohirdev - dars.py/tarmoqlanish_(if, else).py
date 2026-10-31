# 09-dars. TARMOQWLANISH (if, else)
# sana: 10/12/2025
# Mualif: Raxmatillo

# avtolar =  ['audi', 'bmw', 'volvo', 'kia', 'hyundai']

# for avto in avtolar: # avtolar ichidadi har bir avto uchun ...
#     if avto == 'bmw': #...agar avto bmw ga teng bo'lsa ...
#         print(avto.upper()) # avto nomini hamma harflarini katta qiladi ...
#     else: # aks holda ...
#         print(avto.title()) # avto nomini faqat birinchi harfini katta qiladi ...


# ism = input('ismingiz nma ?\n>>>') # Foydalanuvchi ism soralmoqda ...
# if ism.lower() != 'ali': # Agar ism Aliga teng bolmasa ...
#     print(f"Uzr, {ism.title()} biz Alini kutyapmiz") 
# else:
#     print("Salom, Ali")

# javob = float(input("12x6 nechiga teng? >>>"))
# if javob!= 72:
#     print('Javob xato')

# yosh = int(input("Yoshingiz nechida?>>>"))
# if yosh>= 18: # yosh 18 dan yoki teng bolsa 
#     print("Xush kelibsz!")
# else: # aks holda 
#     print("Kirish mumkin emas!")

# login = input("Yangi login tanlang:")
# if len(login) <= 5: # login uzunligini tekshiramiz
#     print(" Login 5 harfdan koproq bolishi shart!")

# yil = int(input("Tugilgan yilingizni kiriting: "))
# if 2025-yil<18: # foydalanuvchining yoshini hisoblaymiz
#     print(f"Yoshingiz {2025-yil} da ekan.") 
#     print("Kirish mumkin emas!")
# else:
#     print("Xush kelibsiz!")

# yosh = int(input("Yoshingiz nechida?>>>"))
# if yosh>65: print("Siz COVID-19 risk guruhida ekansiz")

# x, y = 25, 50 # x=25 va y=50
# print("x > y") if x>y else print("x < y")

# AMALIYOT

#  1. Yangi cars = ['toyota', 'mazda', 'hyundai', 'gm', 'kia'] degan ro'yxat tuzing,
#  ro'yxat elementlarining birinchi harfini katta qilib konsolga chqaring. GM uchun ikkala harfni katta qiling. ✅

# cars = ['toyota', 'mazda', 'hyundai', 'gm', 'kia']
# for car in cars:
#     if car=='gm':
#         print(car.upper())
#     else:
#         print(car.title())

# 2. Yuqoridagi mashqni teng emas (!=) operatori yordamida bajaring.✅

# cars = ['toyota', 'mazda', 'hyundai', 'gm', 'kia']
# for car in cars:
#     if car!='gm':
#         print(car.title())
#     else:
#         print(car.upper())

# Foydalanuvchi login ismini so'rang. Agar login admin bo'lsa, "Xush kelibsiz, Admin.
# Foydalanuvchilar ro'yxatini ko'rasizmi?" xabarini konsolga chiqaring.
# Aks holda, "Xush kelibsiz, {foydalanuvchi_ismi}!" matnini konsolga chiqaring.

