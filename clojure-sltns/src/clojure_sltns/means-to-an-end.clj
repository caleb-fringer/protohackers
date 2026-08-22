(ns clojure-sltns.means-to-an-end
  (:import [java.io InputStream OutputStream ByteArrayInputStream IOException]
           [java.nio.charset StandardCharsets]
           [java.nio ByteBuffer])
  (:require
   [clojure.java.io :as io]))

(defrecord Message [^char message-type ^int timestamp ^int price])

(defn parse-msg
  [^bytes msg]
  (let [buf (ByteBuffer/wrap msg)]
    (->Message
      ; Message only has 1 byte, so I need to pad a 0 to interpet it as a char
     (char (.get buf 0))
     (.getInt buf 1)
     (.getInt buf 5))))

(defn read-msg
  "Reads a single, 9 byte msg from in. If the resulting message read is less than 9 bytes, nil is returned."
  [^InputStream in
   ^bytes buf]
  (let [cb (.readNBytes in buf 0 9)]
    (if (= cb 9) (parse-msg buf) nil)))

(defn connection-handler
  [^InputStream in
   ^OutputStream out]
  (let [buf (byte-array 9)]
    (try
      (loop [msg (read-msg in buf)]
        (.write out (.getBytes (str (pr-str msg) \newline) "UTF-8"))
        (if (not (nil? msg))
          (recur (read-msg in buf))
          nil))
      (catch IOException e
        (print "Caught exception: " (.getMessage e)))
      (finally (.close in)))))

(def sample-session
  (byte-array
   [0x49 0x00 0x00 0x30 0x39 0x00 0x00 0x00 0x65
    0x49 0x00 0x00 0x30 0x3a 0x00 0x00 0x00 0x66
    0x49 0x00 0x00 0x30 0x3b 0x00 0x00 0x00 0x64
    0x49 0x00 0x00 0xa0 0x00 0x00 0x00 0x00 0x05
    0x51 0x00 0x00 0x30 0x00 0x00 0x00 0x40 0x00]))

(connection-handler
 (ByteArrayInputStream. sample-session)
 System/out)
