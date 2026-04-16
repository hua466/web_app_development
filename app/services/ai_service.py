"""
app/services/ai_service.py

封裝所有與 LLM API 互動的邏輯。
目前串接 Google Gemini API（可替換為 OpenAI 等其他模型）。
"""

import os
import json
import google.generativeai as genai

# ── 初始化 Gemini 用戶端 ──────────────────────────────────────
_api_key = os.environ.get('GEMINI_API_KEY', '')
if _api_key:
    genai.configure(api_key=_api_key)

_MODEL_NAME = 'gemini-1.5-flash'


def _get_model():
    """取得 Gemini GenerativeModel 實例。"""
    return genai.GenerativeModel(_MODEL_NAME)


# ── 公開函式 ──────────────────────────────────────────────────

def summarize(raw_content: str) -> str:
    """
    將使用者的零散筆記整理成結構化重點摘要。

    Args:
        raw_content: 使用者輸入的原始筆記文字。

    Returns:
        AI 整理後的結構化摘要（Markdown 格式字串）。
        若 API 呼叫失敗，回傳空字串。
    """
    prompt = f"""你是一位專業的學習助理。請將以下筆記整理成清楚的結構化重點摘要。
要求：
- 使用繁體中文回覆
- 以 Markdown 格式輸出（標題、條列式重點）
- 保留所有重要概念，去除冗詞
- 長度控制在原文的 60% 以內

筆記內容：
{raw_content}
"""
    try:
        model = _get_model()
        response = model.generate_content(prompt)
        return response.text.strip()
    except Exception as e:
        print(f"[ai_service] summarize 失敗：{e}")
        return ''


def generate_questions(summary: str, count: int = 5) -> list[dict]:
    """
    根據筆記摘要，生成單選題題目清單。

    Args:
        summary:  筆記的 AI 摘要文字。
        count:    要生成的題目數量（預設 5 題）。

    Returns:
        題目字典的清單，每個字典格式如下：
        {
            "question_text": "...",
            "option_a": "...",
            "option_b": "...",
            "option_c": "...",
            "option_d": "...",
            "correct_answer": "A",   # 'A' | 'B' | 'C' | 'D'
            "explanation": "..."
        }
        若 API 呼叫失敗，回傳空清單。
    """
    prompt = f"""你是一位出題老師。請根據以下學習內容，出 {count} 道繁體中文單選題。

要求：
- 每題有四個選項（A、B、C、D）
- 標示正確答案（correct_answer 填 'A'、'B'、'C' 或 'D'）
- 附上簡短解析（explanation）
- 嚴格以 JSON 陣列格式回傳，不要有任何額外文字

回傳格式範例：
[
  {{
    "question_text": "題目內容",
    "option_a": "選項A",
    "option_b": "選項B",
    "option_c": "選項C",
    "option_d": "選項D",
    "correct_answer": "A",
    "explanation": "解析說明"
  }}
]

學習內容：
{summary}
"""
    try:
        model = _get_model()
        response = model.generate_content(prompt)
        text = response.text.strip()
        # 移除可能的 markdown code block 包裝
        if text.startswith('```'):
            text = text.split('\n', 1)[1].rsplit('```', 1)[0].strip()
        return json.loads(text)
    except Exception as e:
        print(f"[ai_service] generate_questions 失敗：{e}")
        return []


def analyze_weakness(wrong_questions: list[dict]) -> str:
    """
    根據答錯的題目，生成個人化弱點分析與複習建議。

    Args:
        wrong_questions: 答錯題目的資訊清單，每個元素含 question_text 與 explanation。

    Returns:
        AI 生成的弱點分析建議文字（繁體中文，純文字或 Markdown）。
        若 API 呼叫失敗或沒有錯題，回傳空字串。
    """
    if not wrong_questions:
        return ''

    questions_text = '\n'.join(
        f"- {q.get('question_text', '')}（正確解析：{q.get('explanation', '')}）"
        for q in wrong_questions
    )

    prompt = f"""你是一位學習顧問。以下是學生在測驗中答錯的題目及正確解析：

{questions_text}

請根據以上資訊：
1. 分析學生可能的薄弱概念
2. 提供具體的複習建議（2~3 點）
3. 使用繁體中文，語氣鼓勵且具體
4. 回答控制在 150 字以內
"""
    try:
        model = _get_model()
        response = model.generate_content(prompt)
        return response.text.strip()
    except Exception as e:
        print(f"[ai_service] analyze_weakness 失敗：{e}")
        return ''
