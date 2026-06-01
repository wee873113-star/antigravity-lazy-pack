import asyncio, edge_tts
from pathlib import Path

OUT = Path(__file__).parent / "assets" / "narration"
OUT.mkdir(parents=True, exist_ok=True)

VOICE = "zh-TW-YunJheNeural"
RATE = "-5%"
PITCH = "-2Hz"

SCRIPT = [
    (1, "懷著對棒球的憧憬，你第一次踏上了這片紅土球場。"),
    (2, "無數次的揮棒與奔跑，汗水濕透了衣背，這是新人的起步。"),
    (3, "終於迎來了第一次上場的機會，心跳如鼓，雙手緊握球棒。"),
    (4, "然而，命運開了個玩笑。一次意外的跌倒，讓你與勝利擦身而過。"),
    (5, "拍拍身上的泥土。你沒有哭泣，只是在無人的球場上練得更勤。"),
    (6, "失敗化作了養分。漸漸地，你的球技更加犀利，眼神也變得更加堅定。"),
    (7, "第二次大型正式比賽，當哨音響起，這一次，你不再猶豫。"),
    (8, "隨著一記清脆的擊球聲，首勝到手！全場的歡呼屬於堅持到底的你。"),
    (9, "這只是個開始。抬起頭，甲子園的金色大門，正緩緩為你們開啟。")
]

async def synth(i, text):
    out = OUT / f"page-{i:02d}.mp3"
    c = edge_tts.Communicate(text, VOICE, rate=RATE, pitch=PITCH)
    await c.save(str(out))
    print(f"OK page-{i:02d}.mp3")

async def main():
    for i, t in SCRIPT:
        for r in range(3):
            try:
                await synth(i, t)
                break
            except Exception as e:
                print(f"retry {i} ({r+1}): {e}")
                await asyncio.sleep(2)
    print("All done.")

if __name__ == "__main__":
    asyncio.run(main())
