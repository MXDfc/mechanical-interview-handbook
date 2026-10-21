"""Compose five reading volumes from source blocks without rewriting questions."""
from pathlib import Path
import json,re,hashlib
from site_common import ROOT,catalog

QUESTION=re.compile(r'(^### (Q\d{3})[^\n]*\n.*?)(?=^### |^## |\Z)',re.M|re.S)
SECTION=re.compile(r'^## ([^\n]+)\n(.*?)(?=^## |\Z)',re.M|re.S)
SUBSECTION=re.compile(r'(^### ([^\n]+)\n.*?)(?=^### |\Z)',re.M|re.S)

def main():
    cfg=catalog();org=json.loads((ROOT/cfg['organization']).read_text(encoding='utf-8'))
    text=(ROOT/cfg['master']).read_text(encoding='utf-8')
    text=re.sub(r'<!-- (NAV|VERSIONS)_START -->.*?<!-- \1_END -->','',text,flags=re.S)
    questions={m[2]:m[1].strip() for m in QUESTION.finditer(text)}
    sections={m[1]:m[2].strip() for m in SECTION.finditer(text)}
    source_usage=[]
    def support(spec):
        matches=[(title,body) for title,body in sections.items() if title==spec['section'] or title.startswith(spec['section']+'. ')]
        if len(matches)!=1:raise ValueError(('source section',spec,matches))
        title,body=matches[0]
        blocks=list(SUBSECTION.finditer(body+'\n'))
        if 'subsection' in spec:
            found=[m for m in blocks if m[2].startswith(spec['subsection']) and not re.match(r'Q\d{3}',m[2])]
            if len(found)!=1:raise ValueError(('source subsection',spec))
            result=found[0][1].strip()
        else:
            # Section lead text and each non-question subsection remain verbatim.
            chunks=[body[:blocks[0].start()].strip()] if blocks else [body]
            chunks += [m[1].strip() for m in blocks if not re.match(r'Q\d{3}',m[2]) and m[2] not in spec.get('exclude',[])]
            result='\n\n'.join(c for c in chunks if c)
        source_usage.append({'source':spec,'sha256':hashlib.sha256(result.encode()).hexdigest()})
        # Keep prose outside the preceding question's immutable block.
        return result if result.startswith('### ') else '### '+title+'\n\n'+result
    for category in org['categories']+org.get('topics',[]):
        n=len(category['question_ids'])
        out=[f"# {category['title']}",'',f"**机械结构工程师线上面试学习资料｜{n}题｜{cfg['current_version']}**",'',category['description'],'',
             '按目录选择主题；每题先读口头首答，再按需展开依据、算例与操作。','',
             '[五板块总索引](index.html) · [完整主手册](机械结构工程师面试与知识强化手册.html)','']
        if category.get('preamble'):
            out += [category['preamble'],'']
        for g in category['groups']:
            out += [f"## {g['code']}. {g['title']}",'']
            if g['links']:
                out += ['关联速查：'+' · '.join(f"[{x['label']}]({x['file']}#{x['anchor']})" for x in g['links']),'']
            out += [questions[q]+'\n' for q in g['question_ids']]
            out += [support(spec)+'\n' for spec in g['support']]
        content='\n'.join(out).rstrip()+'\n'
        matches=list(QUESTION.finditer(content))
        if matches and matches[-1].end()==len(content):
            # Keep the generated version marker outside a final question block.
            content+='\n### 继续阅读\n\n[五板块总索引](index.html) · [完整主手册](机械结构工程师面试与知识强化手册.html)\n'
        actual={m[2]:m[1].strip() for m in QUESTION.finditer(content)}
        assert set(actual)==set(category['question_ids'])
        assert all(value==questions[key] for key,value in actual.items()),category['id']
        (ROOT/category['file']).write_text(content,encoding='utf-8')
        print('Composed:',category['file'],n,'unchanged questions')
    (ROOT/'maintenance/section-sources.json').write_text(json.dumps(source_usage,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')

if __name__=='__main__':main()
