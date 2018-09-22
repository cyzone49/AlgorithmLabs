import math
import sys

def extended_euclids(a,N):
    if N == 0:
        return (1,0,a)
    (x,y,d) = extended_euclids(N, a%N)
    return (y, x - math.floor(a/N)*y, d)


def main():

    a = int(sys.argv[1])
    N = int(sys.argv[2])

    if math.gcd(a,N) != 1:
        print('gcd(' + str(a) + ',' + str(N) + ') != 1')
        print('DNE')
    else:
        print(extended_euclids(a,N))

if __name__ == "__main__":
    main()
