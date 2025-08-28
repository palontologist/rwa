; sample tasks and a day calendar
(task T1) (duration T1 60) (priority T1 5) (deadline T1 1754005200000)
(task T2) (duration T2 30) (priority T2 3) (deadline T2 1754008800000)
(task T3) (duration T3 90) (priority T3 4) (deadline T3 1754012400000)
; (depends T3 T1)

(work-window d1 1754000400000 1754029200000)
(busy-slot d1 1754004600000 1754006400000)

!(bind! &tasks (list (T1 T2 T3)))