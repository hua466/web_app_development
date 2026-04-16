-- ============================================================
-- AI 學習助理系統 - SQLite 資料庫建表語法
-- ============================================================

PRAGMA foreign_keys = ON;

-- ------------------------------------------------------------
-- 1. user - 使用者帳號
-- ------------------------------------------------------------
CREATE TABLE IF NOT EXISTS user (
    id            INTEGER      PRIMARY KEY AUTOINCREMENT,
    username      VARCHAR(50)  NOT NULL UNIQUE,
    email         VARCHAR(120) NOT NULL UNIQUE,
    password_hash VARCHAR(256) NOT NULL,
    created_at    DATETIME     NOT NULL DEFAULT (datetime('now'))
);

-- ------------------------------------------------------------
-- 2. note - 筆記資料
-- ------------------------------------------------------------
CREATE TABLE IF NOT EXISTS note (
    id          INTEGER      PRIMARY KEY AUTOINCREMENT,
    user_id     INTEGER      NOT NULL,
    title       VARCHAR(200) NOT NULL,
    raw_content TEXT         NOT NULL,
    summary     TEXT,
    created_at  DATETIME     NOT NULL DEFAULT (datetime('now')),
    updated_at  DATETIME     NOT NULL DEFAULT (datetime('now')),
    FOREIGN KEY (user_id) REFERENCES user(id) ON DELETE CASCADE
);

-- ------------------------------------------------------------
-- 3. exam - 測驗紀錄
-- ------------------------------------------------------------
CREATE TABLE IF NOT EXISTS exam (
    id              INTEGER  PRIMARY KEY AUTOINCREMENT,
    note_id         INTEGER  NOT NULL,
    user_id         INTEGER  NOT NULL,
    score           INTEGER,
    total_questions INTEGER  NOT NULL,
    taken_at        DATETIME NOT NULL DEFAULT (datetime('now')),
    FOREIGN KEY (note_id) REFERENCES note(id) ON DELETE CASCADE,
    FOREIGN KEY (user_id) REFERENCES user(id) ON DELETE CASCADE
);

-- ------------------------------------------------------------
-- 4. question - 測驗題目
-- ------------------------------------------------------------
CREATE TABLE IF NOT EXISTS question (
    id              INTEGER      PRIMARY KEY AUTOINCREMENT,
    exam_id         INTEGER      NOT NULL,
    question_text   TEXT         NOT NULL,
    option_a        VARCHAR(300) NOT NULL,
    option_b        VARCHAR(300) NOT NULL,
    option_c        VARCHAR(300) NOT NULL,
    option_d        VARCHAR(300) NOT NULL,
    correct_answer  VARCHAR(1)   NOT NULL CHECK(correct_answer IN ('A','B','C','D')),
    explanation     TEXT,
    FOREIGN KEY (exam_id) REFERENCES exam(id) ON DELETE CASCADE
);

-- ------------------------------------------------------------
-- 5. answer - 使用者作答紀錄
-- ------------------------------------------------------------
CREATE TABLE IF NOT EXISTS answer (
    id          INTEGER    PRIMARY KEY AUTOINCREMENT,
    exam_id     INTEGER    NOT NULL,
    question_id INTEGER    NOT NULL,
    user_answer VARCHAR(1) NOT NULL CHECK(user_answer IN ('A','B','C','D')),
    is_correct  BOOLEAN    NOT NULL DEFAULT 0,
    FOREIGN KEY (exam_id)     REFERENCES exam(id)     ON DELETE CASCADE,
    FOREIGN KEY (question_id) REFERENCES question(id) ON DELETE CASCADE
);
