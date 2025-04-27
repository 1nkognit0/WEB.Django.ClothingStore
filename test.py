a = [63, 80, 62, 69, 71, 37, 12, 90, 19, 67]
N = len(a)

for i in range(N-1):
    for j in range(N-1-i):
        if a[j] > a[j+1]:
            a[j], a[j+1] = a[j+1], a[j]

print(a)