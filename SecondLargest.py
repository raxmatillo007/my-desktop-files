"""
ALGORITM #2:
    Ikkinchi Eng Katta Son

Masala:
    Berilgan ro'yxatda ikkinchi eng katta sonni toping.
"""

def second_largest(lst):
    """
    Ro'yxatdagi ikkinchi eng katta sonni qaytaradi.
    
    Agar:
        - ro'yxat bo'sh bo'lsa → None
        - bitta element bo'lsa → None
        - bir xil elementlar keskin bo'lsa → None
    """
    if not lst or len(lst) < 2:
        return None
    
    # Birlashtirilgan (takrorlantirilgan) elementlarni silish
    unique = sorted(set(lst))
    
    # Agar bitta turli element bo'lsa
    if len(unique) < 2:
        return None
    
    # Eng oxirgi element = eng katta, undan bir oldigi = ikkinchi
    return unique[-2]


def second_largest_optimized(lst):
    """
    Optimal ko'rinish: bitta bor o'tishda (O(n) vaqt).
    """
    if not lst or len(lst) < 2:
        return None
    
    largest = second = float('-inf')
    
    for num in lst:
        if num > largest:
            # Yangi katta topildi
            second = largest
            largest = num
        elif num > second and num != largest:
            # Eng katta emas, lekin kattasi nazarda tutilsa
            second = num
    
    # Agar ikkinchi katta topilmagan bo'lsa
    return second if second != float('-inf') else None


def main():
    # Test holillari
    test_cases = [
        [1, 5, 3, 9, 9, 4],
        [10, 10, 10],
        [7, 2, 7, 3],
        [],
        [42],
        [5, 5, 5, 5],
        [1, 2, 3, 4, 5],
        [-1, -5, -3, -9],
    ]
    
    print("===== II. IKKINCHI ENG KATTA SON =====\n")
    
    for i, lst in enumerate(test_cases, 1):
        print(f"Test#{i}: {lst} → {second_largest(lst)}")
    
    print("\n--- Optimal variant (second_largest_optimized) ---")
    for lst in test_cases:
        print(f"{lst} → {second_largest_optimized(lst)}")


if __name__ == "__main__":
    main()
