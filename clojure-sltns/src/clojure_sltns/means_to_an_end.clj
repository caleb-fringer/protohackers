(ns clojure-sltns.means-to-an-end
  (:import [java.io InputStream OutputStream IOException]
           [java.nio ByteBuffer]))

(defrecord Message [^char message-type ^int a ^int b])

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

(defn get-avg
  [coll]
  (if (empty? coll) (int 0)
      (int (/ (apply + (map second coll))
              (count coll)))))
(defn write-int
  [^OutputStream out i]
  (doseq [j (reverse (map (fn [x] (* 8 x)) (range 4)))]
    (.write out (bit-shift-right i j))))

(defn connection-handler
  [^InputStream in
   ^OutputStream out]
  (let [buf (byte-array 9)]
    (try
      (loop [msg (read-msg in buf)
             prices (sorted-map)]
        (if (not (nil? msg))
          (let [{t :message-type a :a b :b} msg]
            (printf "Received msg with type %s\n" t)
            (flush)
            (cond (= t \I) (recur (read-msg in buf) (assoc prices a b))
                  (= t \Q) (let
                            [requested-prices (subseq prices >= a <= b)]
                             (write-int out (get-avg requested-prices))
                             (recur (read-msg in buf) prices))
                  :else (.write out (.getBytes "Bad message type received!\n"))))
          nil))
      (catch IOException e
        (print "Caught exception: " (.getMessage e)))
      (finally (.close in)))))
