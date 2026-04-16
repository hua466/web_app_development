/**
 * speech.js — Web Speech API 語音輸入整合
 * 使用瀏覽器內建 SpeechRecognition，將語音轉為文字後填入 #raw_content。
 */

(function () {
  'use strict';

  const btn       = document.getElementById('voiceBtn');
  const status    = document.getElementById('voiceStatus');
  const textarea  = document.getElementById('raw_content');

  // 若頁面沒有語音按鈕則直接結束
  if (!btn || !textarea) return;

  // 檢查瀏覽器支援
  const SpeechRecognition =
    window.SpeechRecognition || window.webkitSpeechRecognition;

  if (!SpeechRecognition) {
    btn.disabled = true;
    btn.title    = '你的瀏覽器不支援語音輸入（建議使用 Chrome）';
    if (status) status.textContent = '⚠️ 瀏覽器不支援語音輸入';
    return;
  }

  const recognition        = new SpeechRecognition();
  recognition.lang         = 'zh-TW';
  recognition.continuous   = true;   // 持續錄音，不自動停止
  recognition.interimResults = true; // 顯示中間結果

  let isRecording  = false;
  let finalText    = '';

  // ── 開始／停止切換 ──────────────────────────────────────
  btn.addEventListener('click', function () {
    if (!isRecording) {
      startRecording();
    } else {
      stopRecording();
    }
  });

  function startRecording() {
    finalText   = textarea.value;   // 保留已有文字
    isRecording = true;
    btn.classList.add('recording');
    btn.innerHTML = '<i class="bi bi-stop-circle me-1"></i> 停止錄音';
    if (status) status.textContent = '🎙️ 錄音中…';
    recognition.start();
  }

  function stopRecording() {
    isRecording = false;
    btn.classList.remove('recording');
    btn.innerHTML = '<i class="bi bi-mic me-1"></i> 開始錄音';
    if (status) status.textContent = '✅ 語音已填入';
    recognition.stop();
  }

  // ── 語音結果處理 ────────────────────────────────────────
  recognition.addEventListener('result', function (event) {
    let interim = '';
    for (let i = event.resultIndex; i < event.results.length; i++) {
      const transcript = event.results[i][0].transcript;
      if (event.results[i].isFinal) {
        finalText += transcript;
      } else {
        interim += transcript;
      }
    }
    textarea.value = finalText + interim;
  });

  recognition.addEventListener('error', function (event) {
    console.warn('SpeechRecognition error:', event.error);
    if (status) status.textContent = `⚠️ 語音辨識錯誤：${event.error}`;
    stopRecording();
  });

  recognition.addEventListener('end', function () {
    if (isRecording) {
      // 若仍在錄音狀態（自動斷開），重新啟動
      recognition.start();
    }
  });
})();
