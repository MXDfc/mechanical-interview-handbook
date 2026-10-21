"""Shared metadata and stable anchors for the offline handbook site."""
from pathlib import Path
import json,re,html,sys

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'maintenance/vendor'))
import markdown

def catalog():
    return json.loads((ROOT/'maintenance/catalog.json').read_text(encoding='utf-8'))

def heading_id(title,index):
    if title=='版本记录':return 'version-history'
    if title=='阅读导航':return 'reading-guide'
    code=re.match(r'^([A-Z]\d*)\.',title)
    if code:return 'chapter-'+code.group(1).lower()
    fixed={'使用说明与考核尺度':'usage','材料映射：哪些内容值得重点问':'evidence-map',
           '理论力学基础：10道题':'theory-basics','仿真、测试与可靠性基础：18道题':'simulation-basics'}
    return fixed.get(title,f'section-{index:02}')

def headings(text):
    return [(m.group(1),heading_id(m.group(1),i)) for i,m in enumerate(re.finditer(r'^## (.+)$',text,re.M),1)]

def render(text):
    rendered=markdown.markdown(text,extensions=['extra','toc','sane_lists'])
    ids=iter([i for _,i in headings(text)])
    return re.sub(r'<h2 id="[^"]*">',lambda m:f'<h2 id="{next(ids)}">',rendered)

def document_for(filename):
    return next(d for d in catalog()['documents'] if d['file']==filename)

def html_name(document):
    return str(Path(document['file']).with_suffix('.html'))

def doc_link(document,fragment=''):
    return html.escape(html_name(document)+('#'+fragment if fragment else ''),quote=True)
