v = int(input())

q = v // 100
r = v % 100
if (q != 0):
    print(q, "nota(s) de R$ 100,00")
else:
    print("0 nota(s) de R$ 100,00")
    
v = r
q = v // 50
r = v % 50
if (q != 0):
    print(q, "nota(s) de R$ 50,00")
else:
    print("0 nota(s) de R$ 50,00")
    
v = r
q = v // 20
r = v % 20
if (q != 0):
    print(q, "nota(s) de R$ 20,00")
else:
    print("0 nota(s) de R$ 20,00")
    
v = r
q = v // 10
r = v % 10
if (q != 0):
    print(q, "nota(s) de R$ 10,00")
else:
    print("0 nota(s) de R$ 10,00")
    
v = r
q = v // 5
r = v % 5
if (q != 0):
    print(q, "nota(s) de R$ 5,00")
else:
    print("0 nota(s) de R$ 5,00")
    
v = r
q = v // 2
r = v % 2
if (q != 0):
    print(q, "nota(s) de R$ 2,00")
else:
    print("0 nota(s) de R$ 2,00")

v = r
q = v // 1
r = v % 1
if (q != 0):
    print(q, "nota(s) de R$ 1,00")
else:
    print("0 nota(s) de R$ 1,00")


"""576
5 nota(s) de R$ 100,00
1 nota(s) de R$ 50,00
1 nota(s) de R$ 20,00
0 nota(s) de R$ 10,00
1 nota(s) de R$ 5,00
0 nota(s) de R$ 2,00
1 nota(s) de R$ 1,00"""