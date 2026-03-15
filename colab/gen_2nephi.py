"""Generate 2 Nephi chapters 1-5 with Samuel voice (test batch)."""
import os, json, hashlib, time
from pathlib import Path

BOOK_ID = "2nephi"
BOOK_NAME = "2 Nephi"
TOTAL_CHAPTERS = 5
SAMUEL_VOICE_ID = "ddDFRErfhdc2asyySOG5"

Path("audio").mkdir(exist_ok=True)
results = []

for ch in range(1, TOTAL_CHAPTERS + 1):
    print("=== " + BOOK_NAME + " Chapter " + str(ch) + " ===")
    lines, timing = parse_chapter("books/" + BOOK_ID + ".html", BOOK_ID, ch)
    speakable = [l for l in lines if l.get("text", "").strip()]
    print("  Lines: " + str(len(speakable)))
    audio_segments = []
    stats = {"cached": 0, "generated": 0, "chars_used": 0}
    for i, line_item in enumerate(speakable):
        txt = line_item["text"].strip()
        cache_key = hashlib.sha256(
            (txt + "|" + SAMUEL_VOICE_ID + "|" + MODEL_ID + "|" + str(VOICE_SETTINGS)).encode()
        ).hexdigest()[:16]
        cache_path = Path("cache") / (cache_key + ".mp3")
        if cache_path.exists():
            audio_segments.append(str(cache_path))
            stats["cached"] += 1
        else:
            audio_data = call_elevenlabs(txt, SAMUEL_VOICE_ID)
            cache_path.parent.mkdir(exist_ok=True)
            with open(cache_path, "wb") as f:
                f.write(audio_data)
            audio_segments.append(str(cache_path))
            stats["generated"] += 1
            stats["chars_used"] += len(txt)
            time.sleep(0.3)
        if (i + 1) % 10 == 0:
            pct = str(i + 1) + "/" + str(len(speakable))
            print("    " + pct + " lines done")

    mp3_path = "audio/" + BOOK_ID + "-" + str(ch) + "-samuel.mp3"
    json_path = "audio/" + BOOK_ID + "-" + str(ch) + "-samuel.json"
    duration_s = stitch_chapter(audio_segments, speakable, mp3_path)
    file_size = os.path.getsize(mp3_path)

    manifest = {
        "book": BOOK_ID,
        "chapter": ch,
        "voice": {
            "provider": "elevenlabs",
            "voice_id": SAMUEL_VOICE_ID,
            "model_id": MODEL_ID,
            "settings": VOICE_SETTINGS,
            "name": "Samuel",
        },
        "pauses": {"line_ms": LINE_PAUSE_MS, "verse_ms": VERSE_PAUSE_MS},
        "duration": round(duration_s, 3),
        "lines": timing,
    }
    with open(json_path, "w") as f:
        json.dump(manifest, f, indent=2)

    results.append({
        "ch": ch,
        "lines": len(speakable),
        "duration": duration_s,
        "size_kb": file_size / 1024,
        "cached": stats["cached"],
        "generated": stats["generated"],
        "chars_used": stats["chars_used"],
    })
    dur_str = str(round(duration_s, 1))
    size_str = str(round(file_size / 1024))
    print("  MP3: " + dur_str + "s, " + size_str + "KB")
    print("  Cache: " + str(stats["cached"]) + ", New: " + str(stats["generated"]))

print("")
print("DONE - " + str(TOTAL_CHAPTERS) + " chapters")
for r in results:
    ch_str = str(r["ch"])
    lines_str = str(r["lines"])
    dur_str = str(round(r["duration"], 1))
    print("  Ch" + ch_str + ": " + lines_str + " lines, " + dur_str + "s")
