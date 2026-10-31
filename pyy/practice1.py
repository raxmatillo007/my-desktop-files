# 1. Navbatma va navbat yigindi 
# nums = [5, 3, 8, 2, 6]

# natija = 0

# for i in range(len(nums)):
#     if i % 2 == 0:
#         natija += nums[i]
#     else:
#         natija -= nums[i]

# print(natija)

# 2. Yonalish ozgarisharni sanash
nums = [2, 5, 8, 6, 4, 7, 7, 3]

count = 0
direction = None

for i in range (len(nums) -1):
    if nums[i] == nums[i + 1]:
        continue
    elif nums[i] < nums[i + 1]:
        yonalish = "up"
    elif nums[i] > nums[i + 1]:
        yonalish = "down"
    if direction is not None and yonalish != direction:
        count += 1
    direction = yonalish
    
print(count)

