# shu fayl yordamida biz mahsulotlar, mijoz va sotuv ma'lumotlarini saqlaymiz .
# Ma'lumotlar ombori - OOP bilan

from abc import ABC, abstractmethod

class Product(ABC):
    def __init__(self, id, name, price, status):
        self._id = id
        self._name = name
        self._price = price
        self._status = status

    @property
    def id(self):
        return self._id

    @property
    def name(self):
        return self._name

    @property
    def price(self):
        return self._price

    @property
    def status(self):
        return self._status

    @abstractmethod
    def get_category(self):
        pass

    def display_info(self):
        return f"ID: {self._id}, Nomi: {self._name}, Narxi: {self._price}, Holati: {self._status}"

class KitchenProduct(Product):
    def get_category(self):
        return "Oshxona texnikasi"

class CleaningProduct(Product):
    def get_category(self):
        return "Tozalash texnikasi"

class HVACProduct(Product):
    def get_category(self):
        return "Isitish va sovutish qurilmalari"

class PersonalCareProduct(Product):
    def get_category(self):
        return "Shaxsiy parvarish qurilmalari"

class SmartHomeProduct(Product):
    def get_category(self):
        return "Aqilliy uy texnikasi"

class Customer:
    def __init__(self, id, ism, telefon, manzil, azolik, ballar):
        self._id = id
        self._ism = ism
        self._telefon = telefon
        self._manzil = manzil
        self._azolik = azolik
        self._ballar = ballar

    @property
    def id(self):
        return self._id

    @property
    def ism(self):
        return self._ism

    @property
    def telefon(self):
        return self._telefon

    @property
    def manzil(self):
        return self._manzil

    @property
    def azolik(self):
        return self._azolik

    @property
    def ballar(self):
        return self._ballar

class Sale:
    def __init__(self, id, product_id, mijoz_id, sana):
        self._id = id
        self._product_id = product_id
        self._mijoz_id = mijoz_id
        self._sana = sana

    @property
    def id(self):
        return self._id

    @property
    def product_id(self):
        return self._product_id

    @property
    def mijoz_id(self):
        return self._mijoz_id

    @property
    def sana(self):
        return self._sana

class Database:
    def __init__(self):
        self._products = [
            KitchenProduct(1, "Mikroto'lqinli pech", 2_500_000, "mavjud"),
            CleaningProduct(2, "Changyutgich", 3_500_000, "mavjud"),
            HVACProduct(3, "Konditsioner", 15_000_000, "mavjud"),
            PersonalCareProduct(4, "Elektr soch qurutgichi", 1_200_000, "mavjud"),
            SmartHomeProduct(5, "Aqlli chiroq", 800_000, "mavjud"),
        ]
        self._customers = []
        self._sales = []

    def init_db(self):
        pass

    def mahsulotni_qidirish(self, sorov):
        return [mahsulot for mahsulot in self._products if sorov.lower() in mahsulot.name.lower()]

    def mahsulotni_idsi_olish(self, mahsulot_id):
        for mahsulot in self._products:
            if mahsulot.id == mahsulot_id:
                return mahsulot
        return None

    def mahsulotlarni_kategoriyasi_olish(self, kategoriya):
        return [mahsulot for mahsulot in self._products if mahsulot.get_category() == kategoriya]

    def mahsulot_qoshish(self, name, price, category):
        yangi_id = len(self._products) + 1
        if category == "Oshxona texnikasi":
            yangi_mahsulot = KitchenProduct(yangi_id, name, price, "Mavjud")
        elif category == "Tozalash texnikasi":
            yangi_mahsulot = CleaningProduct(yangi_id, name, price, "Mavjud")
        elif category == "Isitish va sovutish qurilmalari":
            yangi_mahsulot = HVACProduct(yangi_id, name, price, "Mavjud")
        elif category == "Shaxsiy parvarish qurilmalari":
            yangi_mahsulot = PersonalCareProduct(yangi_id, name, price, "Mavjud")
        elif category == "Aqilliy uy texnikasi":
            yangi_mahsulot = SmartHomeProduct(yangi_id, name, price, "Mavjud")
        else:
            yangi_mahsulot = Product(yangi_id, name, price, "Mavjud")  # but abstract, so error, but assume category exists
        self._products.append(yangi_mahsulot)
        return yangi_id

    def mijoz_qoshish(self, ism, telefon, manzil, azolik, ballar):
        yangi_id = len(self._customers) + 1
        yangi_mijoz = Customer(yangi_id, ism, telefon, manzil, azolik, ballar)
        self._customers.append(yangi_mijoz)
        return yangi_id

    def sotuv_qoshish(self, product_id, mijoz_id, sana):
        yangi_id = len(self._sales) + 1
        yangi_sotuv = Sale(yangi_id, product_id, mijoz_id, sana)
        self._sales.append(yangi_sotuv)
        return True
   
    def mahsulot_statusini_yangilash(self, mahsulot_id, yangi_status):
        for mahsulot in self._products:
            if mahsulot.id == mahsulot_id:
                mahsulot._status = yangi_status
                return True
        return False

    def mijoz_tolovini_olish(self, mijoz_id):
       return [sotuv.product_id for sotuv in self._sales if sotuv.mijoz_id == mijoz_id]

    def sotuvlar(self):
        return self._sales

    def mijozlar(self):
        return self._customers

# Instance yaratish
db = Database()