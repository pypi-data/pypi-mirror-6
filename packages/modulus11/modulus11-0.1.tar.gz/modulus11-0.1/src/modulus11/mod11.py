""" Calculate check digit for TNT consignements.

>>> calc_check_digit("18392825")
2
>>> calc_check_digit("48025347")
0
"""

def calc_check_digit(number, factors = "86423597"):
    sum = 0
    for (f,n) in zip(factors, number):
        sum += int(f)*int(n)

    chk =  sum % 11
    if chk == 0:
        return 5
    if chk == 1:
        return 0

    return 11 - chk

if __name__ == "__main__":
    import doctest
    doctest.testmod()
