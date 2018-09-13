import random
import math



def prime_test(N, k):
    # You will need to implements this function and change the return value.

    # To generate random values for a, you will most likley want to use
    # random.randint(low,hi) which gives a random integer between low and
    #  hi, inclusive.

	# Remember to ensure that all of your random values are unique

    # Should return one of three values: 'prime', 'composite', or 'carmichael'

    a_set = set()
    while k > 0:
        a = random.randint(1,N-1)
        if (a in a_set)==False:
            a_set.add(a)
            k = k - 1
            if (mod_exp(a, N-1, N) != 1):
                return 'composite'
            else:
                if is_carmichael(N,a) == True:
                    return 'carmichael'

    return 'prime'


def mod_exp(x, y, N):
    if y == 0:
        return 1
    else:
        z = mod_exp(x, math.floor(y/2), N)
        if (y%2)==0:
            return ( ( pow( z, 2 ) ) % N )
        else:
            return ( ( pow( z, 2 ) * x ) % N )

def probability(k):
    # You will need to implements this function and change the return value.
    return (1 - 0.5**k)

def is_carmichael(N,a):
    return test_mod(a, N-1, N) # a**N-1 === 1 mod N

def test_mod(a, y, N):
    if y%2 == 1:
        return False
    else: #continue testing mod N for sqrt sequence
        mod_result = mod_exp(a, int(y/2), N)
        if mod_result == 1:
            return test_mod(a, int(y/2), N)
        elif mod_result == N-1:
            return False
        else:
            return True
