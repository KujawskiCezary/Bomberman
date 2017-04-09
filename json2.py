def aa(obj):
    print(obj)
    for i in range(len(obj)):
        print(obj[i])
        del obj[i]

    return obj

a = [0,1,2,3,4]
b = aa(a)
print(a)
print(b)
