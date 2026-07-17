# Copied into .venv/Lib/site-packages/ by tools/bootstrap.py.
# Forces UTF-8 stdio so the pipeline's helper tools don't crash on Windows cp1252
# consoles (emoji, smart quotes, box-drawing in output). Recreate if the venv is rebuilt.
import sys

for _s in (sys.stdout, sys.stderr):
    try:
        _s.reconfigure(encoding="utf-8")
    except Exception:
        pass
