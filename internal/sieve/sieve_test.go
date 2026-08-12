package sieve

import (
	"testing"
)

func TestSieve(t *testing.T) {
	test_cases := []bool{false, false, true, true, false, true, false, true, false, false, false, true, false}

	sieve := NewSieve(len(test_cases))
	for i, v := range test_cases {
		isPrime := sieve[i]
		if isPrime != v {
			t.Errorf("Invalid prime: Expected %v to be %v, got %v\n", i, v, sieve[i])
		}
	}
}
