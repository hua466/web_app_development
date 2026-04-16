# 路由設計文件 (ROUTES) - AI 學習助理系統

本文件根據 PRD.md、ARCHITECTURE.md、FLOWCHART.md 與 DB_DESIGN.md，規劃所有 Flask 路由的 URL、HTTP 方法、輸入輸出與對應模板。

---

## 1. 路由總覽表格

| 功能               | HTTP 方法 | URL 路徑                        | 對應模板                              | Blueprint        |
|--------------------|-----------|---------------------------------|---------------------------------------|------------------|
| 首頁（重導向）      | GET       | `/`                             | —（redirect to `/dashboard`）         | `dash_routes`    |
| **── 驗證 ──**    |           |                                 |                                       |                  |
| 顯示登入頁          | GET       | `/login`                        | `auth/login.html`                     | `auth_routes`    |
| 執行登入            | POST      | `/login`                        | —（成功→`/dashboard`；失敗→`/login`） | `auth_routes`    |
| 顯示註冊頁          | GET       | `/register`                     | `auth/register.html`                  | `auth_routes`    |
| 執行註冊            | POST      | `/register`                     | —（成功→`/login`；失敗→`/register`）  | `auth_routes`    |
| 登出               | GET       | `/logout`                       | —（redirect to `/login`）             | `auth_routes`    |
| **── Dashboard ──**|          |                                 |                                       |                  |
| 儀表板首頁          | GET       | `/dashboard`                    | `dashboard/index.html`                | `dash_routes`    |
| **── 筆記 ──**    |           |                                 |                                       |                  |
| 筆記列表            | GET       | `/notes`                        | `notes/list.html`                     | `note_routes`    |
| 顯示新增筆記頁       | GET       | `/notes/new`                    | `notes/new.html`                      | `note_routes`    |
| 上傳並 AI 整理筆記  | POST      | `/notes/upload`                 | —（成功→`/notes/<note_id>`）          | `note_routes`    |
| 單一筆記檢視        | GET       | `/notes/<int:note_id>`          | `notes/view.html`                     | `note_routes`    |
| 刪除筆記            | POST      | `/notes/<int:note_id>/delete`   | —（redirect to `/notes`）             | `note_routes`    |
| **── 測驗 ──**    |           |                                 |                                       |                  |
| 生成測驗（AI 出題） | POST      | `/exams/generate/<int:note_id>` | —（成功→`/exams/<exam_id>`）          | `exam_routes`    |
| 測驗作答頁          | GET       | `/exams/<int:exam_id>`          | `exams/take_exam.html`                | `exam_routes`    |
| 送出並批改          | POST      | `/exams/submit/<int:exam_id>`   | —（redirect to `/exams/result/<id>`） | `exam_routes`    |
| 成績解析頁          | GET       | `/exams/result/<int:exam_id>`   | `exams/result.html`                   | `exam_routes`    |

---

## 2. 每個路由的詳細說明

### 2.1 驗證模組（`auth_routes.py`）

#### `GET /login` — 顯示登入頁
- **輸入**：無
- **邏輯**：若已登入則 redirect 至 `/dashboard`
- **輸出**：渲染 `auth/login.html`
- **錯誤**：無

#### `POST /login` — 執行登入
- **輸入**（表單）：`email`、`password`
- **邏輯**：
  1. `User.get_by_email(email)` 查找使用者
  2. `user.check_password(password)` 驗證密碼
  3. 成功則寫入 `session['user_id']`
- **輸出**：成功→ redirect `/dashboard`；失敗→ redirect `/login`（帶 flash 錯誤訊息）
- **錯誤**：帳號不存在或密碼錯誤 → flash `"帳號或密碼錯誤"`

#### `GET /register` — 顯示註冊頁
- **輸入**：無
- **邏輯**：若已登入則 redirect 至 `/dashboard`
- **輸出**：渲染 `auth/register.html`

#### `POST /register` — 執行註冊
- **輸入**（表單）：`username`、`email`、`password`、`confirm_password`
- **邏輯**：
  1. 驗證兩次密碼一致
  2. 確認 `email` 與 `username` 未重複
  3. `User.create(...)` 寫入資料庫
- **輸出**：成功→ redirect `/login`；失敗→ redirect `/register`（帶 flash 錯誤訊息）
- **錯誤**：密碼不符、Email 已存在 → flash 對應訊息

#### `GET /logout` — 登出
- **輸入**：無
- **邏輯**：清除 `session`
- **輸出**：redirect `/login`

---

### 2.2 儀表板模組（`dash_routes.py`）

#### `GET /dashboard` — 儀表板首頁
- **輸入**：無（從 session 取 `user_id`）
- **邏輯**：
  1. 查詢該使用者最近 5 筆筆記（`Note.get_by_user(user_id)`）
  2. 查詢該使用者所有測驗紀錄（`Exam.get_by_user(user_id)`）
  3. 計算平均成績、總測驗次數
  4. 取得答錯題目（`Answer.get_wrong_answers(user_id)`）作為弱點摘要
- **輸出**：渲染 `dashboard/index.html`，傳入 `recent_notes`、`exams`、`avg_score`、`wrong_answers`
- **錯誤**：未登入 → redirect `/login`

---

### 2.3 筆記模組（`note_routes.py`）

#### `GET /notes` — 筆記列表
- **輸入**：無
- **邏輯**：`Note.get_by_user(user_id)` 取得所有筆記
- **輸出**：渲染 `notes/list.html`，傳入 `notes`
- **錯誤**：未登入 → redirect `/login`

#### `GET /notes/new` — 顯示新增筆記頁
- **輸入**：無
- **輸出**：渲染 `notes/new.html`（含文字輸入區與語音錄音按鈕）

#### `POST /notes/upload` — 上傳並 AI 整理筆記
- **輸入**（表單）：`title`、`raw_content`
- **邏輯**：
  1. 驗證 `raw_content` 非空
  2. 呼叫 `ai_service.summarize(raw_content)` 取得 AI 摘要
  3. `Note.create(user_id, title, raw_content, summary)` 儲存
- **輸出**：redirect `/notes/<note_id>`
- **錯誤**：內容為空 → flash `"請輸入筆記內容"`；AI 服務失敗 → flash 錯誤並存原始筆記（summary=None）

#### `GET /notes/<note_id>` — 單一筆記檢視
- **輸入**：URL `note_id`
- **邏輯**：`Note.get_by_id(note_id)`，驗證筆記屬於當前使用者
- **輸出**：渲染 `notes/view.html`，傳入 `note`、`exams`（該筆記的歷史測驗）
- **錯誤**：筆記不存在 → 404；非本人 → 403

#### `POST /notes/<note_id>/delete` — 刪除筆記
- **輸入**：URL `note_id`
- **邏輯**：驗證筆記屬於當前使用者，呼叫 `note.delete()`
- **輸出**：redirect `/notes`（帶 flash `"筆記已刪除"`）
- **錯誤**：筆記不存在 → 404；非本人 → 403

---

### 2.4 測驗模組（`exam_routes.py`）

#### `POST /exams/generate/<note_id>` — AI 生成測驗
- **輸入**：URL `note_id`
- **邏輯**：
  1. 確認筆記屬於當前使用者
  2. 呼叫 `ai_service.generate_questions(note.summary)` 取得 JSON 題目清單
  3. `Exam.create(note_id, user_id, total_questions=len(questions))` 建立測驗
  4. `Question.bulk_create(exam_id, questions)` 批次寫入題目
- **輸出**：redirect `/exams/<exam_id>`
- **錯誤**：AI 服務失敗 → flash 錯誤；筆記尚未有摘要 → flash `"請先整理筆記"`

#### `GET /exams/<exam_id>` — 測驗作答頁
- **輸入**：URL `exam_id`
- **邏輯**：取得 `Exam.get_by_id(exam_id)`、`Question.get_by_exam(exam_id)`
- **輸出**：渲染 `exams/take_exam.html`，傳入 `exam`、`questions`
- **錯誤**：測驗不存在 → 404；非本人 → 403；已作答 → redirect `/exams/result/<exam_id>`

#### `POST /exams/submit/<exam_id>` — 送出並批改
- **輸入**（表單）：各題作答 `answer_<question_id>`
- **邏輯**：
  1. 取出所有題目並對照使用者答案
  2. 計算答對數 `score`
  3. `Answer.bulk_create(answers_data)` 批次儲存作答紀錄
  4. `exam.submit(score)` 更新分數
- **輸出**：redirect `/exams/result/<exam_id>`
- **錯誤**：測驗不存在 → 404；非本人 → 403

#### `GET /exams/result/<exam_id>` — 成績解析頁
- **輸入**：URL `exam_id`
- **邏輯**：
  1. `Exam.get_by_id(exam_id)` 取測驗資訊
  2. `Answer.get_by_exam(exam_id)` 取作答紀錄
  3. 篩選答錯題目，呼叫 `ai_service.analyze_weakness(wrong_questions)` 取得弱點建議文字
- **輸出**：渲染 `exams/result.html`，傳入 `exam`、`answers`、`weakness_advice`
- **錯誤**：測驗不存在 → 404；非本人 → 403；尚未作答 → redirect `/exams/<exam_id>`

---

## 3. Jinja2 模板清單

| 模板路徑                          | 繼承自          | 說明                                 |
|-----------------------------------|-----------------|--------------------------------------|
| `templates/base.html`             | —               | 共用版型（導覽列、CSS、JS）           |
| `templates/auth/login.html`       | `base.html`     | 登入表單                              |
| `templates/auth/register.html`    | `base.html`     | 註冊表單                              |
| `templates/dashboard/index.html`  | `base.html`     | 儀表板（近期筆記、成績統計、弱點摘要）|
| `templates/notes/list.html`       | `base.html`     | 所有筆記列表                          |
| `templates/notes/new.html`        | `base.html`     | 新增筆記（文字輸入 + 語音按鈕）       |
| `templates/notes/view.html`       | `base.html`     | 單一筆記檢視（摘要 + 開始測驗按鈕）  |
| `templates/exams/take_exam.html`  | `base.html`     | 測驗作答頁（選項卡片互動）            |
| `templates/exams/result.html`     | `base.html`     | 成績解析（答對率、錯題列表、AI 建議） |

---

## 4. 登入保護機制

所有需要登入的路由，皆透過 `login_required` 裝飾器攔截，統一 redirect 至 `/login`：

```python
from functools import wraps
from flask import session, redirect, url_for

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return redirect(url_for('auth.login'))
        return f(*args, **kwargs)
    return decorated_function
```

需要登入的路由：`/dashboard`、`/notes/*`、`/exams/*`
