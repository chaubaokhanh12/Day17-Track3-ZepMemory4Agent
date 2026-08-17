# Lab 17 Golden Set Report

- Implementation: `student`
- Kind: `golden`
- Cases: **20**
- Passed: **20/20**
- Evidence hit rate: **100.0%**
- Average retrieval latency: **1083.7 ms**
- Average token reduction vs full source context: **8.7%**
- Golden bonus: **10/10** (100% required)

| Case | Layer | Pass | Latency ms | Retrieved tokens | Token reduction | Missing / Error |
| --- | --- | --- | ---: | ---: | ---: | --- |
| G01 | short_term | PASS | 0.3 | 227 | 0.0% |  |
| G02 | short_term | PASS | 0.0 | 133 | 0.0% |  |
| G08 | long_term | PASS | 1953.5 | 1026 | 0.0% |  |
| G09 | long_term | PASS | 1648.7 | 2005 | 0.0% |  |
| G12 | semantic | PASS | 231.5 | 365 | 20.5% |  |
| G14 | semantic | PASS | 231.8 | 217 | 43.9% |  |
| G15 | semantic | PASS | 221.4 | 217 | 52.7% |  |
| G19 | mixed | PASS | 1676.6 | 581 | 0.0% |  |
| G03 | long_term | PASS | 1526.3 | 1966 | 0.0% |  |
| G04 | long_term | PASS | 1519.7 | 1937 | 0.0% |  |
| G05 | long_term | PASS | 1498.8 | 2011 | 0.0% |  |
| G10 | episodic | PASS | 490.0 | 548 | 0.0% |  |
| G11 | episodic | PASS | 490.0 | 575 | 0.0% |  |
| G13 | semantic | PASS | 223.5 | 363 | 35.8% |  |
| G16 | mixed | PASS | 1724.7 | 581 | 0.0% |  |
| G18 | mixed | PASS | 771.2 | 489 | 13.5% |  |
| G20 | mixed | PASS | 2455.1 | 831 | 0.0% |  |
| G06 | long_term | PASS | 1537.0 | 1995 | 0.0% |  |
| G07 | long_term | PASS | 1646.7 | 2011 | 0.0% |  |
| G17 | mixed | PASS | 1826.7 | 581 | 8.1% |  |

## Evidence excerpts

### G01 - short_term

`<SESSION_SUMMARY> user: Constraint HOLD-ALPHA-0900: standup is 09:00 sharp and must not be forgotten. | assistant: Noted standup constraint. | user: Constraint HOLD-BETA-STAGING: writes go to staging DB only. | assistant: Noted staging constraint. | user: Filler A about button padding. | assistant: Filler A. | user: Filler B about color tokens. | assistant: Filler B. | user: Filler C about copy tone. | assistant: Filler C. </SESSION_SUMMARY> <DURABLE_NOTES> - user: Constraint HOLD-ALPHA-0900: standup is 09:00 sharp and must not be forgotten. - assistant: Noted standup constraint. - user: Constraint HOLD-BETA-STAGING: writes go to staging DB only. - assistant: Noted staging constraint. </DURA`

### G02 - short_term

`<RECENT_TURNS> user: Ten du an ca nhan cua toi la ORCHID-27. Toi thich Python va khong thich Java. Khi giai thich code, hay dung vi du ngan. assistant: Da hieu: demo ca nhan ORCHID-27, uu tien Python, tranh Java, vi du ngan. user: Toi dang hoc async/await va hay nham coroutine voi Task. Neu sau nay gap chu de nay, hay giai thich bang timeline. assistant: Toi se uu tien timeline khi giai thich coroutine va Task. user: TODO: hoan thanh benchmark report truoc thu Sau luc 16:00. Day la open loop LAB-REPORT-1600. </RECENT_TURNS>`

### G08 - long_term

`<USER_SUMMARY> Lan's main pursuit is the LOTUS-88 project, prioritizing Java and Spring Boot for backend development and explicitly avoiding Python.  Lan prefers using Java and Spring Boot for backend development and does not use Python in this context. </USER_SUMMARY>  <EPISODES> Episodes are source message or document excerpts shown in selection order.   - Created At: 2026-08-17 11:18:27     Source: message     Content: [user] {   "user_id": "lan-lab17",   "first_name": "Lan",   "last_name": "Tran",   "user_alias": "Evaluation User" }: Minh la Lan, minh dang muon them retry cho phan goi payment trong san pham cua minh va minh muon vi du code hop voi dung stack ma minh dang dung chu dung du`

### G09 - long_term

`<USER_SUMMARY> Minh Nguyen's personal project is named ORCHID-27, and they prefer using Python for it. For the company project BLUEBIRD-42, the backend must use TypeScript with NestJS, and Python is not to be used.  Minh Nguyen prefers Python and dislikes Java. When explaining code, Minh prefers concise examples. Minh Nguyen prefers explanations presented as a timeline when discussing async/await and coroutines versus Tasks. </USER_SUMMARY>  <EPISODES> Episodes are source message or document excerpts shown in selection order.   - Created At: 2026-08-17 11:18:42     Source: message     Content: [user] {   "user_id": "minh-lab17",   "first_name": "Minh",   "last_name": "Nguyen",   "user_alias"`

### G12 - semantic

`EPISODE: {"id":"kb-payment-retry","entity":"Payment API Retry Policy","summary":"For POST /payments, every retryable request MUST send the same Idempotency-Key. Retry only HTTP 429 or transient 5xx errors, use exponential-backoff, and stop after max-3-retries. Marker: PAYMENT-RULE-3.","source":"internal-api-guideline-v3","updated_at":"2026-08-10T00:00:00Z"} metadata= EPISODE: For POST /payments, every retryable request MUST send the same Idempotency-Key. Retry only HTTP 429 or transient 5xx errors, use exponential-backoff, and stop after max-3-retries. Marker: PAYMENT-RULE-3. metadata= EPISODE: {"id":"kb-memory-privacy","entity":"Agent Memory Privacy Rule","summary":"Do not persist personal `

### G14 - semantic

`EPISODE: {"id":"kb-memory-privacy","entity":"Agent Memory Privacy Rule","summary":"Do not persist personal data without explicit opt-in. A deletion request must remove user-scoped memory and be verified across every store. Marker: DELETE-VERIFY-ALL.","source":"memory-governance-policy","updated_at":"2026-08-12T00:00:00Z"} metadata= EPISODE: Do not persist personal data without explicit opt-in. A deletion request must remove user-scoped memory and be verified across every store. Marker: DELETE-VERIFY-ALL. metadata= EPISODE: {"id":"kb-context-budget","entity":"Memory Context Budget","summary":"Reserve bounded context for memory. This lab uses short-term 10 percent, long-term 4 percent, episodi`

### G15 - semantic

`EPISODE: {"id":"kb-memory-privacy","entity":"Agent Memory Privacy Rule","summary":"Do not persist personal data without explicit opt-in. A deletion request must remove user-scoped memory and be verified across every store. Marker: DELETE-VERIFY-ALL.","source":"memory-governance-policy","updated_at":"2026-08-12T00:00:00Z"} metadata= EPISODE: Do not persist personal data without explicit opt-in. A deletion request must remove user-scoped memory and be verified across every store. Marker: DELETE-VERIFY-ALL. metadata= EPISODE: {"id":"kb-context-budget","entity":"Memory Context Budget","summary":"Reserve bounded context for memory. This lab uses short-term 10 percent, long-term 4 percent, episodi`

### G19 - mixed

`<LONG_TERM> <USER_SUMMARY> Lan's main pursuit is the LOTUS-88 project, prioritizing Java and Spring Boot for backend development and explicitly avoiding Python.  Lan prefers using Java and Spring Boot for backend development and does not use Python in this context. </USER_SUMMARY>  <EPISODES> Episodes are source message or document excerpts shown in selection order.   - Created At: 2026-08-17 11:20:23     Source: message     Content: [user] {   "user_id": "lan-lab17",   "first_name": "Lan",   "last_name": "Tran",   "user_alias": "Evaluation User" }: Lan uu tien stack backend nao cho LOTUS-88?   - Created At: 2026-08-01 11:00:20     Source: message     Content: Lab Assistant (assistant): Da h`

### G03 - long_term

`<USER_SUMMARY> Minh Nguyen's personal project is named ORCHID-27, and they prefer using Python for it. For the company project BLUEBIRD-42, the backend must use TypeScript with NestJS, and Python is not to be used.  Minh Nguyen prefers Python and dislikes Java. When explaining code, Minh prefers concise examples. Minh Nguyen prefers explanations presented as a timeline when discussing async/await and coroutines versus Tasks. </USER_SUMMARY>  <EPISODES> Episodes are source message or document excerpts shown in selection order.   - Created At: 2026-08-17 11:20:24     Source: message     Content: [user] {   "user_id": "minh-lab17",   "first_name": "Minh",   "last_name": "Nguyen",   "user_alias"`

### G04 - long_term

`<USER_SUMMARY> Minh Nguyen's personal project is named ORCHID-27, and they prefer using Python for it. For the company project BLUEBIRD-42, the backend must use TypeScript with NestJS, and Python is not to be used.  Minh Nguyen prefers Python and dislikes Java. When explaining code, Minh prefers concise examples. Minh Nguyen prefers explanations presented as a timeline when discussing async/await and coroutines versus Tasks. </USER_SUMMARY>  <EPISODES> Episodes are source message or document excerpts shown in selection order.   - Created At: 2026-08-17 11:20:26     Source: message     Content: [user] {   "user_id": "minh-lab17",   "first_name": "Minh",   "last_name": "Nguyen",   "user_alias"`

### G05 - long_term

`<USER_SUMMARY> Minh Nguyen's personal project is named ORCHID-27, and they prefer using Python for it. For the company project BLUEBIRD-42, the backend must use TypeScript with NestJS, and Python is not to be used.  Minh Nguyen prefers Python and dislikes Java. When explaining code, Minh prefers concise examples. Minh Nguyen prefers explanations presented as a timeline when discussing async/await and coroutines versus Tasks. </USER_SUMMARY>  <EPISODES> Episodes are source message or document excerpts shown in selection order.   - Created At: 2026-08-01 09:02:00     Source: message     Content: [user] {   "user_id": "minh-lab17",   "first_name": "Minh",   "last_name": "Nguyen",   "user_alias"`

### G10 - episodic

`EPISODE: Toi nay minh muon viet cho tron ven cai retry payment ma vua dung so thich stack ca nhan cua minh, vua theo dung policy thanh toan chinh thuc, vua tranh dam lai dung cai su co async ma lan truoc minh  EPISODE: Tuan nay minh phai them chuc nang retry payment vao dung cai backend cua du an ben cong ty chu khong phai project ca nhan, nen minh can lam theo dung chuan cong nghe ma cong ty bat buoc. Ban giup minh EPISODE: Hom nay toi debug async HTTP. Toi da thu tang timeout len 60s nhung van fail. EPISODE: Cach hieu qua la reuse aiohttp ClientSession va dat concurrency=20. Reflection: loi chinh la connection churn, khong phai timeout threshold. Ma su co ASYNC-FIX-20. EPISODE: Minh dang n`

### G11 - episodic

`EPISODE: Toi nay minh muon viet cho tron ven cai retry payment ma vua dung so thich stack ca nhan cua minh, vua theo dung policy thanh toan chinh thuc, vua tranh dam lai dung cai su co async ma lan truoc minh  EPISODE: Minh dang setup lai moi truong dev cho mot buoi ngoi code mot minh cuoi tuan nay, kieu khong co ai chung nhom, chi lam project rieng cua minh cho vui thoi. Truoc khi minh chon template va cai dependen EPISODE: Minh dang viet mot cai note tong ket ngan de tuan sau trinh bay cho ca nhom nghe ve cach minh phan biet giua viec ca nhan va viec o cong ty, vi may ban trong nhom hay bi lan lon. De minh giai thich ch EPISODE: Sang mai minh phai hop review tien do voi mentor nen toi nay `

### G13 - semantic

`EPISODE: When async HTTP calls time out, inspect connection pooling, downstream saturation and concurrency before increasing timeout. Reuse a long-lived client session where possible. Marker: CONN-POOL-FIRST. metadata= EPISODE: {"id":"kb-async-http","entity":"Async HTTP Incident Playbook","summary":"When async HTTP calls time out, inspect connection pooling, downstream saturation and concurrency before increasing timeout. Reuse a long-lived client session where possible. Marker: CONN-POOL-FIRST.","source":"incident-playbook-2026","updated_at":"2026-08-11T00:00:00Z"} metadata= EPISODE: {"id":"kb-memory-privacy","entity":"Agent Memory Privacy Rule","summary":"Do not persist personal data witho`

### G16 - mixed

`<LONG_TERM> <USER_SUMMARY> Minh Nguyen's personal project is named ORCHID-27, and they prefer using Python for it. For the company project BLUEBIRD-42, the backend must use TypeScript with NestJS, and Python is not to be used.  Minh Nguyen prefers Python and dislikes Java. When explaining code, Minh prefers concise examples. Minh Nguyen prefers explanations presented as a timeline when discussing async/await and coroutines versus Tasks. </USER_SUMMARY>  <EPISODES> Episodes are source message or document excerpts shown in selection order.   - Created At: 2026-08-17 11:18:42     Source: message     Content: [user] {   "user_id": "minh-lab17",   "first_name": "Minh",   "last_name": "Nguyen",   `

### G18 - mixed

`<EPISODIC> EPISODE: Toi nay minh muon viet cho tron ven cai retry payment ma vua dung so thich stack ca nhan cua minh, vua theo dung policy thanh toan chinh thuc, vua tranh dam lai dung cai su co async ma lan truoc minh  EPISODE: Minh dang lam kiem ke lai mo hinh cac du an backend de bao cao, ma minh rat so cai vu bi gan nham du an cua nguoi khac vao ho so cua minh, chuyen do tung xay ra roi nen lan nay minh can cham. Ban liet EPISODE: Tuan nay minh phai them chuc nang retry payment vao dung cai backend cua du an ben cong ty chu khong phai project ca nhan, nen minh can lam theo dung chuan cong nghe ma cong ty bat buoc. Ban giup minh EPISODE: Cach hieu qua la reuse aiohttp ClientSession va da`

### G20 - mixed

`<LONG_TERM> <USER_SUMMARY> Minh Nguyen's personal project is named ORCHID-27, and they prefer using Python for it. For the company project BLUEBIRD-42, the backend must use TypeScript with NestJS, and Python is not to be used.  Minh Nguyen prefers Python and dislikes Java. When explaining code, Minh prefers concise examples. Minh Nguyen prefers explanations presented as a timeline when discussing async/await and coroutines versus Tasks. </USER_SUMMARY>  <EPISODES> Episodes are source message or document excerpts shown in selection order.   - Created At: 2026-08-17 11:18:42     Source: message     Content: [user] {   "user_id": "minh-lab17",   "first_name": "Minh",   "last_name": "Nguyen",   `

### G06 - long_term

`<USER_SUMMARY> Minh Nguyen's personal project is named ORCHID-27, and they prefer using Python for it. For the company project BLUEBIRD-42, the backend must use TypeScript with NestJS, and Python is not to be used.  Minh Nguyen prefers Python and dislikes Java. When explaining code, Minh prefers concise examples. Minh Nguyen prefers explanations presented as a timeline when discussing async/await and coroutines versus Tasks. </USER_SUMMARY>  <EPISODES> Episodes are source message or document excerpts shown in selection order.   - Created At: 2026-08-17 11:18:42     Source: message     Content: [user] {   "user_id": "minh-lab17",   "first_name": "Minh",   "last_name": "Nguyen",   "user_alias"`

### G07 - long_term

`<USER_SUMMARY> Minh Nguyen's personal project is named ORCHID-27, and they prefer using Python for it. For the company project BLUEBIRD-42, the backend must use TypeScript with NestJS, and Python is not to be used.  Minh Nguyen prefers Python and dislikes Java. When explaining code, Minh prefers concise examples. Minh Nguyen prefers explanations presented as a timeline when discussing async/await and coroutines versus Tasks. </USER_SUMMARY>  <EPISODES> Episodes are source message or document excerpts shown in selection order.   - Created At: 2026-08-17 11:18:42     Source: message     Content: [user] {   "user_id": "minh-lab17",   "first_name": "Minh",   "last_name": "Nguyen",   "user_alias"`

### G17 - mixed

`<LONG_TERM> <USER_SUMMARY> Minh Nguyen's personal project is named ORCHID-27, and they prefer using Python for it. For the company project BLUEBIRD-42, the backend must use TypeScript with NestJS, and Python is not to be used.  Minh Nguyen prefers Python and dislikes Java. When explaining code, Minh prefers concise examples. Minh Nguyen prefers explanations presented as a timeline when discussing async/await and coroutines versus Tasks. </USER_SUMMARY>  <EPISODES> Episodes are source message or document excerpts shown in selection order.   - Created At: 2026-08-05 08:00:00     Source: message     Content: [user] {   "user_id": "minh-lab17",   "first_name": "Minh",   "last_name": "Nguyen",   `
