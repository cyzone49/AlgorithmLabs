import math
import random
import sys

def mod_exp(x, y, N):

    if y == 0:
        return 1
    else:
        z = mod_exp(x, math.floor(y/2), N)
        # print('z = ' + str(z))
        # print('y = ' + str(y))
        if (y%2)==0:
            return ( ( pow( z, 2 ) ) % N )
        else:
            return ( ( pow( z, 2 ) * x ) % N )

def prime_test(N, k):
    a_set = set()
    while k > 0:
        a = random.randint(1,N-1)
        if (a in a_set)==False:
            a_set.add(a)
            # print(a)
            k = k - 1
            if (mod_exp(a, N-1, N) != 1):
                print('nope. mod_exp('+str(a)+', '+str(N-1)+', '+ str(N) + ') is '+ str(mod_exp(a,N-1,N)))
                return 'composite'
            else:
                print('mod_exp('+str(a)+', '+str(N-1)+', '+ str(N) + ') is '+ str(mod_exp(a,N-1,N)))
                print('not yet, still going. Testing Carmichael')
                if is_carmichael(N,a) == True:
                    return 'carmichael'

    print('a set is ' + str(a_set))

    for i in a_set:
        if is_carmichael(N,i) == True:
            return 'carmichael'

    return 'prime'

def is_carmichael(N,a):
    return test_mod(a, N-1, N) # a**N-1 === 1 mod N

def test_mod(a, y, N):
    print('starting a recursive round (' + str(a) + ', ' + str(y) + ', ' + str(N) + ')')
    if y%2 == 1:
        return False
    else: #continue testing mod N for sqrt sequence
        if mod_exp(a, int(y/2), N) == 1:
            return test_mod(a, int(y/2), N)
        elif mod_exp(a, int(y/2), N) == -1:
            return False
        else:
            return True

def main():
    # print command line arguments
    # for arg in sys.argv[1:]:
        # print(arg)


    print(mod_exp(int(sys.argv[1]), int(sys.argv[2]), int(sys.argv[3])))
    # print(prime_test(int(sys.argv[1]), int(sys.argv[2])))

if __name__ == "__main__":
    main()


#
# print(mod_exp(2,3,6))
# print(mod_exp(2,4,6))
# print(mod_exp(2,5,6))
# print(mod_exp(2,6,6))
# print(mod_exp(2,7,6))
# print(mod_exp(2,8,6))
# print(mod_exp(2,9,6))
# print(mod_exp(2,10,6))
