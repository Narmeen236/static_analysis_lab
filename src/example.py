def calc(a, b):
    x = 0
    if a > 0 and b > 0:
        x = a - b if a > b else b - a
    return x
