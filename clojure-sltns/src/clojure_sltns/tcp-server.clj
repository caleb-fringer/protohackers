(ns clojure-sltns.tcp-server
  (:import [java.net ServerSocket
            SocketException]
           [java.util.concurrent ThreadPoolExecutor Executors TimeUnit ArrayBlockingQueue RejectedExecutionException]))

(defn echo-handler
  [in out]
  (Thread/sleep 5000)
  (loop [read-byte (.read in)]
    (when (not= read-byte -1)
      (.write out read-byte)
      (recur (.read in)))))

(defn handle-client
  [client handler]
  (with-open [client client]
    (let [in (.getInputStream client)
          out (.getOutputStream client)]
      (handler in out))))

(defn serve
  "Continuously accept incoming connections, dispatching them to the `workers` ThreadPool"
  [server workers handler]
  (try
    (loop []
      (let [client (.accept server)]
        (try
          (.submit workers #(handle-client client handler))
          (catch RejectedExecutionException _
            (println "ThreadPool full, rejecting and closing connection")
            (.close client)))
        (recur)))
    (catch SocketException e
      (if (.isClosed server)
        (println "Server closed, not accepting new connections.")
        (throw e)))))

(defn start-server
  "Create & start the server w/ the given port, handler func, capacity, and keepalive time. Returns a function to stop the server and cleanup the thread pool."
  [port handler capacity keepalive]
  (let [server (ServerSocket. port)
        workers (ThreadPoolExecutor.
                 capacity
                 capacity
                 keepalive
                 TimeUnit/MILLISECONDS
                 (ArrayBlockingQueue. capacity))]
    (future (serve server workers handler))
    (fn []
      (.close server)
      (.shutdown workers)
      (println "Waiting for existing connections to terminate...")
      (.awaitTermination workers 10 TimeUnit/SECONDS)
      (println "Done."))))

(def stop-server (start-server 8080 echo-handler 10 500))
(stop-server)
