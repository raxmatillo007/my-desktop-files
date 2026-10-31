# shu fayl yodamida bizning dasturimizni tartibli va chiroyli ko'rinishga keltiramiz .

import os

def oynani_tozalash():
    os.system('cls' if os.name == 'nt' else 'clear')

def sarlavha():
    print("===================================")
    print("      Tech House Do'koni")
    print("   Eng so'ngi texnologiyalar")
    print("===================================\n")

def ajratib_beruvchi(char='=', length=35):
    print(char * length)