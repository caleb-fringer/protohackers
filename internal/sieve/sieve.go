package sieve

func NewSieve(n int) []bool {
	sieve := make([]bool, n)

	for i := 2; i < n; i++ {
		sieve[i] = true
	}

	for i := 2; i < n; {
		for j := i; i*j < n; j++ {
			sieve[i*j] = false
		}
		nextPrime := i + 1
		for nextPrime < n && sieve[nextPrime] == false {
			nextPrime++
		}
		i = nextPrime
	}
	return sieve
}
