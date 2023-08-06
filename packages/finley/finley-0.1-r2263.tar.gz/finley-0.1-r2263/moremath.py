# system modules
import math
import numpy
import numpy.linalg
import random
import fractions
import decimal
import collections

def vector_length(iterable):
    return math.sqrt(sum([_*_ for _ in iterable]))

def reverse_number(number):
    return int(str(number)[::-1])

def is_palindrome(number):
    return reverse_number(number) == number

def is_lychrel_number(candidate, max_iter=50):
    if max_iter < 1:
        raise ValueError('Invalid number of maximum iterations.')

    cur_iter = 1
    s = candidate
    while cur_iter <= max_iter:
        s = s + reverse_number(s)
        if is_palindrome(s):
            return (False, cur_iter)
        cur_iter += 1

    return (True, max_iter)

def digital_sum(number):
    return sum(map(int, str(number)))

def sqrt_2_series(iteration=1):
    if iteration < 0:
        raise ValueError('Invalid iteration count.')

    if iteration == 0:
        return fractions.Fraction(1, 1)

    base = fractions.Fraction(1, 2)
    while iteration > 1:
        iteration -= 1
        base = 1 / (2 + base)

    return 1 + base

def is_prime_sieve(num, sorted_primes=None):
    if num < 2:
        return False
    if num == 2:
        return True
    iterable = sorted_primes if sorted_primes is not None else xrange(2, int(math.ceil(math.sqrt(num)))+1)
    for i in iterable:
        if num % i == 0:
            return i
        if i*i > num:
            break
    return True

def digit_factorial_chain(num):
    yield num
    while True:
        digits = collections.Counter(str(num))
        num = 0
        for digit in digits:
            num += math.factorial(int(digit)) * digits[digit]
        yield num

def digit_square_chain(num):
    yield num
    while True:
        digits = collections.Counter(str(num))
        num = 0
        for digit in digits:
            num += int(digit)**2 * digits[digit]
        yield num

def is_prime_percentage(list_of_ints):
    return len([_ for _ in list_of_ints if is_prime_sieve(_)])*1.0/len(list_of_ints)

def anticlockwise_spiral_diagonals(side_length):
    if side_length < 3 or side_length % 2 == 0:
        return ValueError('Invalid side length.')

    steps = (side_length-1)/2

    result = [1]
    last = 1
    for step in range(1, steps+1):
        diff = 2*step
        result += [last + diff, last + 2*diff, last+3*diff, last+4*diff]
        last = result[-1]
    return result

def triangle(n):
    return n*(n+1)/2

def square(n):
    return n*n

def pentagonal(n):
    return n*(3*n-1)/2

def hexagonal(n):
    return n*(2*n-1)

def heptagonal(n):
    return n*(5*n-3)/2

def octagonal(n):
    return n*(3*n-2)

def sorted_number(n):
    return ''.join(sorted(str(n))[::-1])

def prime_factors_single(n): 
    pFact, limit, check, num = [], int(math.sqrt(n)) + 1, 2, n 
    if n == 1: return [1] 
    for check in range(2, limit): 
         while num % check == 0: 
            pFact.append(check) 
            num /= check 
    if num > 1: 
      pFact.append(num) 
    return pFact 

def prime_factors_sieve(n, sorted_primes):
    factors = []
    while True:
        candidate = is_prime_sieve(n, sorted_primes=sorted_primes)
        if candidate is True:
            factors.append(n)
            break
        else:
            factors.append(candidate)
            n /= candidate
    return factors

def prime_build_list(up_to):
    res = [2]
    i = 1
    up_to -= 2
    while i <= up_to:
        i += 2
        prime = True
        for p in res:
            if i % p == 0:
                prime = False
                break
            if p*p > i:
                break
        if prime:
            res.append(i)
    return res

def euler_totient(n, sorted_primes=None):
    factors = []
    if sorted_primes is None:
        factors = prime_factors_single(n)
    else:
        factors = prime_factors_sieve(n, sorted_primes)

    cnt = collections.Counter(factors)
    res = 1
    for val in cnt:
        res *= val**(cnt[val]-1)*(val-1)
    return res

def continued_fraction(n, precision=28):
    decimal.getcontext().prec = precision
    alpha = decimal.Decimal(n)

    while True:
        q, r = divmod(alpha, 1)
        yield (q, alpha)
        if r.is_zero():
            return

        alpha = 1/(alpha-q)

def detect_periodicity(iterable, limit=50, etol=0, valueqeualsstate=False):
    states = []
    values = []

    is_periodic = False
    periodic_state = None
    while len(values) <= limit:
        try:
            if valueqeualsstate:
                value = next(iterable)
                state = value
            else:
                value, state = next(iterable)
        except:
            break
        for former in states:
            if abs(former-state) <= etol:
                is_periodic = True
                periodic_state = former
        if is_periodic:
            break
        else:
            states.append(state)
            values.append(value)

    if is_periodic:
        split = states.index(periodic_state)
        return (is_periodic, values[:split], values[split:])
    else:
        return (is_periodic, values, [])

def all_indices(needle, haystack): #isdoc
    if not isinstance(haystack, list):
        raise ValueError('Expecting instance of list')

    indices = range(len(haystack))
    parts = zip(indices, haystack)
    return [x[0] for x in parts if x[1] == needle]

def list_diff(l, NullInclude=False): #isdoc
    if not isinstance(l, list):
        raise ValueError('Expecting instance of list')

    r = []
    if NullInclude:
        r.append(l[0])
    for i in range(len(l)-1):
        r.append(l[i+1]-l[i])
    return r

class vector(object): #isdoc #doc-contains: _size, _pos
    def __init__(self, size): #isdoc
        self._size = size
        self._pos = [0]*size

    def __str__(self): #isdoc
        s = 'vector['
        for i in range(self._size):
            s += '{0:10f} '.format(self._pos[i])
            if (i % 5) == 4:
                s += '\n         '
        return s + ']'

    def __mul__(self, factor): #isdoc
        if type(factor) in (float, int):
            self._pos = map(lambda x: x*factor, self._pos)
        elif type(factor) == vector:
            if self._size == factor.size:
                return sum([x[0]*x[1] for x in zip(self._pos, other,pos)])
            else:
                raise ArithmeticError('Unable to multiply vectors of different lengths.')
        else:
            raise NotImplementedError('Unknown factor')
        return self

    def __add__(self, other): #isdoc
        if type(other) == vector:
            if len(self._pos) == len(other.pos):
                self._pos = [x[0]+x[1] for x in zip(self._pos, other.pos)]
            else:
                raise ArithmeticError('Unable to add vectors of different lengths.')
        else:
            raise NotImplementedError('Unknown summand')
        return self

    def __rmul__(self, factor): #isdoc
        return self*factor

    def __len__(self): #isdoc
        if self._size == len(self._pos):
            return self._size
        else:
            raise IndexError('Length cache mismatch.')

    def __div__(self, divisor): #isdoc
        if type(divisor) in (float, int):
            self._pos = map(lambda x: x/divisor, self._pos)
        else:
            raise NotImplementedError('Unknown factor')
        return self

    def random_normalvariate(self, mu = 0, sigma = 1): #isdoc
        self._pos = map(lambda x: random.normalvariate(mu, sigma), self._pos)
        return self

    def random_univariate(self, minimum = 0, maximum = 1): #isdoc
        self._pos = map(lambda x: random.uniform(minimum, maximum), self._pos)
        return self

    def __abs__(self): #isdoc
        return math.sqrt(sum([x*x for x in self._pos]))

    def __getitem__(self, key): #isdoc
        return self._pos[key]

    def normalize(self): #isdoc
        a = abs(self)
        if a == 0:
            raise ArithmeticError('Unable to normalize null vector')
        return self/a

    def derive_random_normal(self): #isdoc
        js = [x for x in range(self._size) if not self._pos[x] == 0]
        if len(js) == 0:
            raise ArithmeticError('Unable to derive from null vector')
        j = random.choice(js)
        b = vector(self._size).random_normalvariate()
        temp = sum([x[0]*x[1] for x in zip(self._pos, b.pos)])
        temp -= self._pos[j]* b.pos[j]
        temp /= self._pos[j]
        b.pos[j] = -temp
        return b

    def derive_random_angle(self, angle): #isdoc
        b = self.derive_random_normal()
        b.normalize()
        factor = abs(self) * math.sqrt((1/math.cos(angle)**2-1))
        b * factor
        return (self+b)

    def rescale_to_length(self, length): #isdoc
        f = length/abs(self)
        return self * f

def weighted_select(items, weights): #isdoc
    s = sum(weights)
    v = random.uniform(0, s)
    s = 0
    for i, w in enumerate(weights):
        s += w
        if v < s:
            return items[i]

def flattenlist(o): #isdoc
    if isinstance(o, list):
        nonlist = [x for x in o if not isinstance(x, list)]
        listelems = [x for x in o if isinstance(x, list)]
        listelems = [flattenlist(x) for x in listelems]
        listelems = sum(listelems, [])
        return nonlist+listelems
    else:
        return [o]

def rotate_vector(v, n, angle): #isdoc
    if isinstance(v, vector):
        v = v._pos
    if isinstance(n, vector):
        n = n._pos
    
    a = math.sqrt(sum([x*x for x in n]))
    n = map(lambda x: x/a, n)

    n = numpy.array(n)
    v = numpy.array(v)

    return list(n*numpy.dot(n, v) + numpy.cross(math.cos(angle)*numpy.cross(n, v), n) + math.sin(angle)*numpy.cross(n, v))

def distance_line_point(point_line, n, point): #isdoc
    n = numpy.array(n)
    a = numpy.array(point_line)
    p = numpy.array(point)
    n /= numpy.linalg.norm(n)
    d = a - p
    d = d - d.dot(n)*n
    return numpy.linalg.norm(d)

def backtracking_assign_unique(options):
    def _run(sel, options):
        if len(sel) == len(options):
            if list(set(sel)) == sel:
                return True
            else:
                return False

        idx = len(sel)
        for v in options[idx][:]:
            if v in sel:
                continue
            sel.append(v)
            options[idx].remove(v)
            if _run(sel, options):
                return True
            sel.pop()
            options[idx].append(v)

    # TODO: test preconditions
    return _run([], options)
