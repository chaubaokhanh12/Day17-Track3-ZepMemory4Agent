# Worklog — Lab 17: Multi-Memory Agent với Zep

Nhật ký quá trình làm bài. Ghi theo thứ tự thời gian thực, kèm lệnh đã chạy và
kết quả quan sát được. Mục tiêu: trần 80 + golden 10 + UI 10.

---

## 0. Khảo sát starter kit

**Đã đọc:** `README.md`, `LAB.md`, `src/*.py`, `data/sessions.json`,
`data/knowledge.jsonl`, `tests/`, `Makefile`, `docker-compose.yml`.

Những điểm quyết định cách implement, rút ra từ code chứ không từ đề:

| Quan sát | Nguồn | Hệ quả |
| --- | --- | --- |
| `evaluate.py` chấm trên **text trả về**, không qua LLM | [src/evaluate.py:57-61](src/evaluate.py#L57-L61) | Retrieval phải chứa marker **nguyên văn**; không được tóm tắt lại |
| Budget 10/4/3/3 + priority đã có sẵn trong `ContextBudgetManager.assemble` | [src/context_budget.py:38-52](src/context_budget.py#L38-L52) | TODO 4/4 chỉ cần gọi lại, không tự viết trim |
| `trim()` giữ **đầu** chuỗi, bỏ đuôi | [src/context_budget.py:28-36](src/context_budget.py#L28-L36) | Với E07, marker phải nằm ở phần đầu mỗi layer → xếp hạng của Zep quan trọng |
| `prime_eval_thread` gọi `recreate_thread` → **xoá rồi tạo lại** thread | [src/zep_common.py:41-65](src/zep_common.py#L41-L65) | Không bao giờ được prime lên thread đã seed (`minh-s1`…), sẽ phá dữ liệu benchmark. Ảnh hưởng trực tiếp tới cách viết UI |
| `render_graph_search` có tham số `episode_char_cap` | [src/zep_common.py:88-96](src/zep_common.py#L88-L96) | Dùng cho episodic để nhiều episode khác nhau cùng lọt budget |
| `cap_query(text, 400)` | [src/utils.py:45-55](src/utils.py#L45-L55) | Golden query dài 450-600 ký tự → **bắt buộc** bọc mọi `graph.search` |
| Tất cả message trong dataset đều < 200 ký tự | `data/sessions.json` | `episode_char_cap=600` an toàn, không cắt mất marker |

Bảng marker cần có, đối chiếu với nội dung thật của session:

- `ASYNC-FIX-20`, `ClientSession`, `concurrency=20`, `connection churn`,
  `timeout threshold` — **cùng nằm trong 1 message** của `minh-s2` → episodic
  search chỉ cần trả đúng episode đó.
- `benchmark report` + `16:00` — nằm trong message cuối của `minh-s1`
  ("open loop LAB-REPORT-1600") → đây là fact có tính deadline, dễ bị Context
  Block lược bỏ.
- `BLUEBIRD-42`/`TypeScript`/`NestJS` (stage 3) mâu thuẫn có phạm vi với
  `ORCHID-27`/`Python` (stage 1) → case recency E08.

---

## 1. Môi trường

```bash
cp .env.example .env          # .env đã nằm trong .gitignore
docker compose build          # OK
```

**Sự cố:** Docker Desktop tắt daemon ngay sau khi build
(`npipe:////./pipe/dockerDesktopLinuxEngine ... cannot find the file specified`).
Để không bị chặn, dựng thêm một venv local chạy song song:

```bash
python -m venv .venv
.venv/Scripts/python.exe -m pip install -r requirements.txt
echo ".venv/" >> .gitignore
```

Zep là dịch vụ cloud nên benchmark chạy được từ venv; Redis/Qdrant chỉ cần cho
`src.smoke` và `src.local_baseline` nên vẫn dùng Docker khi daemon sống lại.

```bash
.venv/Scripts/python.exe -m pytest -q
# 11 passed, 1 skipped in 0.25s
```

Starter kit chưa bị phá. Đây là mốc để so lại sau mỗi lần sửa code.

---

## 2. TODO 1-4 trong `src/memory_student.py`

Viết toàn bộ từ đặc tả trong `LAB.md` + docstring của starter kit.
**Không** đọc/copy `src/memory_reference.py`.

### Quyết định thiết kế

**`_search()` helper.** Bọc `graph.search` để lỗi trả `None` thay vì raise.
Lý do: `run_case` bắt exception và cho case = FAIL với `retrieved=""`
([src/evaluate.py:140-146](src/evaluate.py#L140-L146)). Một scope không được
server hỗ trợ sẽ thổi bay cả case, kể cả khi các phần khác đã lấy được bằng
chứng. Có helper thì fallback mới khả thi.

**TODO 1/4 `retrieve_long_term` — Context Block + edge facts.**
`thread.get_user_context` trả context đã được Zep tóm tắt theo relevance. Vấn
đề: E03 hỏi open loop/deadline, và một open loop có mốc thời gian rất dễ bị
lược khỏi bản tóm tắt. Nên nối thêm `graph.search(scope="edges", limit=25)`:

- `scope="edges"` trả **fact thô** kèm `valid_at`/`invalid_at`
  ([src/zep_common.py:102-107](src/zep_common.py#L102-L107)) — chính khoảng
  validity này làm "recency wins" của E08 kiểm chứng được, thay vì tin vào tóm tắt.
- `limit=25` chứ không phải mặc định nhỏ: docstring starter kit cảnh báo limit
  thấp làm rơi fact deadline/open-loop.
- Cả hai lời gọi đều scope theo `user_id`. Đây là toàn bộ đảm bảo cách ly của
  E09 — chỉ cần một lần đổi sang `graph_id` dùng chung là leak.

**TODO 2/4 `retrieve_episodic` — `scope="episodes"`, không phải `edges`.**
Episode là source thô đã ingest, giữ nguyên marker chữ hoa (`ASYNC-FIX-20`).
Fact được trích xuất thì diễn giải lại và làm rơi mã. Dùng `limit=8` +
`episode_char_cap=600`: giữ nhiều episode khác biệt hơn trong cùng budget, và
vì message dài nhất trong dataset chỉ 185 ký tự nên cap này không cắt mất gì.

**TODO 3/4 `retrieve_semantic` — `graph_id`, `scope="episodes"`, fallback `nodes`.**
`scope="auto"` trả entity/fact đã trích xuất và **làm mất** `PAYMENT-RULE-3` /
`CONN-POOL-FIRST`, đúng cảnh báo trong LAB.md. Fallback `nodes` chỉ chạy khi
episodes rỗng (graph vừa seed, chưa index xong).

**TODO 4/4 `assemble_context`.** Gọi thẳng `self.budget.assemble(layers)`.
`ContextBudgetManager` đã encode cả tỷ lệ 10/4/3/3 lẫn thứ tự ưu tiên
short_term → long_term → episodic → semantic, và `test_context_budget.py` đã
khoá hành vi đó. Viết lại tay chỉ tạo cơ hội lệch khỏi test.

Hằng số retrieval để tên ở đầu file (`LONG_TERM_FACT_LIMIT` = 25,
`EPISODIC_LIMIT` = 8, `EPISODIC_CHAR_CAP` = 600, `SEMANTIC_LIMIT` = 8) để
đánh đổi recall/token nhìn thấy được thay vì là magic number.

---

## 3. Pha A — Short-term: buffer vs summary vs sliding (T3, E01 + E10)

```bash
.venv/Scripts/python.exe -m src.demo_short_term     # k = 6, mặc định
```

Sau đó chạy lại với `max_recent_messages=4` (chạy bằng script inline, không sửa
file starter kit) — log: `reports/logs/demo_short_term_k6_vs_k4.log`.

| k | strategy | messages_kept | durable_notes | compactions | tokens | giữ được `REVIEW-DEADLINE-1600` |
| ---: | --- | ---: | ---: | ---: | ---: | --- |
| 6 | buffer | 16 | 0 | 0 | 231 | có |
| 6 | summary | 6 | 1 | 2 | 247 | có |
| 6 | sliding | 6 | 1 | 10 | 287 | có |
| 4 | buffer | 16 | 0 | 0 | 231 | có |
| 4 | summary | 4 | 1 | 4 | 288 | có |
| 4 | sliding | 4 | 1 | 12 | 288 | có |

Hạ k từ 6 → 4: raw turn cũ bị evict thêm (compactions 10 → 12) nhưng constraint
vẫn còn, vì nó đã được `extract_durable_notes` nâng lên `<DURABLE_NOTES>`.
Đó chính là điều E10 chấm.

**Nhận xét quan trọng:** ở quy mô 16 turn thì buffer cũng "đúng", nên demo mặc
định *chưa* chứng minh được gì. Phải kéo dài hội thoại mới thấy sự khác biệt
(`reports/logs/short_term_scaling.log`):

| số turn | buffer (tokens) | sliding (tokens) | cả hai còn constraint? |
| ---: | ---: | ---: | --- |
| 16 | 231 | 287 | có |
| 62 | 892 | 763 | có |
| 202 | **2930** | **764** | có |

Buffer tăng tuyến tính không giới hạn — ở 202 turn nó tốn gấp ~4 lần sliding
cho cùng một lượng thông tin dùng được. Và khi bị chặn cứng, cách cắt ngây thơ
sẽ giết constraint (`reports/logs/naive_window_vs_compaction.log`):

```text
naive last-6 window keeps REVIEW-DEADLINE-1600 ? False
sliding+compaction keeps it ?                    True   (196 lần compaction)
```

Kết luận cho báo cáo: compaction không phải "tóm tắt cho ngắn". Cửa sổ trượt
thuần tuý và compaction có cùng chi phí token, nhưng chỉ compaction giữ lại
state/decision/TODO/constraint. Cái mất khi cắt ngây thơ là *ràng buộc*, không
phải *độ dài*.

---

## 4. Môi trường thật: hai sự cố hạ tầng

**(a) Docker Desktop tự tắt daemon.** Khởi động lại được, Redis/Qdrant chạy bình thường.

**(b) Image `app` không build được.** PyPI/Docker Hub timeout TLS trong lúc build:

```text
docker: ... registry-1.docker.io ...: net/http: TLS handshake timeout
ERROR: ResolutionImpossible: protobuf / pydantic-core  (no matching distributions)
```

Không phải lỗi `requirements.txt` — cùng bộ deps cài sạch trong venv local. Nên
toàn bộ lệnh chạy qua `.venv` với `REDIS_URL`/`QDRANT_URL` trỏ `localhost`
(Redis/Qdrant vẫn là container thật). Zep là dịch vụ cloud nên benchmark không
bị ảnh hưởng. Lệnh `docker compose run --rm app python -m ...` tương đương vẫn
nằm trong `Makefile`.

---

## 5. Chạy thật: T1 → T8

```bash
python -m src.smoke
# [OK] Redis reachable / [OK] Qdrant reachable
# [OK] sessions.json valid: 11 evaluations / [OK] ZEP_API_KEY is present

python -m src.seed          # reset 2 user + semantic graph, ingest stage 1-3
python -m src.evaluate --impl no_memory
python -m src.evaluate --impl student --reuse-seeded
python -m src.compare_reports
```

### Kết quả

| | Memory-enabled | No-memory |
| --- | ---: | ---: |
| Hit rate | **100.0% (11/11)** | 18.2% (2/11) |
| Latency TB | 1199.1 ms | 0.0 ms |
| Token reduction TB | 14.2% | 81.8% |

Cả 11 case PASS ngay lần chạy đầu, không phải sửa lại lần nào. Chạy lại **3 lần
độc lập** (1 lần trong đó sau khi seed lại từ đầu) — đều 11/11, nên đây không
phải may mắn về thứ tự index của Zep.

Bằng chứng từng layer (`--only-layer`, log trong `submission/`):

- `long_term` → E02, E03, E08, E09 PASS
- `episodic` → E04, E05 PASS
- `semantic` → E06, E11 PASS

> **Bẫy đã tránh:** `evaluate.py` ghi đè `reports/benchmark.json` sau **mọi** lần
> chạy, kể cả `--only-layer`. Chạy per-layer để lấy bằng chứng sẽ âm thầm biến
> báo cáo nộp bài thành bản 2 case. Sau mỗi đợt per-layer đều chạy lại full set.

### Số liệu dùng cho phần phân tích

| case | layer | retrieved tok | full source tok | reduction |
| --- | --- | ---: | ---: | ---: |
| E03 | long_term | 1478 | 221 | 0.0% |
| E02 | long_term | 1473 | 221 | 0.0% |
| E08 | long_term | 1469 | 288 | 0.0% |
| E09 | long_term | 784 | 44 | 0.0% |
| E07 | mixed | 485 | 565 | 14.2% |
| E04 | episodic | 249 | 221 | 0.0% |
| E06 | semantic | 148 | 459 | 67.8% |

Phát hiện đáng nói: các case long-term có reduction **0%** — retrieval trả về
*nhiều token hơn cả transcript gốc*. Context Block + 25 edge fact tốn ~1470
token trong khi cả session chỉ 221. Ở quy mô dataset lab thì "nhớ" đắt hơn "đọc
lại tất cả"; reduction chỉ thắng khi lịch sử lớn hơn context block nhiều lần.
Đây là lý do không được đọc token reduction tách rời hit rate — no-memory đạt
81.8% reduction đúng vì nó không trả gì cả.

E07 cho thấy budget hoạt động: long-term raw 1465 token → cắt còn 324
(limit 320), semantic 148 (limit 240), và vẫn giữ đủ `Python` +
`Idempotency-Key`. Giữ được là nhờ `trim()` giữ **đầu** chuỗi và Zep xếp fact
liên quan nhất lên trước.

---

## 6. Mini-drill (T9)

```bash
python -m src.episodic_maintenance
python -m src.heartbeat --dry-run
python -m src.local_baseline
```

- `episodic_maintenance`: importance decay (ep-async 0.475 → ep-ui 0.058), LRU
  chọn evict `ep-ui`/`ep-naming`, consolidation gộp trajectory thành chiến lược
  tái dùng ("kiểm tra connection pooling trước khi tăng timeout").
- `heartbeat --dry-run`: liệt kê 3 open loop, và quan trọng là **không ghi gì**.
  Đây chính là guardrail chống memory poisoning viết trong bài nộp.
- `local_baseline`: Redis trả profile đúng schema đặt tay; Qdrant xếp hạng
  similarity thuần — payment doc 0.475 so với 0.047. Đủ để trả lời câu trade-off:
  thứ Zep cho không mà local phải tự xây là **validity theo thời gian** và
  **phát hiện mâu thuẫn**.

---

## 7. Privacy drill (T10)

Thứ tự bắt buộc: lưu `reports/benchmark.json` (11/11) **trước**, rồi mới xoá.

```bash
python -m src.forget --user-id minh-lab17
# Redis keys deleted: 3
# Zep user absent: True
# Redis user keys remaining: 0

python -m src.forget --user-id minh-lab17 --verify-only
# Zep user absent: True
# Redis user keys remaining: 0
```

Semantic KB dùng chung được giữ nguyên (domain knowledge, không chứa PII).
Sau khi lấy bằng chứng đã `python -m src.seed` lại ngay, rồi chạy lại full
benchmark — vẫn 11/11 — để repo ở trạng thái sẵn sàng cho golden.

---

## 8. Bonus UI (T13)

Hoàn thiện `retrieve_for_case` trong `src/demo_ui.py`.

**Lỗi nghiêm trọng phát hiện khi viết hàm này:** `retrieve_long_term` gọi
`prime_eval_thread` → `recreate_thread` → **`thread.delete` rồi `thread.create`**.
Nếu UI truyền `thread_id` của case vào, nó xoá luôn session đã seed. E01 dùng
`thread_id = minh-s1` — một thread thật. Bấm "Run retrieval" trên E01 ở chế độ
chat (có fetch long-term) là mất dữ liệu stage 1, benchmark hỏng im lặng.
Cách xử lý: luôn prime lên thread nháp `ui-scratch-<case>-<user>`, giao diện vẫn
hiển thị `thread_id` thật của case.

Hai điểm thiết kế khác:

- Chọn layer theo `expected_layer` / `retrieve_layers` của case; nhưng khi người
  dùng bắt đầu gõ chat thì mở rộng ra cả 4 layer, vì câu hỏi tự do không còn bị
  ràng buộc vào layer của case.
- Máy này có OpenAI key chứ không có Gemini, mà `src/llm.py` chỉ nói chuyện với
  Gemini. Thêm đường OpenAI **ngay trong `demo_ui.py`** (file học viên được sửa)
  thay vì vá module starter kit, và dùng `requests` — vốn đã là dependency — nên
  `requirements.txt`/image không đổi.

Chạy thật, không mock:

```text
chat backend: OpenAI · gpt-4o-mini
layers active: ['long_term', 'semantic']
  short_term  used=    0 limit=  800 raw=    0
  long_term   used=  324 limit=  320 raw= 1465
  episodic    used=    0 limit=  240 raw=    0
  semantic    used=  148 limit=  240 raw=  148
markers -> Python: True | Idempotency-Key: True
chat-mode layers: ['short_term', 'long_term', 'episodic', 'semantic']
--- OpenAI grounded reply ---
Bạn nên viết retry cho POST /payments bằng ngôn ngữ TypeScript, theo quy tắc sau:
- Mỗi yêu cầu retryable PHẢI gửi cùng một Idempotency-Key.
- Chỉ retry cho các lỗi HTTP 429 hoặc các lỗi 5xx tạm thời.
- Sử dụng exponential-backoff và dừng sau tối đa 3 lần retry.
(Marker: PAYMENT-RULE-3)
```

Câu trả lời bám đúng memory context và trích marker `PAYMENT-RULE-3`. Chi tiết
thú vị: model chọn **TypeScript** vì long-term context chứa cả bản cập nhật
BLUEBIRD-42 lẫn preference Python của ORCHID-27 — đúng tình huống mâu thuẫn có
phạm vi của E08, chỉ khác là lần này để LLM phân xử.

Streamlit phục vụ tại `http://127.0.0.1:8501` (HTTP 200).

### 8.1. Mạng chập chờn khi gọi OpenAI — và cách xử lý

Trong lúc demo, chat UI văng:

```text
SSLError: HTTPSConnectionPool(host='api.openai.com', port=443):
  [SSL: TLSV1_ALERT_PROTOCOL_VERSION] tlsv1 alert protocol version
```

Chẩn đoán trước khi sửa, thay vì đoán:

- Bắt tay TLS thô tới `api.openai.com` từ đúng venv đó: **OK, TLSv1.3**, cert
  Google Trust Services. Python 3.13.12 / OpenSSL 3.5.5 — không hề cũ.
- Chạy lại đúng lời gọi `openai_reply` ngay sau đó: **thành công**.
- Chạy 3 lần liên tiếp: 2 thành công, 1 chết vì `ReadTimeout`.

Vậy đây không phải lỗi cấu hình TLS mà là **lỗi chập chờn của đường mạng**.
`TLSV1_ALERT_PROTOCOL_VERSION` là alert do *phía bên kia* gửi về ("không nhận
phiên bản TLS mày đề nghị") — trong khi OpenAI rõ ràng nhận TLS 1.3. Nên thứ trả
alert đó nhiều khả năng là một middlebox chen giữa (antivirus/firewall có TLS
inspection, VPN hoặc proxy) chỉ nói được TLS cũ hơn. Khớp với việc build Docker
cũng dính `TLS handshake timeout` tới `registry-1.docker.io` (mục 4) — ba triệu
chứng khác nhau, một nguyên nhân.

Cách xử lý: retry có backoff (2s, 4s) cho `SSLError`, `ConnectionError`,
`Timeout`, kèm thông báo lỗi nói rõ retrieval **không** bị ảnh hưởng — chỉ câu
trả lời chat cần lời gọi này. Sau khi thêm: **5/5 lời gọi thành công**.

Không đụng gì tới `verify=False` hay hạ phiên bản TLS: tắt xác thực chứng chỉ để
chữa một lỗi chập chờn là đổi một sự cố demo lấy một lỗ hổng bảo mật.

---

## 9. Trạng thái điểm

| Khối | Tối đa | Đạt | Căn cứ |
| --- | ---: | ---: | --- |
| Auto E01-E11 | 56 | **56** | `reports/benchmark.json`, 11/11 |
| Privacy drill | 6 | **6** | delete + verify, `submission/evidence_privacy.log` |
| Phân tích + comparison | 6 | **6** | `reports/comparison.md` + 4 câu |
| README_submission 3 câu | 6 | **6** | `README_submission.md` |
| Artefact | 6 | **6** | 4 hàm xong, report đủ, bằng chứng đủ |
| **Trần nền** | **80** | **80** | |
| Golden 20/20 | +10 | **chờ** | `data/golden_eval.json` chưa được phát |
| UI demo | +10 | **10** | đủ 4 mục checklist, chat OpenAI thật |

**Còn thiếu để trọn 100:** file golden của giảng viên. Khi có, copy vào
`data/golden_eval.json` rồi chạy đúng một lệnh:

```bash
python -m src.evaluate --impl student --reuse-seeded --golden
```

Graph đang ở trạng thái vừa seed lại nên chạy được ngay. Golden query có thể dài
450-600 ký tự — mọi `graph.search` đã bọc `cap_query()` sẵn nên không bị Zep từ chối.

**Chưa làm được thay bạn:** 4 file `.png` screenshot. Bằng chứng dạng log đã đủ
trong `submission/` (`evidence_long_term.log`, `evidence_episodic.log`,
`evidence_semantic.log`, `evidence_privacy.log`, `evidence_ui.log`) — chụp màn
hình terminal/UI thì cần thao tác người thật.
