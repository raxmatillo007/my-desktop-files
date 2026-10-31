# 1.
# nums=[1,2,3,4,5] 
# nums=[1,2,3,4] 
# idx1 = 0
# idx2 = len(nums)-1

# while True:
#     if idx2 <= idx1:
#         break
#     a = nums[idx1]
#     b = nums[idx2]
#     nums[idx1] = b 
#     nums[idx2] = a
#     idx1 +=1
#     idx2 -=1
    
# print(nums)




# 2.
# a = [1,2,3]
# b = [4,5,6]
# idx = 0
# newlist = []

# while True:
#     g= a[idx]+b[idx]
#     newlist.append(g)
#     idx += 1
#     if idx == len(a):
#         break
# print(newlist)



# 3.
# grades = {
#     "Ali": 85,
#     "Vali": 72,
#     "Malika": 95,
#     "Aziza": 80,
# }
# for student, grade in grades.items():
#     if grade > 80:
#         print(student)

# 1. bankomat
# balance = 500000
# amount = 175000

# if amount <= 0:
#     print("Pul yechish rad etildi.")
# elif amount % 50000 != 0:
#     print("pul yechish rad etildi summa 50000 somga karrali bolishi kerak.")
# elif amount > balance:
#     print("pul yechish rad etildi balans yetarli mas.")

# else:
#     balance -= amount
#     print(f"pul yechishga ruxsat berildi Yechilgan summa: {amount} som Balans: {balance} som")



# 2. elektr energiyasi tolovi

# sarif = 250

# if sarif <= 100:
#     print(f"tolov: {sarif*450}som")
# elif sarif <= 200:
#     print(f"tolov:{(100*450) + (sarif-100)*900} som")
# elif sarif > 200:
#     print(f"tolov: {(100*450) + (100*900) + (sarif-200)*1500} som")

# 3. yetkazib berish narxi

# buyutma = 120000
# is_inside_city = False

# qabu_qilindi = False     
# yetkazish_narxi = 0
# jami_sum = 0

# if buyutma < 0:
#     print("buyutma manfiy bolishi mumkin emas")
# elif buyutma < 30000:
#     print("buyutma 30000 sumdan kam ")
# else:
#     qabu_qilindi = True
#     if buyutma >= 200000:
#         yetkazish_narxi = 0
#     else:
#         if is_inside_city:
#             yetkazish_narxi = 15000
#         else:
#             yetkazish_narxi = 30000
# jami_sum = buyutma + yetkazish_narxi

# if qabu_qilindi:
#     print("Buyurtma qabul qilindi")
#     print(f"Yetkazib berish narxi: {yetkazish_narxi} sum")
#     print(f"Jami summa: {jami_sum} sum")


# 4. Universitetga qabul
score = 88
age = 18 
interview_passed = True

if score < 0 or score > 100:
    print("qiymat notori")
elif age < 16:
    print("qabul qilindi")
elif score >= 85 and interview_passed:
    print("Stipendiya beriladi")
elif score >= 70 and interview_passed:
    print("oqishga qabul qilinadi")
else:
    print("Rad etiladi")


# 5. avtoturargoh tolov
hours = 4
is_member = True

if hours <= 0:
    print("qimat notogri")
elif hours > 24:
    print("kundalik limet oshib ketti")
else:
     if hours <= 2:
         total_price = hours * 5000
     else: 
        total_price = (2*5000) + ((hours - 2 ) * 3000)
        if is_member:
            total_price = total_price * 0.8 
print(f"Avtoturargoh tolov {int(total_price)} sum")
