"""Damm algorithm hexadecimal check digit

Note that check digits are NOT used for verification of data transfers between
computers -- use a CRC or a hash for that purpose! Check digits are used to
check *manual* entry of a digit into a computer system.

A Damm check digit is a single hexadecimal check digit that can detect any
single-digit error as well as any adjacent-digit transpositions. The digit
computed in this module also detects some important phonetic errors (13<->30,
14<->40, ... 19<-->90). It also detects all jump-transposition errors (abc
-> cba), 93.5 % of all twin digit errors (aa -> bb) and 93.5 % of all jump
twin digit errors (aca -> bcb).

There are two functions in this module: `encode` and `check`. The first,
`encode` is used to calculate the check digit for a number that you have. The
second, `check` is used to check that a number that was entered was entered
correctly. If you want to supply your own totally anti-symmetric quasigroup
for computing the check digit, initialize Damm16CheckDigit with the
multiplication table of that group.

The Damm check digit is computed by starting with a check digit of zero and then
continually multiplying this check digit with the digits of a given number,
using the multiplication of a totally anti-symmetric quasigroup. The properties
and the selection of the group ensure the qualities of the check digit stated
above.

For further reference on how the algorithm works see
http://en.wikipedia.org/wiki/Damm_algorithm

"""


TATABLE = (
    (0, 2, 4, 6, 8, 10, 12, 14, 3, 1, 7, 5, 11, 9, 15, 13),
    (2, 0, 6, 4, 10, 8, 14, 12, 1, 3, 5, 7, 9, 11, 13, 15),
    (4, 6, 0, 2, 12, 14, 8, 10, 7, 5, 3, 1, 15, 13, 11, 9),
    (6, 4, 2, 0, 14, 12, 10, 8, 5, 7, 1, 3, 13, 15, 9, 11),
    (8, 10, 12, 14, 0, 2, 4, 6, 11, 9, 15, 13, 3, 1, 7, 5),
    (10, 8, 14, 12, 2, 0, 6, 4, 9, 11, 13, 15, 1, 3, 5, 7),
    (12, 14, 8, 10, 4, 6, 0, 2, 15, 13, 11, 9, 7, 5, 3, 1),
    (14, 12, 10, 8, 6, 4, 2, 0, 13, 15, 9, 11, 5, 7, 1, 3),
    (3, 1, 7, 5, 11, 9, 15, 13, 0, 2, 4, 6, 8, 10, 12, 14),
    (1, 3, 5, 7, 9, 11, 13, 15, 2, 0, 6, 4, 10, 8, 14, 12),
    (7, 5, 3, 1, 15, 13, 11, 9, 4, 6, 0, 2, 12, 14, 8, 10),
    (5, 7, 1, 3, 13, 15, 9, 11, 6, 4, 2, 0, 14, 12, 10, 8),
    (11, 9, 15, 13, 3, 1, 7, 5, 8, 10, 12, 14, 0, 2, 4, 6),
    (9, 11, 13, 15, 1, 3, 5, 7, 10, 8, 14, 12, 2, 0, 6, 4),
    (15, 13, 11, 9, 7, 5, 3, 1, 12, 14, 8, 10, 4, 6, 0, 2),
    (13, 15, 9, 11, 5, 7, 1, 3, 14, 12, 10, 8, 6, 4, 2, 0)
)


# a mapping of character to their index values
charmap = ('0', '1', '2', '3', '4', '5', '6', '7', '8', '9', 'a', 'b', 'c', 'd', 'e', 'f')


class Damm16CheckDigit():

    def __init__(self, tatable=None):
        if tatable == None:
            self.tatable = TATABLE
        else:
            self.tatable = tatable


    def encode(self, number):
        """Compute the Damm check digit for the given number.
        
        The number can be in any format that is convertible to a string. If the
        resulting string contains any digits that are not 0-9, a-f or A-F, a
        ValueError will be thrown.
        """
        number = str(number).lower()
        checkdigit = 0

        for digit in number:
            digitvalue = charmap.index(digit)
            checkdigit = self.tatable[checkdigit][digitvalue]
                
        return charmap[checkdigit]
    
    
    def check(self, number):
        """Compute the Damm check digit for the given number and check its correctness.
        
        The number can be in any format that is convertible to a string. All
        characters that are not digits are ignored.
        """
        return encode(number) == '0'
    

d16c = Damm16CheckDigit()
encode = d16c.encode
check = d16c.check

    
    
if __name__ == '__main__':
    # quick self-test
    assert encode('572') == '5'  # check a digit we know
    assert check('5725')         # check that it checks the digit we know
    for c in charmap:
        if c != '5':
            assert not check('572'+c) # check that all others are rejected
    assert encode('572a') == 'd' # check another digit we know
    assert encode('abcdef') == encode('ABCDEF') # check that lower/upper case makes no difference
    assert encode('572B') == 'f' # check another digit we know
    assert check('572BF')        # check that it checks out
    assert check('0000572bf')    # check that leading zeros don't matter
    
    print("self-test ok")
