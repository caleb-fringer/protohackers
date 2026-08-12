package sieve

import "testing"

func TestSieve(t *testing.T) {
	test_cases := []bool{false, false, true, true, false, true, false, true, false, false, false, true, false}

	sieve := NewSieve(len(test_cases))
	for num, expected := range test_cases {
		isPrime := sieve.IsPrime(num)
		if isPrime != expected {
			t.Errorf("Invalid prime: Expected %v to be %v, got %v\n", num, expected, isPrime)
		}
	}
}

func TestMarkComposite(t *testing.T) {
	sieve := Sieve{
		n:    16,
		nums: make([]byte, 16/8),
	}
	sieve.nums[0] = 0xFF
	sieve.nums[1] = 0xFF

	err := sieve.markComposite(9)
	if err != nil {
		t.Fatalf("Error marking 9 as composite: %v\n", err)
	}
	if sieve.IsPrime(9) {
		t.Errorf("Sieve.markComposite(9) failed to mark 9 as composite\n")
	}
}
