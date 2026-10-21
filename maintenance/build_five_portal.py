"""Build the five-section entry with a dedicated index for each category."""
import json,re,html
from site_common import ROOT,catalog,headings,html_name

cfg=catalog();docs=sorted(cfg['documents'],key=lambda d:d['order'])
org=json.loads((ROOT/cfg['organization']).read_text(encoding='utf-8'))
master=(ROOT/cfg['master']).read_text(encoding='utf-8')
blocks=re.compile(r'(^### (Q\d{3})｜([^\n]+)\n.*?)(?=^### |^## |\Z)',re.M|re.S)
owners={q:(c,g) for c in org['categories'] for g in c['groups'] for q in g['question_ids']}
def plain(s):
    s=re.sub(r'\[([^\]]+)\]\([^)]+\)',r'\1',s)
    return re.sub(r'[*`#_>]', '',s).strip()
questions=[]
for m in blocks.finditer(master):
    raw,key,title=m.groups();category,group=owners[key]
    oral=re.search(r'\*\*口头首答（约30～60秒）\*\*：([^\n]+)',raw)[1]
    questions.append({'id':key,'title':re.sub(r'【P\d】','',title).strip(),'priority':re.search(r'【(P\d)】',title)[1],
                      'topic':category['title'],'category':category['id'],'subject':group['title'] if category['id']=='knowledge' else '',
                      'section':group['title'],'oral':plain(oral),'search':plain(raw),'documents':[d['id'] for d in docs if key in d['question_ids']],
                      'preferred':category['id']})
expected_total=len(next(d for d in docs if d['id']=='master')['question_ids'])
assert len(questions)==len({q['id'] for q in questions})==len(owners)==expected_total
questions.sort(key=lambda q:q['id'])
data_docs=[]
for d in docs:
    content=(ROOT/d['file']).read_text(encoding='utf-8')
    data_docs.append({**{k:d[k] for k in ['id','label','title','description','scope','kind']},'file':html_name(d),'source':d['file'],'count':len(d['question_ids']),
                      'chapters':[{'title':title,'anchor':anchor} for title,anchor in headings(content) if title not in ['阅读导航','版本记录']]})
categories=[{'id':c['id'],'title':c['title'],'groups':[{'title':g['title'],'anchor':'chapter-'+g['code'].lower(),'questions':g['question_ids']} for g in c['groups']]} for c in org['categories']]
payload={'version':cfg['current_version'],'date':cfg['updated_at'],'documents':data_docs,'categories':categories,'questions':questions}
data=json.dumps(payload,ensure_ascii=False).replace('<','\\u003c')
esc=lambda s:html.escape(str(s),quote=True)
def read(file,anchor,label,cls=''):
    target=file+('#'+anchor if anchor else '')
    return f'<a class="{cls}" href="{esc(target)}" data-read="{esc(target)}">{esc(label)}</a>'
byid={d['id']:d for d in data_docs};byq={q['id']:q for q in questions}
cards=[];indexes=[]
for i,c in enumerate(categories,1):
    d=byid[c['id']]
    sublinks=''.join(read(d['file'],g['anchor'],g['title'],'subject-link') for g in c['groups']) if c['id']=='knowledge' else ''
    cards.append(f'<article class="category-card"><span class="number">0{i}</span><span class="meta">{d["count"]}题</span><h2>{esc(c["title"])}</h2><p>{esc(d["description"])}</p><div class="subjects">{sublinks}</div><div class="actions"><a class="primary" href="#index-{c["id"]}">板块索引</a>{read(d["file"],"","阅读全文")}</div></article>')
    groups=[]
    for g in c['groups']:
        qlist=''.join(f'<li><span>{q}</span>{read(d["file"],q,byq[q]["title"])}</li>' for q in g['questions'])
        listing=f'<details class="question-index"><summary>查看{len(g["questions"])}道题目</summary><ul>{qlist}</ul></details>' if qlist else '<p class="quiet">公式、表格与复习资料</p>'
        groups.append(f'<article class="group-index"><h3>{read(d["file"],g["anchor"],g["title"])}</h3>{listing}</article>')
    indexes.append(f'<section class="section category-index" id="index-{c["id"]}"><div class="section-head"><div><span class="eyebrow">0{i} · {d["count"]}题</span><h2>{esc(c["title"])}</h2></div><div class="actions">{read(d["file"],"","阅读本板块","primary")}<button data-filter="{c["id"]}">检索本板块</button></div></div><div class="group-grid">{"".join(groups)}</div></section>')
compat=''.join(f'<li>{read(d["file"],"",d["title"])} · <a href="{esc(d["source"])}">Markdown</a></li>' for d in data_docs if d['kind'] in ('source','legacy'))
topics=''.join(f'<section class="section topic-entry" id="topic-{d["id"]}"><div><span class="eyebrow">专题复习 · 跨五板块</span><h2>{esc(d["title"])}</h2><p>{esc(d["description"])}</p><p class="quiet">{esc(d["scope"])}</p></div><div class="actions">{read(d["file"],"","进入专题","primary")}{read(d["file"],"chapter-m3","结构与装配场景")}{read(d["file"],"chapter-m5","公式与算例")}</div></section>' for d in data_docs if d['kind']=='topic')
nav=''.join(f'<a href="#index-{c["id"]}" data-home>{esc(label)}</a>' for c,label in zip(categories,['理论知识','生活场景','生产场景','仿真测试','数据公式']))
css=(ROOT/'maintenance/portal.css').read_text(encoding='utf-8')
script=(ROOT/'maintenance/portal.js').read_text(encoding='utf-8')
page=f'''<!doctype html><html lang="zh-CN"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>面经聚合 · 五板块索引</title><style>{css}</style></head><body>
<header class="topbar"><a class="brand" href="index.html">面经聚合</a><nav aria-label="五板块导航">{nav}<a href="#question-bank" data-home>全题检索</a></nav></header>
<main class="wrap" id="home"><section class="hero"><div><div class="eyebrow">MECHANICAL ENGINEERING · INTERVIEW HANDBOOK</div><h1>五个板块，按主题查阅</h1><p class="lede">从四门理论科目，到生活、量产与仿真测试实践，再到常用数据和公式。选择板块索引，或直接检索题号与关键词。</p></div><div class="stats"><div class="stat"><strong>{len(questions)}</strong><span>道题目</span></div><div class="stat"><strong>5</strong><span>个板块</span></div><div class="stat"><strong>4</strong><span>门理论科目</span></div></div></section>
<section id="library" class="category-cards" aria-label="五板块入口">{''.join(cards)}</section>
{topics}
<section class="section" id="question-bank"><div class="section-head"><h2>全题检索</h2><p>按板块、理论科目、题号或关键词查找</p></div><div class="search-panel"><div class="filters"><input type="search" id="search" aria-label="搜索全部题目" placeholder="题号或关键词，例如：Q347、预紧、注塑"><select id="topic" aria-label="板块"><option value="">全部板块</option></select><select id="subject" aria-label="理论科目"><option value="">全部理论科目</option></select><select id="priority" aria-label="优先级"><option value="">全部优先级</option><option>P0</option><option>P1</option></select></div><div class="result-meta"><span id="result-count" aria-live="polite"></span><div><button id="reset">重置</button> <button id="preview-toggle" aria-pressed="false">隐藏口头答案</button></div></div><div id="results" class="result-list"></div><p id="empty" class="empty" hidden>没有匹配题目。请调整关键词或筛选条件。</p><button id="more" class="more">加载更多题目</button></div></section>
<div id="chapter-index">{''.join(indexes)}</div>
<details class="source-library"><summary>完整主手册与原专题链接</summary><ul>{compat}</ul></details>
<footer><a href="01-手册索引.md">Markdown索引</a><a href="{esc(cfg['master'].replace('.md','.html'))}#version-history">版本记录</a><a href="00-工作总结与编辑交接.html">编辑交接</a><span>{cfg['current_version']} · {cfg['updated_at']}</span></footer></main>
<section class="reader" id="reader" hidden><div class="reader-bar"><button id="back-home">← 返回索引与检索</button><strong id="reader-title"></strong><a id="reader-standalone" target="_blank" rel="noopener">独立打开 ↗</a></div><iframe id="reader-frame" title="手册阅读区"></iframe></section>
<script type="application/json" id="site-data">{data}</script><script>{script}</script></body></html>'''
(ROOT/'index.html').write_text(page,encoding='utf-8')
index=['# 面经聚合 · 五板块索引','',f'**{cfg["current_version"]}｜{len(questions)}道题目｜五个板块、四门理论科目**','','[打开HTML入口](index.html)','']
for d in data_docs:
    if d['kind']=='topic':
        index += ['## 专题入口','',f'[{d["title"]}]({d["file"]}) · [Markdown正文]({d["source"]})','',d['scope'],'']
for c in categories:
    d=byid[c['id']];index += ['## '+c['title'],'',f'[{d["count"]}题 · 阅读本板块]({d["file"]}) · [Markdown正文]({d["source"]})','']
    for g in c['groups']:
        index += [f'### [{g["title"]}]({d["file"]}#{g["anchor"]})','']
        index += [f'- [{q}｜{byq[q]["title"]}]({d["file"]}#{q})' for q in g['questions']]
        if not g['questions']:index += ['公式、表格与复习资料。']
        index += ['']
index += ['## 完整原文与维护','',f'[完整主手册]({cfg["master"].replace(".md",".html")}) · [编辑交接](00-工作总结与编辑交接.html)','']
(ROOT/'01-手册索引.md').write_text('\n'.join(index),encoding='utf-8')
(ROOT/'maintenance/search-index.json').write_text(json.dumps(payload,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
print(f'Portal: {len(questions)} unique unchanged questions; five dedicated category indexes')
