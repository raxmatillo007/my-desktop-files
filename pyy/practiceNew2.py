# 1. juf va toq sonlar navbatlashishni sanash 

nums = [2, 5, 8, 7, 4, 6, 3]
qoshish = 0
for i in range(len(nums)-1):

    if nums[i] % 2 != nums[i+1]% 2:
       
        qoshish += 1
print(qoshish)

# 2. Har ikkinchi elementni teskari tartiblash

# nums = [10, 20, 30, 40, 50, 60, 70]
# toqlar = []
# for i in range(len(nums)):
#     if i % 2 !=0:
#         toqlar.append(nums[i])
# toqlar.reverse()

# for i in range(len(nums)):
#     if i % 2 != 0:
#         nums[i] = toqlar.pop(0)


# print(nums)
