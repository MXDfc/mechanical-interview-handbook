"""Build the current five-section portal."""
import runpy
from pathlib import Path
runpy.run_path(str(Path(__file__).with_name("build_five_portal.py")),run_name="__main__")
