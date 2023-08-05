"""Damm algorithm decimal check digit

Note that check digits are NOT used for verification of data transfers between
computers -- use a CRC or a hash for that purpose! Check digits are used to
check *manual* entry of a digit into a computer system.

A Damm check digit is a single decimal check digit that can detect any
single-digit error as well as any adjacent-digit transpositions. The digit
computed in this module also detects some important phonetic errors (13<->30,
14<->40, ... 19<-->90).

This makes the Damm check digit better than other, more well-known check digits
like the Luhn code (used in credit cards) and the ISBN base-11 check digit. It
is equal in detection strength to a Verhoeff check digit, but much simpler to
compute.

There are two functions in this module: `encode` and `check`. The first,
`encode` is used to calculate the check digit for a number that you have. The
second, `check` is used to check that a number that was entered was entered
correctly.

The Damm check digit is computed by starting with a check digit of zero and then
continually multiplying this check digit with the digits of a given number,
using the multiplication of a totally anti-symmetric quasigroup. The properties
and the selection of the group ensure the qualities of the check digit stated
above.

For further reference on how the algorithm works see
http://en.wikipedia.org/wiki/Damm_algorithm

If you run this module as a python script, a handful of test cases are executed.

"""


# we use the matrix given in the WP article because it's a good one
matrix = (
    (0, 3, 1, 7, 5, 9, 8, 6, 4, 2),
    (7, 0, 9, 2, 1, 5, 4, 8, 6, 3),
    (4, 2, 0, 6, 8, 7, 1, 3, 5, 9),
    (1, 7, 5, 0, 9, 8, 3, 4, 2, 6),
    (6, 1, 2, 3, 0, 4, 5, 9, 7, 8),
    (3, 6, 7, 4, 2, 0, 9, 5, 8, 1),
    (5, 8, 6, 9, 7, 2, 0, 1, 3, 4),
    (8, 9, 4, 5, 3, 6, 2, 0, 1, 7),
    (9, 4, 3, 8, 6, 1, 7, 2, 0, 5),
    (2, 5, 8, 1, 4, 3, 6, 7, 9, 0)
)


def encode(number):
    """Compute the Damm check digit for the given number.
    
    The number can be in any format that is convertible to a string. All
    characters that are not digits are ignored.
    """
    number = str(number)
    interim = 0
    digits = ('0','1','2','3','4','5','6','7','8','9','0')
    
    for digit in number:
        if digit in digits:
            interim = matrix[interim][int(digit)]
        
    return interim
    
    
def check(number):
    """Compute the Damm check digit for the given number and check its correctness.
    
    The number can be in any format that is convertible to a string. All
    characters that are not digits are ignored.
    """
    return encode(number) == 0
    
    
    
if __name__ == '__main__':
    # quick self-test
    assert encode(572) == 4
    assert check(5724)
    assert encode('43881234567') == 9
    assert check('long number, computed by hand: 438812345679')
    assert encode('abcdef1') == 3
    assert check(' this is 5 an 7 awesome 2 test 4')
    print("self-test ok")