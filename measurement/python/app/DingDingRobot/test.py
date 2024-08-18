
print("test")
i=0
with open("cls","r") as f:
    cls=f.readlines()
    for name in cls[:-1]:
        a=name.split("\n")[0]
        print(r"'"+a+"':"+str(i)+",")
        i+=1
