# Lab 17 — Bài nộp

**Practice 11/11 (100%)**; no-memory 2/11 (18.2%). **Golden 20/20**
(`perfect: true`), lặp lại cả khi không seed lại.

## 3 câu bắt buộc

**1. Layer quan trọng nhất.** Long-term: 4/11 case (E02, E03, E08, E09), là layer duy nhất
chịu cả recency (E08) lẫn isolation (E09), và cấp nửa bằng chứng cho E07 → bỏ đi mất 5 case.

**2. Zep vs tự build Redis + Qdrant.** Zep cho sẵn trích xuất fact, khoảng
`valid_at`/`invalid_at` để xử mâu thuẫn, và cách ly theo `user_id`; giá phải trả là
1.2 s/query và context dài (E03: 1478 token cho session 221 token). Local nhanh hơn nhưng
phải tự viết mọi thứ: Redis chỉ trả schema đặt tay, Qdrant xếp hạng similarity thuần —
không có chiều thời gian, không phát hiện mâu thuẫn.

**3. Guardrail chống memory poisoning.** Tách quyền ghi khỏi quyền đọc: `heartbeat` chỉ
khử trùng lặp note, đánh dấu task cũ, tạo recap — **không** tự thêm instruction hay quyền
mới vào durable memory. Cộng consent gate, redact PII, giữ provenance để truy vết fact bẩn.

## 4 câu phân tích

1. **Layer yếu nhất:** không có — cả 4 layer 100%. Ở no-memory,
   long-term/episodic/semantic đều 0%.
2. **Tốn token nhất:** E03 (1478), E02 (1473), E08 (1469) — đều long-term, do Context
   Block cộng 25 edge fact.
3. **E07** cần long-term + semantic: `Python` (user graph) và `Idempotency-Key`
   (standalone KB). Budget cắt 1465 → 324 token vẫn giữ marker vì `trim()` giữ đầu.
4. **Token reduction:** 14.2% vs 81.8%. No-memory "tiết kiệm" vì không trả gì — kèm hit
   rate 18.2%. Case long-term reduction 0%: retrieval dài hơn transcript gốc do dataset quá
   nhỏ. Chỉ đọc cùng hit rate mới có nghĩa.

## E08 recency, E10 compaction, golden

**E08:** BLUEBIRD-42 dùng TypeScript/NestJS nhưng ORCHID-27 vẫn Python — mâu thuẫn **có
phạm vi**, không phải ghi đè. Thêm `scope="edges"` lấy fact thô kèm validity.

**E10:** ở 202 turn, buffer phình 2930 token còn sliding giữ 764. Cắt cửa sổ ngây thơ thì
`REVIEW-DEADLINE-1600` biến mất; compaction giữ được nhờ `<DURABLE_NOTES>`. Nén sai làm
mất *ràng buộc*, không phải *độ dài*.

**Golden:** 3 lỗi, không lỗi nào do sai API. (1) Fact bị diễn giải lại nên rơi mã
`LAB-REPORT-1600` → nối `scope="episodes"`. (2) `prime_eval_thread` ghi query vào user
graph: evaluator tự đầu độc bộ nhớ nó đang đo → `episode_char_cap` 600→200. (3) `limit`
≥ corpus làm Zep bỏ ranking → episodic hai tầng. Chi tiết: `worklog.md`.
