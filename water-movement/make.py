import os
import sys
import subprocess
import urllib.request
from pathlib import Path

# 定義路徑
BASE_DIR = Path(__file__).parent
ASSETS_DIR = BASE_DIR / "assets"
NARRATION_DIR = ASSETS_DIR / "narration"
AUDIO_DIR = ASSETS_DIR / "audio"
RENDERS_DIR = BASE_DIR / "renders"

RENDERS_DIR.mkdir(parents=True, exist_ok=True)
AUDIO_DIR.mkdir(parents=True, exist_ok=True)

# 頁面及時長 (與 index.html 相同)
PAGES = [
    {"i": 1,  "dur": 9.65},
    {"i": 2,  "dur": 8.42},
    {"i": 3,  "dur": 10.51},
    {"i": 4,  "dur": 8.88},
    {"i": 5,  "dur": 10.73},
    {"i": 6,  "dur": 11.16},
    {"i": 7,  "dur": 10.61},
    {"i": 8,  "dur": 9.91},
    {"i": 9,  "dur": 7.90},
    {"i": 10, "dur": 9.62},
    {"i": 11, "dur": 10.46}
]

def run_cmd(args, cwd=None):
    print(f"Executing: {' '.join(args)}")
    subprocess.run(args, check=True, cwd=cwd, shell=True)

def main():
    print("=== Step 1: 將各頁旁白音訊對齊時長 ===")
    padded_files = []
    for p in PAGES:
        i = p["i"]
        dur = p["dur"]
        src = NARRATION_DIR / f"page-{i:02d}.mp3"
        dest = NARRATION_DIR / f"page-{i:02d}-padded.mp3"
        
        # 使用 apad 填充或截斷音訊至指定秒數
        cmd = [
            "ffmpeg", "-y",
            "-i", str(src),
            "-filter_complex", "apad",
            "-t", str(dur),
            str(dest)
        ]
        run_cmd(cmd)
        padded_files.append(dest)

    print("\n=== Step 2: Concat 合併所有旁白 ===")
    list_file = BASE_DIR / "list.txt"
    with open(list_file, "w", encoding="utf-8") as f:
        for pf in padded_files:
            # 必須使用相對路徑或 FFmpeg 格式的絕對路徑；
            # 為防中文路徑，使用相對於 BASE_DIR 的路徑
            rel_path = pf.relative_to(BASE_DIR)
            f.write(f"file '{rel_path.as_posix()}'\n")

    narration_only = RENDERS_DIR / "narration_only.mp3"
    cmd_concat = [
        "ffmpeg", "-y",
        "-f", "concat",
        "-safe", "0",
        "-i", str(list_file),
        "-c", "copy",
        str(narration_only)
    ]
    run_cmd(cmd_concat)
    
    # 刪除暫存 list.txt
    if list_file.exists():
        list_file.unlink()

    print("\n=== Step 3: 下載/準備背景音樂 BGM ===")
    bgm_file = AUDIO_DIR / "bgm.mp3"
    if not bgm_file.exists():
        bgm_url = "https://www.soundhelix.com/examples/mp3/SoundHelix-Song-8.mp3"
        print(f"下載 Sample BGM: {bgm_url}...")
        headers = {'User-Agent': 'Mozilla/5.0'}
        req = urllib.request.Request(bgm_url, headers=headers)
        with urllib.request.urlopen(req) as response:
            bgm_file.write_bytes(response.read())
        print("BGM 下載完成！")
    else:
        print("BGM 已存在。")

    print("\n=== Step 4: 混音 (BGM + 旁白) ===")
    master_audio = RENDERS_DIR / "master_audio.mp3"
    # [1:a]volume=0.12 將背景音樂降低音量，amix 將兩路音訊合併並以第一輸入(旁白)時長為準
    cmd_mix = [
        "ffmpeg", "-y",
        "-i", str(narration_only),
        "-i", str(bgm_file),
        "-filter_complex", "[1:a]volume=0.12[bg];[0:a][bg]amix=inputs=2:duration=first:dropout_transition=2",
        "-c:a", "libmp3lame",
        "-b:a", "192k",
        str(master_audio)
    ]
    run_cmd(cmd_mix)

    print("\n=== Step 5: 執行 Playwright 進行網頁錄影 ===")
    # 執行 record.cjs
    run_cmd(["node", "record.cjs"], cwd=str(BASE_DIR))

    print("\n=== Step 6: FFmpeg 進行音視訊合併 (Mux) ===")
    # 搜尋 renders 目錄中的 webm 影片檔案 (Playwright 命名通常為隨機)
    webm_files = list(RENDERS_DIR.glob("*.webm"))
    if not webm_files:
        print("Error: 找不到錄製的 WebM 檔案！")
        sys.exit(1)
    
    # 選擇最新修改的 webm 檔案
    latest_webm = max(webm_files, key=lambda f: f.stat().st_mtime)
    print(f"最新錄製 WebM 影片: {latest_webm}")

    final_output = BASE_DIR / "water_movement.mp4"
    # -map 0:v:0 -map 1:a:0 精確對齊無聲 webm 的視訊軌與混音 mp3 的音訊軌
    cmd_mux = [
        "ffmpeg", "-y",
        "-i", str(latest_webm),
        "-i", str(master_audio),
        "-map", "0:v:0",
        "-map", "1:a:0",
        "-c:v", "libx264",
        "-crf", "20",
        "-pix_fmt", "yuv420p",
        "-c:a", "aac",
        "-b:a", "192k",
        "-shortest",
        str(final_output)
    ]
    run_cmd(cmd_mux)
    print(f"\n✅ 影片製作完成！最終檔案已輸出至: {final_output}")

if __name__ == "__main__":
    main()
