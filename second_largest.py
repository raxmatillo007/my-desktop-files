def second_largest(lst):
    """
    Ro'yxatdagi ikkinchi eng katta sonni qaytaradi.
    Eslat: teng elementlar faqat bitta turli son deb hisoblanadi.
    """
    if not lst or len(lst) < 2:      # bo'sh yoki bitta element
        return None

    uniq = sorted(set(lst))          # takrorlar olib tashlanadi, tartib beriladi
    if len(uniq) < 2:                # bitta turli son bo'lsa
        return None

    return uniq[-2]                  # oxirgi = eng katta, undan bir oldiki = ikkinchi


# Testlar
print(second_largest([1, 5, 3, 9, 9, 4]))   # 5
print(second_largest([10, 10, 10]))         # None
print(second_largest([7, 2, 7, 3]))         # 3
print(second_largest([]))                   # None
print(second_largest([42]))                 # None
