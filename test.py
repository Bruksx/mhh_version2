li = [1, 2, 3, 4, 4, 5, 5]
maximum = []
maximum.append(li[0])
for item in li:
    if item > maximum[0]:
        for itm in maximum:
            li.pop(itm)
        maximum.append(item)
    if item == maximum[0]:
        maximum.append(item)
        


print(maximum)