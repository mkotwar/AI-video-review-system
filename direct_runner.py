import sys
import traceback
import builtins

with open("c:/Mukul K/vinfo1/video-search-engine/error_log.txt", "w", encoding="utf-8") as f:
    builtins.print = lambda *args, **kwargs: f.write(" ".join(map(str, args)) + "\n")
    try:
        from regenerate_pipeline import regenerate
        regenerate()
    except Exception as e:
        f.write(traceback.format_exc())
