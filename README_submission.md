# Lab 17 — Bài nộp

**11/11 PASS, hit rate 100%** (`reports/benchmark.json`); no-memory 2/11 (18.2%).
Lặp lại được qua 3 lần chạy độc lập.

## 3 câu bắt buộc

**1. Layer quan trọng nhất.** Long-term: 4/11 case (E02, E03, E08, E09), và là layer duy
nhất chịu cả recency (E08) lẫn isolation (E09). Nó cấp nửa bằng chứng cho E07 → bỏ đi mất
5 case.

**2. Zep Context Block vs tự build Redis + Qdrant.** Zep cho sẵn trích xuất fact, khoảng
`valid_at`/`invalid_at` để xử mâu thuẫn, và cách ly theo `user_id`; giá phải trả là
1.2 s/query và context dài (E03: 1478 token cho session 221 token). Baseline local nhanh
hơn nhưng phải tự viết mọi thứ: Redis chỉ trả đúng schema đặt tay, Qdrant xếp hạng
similarity thuần (0.475 vs 0.047) — không có chiều thời gian, không phát hiện mâu thuẫn.

**3. Guardrail chống memory poisoning.** Tách quyền ghi khỏi quyền đọc: `heartbeat` chỉ
khử trùng lặp note, đánh dấu task cũ, tạo recap — **không** tự thêm instruction hay quyền
mới vào durable memory; thay đổi high-impact phải qua review. Cộng consent gate + redact
PII trước ingest, và giữ provenance để truy vết fact bẩn.

## 4 câu phân tích

1. **Layer yếu nhất:** không có — cả 4 layer 100%. Ở no-memory,
   long-term/episodic/semantic đều 0%.
2. **Tốn token nhất:** E03 (1478), E02 (1473), E08 (1469) — đều long-term, do Context
   Block cộng 25 edge fact.
3. **E07** cần long-term + semantic: bắt buộc có `Python` (user graph) và `Idempotency-Key`
   (standalone KB). Budget cắt long-term 1465 → 324 token vẫn giữ marker, vì `trim()` giữ đầu.
4. **Token reduction:** 14.2% vs 81.8%. No-memory "tiết kiệm" chỉ vì không trả gì —
   81.8% reduction đi kèm 18.2% hit rate. Case long-term reduction 0%: retrieval dài hơn
   transcript gốc, do dataset quá nhỏ. Chỉ đọc cùng hit rate mới có nghĩa.

## E08 recency & E10 compaction

**E08:** stage 3 bắt BLUEBIRD-42 dùng TypeScript/NestJS, nhưng ORCHID-27 vẫn Python —
mâu thuẫn **có phạm vi**, không phải ghi đè. Tôi thêm `graph.search(scope="edges", limit=25)`
cạnh Context Block để lấy fact thô kèm validity, nhờ đó "recency wins" kiểm chứng được.

**E10:** ở 202 turn, buffer phình 2930 token còn sliding giữ 764. Cắt cửa sổ ngây thơ thì
`REVIEW-DEADLINE-1600` biến mất; compaction giữ được vì constraint đã lên
`<DURABLE_NOTES>`. Nén sai làm mất *ràng buộc*, không phải *độ dài*.

Bằng chứng: `submission/`, `reports/`. Quá trình: `worklog.md`.
