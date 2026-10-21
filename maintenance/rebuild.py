"""Compose the five reading sections and rebuild all current reading pages."""
from pathlib import Path
import json,subprocess,sys

root=Path(__file__).resolve().parents[1]
config=json.loads((root/'maintenance/catalog.json').read_text(encoding='utf-8'))
subprocess.run([sys.executable,str(root/'maintenance/build_sections.py')],check=True)
subprocess.run([sys.executable,str(root/'maintenance/update_document_navigation.py')],check=True)
subprocess.run([sys.executable,str(root/'maintenance/sync_questions.py')],check=True)
for item in config['documents']:
    subprocess.run([sys.executable,str(root/'maintenance/build_handbook.py'),str(root/item['file'])],check=True)
subprocess.run([sys.executable,str(root/'maintenance/build_portal.py')],check=True)
subprocess.run([sys.executable,str(root/'maintenance/render_summary.py')],check=True)
subprocess.run([sys.executable,str(root/'maintenance/validate.py')],check=True)
