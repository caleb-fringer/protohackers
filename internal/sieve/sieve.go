package sieve

import (
	"fmt"
	"math"
)

type Sieve struct {
	n    int
	nums []byte
}

func (s Sieve) markComposite(i int) error {
	if i < 0 || i >= s.n {
		return fmt.Errorf("Index %v is out of bounds", i)
	}
	byteIndex := i / 8
	byteOffset := i % 8
	s.nums[byteIndex] &= ^(1 << byteOffset)
	return nil
}

func (s Sieve) IsPrime(i int) bool {
	if i < 0 || i >= s.n {
		return false
	}

	byteIndex := i / 8
	byteOffset := i % 8
	return s.nums[byteIndex]&(1<<byteOffset) > 0
}

func NewSieve(n int) Sieve {
	numBytes := int(math.Ceil(float64(n) / 8))
	sieve := Sieve{
		n:    n,
		nums: make([]byte, numBytes),
	}

	// Initialize the array to true
	for i := range numBytes {
		sieve.nums[i] = 0xFF
	}
	// Mark 0 and 1 as composite.
	sieve.nums[0] &= 0xFC

	root_n := int(math.Sqrt(float64(n)))
	for i := 2; i <= root_n; {
		for j := i; i*j < n; j++ {
			sieve.markComposite(i * j)
		}
		primeCandidate := i + 1
		for primeCandidate < n && !sieve.IsPrime(primeCandidate) {
			primeCandidate++
		}
		i = primeCandidate
	}
	return sieve
}
