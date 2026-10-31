# 08-dars. Lists (ro'yhatlar) 
# sana: 24/11/2025
# Mualif: Raxmatillo

# cars = ['malibu', 'byd', 'jetaur', 'l9', 'Bmw', 'mers', 'damas', 'labo']

# print(len(cars)) # len funksiyasi ro'yxatdagilarni sanaydi nechtaligini 
# cars.sort()# elementlarni alifbo boyicha tartibda joylash tiradi 
# agar katta hariflarda soz bolsa ular birinchiga chiqib qoladi 
# print(cars) 
# print(sorted(cars)) # sorted ro'yxatdan YANGI tartiblangan ro'yxat yaratadi (asl ro'yxatni o'zgartirmaydi)
# cars.reverse() # reverse metodi elementlarni teskari qilib beradi 
# print(cars)


# sonlar = [12,45,86,9,85,-42,36,96,-15,87,-29]
# print(sorted(sonlar)) # sorted yangi royxat tartiblandi (asil royxat uzgarmagan )
# sonlar.sort() # sonlarni tartiblab chiqishi uchun ham ishlaydi 
# print(sonlar)
# sonlar.sort(reverse=True) # shunda esa shu elementlarni teskarisiga qilib beradi 
# print(sonlar) 

# print(list(range(10))) # range(10) — 0 dan 9 gacha bo'lgan sonlar ketma-ketligini yaratadi

# toq_sonlar = list(range(1,20,2)) # toq sonlar chiqarish uchun " 1 " 1 dan boshlanishi uchun
# # " 20 " esa 19 gacha boradi bunda shunaqa nechi son kiritsayiz ushandan ushandan 1 ayrib tashlaydi " 2 " esa qadam bildiradi
# print(toq_sonlar)

# juft_son = list(range(0,20,2)) # endi esa 0 dan boshlangani uchun faqat qadamlari 2ta 2ta dan yurgani uchun natija faqat juft ciqaradi
# print(juft_son)

# sanash = list(range(0,101,10)) # edi esa 10 dan orasida masofa boladi endi natija shu [0, 10, 20, 30, 40, 50, 60, 70, 80, 90, 100]
# print(sanash)

# toq_sonlar = list(range(1,20,2))
# max_qiymat = max(toq_sonlar) # max funksiyasini vazifasi shu qiymatlar ichidagi eng kattasini topib beradi
# print(max_qiymat)

# toq_sonlar = list(range(1,20,2))
# min_qiymat = min(toq_sonlar) # min funksiyasini vazifasi shu qiymatlar ichidagi eng kichkinasi topib beradi
# jami = sum(toq_sonlar) # sum funksiyasi vazifasi shu qiymatlarni yigindisini chiqarib beradi
# print(min_qiymat)
# print(jami)
# print(toq_sonlar)

# cars = ['malibu', 'byd', 'jetaur', 'l9', 'Bmw', 'mers', 'damas', 'labo']
# my_cars = cars[:] # kopiya qilishi uchun " [:] " shundan foydalanamiz 
# print(my_cars)
# my_cars.remove("byd")
# print(my_cars)
# print(cars)

# TUPLES

# toys = ('bus', 'car', 'bear', 'dino', 'snake', 'lizard') # uzgartib bolmas qiymatlar uchun ishlatami " () "
# print(toys)
# # agarda shu uzgartirb bolmasga qandaydir holatda uzgartirishga tori kelib qolsa shu usul orqali uzgartirse boladi
# toys =list(toys) # tuple ni binichi oddiy list ga utkazib olamz 
# toys.append("teddy") # keyin element qoshamiz 
# print(toys)

# toys = tuple(toys) # va yana shu tuples ga qaytarib qoyamz 
# print(toys)


# AMALIYOT

# 1.O'zingizga ma'lum davlatlarning ro'yxatini tuzing va ro'yxatni konsolga chiqaring✅
# davlatlar = ['uzbekistan', 'russiya', 'amerika', 'germaniya', 'kazagistan', 'tajigistan', 'avganistan', 'portugaliya','fransiya',]
# print(davlatlar)

# 2.Ro'yxatning uzunligini konsolga chiqaring✅
# davlatlar = ['uzbekistan', 'russiya', 'amerika', 'germaniya', 'kazagistan', 'tajigistan', 'avganistan', 'portugaliya','fransiya',]
# print(len(davlatlar))

# 3.sorted() funktsiyasi yordamida ro'yxatni tartiblangan holda konsolga chiqaring✅
# davlatlar = ['uzbekistan', 'russiya', 'amerika', 'germaniya', 'kazagistan', 'tajigistan', 'avganistan', 'portugaliya','fransiya',]
# print(sorted(davlatlar))

# 4.sorted() yordamida ro'yxatni teskari tartibda konsolga chiqaring✅
# davlatlar = ['uzbekistan', 'russiya', 'amerika', 'germaniya', 'kazagistan', 'tajigistan', 'avganistan', 'portugaliya','fransiya',]
# print(sorted(davlatlar, reverse=True))

# 5.Asl ro'yxatni qaytadan konsolga chiqaring✅
# davlatlar = ['uzbekistan', 'russiya', 'amerika', 'germaniya', 'kazagistan', 'tajigistan', 'avganistan', 'portugaliya','fransiya',]
# print(sorted(davlatlar, reverse=True))
# print(davlatlar)

# 6.reverse() metodi yordamida ro'yxatni ortidan boshlab chiqaring✅
# davlatlar = ['uzbekistan', 'russiya', 'amerika', 'germaniya', 'kazagistan', 'tajigistan', 'avganistan', 'portugaliya','fransiya',]
# davlatlar.reverse()
# print(davlatlar)

# 7.sort() metodi yordamida ro'yxatni avval alifbo bo'yicha, keyin esa alifboga teskari tartibda konsolga chiqaring.✅
# davlatlar = ['uzbekistan', 'russiya', 'amerika', 'germaniya', 'kazagistan', 'tajigistan', 'avganistan', 'portugaliya','fransiya',]
# davlatlar.sort()
# print(davlatlar)
# davlatlar.sort(reverse=True)
# print(davlatlar)

# 8.120 dan 1200 gacha bo'lgan juft sonlar ro'yxatini tuzing✅
# sonlar = list(range(120,1200,2))
# print(sonlar)

# 9.Ro'yxatdagi sonlar yig'indisini hisoblang va konsolga chiqaring✅
# sonlar = list(range(120,1200))
# jami = sum(sonlar)
# print(jami)

# 10.Ro'yxatdagi eng katta va eng kichik son o'rtasidagi ayirmani hisoblang va konsolga chiqaring✅
# sonlar = list(range(120,1200))
# print(max(sonlar)-min(sonlar))

# 11.Ro'yxatdagi elementlar sonini hisoblang✅
# sonlar = list(range(120,1200))
# print(len(sonlar))

# 12.Ro'yxatning boshidan, o'rtasidan va oxiridan 20 ta qiymatni konsolga chiqaring✅
# sonlar = list(range(120,1200))
# print(sonlar[:20])
# print(sonlar[-20:])
# print(sonlar[530:550])

# 13.taomlar degan ro'yxat yarating va ichiga istalgan 5ta taomni kiriting✅
# taomlar = ['osh','somsa','norin','shashlik','qozonkabob']
# print(taomlar)

# 14.nonushta degan yangi ro'yxatga taomlardan nusxa oling✅
# taomlar = ['osh','somsa','norin','shashlik','qozonkabob']
# nonushta = taomlar [:]
# taomlar.append('jiz')
# print(taomlar)
# print(nonushta)

# 15.Yangi ro'yxatda faqat nonushtaga yeyiladigan taomlarni qoldiring, va qo'shimcha 2 ta taom qo'shing✅
# taomlar = ['osh','somsa','norin','shashlik','qozonkabob']

# # Nonushtaga yeguliklar ro'yxati
# nonushta = ['somsa', 'norin']  # faqat nonushtaga yeyiladigan taomlar

# # Yangi ro'yxat yaratamiz (nonushta taomlari + 2 ta qo'shimcha)
# nonushta_yangi = nonushta[:]  # asl nonushta ro'yxatini nusxaladik
# nonushta_yangi.append('tuxum')   # 1 ta qo'shimcha
# nonushta_yangi.append('choy')    # 2 ta qo'shimcha

# print(nonushta_yangi)

# 16.Ikkala ro'yxatni ham (taomlar va nonushta) konsolga chiqaring✅

# taomlar = ['osh','somsa','norin','shashlik','qozonkabob']

# # Nonushtaga yeguliklar ro'yxati
# nonushta = ['somsa', 'norin']  # faqat nonushtaga yeyiladigan taomlar

# # Yangi ro'yxat yaratamiz (nonushta taomlari + 2 ta qo'shimcha)
# nonushta_yangi = nonushta[:]  # asl nonushta ro'yxatini nusxaladik
# nonushta_yangi.append('tuxum')   # 1 ta qo'shimcha
# nonushta_yangi.append('choy')    # 2 ta qo'shimcha

# # Konsolga chiqaramiz
# print("Asl taomlar ro'yxati:", taomlar)
# print("Asl nonushta ro'yxati:", nonushta)
# print("Yangi nonushta ro'yxati:", nonushta_yangi)

# 17.Yuqoridagi nonushta ro'yxatini o'zgarmas ro'yxatga aylantiring va nonushta[0] = "qaymoq va non" deb qiymat berib ko'ring.✅

# nonushta = ['somsa', 'norin', 'tuxum','choy']
# nonushta[0] = 'qaymoq va non'
# nonushta = tuple(nonushta)

# print(nonushta)



