---
name: water-science
description: 依 claude-video-specs 第 03 類規範製作 社群科普影片
target: antigravity
---

# 社群科普影片 生成技能（water-science）

## 用途
依照 claude-video-specs 第 03 類規範製作 社群科普影片。

## 觸發情境
- 「做一支社群科普/IG/YouTube Shorts 短片」
- 「按照規範做一支 社群科普影片」
- 「跑 water-science 工作流」

## 工作流
1. 確認主題、片長、素材狀況
2. 讀規範：`C:\2026antiGravity0531\scratch\claude-video-specs/specs/03-*.md`
3. fork 範本：複製 `C:\2026antiGravity0531\scratch\claude-video-specs/examples/03-*/` 到工作目錄
4. 跑該 spec 第 9 / 11 章 checklist
5. Edge-TTS 序列生成旁白
6. Playwright（C:\Users\wen\AppData\Local\Temp\cvs-render）錄製 webm
7. ffmpeg mux master_audio → mp4
8. 給使用者預覽 → 確認後存檔

## 規範路徑
`C:\2026antiGravity0531\scratch\claude-video-specs/specs/03-*.md`

## 範本路徑
`C:\2026antiGravity0531\scratch\claude-video-specs/examples/03-*/`

## 注意
- Playwright node_modules 必須在 `C:\Users\wen\AppData\Local\Temp\cvs-render`，不能放 GDrive
- Edge-TTS 並行會被斷線，序列 + retry 3 次
