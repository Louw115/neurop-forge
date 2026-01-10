"""
Copyright © 2026 Lourens Wasserman. All Rights Reserved.
Neurop Block Forge - https://neurop-forge.com
Commercial use requires a license. See LICENSE file.
"""

"""
Number Theory - Pure functions for number theory and prime operations.
All functions are pure, deterministic, and atomic.
"""

def is_prime(n: int) -> bool:
    """Check if number is prime."""
    if n < 2:
        return False
    if n == 2:
        return True
    if n % 2 == 0:
        return False
    for i in range(3, int(n ** 0.5) + 1, 2):
        if n % i == 0:
            return False
    return True


def next_prime(n: int) -> int:
    """Find next prime after n."""
    candidate = n + 1
    while not is_prime(candidate):
        candidate += 1
    return candidate


def prev_prime(n: int) -> int:
    """Find previous prime before n."""
    if n <= 2:
        return 0
    candidate = n - 1
    while candidate > 1 and not is_prime(candidate):
        candidate -= 1
    return candidate if is_prime(candidate) else 0


def primes_up_to(n: int) -> list:
    """Generate all primes up to n using Sieve of Eratosthenes."""
    if n < 2:
        return []
    sieve = [True] * (n + 1)
    sieve[0] = sieve[1] = False
    for i in range(2, int(n ** 0.5) + 1):
        if sieve[i]:
            for j in range(i * i, n + 1, i):
                sieve[j] = False
    return [i for i in range(n + 1) if sieve[i]]


def first_n_primes(n: int) -> list:
    """Generate first n primes."""
    if n <= 0:
        return []
    primes = []
    candidate = 2
    while len(primes) < n:
        if is_prime(candidate):
            primes.append(candidate)
        candidate += 1
    return primes


def prime_factors(n: int) -> list:
    """Get prime factorization."""
    factors = []
    d = 2
    while d * d <= n:
        while n % d == 0:
            factors.append(d)
            n //= d
        d += 1
    if n > 1:
        factors.append(n)
    return factors


def prime_factor_counts(n: int) -> dict:
    """Get prime factorization with counts."""
    factors = {}
    d = 2
    while d * d <= n:
        while n % d == 0:
            factors[d] = factors.get(d, 0) + 1
            n //= d
        d += 1
    if n > 1:
        factors[n] = factors.get(n, 0) + 1
    return factors


def gcd(a: int, b: int) -> int:
    """Greatest common divisor."""
    while b:
        a, b = b, a % b
    return abs(a)


def lcm(a: int, b: int) -> int:
    """Least common multiple."""
    if a == 0 or b == 0:
        return 0
    return abs(a * b) // gcd(a, b)


def extended_gcd(a: int, b: int) -> dict:
    """Extended Euclidean algorithm."""
    if b == 0:
        return {"gcd": a, "x": 1, "y": 0}
    result = extended_gcd(b, a % b)
    return {"gcd": result["gcd"], "x": result["y"], "y": result["x"] - (a // b) * result["y"]}


def mod_inverse(a: int, m: int) -> int:
    """Modular multiplicative inverse."""
    result = extended_gcd(a, m)
    if result["gcd"] != 1:
        return 0
    return result["x"] % m


def mod_pow(base: int, exp: int, mod: int) -> int:
    """Modular exponentiation."""
    result = 1
    base = base % mod
    while exp > 0:
        if exp % 2 == 1:
            result = (result * base) % mod
        exp //= 2
        base = (base * base) % mod
    return result


def euler_phi(n: int) -> int:
    """Euler's totient function."""
    result = n
    p = 2
    while p * p <= n:
        if n % p == 0:
            while n % p == 0:
                n //= p
            result -= result // p
        p += 1
    if n > 1:
        result -= result // n
    return result


def divisors(n: int) -> list:
    """Get all divisors of n."""
    divs = []
    for i in range(1, int(n ** 0.5) + 1):
        if n % i == 0:
            divs.append(i)
            if i != n // i:
                divs.append(n // i)
    return sorted(divs)


def divisor_count(n: int) -> int:
    """Count divisors of n."""
    count = 0
    for i in range(1, int(n ** 0.5) + 1):
        if n % i == 0:
            count += 1
            if i != n // i:
                count += 1
    return count


def divisor_sum(n: int) -> int:
    """Sum of divisors of n."""
    return sum(divisors(n))


def is_perfect_number(n: int) -> bool:
    """Check if n is a perfect number."""
    return n > 0 and divisor_sum(n) - n == n


def is_abundant(n: int) -> bool:
    """Check if n is abundant."""
    return n > 0 and divisor_sum(n) - n > n


def is_deficient(n: int) -> bool:
    """Check if n is deficient."""
    return n > 0 and divisor_sum(n) - n < n


def coprime(a: int, b: int) -> bool:
    """Check if a and b are coprime."""
    return gcd(a, b) == 1


def fibonacci(n: int) -> int:
    """Get nth Fibonacci number."""
    if n <= 0:
        return 0
    if n == 1:
        return 1
    a, b = 0, 1
    for _ in range(2, n + 1):
        a, b = b, a + b
    return b


def fibonacci_sequence(n: int) -> list:
    """Get first n Fibonacci numbers."""
    if n <= 0:
        return []
    if n == 1:
        return [0]
    seq = [0, 1]
    for _ in range(2, n):
        seq.append(seq[-1] + seq[-2])
    return seq


def factorial(n: int) -> int:
    """Calculate factorial."""
    if n < 0:
        return 0
    result = 1
    for i in range(2, n + 1):
        result *= i
    return result


def binomial(n: int, k: int) -> int:
    """Calculate binomial coefficient (n choose k)."""
    if k < 0 or k > n:
        return 0
    if k == 0 or k == n:
        return 1
    k = min(k, n - k)
    result = 1
    for i in range(k):
        result = result * (n - i) // (i + 1)
    return result


def is_fibonacci(n: int) -> bool:
    """Check if n is a Fibonacci number."""
    def is_perfect_square(x):
        s = int(x ** 0.5)
        return s * s == x
    return is_perfect_square(5 * n * n + 4) or is_perfect_square(5 * n * n - 4)


def digital_root(n: int) -> int:
    """Calculate digital root."""
    if n == 0:
        return 0
    return 1 + (n - 1) % 9
