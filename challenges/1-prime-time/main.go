package main

import (
	"bufio"
	"encoding/json"
	"fmt"
	"log"
	"math"
	"net"
	"os"
	"strconv"
	"time"

	"github.com/caleb-fringer/protohackers/internal/sieve"
)

const DEFAULT_PORT = 8080

func main() {
	var port int
	var err error
	if len(os.Args) < 2 {
		fmt.Printf("No port number provided. Defaulting to %v...\n", DEFAULT_PORT)
		port = DEFAULT_PORT
	} else {
		port, err = strconv.Atoi(os.Args[1])
		if err != nil {
			fmt.Printf("Error parsing port number: %v\n", err)
			os.Exit(1)
		}
	}

	server, err := net.Listen("tcp", fmt.Sprintf(":%v", port))
	if err != nil {
		fmt.Printf("Error starting server: %v\n", err)
		os.Exit(1)
	}
	fmt.Printf("Server started on port %v...\n", port)

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
	Method string      `json:"method"`
	Number json.Number `json:"number"`
}

type Response struct {
	Method string `json:"method"`
	Prime  bool   `json:"prime"`
}

func handleConnection(conn net.Conn, sieve sieve.Sieve) {
	var req Request
	scanner := bufio.NewScanner(conn)
	encoder := json.NewEncoder(conn)

	for scanner.Scan() {
		bytes := scanner.Bytes()
		log.Printf("INFO: Received request:\n\t%s\n", bytes)
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
