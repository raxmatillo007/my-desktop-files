def second_largest(lst):
    if not lst or len(lst) < 2:
        return None
    uniq = sorted(set(lst))
    if len(uniq) < 2:
        return None
    return uniq[-2]   # eng oxirgi = eng katta, undan bir o'tkaz = ikkinchi

# Test
print(second_largest([1, 5, 3, 9, 9, 4]))   # 5
print(second_largest([10, 10, 10]))         # None
print(second_largest([7, 2, 7, 3]))         # 3
