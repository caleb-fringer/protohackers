(ns clojure-sltns.tcp-server
  (:import [java.net ServerSocket
            SocketException]
           [java.util.concurrent Executors]))

(defn echo-handler
  [in out]
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

(defn start-server
  "Create and return a ServerSocket on the given port."
  [port]
  (ServerSocket. port))

(defn serve
  "Continuously accept incoming connections, dispatching them to a Future"
  [server workers handler]
  (try
    (loop []
      (let [client (.accept server)]
        (.submit workers #(handle-client client handler))
        (recur)))
    (catch SocketException e
      (if (.isClosed server)
        (println "Server closed normally.")
        (throw e)))))

(def server (start-server 8080))
(def workers (Executors/newFixedThreadPool 10))
(def server-loop
  (future (serve server workers echo-handler)))

;(.close server)
