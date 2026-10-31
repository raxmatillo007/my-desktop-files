name = "rrr"
balance = 1000     
history = ["Hisob ochildi", "1000 qo'shildi"]

while True:

    
    print("1. Pul qo'shish")
    print("2. Pul olish")
    print("3. Balans")
    print("4. Tarix")
    print("5. Chiqish")

    tanlov = input("Tanla: ")

    if tanlov == "1":
        pul = int(input("Qancha qo'shasiz: "))
        balance += pul
        history.append(f"{pul} qo'shildi")
        print("Pul qo'shildi!")

    elif tanlov == "2":
        pul = int(input("Qancha olasiz: "))
        if pul > balance:
            print("Pul yetmaydi!")
        else:
            balance -= pul
            history.append(f"{pul} olindi")
            print("Pul olindi!")

    elif tanlov == "3":
        print("Balans:", balance)

    elif tanlov == "4":
        for i in history:
            print(i)

    elif tanlov == "5":
        print("Dastur tugadi")
        break

    else:
        print("Noto'g'ri tanlov!")