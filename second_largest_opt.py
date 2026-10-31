def second_largest_opt(lst):
    if not lst or len(lst) < 2:
        return None
    
    largest = second = float('-inf')
    
    for num in lst:
        if num > largest:
            second = largest
            largest = num
        elif num > second and num != largest:
            second = num
    
    return second if second != float('-inf') else None


# Test
print(second_largest_opt([1, 5, 3, 9, 9, 4]))   # 5
print(second_largest_opt([10, 10, 10]))         # None
print(second_largest_opt([7, 2, 7, 3]))         # 3
