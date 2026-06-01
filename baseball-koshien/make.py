import os
import subprocess
import urllib.request
from pathlib import Path

# 定義路徑
BASE_DIR = Path(__file__).parent
ASSETS_DIR = BASE_DIR / "assets"
NARRATION_DIR = ASSETS_DIR / "narration"
AUDIO_DIR = ASSETS_DIR / "audio"
RENDERS_DIR = BASE_DIR / "renders"

# 確保目錄存在
AUDIO_DIR.mkdir(parents=True, exist_ok=True)
RENDERS_DIR.mkdir(parents=True, exist_ok=True)

# 投影片目標時長 (每頁固定 5.0 秒，總長 45.0 秒)
DURATIONS = [5.0] * 9
TOTAL_DURATION = sum(DURATIONS)

def download_bgm():
    bgm_url = "https://www.soundhelix.com/examples/mp3/SoundHelix-Song-4.mp3"
    bgm_path = AUDIO_DIR / "bgm.mp3"
    if not bgm_path.exists():
        print("Downloading BGM from SoundHelix...")
        try:
            urllib.request.urlretrieve(bgm_url, bgm_path)
            print("BGM downloaded successfully.")
        except Exception as e:
            print(f"Error downloading BGM: {e}")
            raise
    else:
        print("BGM already exists.")
    return bgm_path

def process_audio():
    print("Padding and concatenating narration audio files...")
    
    # 1. 產生每個音檔的 Padded 版本
    padded_files = []
    for idx, target_dur in enumerate(DURATIONS, 1):
        filename = f"page-{idx:02d}.mp3"
        input_path = NARRATION_DIR / filename
        padded_path = NARRATION_DIR / f"padded-{idx:02d}.mp3"
        
        if not input_path.exists():
            raise FileNotFoundError(f"Missing narration file: {input_path}")
            
        print(f"Padding {filename} to {target_dur}s...")
        cmd = [
            "ffmpeg", "-y",
            "-i", str(input_path),
            "-af", "apad",
            "-t", str(target_dur),
            str(padded_path)
        ]
        subprocess.run(cmd, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        padded_files.append(padded_path)

    # 2. 建立 concat.txt 列表
    concat_txt_path = BASE_DIR / "concat.txt"
    with open(concat_txt_path, "w", encoding="utf-8") as f:
        for file in padded_files:
            rel_path = file.relative_to(BASE_DIR).as_posix()
            f.write(f"file '{rel_path}'\n")

    # 3. 合併為完整的旁白音軌
    narration_full = RENDERS_DIR / "narration_full.mp3"
    print("Concatenating padded audio tracks...")
    cmd = [
        "ffmpeg", "-y",
        "-f", "concat",
        "-safe", "0",
        "-i", str(concat_txt_path),
        "-c", "copy",
        str(narration_full)
    ]
    subprocess.run(cmd, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

    # 清理暫時的 padded 檔案與 concat.txt
    concat_txt_path.unlink()
    for file in padded_files:
        file.unlink()

    return narration_full

def mix_audio(narration_path, bgm_path):
    print("Mixing narration, BGM, and user custom sound effect 09.mp3...")
    mixed_audio = RENDERS_DIR / "mixed_audio.mp3"
    sfx_path = AUDIO_DIR / "09.mp3"
    
    if not sfx_path.exists():
        raise FileNotFoundError(f"Custom sound effect not found: {sfx_path}")
        
    # 音訊軌對比：
    # [0:a] 主旁白音訊軌 (0-45s)
    # [1:a] 背景音樂 BGM (volume=0.06)
    # [2:a] 專屬音效 09.mp3 (volume=0.25, 並且延遲 15 秒播放，即 15000 毫秒)
    # amix 混合三軌，長度隨第一軌（旁白）結束
    cmd = [
        "ffmpeg", "-y",
        "-i", str(narration_path),
        "-i", str(bgm_path),
        "-i", str(sfx_path),
        "-filter_complex", "[1:a]volume=0.06[bg];[2:a]volume=0.25,adelay=15000|15000[sfx];[0:a][bg][sfx]amix=inputs=3:duration=first[a]",
        "-map", "[a]",
        str(mixed_audio)
    ]
    subprocess.run(cmd, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    return mixed_audio

def record_video():
    print("Executing Playwright script to record video...")
    env = os.environ.copy()
    temp_node_path = Path(os.environ["TEMP"]) / "cvs-render" / "node_modules"
    env["NODE_PATH"] = str(temp_node_path)
    
    # 執行 record.cjs
    cmd = ["node", "record.cjs"]
    subprocess.run(cmd, env=env, check=True)
    
    raw_video = RENDERS_DIR / "raw_recording.webm"
    if not raw_video.exists():
        raise FileNotFoundError("Video recording failed: raw_recording.webm not found.")
    return raw_video

def mux_video_audio(video_path, audio_path):
    print("Muxing final video and audio tracks...")
    final_output = RENDERS_DIR / "baseball_koshien.mp4"
    
    # Mux WebM 影像軌與 MP3 混音軌，限制輸出時長為 TOTAL_DURATION (45.0s)
    cmd = [
        "ffmpeg", "-y",
        "-i", str(video_path),
        "-i", str(audio_path),
        "-map", "0:v:0",
        "-map", "1:a:0",
        "-c:v", "libx264",
        "-pix_fmt", "yuv420p",
        "-t", str(TOTAL_DURATION),
        str(final_output)
    ]
    subprocess.run(cmd, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    print(f"Build complete! Final output saved to: {final_output}")

def main():
    try:
        bgm_path = download_bgm()
        narration_path = process_audio()
        mixed_audio = mix_audio(narration_path, bgm_path)
        raw_video = record_video()
        mux_video_audio(raw_video, mixed_audio)
        
        # 移除中間暫存檔以保持目錄整潔
        if narration_path.exists(): narration_path.unlink()
        if mixed_audio.exists(): mixed_audio.unlink()
        if raw_video.exists(): raw_video.unlink()
        print("Temporary files cleaned up.")
    except Exception as e:
        print(f"Error in make.py build process: {e}")
        raise

if __name__ == "__main__":
    main()
