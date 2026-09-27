# Fresh paired trajectories

All values are percentages; Δ is SA−SM in percentage points. Fixed T1/K32,
80/20 routine/challenge equal-map mixture. U is distinct valid raw routes/K32,
not distinct invalid outputs or a strict unseen-training-signature measure.
Equal updates are equal sampled training exposures, not equal CPU time.

|Seed|Updates|SM Q|SA Q|Δ Q|SM U|SA U|Δ U|
|---|---:|---:|---:|---:|---:|---:|---:|
|1702|1000|24.468|24.691|+0.223|20.832|20.820|-0.011|
|1702|2000|31.064|31.589|+0.524|25.607|25.879|+0.272|
|1702|4000|34.863|34.248|-0.615|27.430|26.338|-1.092|
|1702|8000|38.405|35.884|-2.521|28.831|27.479|-1.353|
|1703|1000|28.221|29.909|+1.688|23.416|24.328|+0.911|
|1703|2000|31.436|30.607|-0.828|24.811|24.434|-0.378|
|1703|4000|33.063|34.302|+1.239|25.174|27.148|+1.974|
|1703|8000|37.202|37.144|-0.059|28.400|28.216|-0.184|
|1704|1000|28.221|28.315|+0.094|23.133|23.140|+0.007|
|1704|2000|29.028|30.083|+1.055|23.724|24.289|+0.565|
|1704|4000|33.498|33.213|-0.285|26.484|26.128|-0.356|
|1704|8000|38.626|37.559|-1.068|28.540|27.912|-0.628|
|1705|1000|28.623|29.468|+0.845|23.156|23.817|+0.661|
|1705|2000|30.869|31.514|+0.645|24.831|25.099|+0.269|
|1705|4000|34.587|33.703|-0.884|26.755|26.395|-0.360|
|1705|8000|38.558|40.410|+1.852|28.644|30.052|+1.408|

|Updates|Mean SM Q|Mean SA Q|Mean SM U|Mean SA U|
|---|---:|---:|---:|---:|
|1000|27.383|28.096|22.634|23.026|
|2000|30.599|30.948|24.743|24.925|
|4000|34.003|33.866|26.461|26.502|
|8000|38.198|37.749|28.604|28.415|

Source: each `replication-SEED-analysis/analysis.json` retained
`stored_fullvalidation[UPDATE].t1.MODE.mixture`, under the original
`execution/model_training_comparison` root. Original event/owner hashes, full
per-problem rows and strata remain in those immutable artifacts.
