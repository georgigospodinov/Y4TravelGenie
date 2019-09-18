ans = [[0, 0, 1, 0, 1], [1, 0, 1, 0, 0],  # 2
    [1, 0, 1, 1, 0],  # 3
    [0, 0, 1, 1, 1],  # 1
    [1, 0, 1, 0, 1]  # 1
]

constant = ans[0]


def custom_compare(a):
    d: int = 0
    for i, x in enumerate(a):
        d += abs(x - constant[i])
    return d


ans.sort(key=custom_compare)
print(ans)
