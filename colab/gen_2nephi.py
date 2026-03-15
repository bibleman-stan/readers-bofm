"""Generate 2 Nephi chapters 1-5 with Samuel voice (test batch)."""
import os, json, time
from pathlib import Path

BOOK_ID = "2nephi"
BOOK_NAME = "2 Nephi"
TOTAL_CHAPTERS = 5
SAMUEL_VOICE_ID = "ddDFRErfhdc2asyySOG5"

OUT_DIR = Path("audio")
OUT_DIR.mkdir(exist_ok=True)
results = []

for ch in range(1, TOTAL_CHAPTERS + 1):
    print("=== " + BOOK_NAME + " Chapter " + str(ch) + " ===")

    # parse_chapter returns a single list of items
    items = parse_chapter("books/" + BOOK_ID + ".html", BOOK_ID, ch)
    speakable = [i for i in items if i.get("type") == "line"]
    print("  Lines: " + str(len(speakable)))

    # stitch_chapter handles TTS + caching + stitching internally
    # Returns (AudioSegment, timing_list, stats_dict)
    combined, timing, stats = stitch_chapter(
        items, voice_id=SAMUEL_VOICE_ID
    )

    # Export MP3
    mp3_path = "audio/" + BOOK_ID + "-" + str(ch) + "-samuel.mp3"
    json_path = "audio/" + BOOK_ID + "-" + str(ch) + "-samuel.json"
    combined.export(mp3_path, format="mp3")
    duration_s = len(combined) / 1000.0
    file_size = os.path.getsize(mp3_path)

    # Write timing manifest
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
    gen_str = str(stats["generated"])
    cache_str = str(stats["cached"])
    chars_str = str(stats["chars_used"])
    print("  Cache: " + cache_str + ", New: " + gen_str + " (" + chars_str + " chars)")

print("")
print("DONE - " + str(TOTAL_CHAPTERS) + " chapters")
total_chars = 0
for r in results:
    ch_str = str(r["ch"])
    lines_str = str(r["lines"])
    dur_str = str(round(r["duration"], 1))
    print("  Ch" + ch_str + ": " + lines_str + " lines, " + dur_str + "s")
    total_chars = total_chars + r["chars_used"]
print("  Total new chars: " + str(total_chars))
