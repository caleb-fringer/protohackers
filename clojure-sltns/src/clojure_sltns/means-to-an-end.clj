(ns clojure-sltns.means-to-an-end
  (:import [java.io InputStream OutputStream ByteArrayInputStream IOException]
           [java.nio.charset StandardCharsets])
  (:require
   [clojure.java.io :as io]))

(defn parse-msg
  [^bytes msg])

(defn read-msg
  "Reads a single, 9 byte msg from in. If the resulting message read is less than 9 bytes, nil is returned."
  [^InputStream in
   ^bytes buf]
  (let [cb (.readNBytes in buf 0 9)]
    (if (= cb 9) buf nil)))

(defn connection-handler
  [^InputStream in
   ^OutputStream out]
  (let [buf (byte-array 9)]
    (try
      (loop [msg (read-msg in buf)]
        (print msg "\n")
        (if (not (nil? msg))
          (recur (read-msg in buf))
          nil))
      (catch IOException e
        (print "Caught exception: " (.getMessage e)))
      (finally (.close in)))))

(connection-handler
 (ByteArrayInputStream.
  (.getBytes "Hello, my name is George clooooooney" StandardCharsets/UTF_8))
 nil)
