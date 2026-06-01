---
name: teaching-video
description: 依 claude-video-specs 第 02 類規範製作 教學影片
target: antigravity
---

# 教學影片 生成技能（teaching-video）

## 用途
依照 claude-video-specs 第 02 類規範製作 國中小學科教學影片。

## 觸發情境
- 「做一支教學影片/學科教學短片」
- 「按照規範做一支 教學影片」
- 「跑 teaching-video 工作流」

## 工作流
1. 確認教學主題、學齡階段（如小學四年級）、片長、素材狀況
2. 讀規範：`C:\2026antiGravity0531\scratch\claude-video-specs/specs/02-*.md`
3. fork 範本：複製 `C:\2026antiGravity0531\scratch\claude-video-specs/examples/02-*/` 到工作目錄
4. 跑該 spec 第 9 / 11 章 checklist，編排引起動機、發展活動、綜合活動三階段
5. Edge-TTS 序列生成旁白（使用 `zh-TW-YunJheNeural` 少年男聲，速率 -10%，音高 -2Hz）
6. Playwright（C:\Users\wen\AppData\Local\Temp\cvs-render）錄製 WebM，需載入源石黑體與 HTML / SVG 互動操作動畫
7. ffmpeg mux 混音背景音樂（如 SoundHelix-Song-8.mp3 音量 0.07）與 Full Audio → 輸出 H.264 mp4
8. 給使用者預覽 → 確認後存檔

## 規範路徑
`C:\2026antiGravity0531\scratch\claude-video-specs/specs/02-*.md`

## 範本路徑
`C:\2026antiGravity0531\scratch\claude-video-specs/examples/02-*/`

## 注意
- Playwright node_modules 必須在 `C:\Users\wen\AppData\Local\Temp\cvs-render`，不能放 GDrive
- Edge-TTS 旁白生成時採用序列處理，每頁加上 1-2 秒緩衝 buffer，防止旁白中斷
