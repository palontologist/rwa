; Requires python_ext.py
!(import! &self python_ext)

(= (null-list? $l) (== $l Nil))
(= (car-list (Cons $x $xs)) $x)
(= (cdr-list (Cons $x $xs)) $xs)

(= (list $expr)
   (if (== $expr ())
        Nil
        (Cons (car-atom $expr) (list (cdr-atom $expr)))))

(= (member $x Nil) False)
(= (member $x (Cons $y $ys)) (if (== $x $y) True (member $x $ys)))
(= (append Nil $ys) $ys)
(= (append (Cons $x $xs) $ys) (Cons $x (append $xs $ys)))
(= (remove $x Nil) Nil)
(= (remove $x (Cons $y $ys)) (if (== $x $y) $ys (Cons $y (remove $x $ys))))

(= (foldl $f $acc Nil) $acc)
(= (foldl $f $acc (Cons $x $xs)) (foldl $f ($f $acc $x) $xs))
(= (reverse $xs) (rev-iter $xs Nil))
(= (rev-iter Nil $acc) $acc)
(= (rev-iter (Cons $x $xs) $acc) (rev-iter $xs (Cons $x $acc)))

(= (make-interval $a $b) ($a . $b))
(= (lower-bound $it) (let ($a . $b) $it $a))
(= (upper-bound $it) (let ($a . $b) $it $b))

(= (overlaps? $a $b)
  (let* (($as (lower-bound $a)) ($ae (upper-bound $a))
         ($bs (lower-bound $b)) ($be (upper-bound $b)))
    (and (< $as $be) (< $bs $ae))))

(= (subtract-one $free $busy)
  (let* (($fs (lower-bound $free)) ($fe (upper-bound $free))
         ($bs (lower-bound $busy)) ($be (upper-bound $busy)))
    (if (not (overlaps? $free $busy))
        (Cons $free Nil)
        (if (and (<= $bs $fs) (>= $be $fe)) Nil
          (if (and (> $bs $fs) (< $be $fe))
              (Cons (make-interval $fs $bs) (Cons (make-interval $be $fe) Nil))
              (if (and (<= $bs $fs) (< $be $fe))
                  (Cons (make-interval $be $fe) Nil)
                  (if (and (> $bs $fs) (>= $be $fe))
                      (Cons (make-interval $fs $bs) Nil)
                      Nil)))))))

(= (subtract-many $free $busyList)
  (if (null-list? $busyList)
      (Cons $free Nil)
      (let ($b (car-list $busyList))
        (let $pieces (subtract-one $free $b)
          (if (== $pieces Nil) Nil
            (append
              (subtract-many (car-list $pieces) (cdr-list $busyList))
              (subtract-many (car-list (cdr-list $pieces)) (cdr-list $busyList))))))))

; collect busy slots (simple enumerator up to 16)
(= (busy-at-index $day $i)
  (case $i
    ((0 (if (busy-slot $day $s0 $e0) (make-interval $s0 $e0) None))
     (1 (if (busy-slot $day $s1 $e1) (make-interval $s1 $e1) None))
     (2 (if (busy-slot $day $s2 $e2) (make-interval $s2 $e2) None))
     (3 (if (busy-slot $day $s3 $e3) (make-interval $s3 $e3) None))
     (4 (if (busy-slot $day $s4 $e4) (make-interval $s4 $e4) None))
     (5 (if (busy-slot $day $s5 $e5) (make-interval $s5 $e5) None))
     (6 (if (busy-slot $day $s6 $e6) (make-interval $s6 $e6) None))
     (7 (if (busy-slot $day $s7 $e7) (make-interval $s7 $e7) None))
     (8 (if (busy-slot $day $s8 $e8) (make-interval $s8 $e8) None))
     (9 (if (busy-slot $day $s9 $e9) (make-interval $s9 $e9) None))
     (10 (if (busy-slot $day $s10 $e10) (make-interval $s10 $e10) None))
     (11 (if (busy-slot $day $s11 $e11) (make-interval $s11 $e11) None))
     (12 (if (busy-slot $day $s12 $e12) (make-interval $s12 $e12) None))
     (13 (if (busy-slot $day $s13 $e13) (make-interval $s13 $e13) None))
     (14 (if (busy-slot $day $s14 $e14) (make-interval $s14 $e14) None))
     (15 (if (busy-slot $day $s15 $e15) (make-interval $s15 $e15) None))
     ($_ None))))

(= (collect-busy-iter $day $i)
  (if (== $i 16) Nil
    (let $cur (busy-at-index $day $i)
      (if (== $cur None)
          (collect-busy-iter $day (+ 1 $i))
          (Cons $cur (collect-busy-iter $day (+ 1 $i)))))))

(= (busy-list-for $day) (collect-busy-iter $day 0))

(= (free-slots-for $day)
  (let* (($s (work-window $day $ws $we) $ws)
         ($e (work-window $day $ws2 $we2) $we2)
         ($free0 (make-interval $s $e))
         ($busy (busy-list-for $day)))
    (subtract-many $free0 $busy)))

; task accessors
(= (get-duration-min $t) (let $d (duration $t $x) $x))
(= (get-priority $t)     (let $p (priority $t $x) $x))
(= (get-deadline $t)     (if (deadline $t $x) $x (+ (timems!) 31536000000)))

; deps ready
(= (ready? $t $done) (ready-deps-iter $t $done 0))
(= (get-dep $t $i)
  (case $i
    ((0 (if (depends $t $u0) $u0 None))
     (1 (if (depends $t $u1) $u1 None))
     (2 (if (depends $t $u2) $u2 None))
     (3 (if (depends $t $u3) $u3 None))
     ($_ None))))
(= (ready-deps-iter $t $done $i)
  (if (== $i 16) True
    (let $u (get-dep $t $i)
      (if (== $u None)
          (ready-deps-iter $t $done (+ 1 $i))
          (if (member $u $done)
              (ready-deps-iter $t $done (+ 1 $i))
              False)))))

; EDF + priority score
(= (score $t)
  (let* (($now (timems!))
         ($dl  (get-deadline $t))
         ($prio (get-priority $t))
         ($urg (/ 1.0 (max 1 (- $dl $now))))
         ($w_p (* 2 $prio)))
    (+ $w_p $urg)))

(= (better-task $a $b) (if (> (score $a) (score $b)) $a $b))
(= (argmax-task $ts)
  (if (== $ts Nil) None
      (foldl (lambda2 $best $x (if (== $best None) $x (better-task $best $x))) None $ts)))

; placement
(= (ms-from-min $m) (* 60000 $m))
(= (fits-in? $slot $t)
  (let* (($len (ms-from-min (get-duration-min $t)))
         ($s (lower-bound $slot))
         ($e (upper-bound $slot)))
    (<= $len (- $e $s))))

(= (place-in-slot $slot $t $slotsTail)
  (let* (($len (ms-from-min (get-duration-min $t)))
         ($s (lower-bound $slot))
         ($e (upper-bound $slot))
         ($ns (+ $s $len)))
    (let $head (Cons (Cons assign (Cons $t (Cons $s (Cons $ns Nil)))) Nil)
      (let $rem (if (< $ns $e) (Cons (make-interval $ns $e) Nil) Nil)
        (Cons $head (append $rem $slotsTail))))))

(= (try-place $t Nil) None)
(= (try-place $t (Cons $slot $rest))
  (if (fits-in? $slot $t)
      (place-in-slot $slot $t $rest)
      (let $res (try-place $t $rest)
        (if (== $res None) None (Cons (car-list $res) (Cons $slot (cdr-list $res)))))))

; main
(= (filter-ready $tasks $done) (filter-ready-iter $tasks $done Nil))
(= (filter-ready-iter Nil $done $acc) (reverse $acc))
(= (filter-ready-iter (Cons $t $ts) $done $acc)
  (filter-ready-iter $ts $done (if (ready? $t $done) (Cons $t $acc) $acc)))

(= (schedule-day $day $tasks)
  (let* (($slots (free-slots-for $day)))
    (sched-iter $slots Nil $tasks Nil)))

(= (sched-iter $slots $doneSyms $pending $assigns)
  (if (== $pending Nil)
      (reverse $assigns)
      (let* (($ready (filter-ready $pending $doneSyms))
             ($pick (argmax-task $ready)))
        (if (== $pick None)
            (Error schedule "No ready tasks (check dependency cycles)")
            (let $placed (try-place $pick $slots)
              (if (== $placed None)
                  (Error schedule "No free slot fits selected task")
                  (let* (($assign (car-list $placed))
                         ($slots2 (cdr-list $placed))
                         ($pending2 (remove $pick $pending))
                         ($done2 (Cons $pick $doneSyms)))
                    (sched-iter $slots2 $done2 $pending2 (Cons $assign $assigns)))))))))