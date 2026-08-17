(ns clojure-sltns.means-to-an-end
  (:require
   [clojure.java.io :as io]))

(defn connection-handler
  [client-socket]
  (let [in (io/reader client-socket)]
    (.read in)))

