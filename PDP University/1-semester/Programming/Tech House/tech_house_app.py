# shu fayl yordamida biz barcha kodimizni yozamiz .
from database import db
from ui import oynani_tozalash, sarlavha, ajratib_beruvchi
from datetime import datetime

class TechHouseApp:
    def __init__(self):
        db.init_db()
        self.savatcha = []

    def asosiy_menu(self):
        while True:
            oynani_tozalash()
            sarlavha()
            print("Asosiy Menu:")
            print("1. Mahsulot Korish")
            print("2. Mahsulot qidirish")
            print("3. Savatcha")
            print("4. Aksiyalar va A'zoliklar")
            print("5. Qo'llab-quvvatlash")
            print("6. Admin paneli")
            print("0. Chiqish")  

            tanlov = input("\nTanlovingiz: ")

            if tanlov == "1":
                self.katigoriyani_korish()
            elif tanlov == "2":
                self.mahsulotlarni_qidirish()
            elif tanlov == "3":
                self.savatcha_korish()
            elif tanlov == "4":
                self.azolik_aksiya()
            elif tanlov == "5":
                self.qollab_quvvatlash()
            elif tanlov == "6":
                self.admin_panel()
            elif tanlov == "0":
                print("Xaridingiz uchun rahmat!")
                break
    

    def katigoriyani_korish(self):
        kategoriyalar = [
            "Oshxona texnikasi",
            "Tozalash texnikasi",
            "Isitish va sovutish qurilmalari",
            "Shaxsiy parvarish qurilmalari",
            "Aqilliy uy texnikasi"
        ]
        while True:
            oynani_tozalash()
            sarlavha()  
            print("Kategoriyalar:")

            for raqam, kategoriya in enumerate(kategoriyalar, 1):
                print(f"{raqam}. {kategoriya}")
            print("0. Orqaga")

            tanlov = input("Kategoriyani tanlang: ")
            if tanlov == "0":
                break

            try:
                idx = int(tanlov) - 1
                if 0 <= idx < len(kategoriyalar):
                    self.mahsulotlar_royxati(kategoriyalar[idx])
                else:
                    input("Noto'g'ri tanlov! Enter bosing...")
            except ValueError:
                input("Faqat raqam kiriting! Enter bosing...")

    def mahsulotlar_royxati(self, kategoriya):
        mahsulotlar = db.mahsulotlarni_kategoriyasi_olish(kategoriya)

        while True:
            oynani_tozalash()
            sarlavha()
            print(f"{kategoriya} bo'yicha mahsulotlar:\n")
            print(f"{'ID':<4} {'Nomi': <25} {'Narxi': <12} {'Holati': <10}")
            ajratib_beruvchi('-',55)

            for mahsulot in mahsulotlar:
                print(f"{mahsulot.id:<4} {mahsulot.name:<25} {mahsulot.price:<12,.0f} {mahsulot.status:<10}")

            print("\n1. Savatchaga qo'shish")
            print("0. Orqaga")

            tanlov = input("\nTanlovingiz: ")

            if tanlov == "0":
                break

            elif tanlov == "1":
                mahsulot_id = int(input("Mahsulot ID raqamini kiriting: "))
                self.mahsulot_savatchaga_qoshish(mahsulot_id)
            else:
                input("Xato! Enter bosing...")


            
    def mahsulotlarni_qidirish(self):
        # mahsulotlar qidirish
        sorov = input("Mahsulot nomini kiriting: ")
        natija = db.mahsulotni_qidirish(sorov)

        if not natija:
            input("Mahsulot topilmadi! Enter bosing...")
            return
        
        oynani_tozalash()
        sarlavha()
        print(f"Qidirilgan mahsulotlar('{sorov}':)\n")
        for mahsulot in natija:
            print(f"ID: {mahsulot.id}, Nomi: {mahsulot.name}, Narxi: {mahsulot.price:,.0f} so'm | {mahsulot.get_category()}")
            tanlov = input("Savatchaga qo'shish? (ha/yo'q): ")
            if tanlov.lower() == "ha":
                self.mahsulot_savatchaga_qoshish(mahsulot.id)


    def mahsulot_savatchaga_qoshish(self, mahsulotlar_id):
        mahsulot = db.mahsulotni_idsi_olish(mahsulotlar_id)

        if mahsulot:
            self.savatcha.append(mahsulot)
            print(f"{mahsulot.name} savatchaga qo'shildi.")
            input("Davom etish uchun Enter bosing...")
        else:
            input("Noto'g'ri mahsulot ID mavjud emas ! Enter bosing...")

    def savatcha_korish(self):
           oynani_tozalash()
           sarlavha()
           if not self.savatcha:
               input("Savatcha bo'sh! Enter bosing...")
               return
           
           jami = 0
           print("Savatchadagi mahsulotlar:")
           for mahsulot in self.savatcha:
               print(f"{mahsulot.name}: {mahsulot.price:,.0f} so'm")
               jami += mahsulot.price

           ajratib_beruvchi('-', 30)   
           print(f"Jami: {jami:,.0f} so'm")

           print("\n1. Buyurtma berish")
           print("2. Buyurtmani bekor qilish")
           print("0. Orqaga")

           tanlov = input("Tanlovingiz: ")
           if tanlov == "1":
                self.buyurtma_berish(jami)
           elif tanlov == "2":
               self.savatcha = []
               input("Savatcha tozalandi! Enter bosing...")

              
    

    def buyurtma_berish(self, jami):
        oynani_tozalash()
        sarlavha()
        print(f"Buyurtmani rasmiylashtirish")

        ism = input("Ismingizni kiriting: ")
        telefon = input("Telefon raqamingizni kiriting: ")
        manzil = input("Manzilingizni kiriting: ")  

        print(f"\nYetkazib berish usuli.")
        print("1. Yetkazib berish (Kuryer)")
        print("2. Olib ketish (Do'kondan)")

        yetkazish_tanlovi = input("Tanlov: ")
        yetkazib_berish_turi = "Yetkazib berish" if yetkazish_tanlovi == "1" else "Olib ketish"

        print("\n Azolik paketingiz bormi?")
        print("1. Bronza (5% chegirma)")
        print("2. Silver (10% chegirma)")
        print("3. Gold (15% chegirma)")
        print("4. Biznes paket (20% chegirma)")
        print("5. Yo'q")

        azolik_tanlovi = input("Tanlov: ")

        chegirma = 0
        azolik = "Oddiy"
        if azolik_tanlovi == "1":
            chegirma = 0.05
            azolik = "Bronza"
        elif azolik_tanlovi == "2":
            chegirma = 0.10
            azolik = "Silver"
        elif azolik_tanlovi == "3":
            chegirma = 0.15
            azolik = "Gold"
        elif azolik_tanlovi == "4":
            chegirma = 0.20
            azolik = "Biznes paket"
        
        asosiy_narx = jami * (1 - chegirma)

        ballar = 0
        if azolik == "Bronza":
            ballar = int(asosiy_narx * 0.01)
        elif azolik == "Silver":
            ballar = int(asosiy_narx * 0.02)
        elif azolik == "Gold":
            ballar = int(asosiy_narx * 0.03)
        elif azolik == "Biznes paket":
            ballar = int(asosiy_narx * 0.05)
        
        print("\n")
        ajratib_beruvchi('-', 30)
        print(f"Mijoz: {ism}")
        print(f"Telefon: {telefon}")
        print(f"Manzil: {manzil}")
        print(f"Yetkazib berish turi: {yetkazib_berish_turi}")
        print(f"chegirma: {jami * chegirma:,.0f} so'm")
        print(f"Umumiy to'lov: {asosiy_narx:,.0f} so'm")
        print(f"Toplangan ballar: {ballar} ball")

        ajratib_beruvchi('-', 30)

        tasdiqlash = input("Buyurtmani tasdiqlaysizmi? (ha/yo'q): ")
        if tasdiqlash.lower() == "ha":
            mijoz_id = db.mijoz_qoshish(ism, telefon, manzil, azolik, ballar)

        dare_now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        for mahsulot in self.savatcha:
            db.sotuv_qoshish(mahsulot.id, mijoz_id, dare_now)

        self.savatcha = []
        print("Buyurtma qabul qilindi! Tez orada siz bilan bog'lanamiz.")
        input("Davom etish uchun Enter bosing...")







    def azolik_aksiya(self):
        oynani_tozalash()
        sarlavha()
        print("A'zolik paketlari:")
        print("1. Bronza - oddiy ballar va 5% chegirmalar.")
        print("2. Silver - ko'proq ballar, 10% ustuvor va chegirmalar.")
        print("3. Gold - bepul yetkazib berish, 15% maxsus narxlar")
        print("4. Biznes paket - ulgurji xaridlar uchun maxsus narxlar.")

        print("Aksiyalar:")
        print("- Har oy yangi mahsulotlarda chegirmalar.")
        input("\nOrqaga qaytish uchun Enter bosing...")
    
    def qollab_quvvatlash(self):
        oynani_tozalash()
        sarlavha()
        print("Qo'llab-quvvatlash bo'limi:")
        print("Telefon: +998 71 123 45 67")
        print("Email: techhouse@gmail.com")
        print("Telegram bot: @TechHouse_Support_Bot")
        print("Ish vaqti: Dushanba - Juma, 9:00 - 18:00")
        input("\nOrqaga qaytish uchun Enter bosing...")
    

    def admin_panel(self):
        parol = input("Admin parolini kiriting: ")
        if parol != "admin78900":
            input("Noto'g'ri parol! Enter bosing...")
            return
        
        while True:
            oynani_tozalash()
            sarlavha()
            print("Admin Panel:")
            
            print("1. Yangi mahsulot qo'shish")
            print("2. Sotuv tarixini ko'rish")
            print("3. Mijozlar ro'yxatini ko'rish")
            print("0. Orqaga")

            tanlov = input("\nTanlovingiz: ")
            if tanlov == "0":
                break

            if tanlov == "1":
                ism = input("Mahsulot nomi: ")
                try:
                    narx = float(input("Mahsulot narxi: "))
                    kategoriya = input("Mahsulot kategoriyasi: ")
                    db.mahsulot_qoshish(ism, narx, kategoriya)
                    print("Mahsulot muvaffaqiyatli qo'shildi!")
                except ValueError:
                    print("Noto'g'ri narx!")
                input("Enter bosing...")
            elif tanlov == "2":
                tolov_royxati = db.sotuvlar()
                print("\nSotuvlar tarixi:")
                for sotuv in tolov_royxati:
                    print(f"Sotuv ID: {sotuv.id}, Mahsulot ID: {sotuv.product_id}, Mijoz ID: {sotuv.mijoz_id}, Sana: {sotuv.sana}")
                    input("\nDavom etish uchun Enter bosing...")
            elif tanlov == "3":
                mijoz_royxati = db.mijozlar()
                print("\nMijozlar ro'yxati:")
                print(f"{'ID':<4} {'Ism':<20} {'Telefon':<15} {'Manzil':<30} {'A\'zolik':<15} {'Ballar':<10}")
                ajratib_beruvchi('-', 100)  

                for mijoz in mijoz_royxati:
                   print(f"{mijoz.id:<4} {mijoz.ism:<20} {mijoz.telefon:<15} {mijoz.manzil:<30} {mijoz.azolik:<15} {mijoz.ballar:<10}")
                   input("\nDavom etish uchun Enter bosing...")
