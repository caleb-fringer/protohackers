package main

import (
	"bufio"
	"encoding/json"
	"fmt"
	"math"
	"net"
	"os"
	"time"

	"github.com/caleb-fringer/protohackers/internal/sieve"
)

const PORT = 443

func main() {
	server, err := net.Listen("tcp", fmt.Sprintf(":%v", PORT))
	if err != nil {
		fmt.Printf("Error starting server: %v\n", err)
		os.Exit(1)
	}
	fmt.Printf("Server started on port %v...\n", PORT)

	fmt.Printf("Generating sieve from 1 to %v...\n", math.MaxInt32)
	start_time := time.Now()
	sieve := sieve.NewSieve(math.MaxInt32)
	elapsed := time.Since(start_time)
	fmt.Printf("Generated sieve in %v seconds\n", elapsed.Seconds())

	for {
		conn, err := server.Accept()
		if err != nil {
			fmt.Printf("Error accepting connection from %v: %v\n", conn.RemoteAddr(), err)
			continue
		}

		go handleConnection(conn, sieve)
	}
}

type Request struct {
	Method string
	Number json.Number
}

type Response struct {
	Method string
	Prime  bool
}

func handleConnection(conn net.Conn, sieve sieve.Sieve) {
	var req Request
	scanner := bufio.NewScanner(conn)
	encoder := json.NewEncoder(conn)

	for scanner.Scan() {
		bytes := scanner.Bytes()
		err := json.Unmarshal(bytes, &req)
		if err != nil {
			encoder.Encode(Response{
				Method: "MalformedResponse",
				Prime:  false,
			})
			conn.Close()
			return
		}

		var isPrime bool
		requestedInt, err := extractJsonInt(req.Number)

		if err != nil {
			isPrime = false
		} else {
			isPrime = sieve.IsPrime(requestedInt)
		}

		encoder.Encode(Response{
			Method: "isPrime",
			Prime:  isPrime,
		})
	}
}

func truncate(f float64) float64 {
	n := int(f)
	return float64(n)
}

func extractJsonInt(number json.Number) (int, error) {
	f, err := json.Number.Float64(number)
	if err != nil {
		return 0, fmt.Errorf("%v (decoded as %v) is not an integer: %v\n", number, f, err)
	}

	if truncate(f) != f {
		return 0, fmt.Errorf("%v (decoded as %v) is not an integer: %v\n", number, f, err)
	}

	n := int(f)
	return n, nil
}
