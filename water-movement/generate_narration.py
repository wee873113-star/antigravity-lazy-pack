import asyncio, edge_tts
from pathlib import Path

OUT = Path(__file__).parent / "assets" / "narration"
OUT.mkdir(parents=True, exist_ok=True)

VOICE = "zh-TW-YunJheNeural"
RATE = "-8%"
PITCH = "-2Hz"

SCRIPT = [
    (1,  "小朋友，你有沒有想過，水沒有腳，為什麼能自己往高處爬，還會像坐雲霄飛車一樣，自動流出來呢？"),
    (2,  "這可不是魔法，而是水寶寶的三個神奇超能力！今天就帶你一起來拆解它們吧！"),
    (3,  "第一個超能力叫「毛細現象」。當水遇到很細很細的縫隙時，水分子會手拉手，自動沿著縫隙往上爬！"),
    (4,  "就像我們用抹布擦水，或者植物從泥土裡吸水一樣，細小的管子或縫隙越窄，水寶寶就爬得越高！"),
    (5,  "第二個超能力叫「連通管原理」。只要底下連在一起，不管管子長得多粗、多細或多奇怪，水面都會一樣高！"),
    (6,  "就像倒茶的時候，茶壺嘴的水面和茶壺裡的水面永遠是平的。大樓的水塔也是用這個原理，把水送到各個家裡喔！"),
    (7,  "第三個超能力叫「虹吸現象」。水寶寶可以用一條水管，像火車一樣手牽手，越過高山流到更低的地方！"),
    (8,  "只要管子裡先裝滿水，低處管口的重力就會把水往下扯，就像拉隱形的鎖鏈一樣，把高處的水源源不絕地拉過來！"),
    (9,  "這三種超能力，可不是只在實驗室裡有喔，在我們的生活周遭，它們天天都在熱心幫忙呢！"),
    (10, "像是植物用毛細現象喝水、大樓用連通管原理把水送上樓，還有幫魚缸換水時的虹吸現象，都是多虧了它們呢！"),
    (11, "水看起來很平凡，但它的移動卻充滿了大自然的魔法！下次洗手或喝水時，記得睜大眼睛觀察一下它們喔！"),
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
