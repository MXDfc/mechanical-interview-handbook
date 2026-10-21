"""Read-only checks of membership, oral answers, shared text, and local HTML links."""
from pathlib import Path
from html.parser import HTMLParser
from urllib.parse import unquote, urlsplit
import json, re, hashlib

ROOT=Path(__file__).resolve().parents[1]
PATTERN=re.compile(r'(^### (Q\d{3})[^\n]*\n.*?)(?=^### |^## |\Z)',re.M|re.S)

class Page(HTMLParser):
    def __init__(self):
        super().__init__();self.ids=[];self.links=[];self.oral=0
    def handle_starttag(self,tag,attrs):
        a=dict(attrs)
        if 'id' in a:self.ids.append(a['id'])
        if tag=='a' and 'href' in a:self.links.append(a['href'])
        if 'oral-answer' in a.get('class','').split():self.oral+=1

def main():
    config=json.loads((ROOT/'maintenance/catalog.json').read_text(encoding='utf-8'))
    errors=[];report=[];pages={}
    master=(ROOT/config['master']).read_text(encoding='utf-8')
    master_blocks={m.group(2):m.group(1).strip() for m in PATTERN.finditer(master)}
    preservation={}
    if config.get('current_version') in ('v2.7.1','v2.7.2'):
        baseline_name={'v2.7.1':'q555-refinement-baseline.json','v2.7.2':'publication-baseline.json'}[config['current_version']]
        baseline=json.loads((ROOT/'maintenance'/baseline_name).read_text(encoding='utf-8'))
        current_hashes={key:hashlib.sha256(value.encode('utf-8')).hexdigest() for key,value in master_blocks.items()}
        original=baseline['original_questions']
        preservation={'unchanged':sum(current_hashes.get(k)==v for k,v in original.items()),
                      'added':sorted(set(current_hashes)-set(original)),
                      'removed':sorted(set(original)-set(current_hashes)),
                      'modified':sorted(k for k,v in original.items() if k in current_hashes and current_hashes[k]!=v)}
        if preservation['added'] or preservation['removed'] or set(preservation['modified'])!=set(baseline['expected_modified']):errors.append('Question refinement differs from authorized scope')
    elif config.get('current_version')=='v2.2':
        baseline=json.loads((ROOT/'maintenance/reorganization-baseline.json').read_text(encoding='utf-8'))
        current_hashes={key:hashlib.sha256(value.encode('utf-8')).hexdigest() for key,value in master_blocks.items()}
        preservation={'unchanged':sum(current_hashes.get(k)==v for k,v in baseline['questions'].items()),
                      'added':sorted(set(current_hashes)-set(baseline['questions'])),
                      'removed':sorted(set(baseline['questions'])-set(current_hashes)),
                      'modified':sorted(k for k,v in baseline['questions'].items() if k in current_hashes and current_hashes[k]!=v)}
        if preservation['added'] or preservation['removed'] or preservation['modified']:errors.append('Reorganization changed question content')
    elif config.get('current_version') in ('v2.3','v2.4','v2.5','v2.6','v2.7'):
        baseline_name={'v2.3':'theory-expansion-baseline.json','v2.4':'tolerance-expansion-baseline.json','v2.5':'bearing-expansion-baseline.json','v2.6':'angular-expansion-baseline.json','v2.7':'motor-expansion-baseline.json'}[config['current_version']]
        baseline=json.loads((ROOT/'maintenance'/baseline_name).read_text(encoding='utf-8'))
        current_hashes={key:hashlib.sha256(value.encode('utf-8')).hexdigest() for key,value in master_blocks.items()}
        original=baseline['original_questions']
        preservation={'unchanged':sum(current_hashes.get(k)==v for k,v in original.items()),
                      'added':sorted(set(current_hashes)-set(original)),
                      'removed':sorted(set(original)-set(current_hashes)),
                      'modified':sorted(k for k,v in original.items() if k in current_hashes and current_hashes[k]!=v)}
        if preservation['removed'] or preservation['modified'] or set(preservation['added'])!=set(baseline['expected_added']):errors.append('Content expansion differs from authorized addition')
    org=json.loads((ROOT/config['organization']).read_text(encoding='utf-8'))
    categorized=[q for c in org['categories'] for g in c['groups'] for q in g['question_ids']]
    if len(org['categories'])!=5 or len(categorized)!=len(set(categorized)) or set(categorized)!=set(master_blocks):errors.append('Five categories must partition the question bank')
    if [g['title'] for g in org['categories'][0]['groups']]!=['理论力学','材料力学','机械原理','机械设计']:errors.append('Theory must have four subjects')
    for item in config['documents']:
        path=ROOT/item['file'];text=path.read_text(encoding='utf-8')
        matches=list(PATTERN.finditer(text));ids=[m.group(2) for m in matches]
        if len(ids)!=len(set(ids)):errors.append(path.name+': duplicate IDs')
        if set(ids)!=set(item['question_ids']):errors.append(path.name+': membership differs from catalog')
        if text.count('**口头首答（约30～60秒）**')!=len(ids):errors.append(path.name+': oral answer count mismatch')
        if '\ufffd' in text:errors.append(path.name+': replacement characters')
        if not re.search(r'## 版本记录\n.*<!-- VERSIONS_END -->\s*\Z',text,re.S):errors.append(path.name+': version table must be last')
        content=text.split('<!-- VERSIONS_START -->')[0]
        if re.search(r'本轮|本次新增|本次扩展|本组原有|原48题|原86题|已移入|已移至|已归入|本轮新增',content):errors.append(path.name+': editorial history leaked into content')
        for m in matches:
            if m.group(1).strip()!=master_blocks.get(m.group(2)):errors.append(path.name+': shared question differs '+m.group(2))
        hpath=path.with_suffix('.html');page=Page();page.feed(hpath.read_text(encoding='utf-8'));pages[hpath.resolve()]=page
        html_ids=[i for i in page.ids if re.fullmatch(r'Q\d{3}',i)]
        if set(html_ids)!=set(ids) or len(html_ids)!=len(ids):errors.append(path.name+': HTML question mismatch')
        if page.oral!=len(ids):errors.append(path.name+': HTML oral answer mismatch')
        if len(page.ids)!=len(set(page.ids)):errors.append(path.name+': duplicate HTML anchors')
        if item.get('kind') in ('source','legacy'):
            owns_balance=item.get('owns_balance',False)
            if any((f'Q{i:03}' in ids)!=owns_balance for i in range(303,317)):errors.append(path.name+': legacy balance ownership mismatch')
            if owns_balance and not (text.index('## B4.')<text.index('### Q303')<text.index('## B5.')):errors.append(path.name+': incorrect legacy B4/B5 placement')
        report.append({'file':path.name,'questions':len(ids),'checklist_items':len(re.findall(r'^- \[ \]',text,re.M))})
    for name in ['index.html','00-工作总结与编辑交接.html']:
        path=ROOT/name
        if not path.exists():errors.append('Missing '+name);continue
        page=Page();page.feed(path.read_text(encoding='utf-8'));pages[path.resolve()]=page
    index=json.loads((ROOT/'maintenance/search-index.json').read_text(encoding='utf-8'))
    indexids=[q['id'] for q in index['questions']]
    if set(indexids)!=set(master_blocks) or len(indexids)!=len(set(indexids)):errors.append('Portal search index must deduplicate all master questions')
    for q in index['questions']:
        owners={d['id'] for d in config['documents'] if q['id'] in d['question_ids']}
        if owners!=set(q['documents']) or q['preferred'] not in owners:errors.append('Portal membership mismatch: '+q['id'])
        primary=[c['id'] for c in org['categories'] if q['id'] in c['question_ids']]
        if primary!=[q['preferred']]:errors.append('Portal primary category mismatch: '+q['id'])
    for hpath,page in pages.items():
        for href in page.links:
            u=urlsplit(href)
            if u.scheme or u.netloc:continue
            target=(hpath.parent/unquote(u.path)).resolve() if u.path else hpath
            if not target.exists():errors.append(f'{hpath.name}: missing {href}');continue
            if u.fragment and target in pages and unquote(u.fragment) not in pages[target].ids:errors.append(f'{hpath.name}: broken anchor {href}')
    result={'documents':report,'preservation':preservation,'category_count':len(org['categories']),'errors':errors}
    (ROOT/'maintenance/last-validation.json').write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding='utf-8')
    print(json.dumps(result,ensure_ascii=False,indent=2))
    if errors:raise SystemExit(1)

if __name__=='__main__':main()
