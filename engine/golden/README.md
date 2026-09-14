# Golden benchmark

Real supplier documents stay local and are ignored by Git. Copy them into `engine/golden/input/` only in the runtime used for testing.

Required cases:
1. `ПРС.107.10.000 РЭ проект 10.09.2026.pdf` — explicit IS100..IS700 periodicity table including IS540.
2. `РТГН.09.64025.03 РЭ ЭВС.pdf` — same family, spacing `IS 100`, IS100 tolerance differs.
3. `9.7 СТНР.661172.701 РЭ3. Часть 4 Техническое обслуживание и ремонт (изм.5).pdf` — hard multi-page maintenance matrix/list.
4. `ЭС104.0.00.000.000 РЭ8 Часть 9 Техническое обслуживание.pdf` — criteria/actions mixed with prose/tables.

Known numeric truth for the first two documents:
`IS100=12500; IS200=25000; IS510=75000; IS520=150000; IS530=300000; IS540=600000; IS600=1200000; IS700=2400000 km`.

The hard-case expected operation/criterion rows must be prepared as concise structured JSON, not copied manual prose. Benchmark must print misses and false positives.
