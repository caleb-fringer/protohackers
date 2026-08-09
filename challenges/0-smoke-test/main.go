package main

import (
	"fmt"
	"net"
	"os"
)

const PORT = 443

func main() {
	listener, err := net.Listen("tcp", fmt.Sprintf(":%v", PORT))
	if err != nil {
		fmt.Printf("Error starting server: %v\n", err)
		os.Exit(1)
	}
	fmt.Printf("Server listening on port %v...\n", PORT)
	defer listener.Close()

	for {
		conn, err := listener.Accept()
		if err != nil {
			fmt.Printf("Error accepting incoming connection: %v\n", err)
			continue
		}

		go handleConnection(conn)
	}
}

func handleConnection(conn net.Conn) {
	defer conn.Close()

	buf := make([]byte, 1024)
	n, err := conn.Read(buf)
	for n > 0 && err == nil {
		m, err := conn.Write(buf[:n])
		if n != m || err != nil {
			fmt.Printf("Error writing bytes back to client: %v\n", err)
			fmt.Printf("Closing connection to client %v\n", conn.RemoteAddr())
			return
		}
		n, err = conn.Read(buf)
	}
}
