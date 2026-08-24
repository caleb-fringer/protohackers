(ns clojure-sltns.core
  (:gen-class)
  (:require [clojure-sltns.means-to-an-end :refer [connection-handler]]
            [clojure-sltns.tcp-server :refer [start-server]]))

(defn -main
  "I don't do a whole lot ... yet."
  [& args]
  (start-server 8080 connection-handler 10 500))
