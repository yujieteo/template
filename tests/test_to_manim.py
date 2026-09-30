import json

import to_manim


def script(*narrations):
    return {"voice": "bf_emma", "scenes": [{"id": f"s{k:02d}", "title": f"Frame {k}", "narration": n}
                                           for k, n in enumerate(narrations, start=1)]}


def test_narration_falls_back_to_the_section_or_the_title():
    assert to_manim.narration_for({"narration": "Said.", "kind": "frame", "title": "T"}) == ("Said.", True)
    section = {"narration": "", "kind": "section", "section_number": 2, "title": "Evidence"}
    assert to_manim.narration_for(section) == ("Part 2. Evidence.", True)
    assert to_manim.narration_for({"narration": "", "kind": "frame", "title": "A finding."}) == ("A finding.", False)


def test_iso_date_reads_the_formats_a_talk_uses():
    assert to_manim.iso_date("1 October 2026") == "2026-10-01"
    assert to_manim.iso_date("October 1, 2026") == "2026-10-01"
    assert to_manim.iso_date("Autumn") == ""


def test_estimated_timeline_is_contiguous_and_one_caption_per_sentence():
    timings = to_manim.estimate_timings(script("One two three. Four five.", "Six seven eight nine ten."))
    first, second = timings["scenes"]
    assert [c["text"] for c in first["captions"]] == ["One two three.", "Four five."]
    assert first["audio_start"] == to_manim.LEAD
    assert first["window_start"] == 0.0
    assert first["window_end"] == second["window_start"] == second["audio_start"]
    assert second["audio_start"] == round(first["audio_end"] + to_manim.GAP, 3)
    assert timings["total_seconds"] == second["window_end"] == round(second["audio_end"] + to_manim.TAIL, 3)
    assert all(c["end"] - c["start"] >= 1.2 for s in timings["scenes"] for c in s["captions"])


def test_srt_numbers_captions_and_formats_times():
    timings = {"scenes": [{"captions": [{"start": 0.5, "end": 3661.25, "text": "Hello."}]}]}
    assert to_manim.srt(timings) == "1\n00:00:00,500 --> 01:01:01,250\nHello.\n"


def test_ass_colour_is_alpha_blue_green_red():
    assert to_manim.ass_colour("#112233", alpha=0x80) == "&H80332211"


def test_stale_narration_with_a_different_scene_count_falls_back_to_the_estimate(tmp_path):
    kokoro = {"voice": "bf_emma", "total_seconds": 2.0,
              "scenes": [{"id": "s01", "captions": [{"start": 0, "end": 1, "text": "One two three."}]}]}
    (tmp_path / "timings.json").write_text(json.dumps(kokoro))
    (tmp_path / "narration.wav").write_bytes(b"")
    timings, audio = to_manim.choose_timings(tmp_path, script("One two three.", "Added frame."))
    assert audio is None
    assert timings["voice"] == "estimate"
    assert len(timings["scenes"]) == 2


def test_matching_narration_keeps_the_kokoro_timeline(tmp_path):
    kokoro = {"voice": "bf_emma", "total_seconds": 2.0,
              "scenes": [{"id": "s01", "captions": [{"start": 0, "end": 1, "text": "One two three."}]}]}
    (tmp_path / "timings.json").write_text(json.dumps(kokoro))
    (tmp_path / "narration.wav").write_bytes(b"")
    timings, audio = to_manim.choose_timings(tmp_path, script("One two three."))
    assert audio == tmp_path / "narration.wav"
    assert timings == kokoro
