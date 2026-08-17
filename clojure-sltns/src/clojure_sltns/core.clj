(ns clojure-sltns.core
  (:gen-class)
  (:import
   [java.net ServerSocket]
   [java.io BufferedReader
    InputStreamReader
    PrintWriter])
  (:require [clojure.java.io :as io]
            [clojure.core.async :as async]))

(defn start-server
  [port]
  (with-open [server (ServerSocket. port)]
    (println (format "Server listening on port %s..." port))

    (with-open [socket (.accept server)
                reader (BufferedReader.
                        (InputStreamReader.
                         (.getInputStream socket)))
                writer (PrintWriter.
                        (.getOutputStream socket)
                        true)]
      (println "Client connected")

      (let [message (.readLine reader)]
        (println "Client said: " message)

        (.println writer
                  (str "Server received: " message))))))

(defn -main
  "I don't do a whole lot ... yet."
  [& args]
  (start-server 8080))
