(ns clojure-sltns.tcp-server
  (:import [java.io InputStream
            OutputStream]
           [java.net ServerSocket]))

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
  [server handler]
  (loop []
    (let [client (.accept server)]
      (future (handle-client client handler))
      (recur))))

(def server (start-server 8080))
(serve server echo-handler)
(.close server)
