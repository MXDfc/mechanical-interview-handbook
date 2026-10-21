from pathlib import Path
import sys, re, html

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'maintenance' / 'vendor'))
import markdown
from site_common import catalog,document_for,render,doc_link,html_name

source = Path(sys.argv[1]).resolve() if len(sys.argv) > 1 else ROOT / '机械结构工程师面试与知识强化手册.md'
text = source.read_text(encoding='utf-8')
config=catalog()
metadata=document_for(source.name)
documents=sorted(config['documents'],key=lambda d:d['order'])
question_count = len(re.findall(r'^### Q\d{3}', text, re.M))
checklist_count = len(re.findall(r'^- \[ \]', text, re.M))
is_theory = '理论力学' in source.stem
is_simulation = '仿真' in source.stem
is_oral = '口头面试' in source.stem
is_phenomena = '工程现象' in source.stem
nav_title = '线上口头面试<br>工程数量级速记' if is_oral else ('SolidWorks 仿真与<br>结构设计实践' if is_simulation else ('理论力学与<br>消费电子刚体分析' if is_theory else '面试与<br>知识强化手册'))
if is_phenomena:
    nav_title = '工程现象分析<br>云台与动平衡'
nav_topics = '口头判断 / 数量级 / 条件 / 来源'
search_hint = '搜索：数量级、扭矩、Cpk、Q252…'
if is_phenomena:
    search_hint = '搜索：水滑、翘头、动平衡、Q303…'
nav_title=html.escape(metadata['label'])
rendered = render(text)
# Keep unchanged source-relative question links usable in curated volumes.
present_ids=set(re.findall(r' id="([^"]+)"',rendered))
rendered=re.sub(r'href="#(Q\d{3})"',lambda m:m.group(0) if m[1] in present_ids else f'href="{html.escape(config["master"].replace(".md",".html"))}#{m[1]}"',rendered)

def question(match):
    title, body = match.groups()
    number = re.search(r'Q\d{3}', title).group()
    priority = re.search(r'【(P\d)】', title).group(1)
    # Stable question IDs make direct links convenient across editions.
    title = re.sub(r'id="[^"]*"', f'id="{number}"', title, count=1)
    oral = re.search(r'<p><strong>口头首答（约30～60秒）</strong>：(.*?)</p>', body, flags=re.S)
    oral_html = ''
    if oral:
        oral_html = '<div class="oral-answer"><div class="oral-label">口头首答 · 约30–60秒</div><p>' + oral.group(1) + '</p></div>'
        body = body[:oral.start()] + body[oral.end():]
        body = re.sub(r'\s*<p><strong>深入复习（按需展开）</strong></p>\s*', '', body, count=1)
    prompt = ''
    given = re.match(r'\s*<p><strong>(?:场景与提问|题目)</strong>.*?</p>\s*', body, flags=re.S)
    if given:
        prompt = '<div class="problem">' + given.group(0) + '</div>'
        body = body[given.end():]
    if oral_html:
        result = oral_html + '<details class="technical-details"><summary>展开依据、算例与操作步骤（按需复习）</summary>' + prompt + body + '</details>'
    else:
        result = prompt + body
    related=[]
    for d in documents:
        if d.get('kind')=='legacy':continue
        if d['file']==source.name or number not in d['question_ids']:continue
        label='主手册同题' if d['id']=='master' else d['label']+'专题'
        related.append(f'<a href="{doc_link(d,number)}">{html.escape(label)}</a>')
    cross='<div class="question-links">关联阅读：'+' · '.join(related)+'</div>' if related else ''
    return f'<article class="question" data-priority="{priority}">{title}<div class="answer">{result}</div>{cross}</article>\n'

rendered = re.sub(r'(<h3 id="[^"]*">Q\d{3}.*?</h3>)(.*?)(?=<h[23]\b|\Z)', question, rendered, flags=re.S)
parts = re.split(r'(<h2 id="[^"]*">.*?</h2>)', rendered, flags=re.S)
intro = parts[0]
chapters, navigation = [], []
for i in range(1, len(parts), 2):
    heading, body = parts[i], parts[i+1]
    target = re.search(r'id="([^"]*)"', heading).group(1)
    title = re.sub('<[^>]+>', '', heading)
    navigation.append(f'<a href="#{html.escape(target, quote=True)}">{title}</a>')
    if target=='reading-guide':body='<details class="reading-toc"><summary>查看本册目录与相关手册</summary>'+body+'</details>'
    chapters.append(f'<section class="chapter">{heading}{body}</section>')

style = '''
:root{--ink:#182c3a;--muted:#526571;--accent:#116b72;--paper:#fff;--line:#dbe5e8;--bg:#f2f5f6}
*{box-sizing:border-box}html{scroll-behavior:smooth;scroll-padding-top:112px}body{margin:0;background:var(--bg);color:var(--ink);font:16px/1.85 "Microsoft YaHei","PingFang SC",system-ui,sans-serif}
a{color:var(--accent);text-underline-offset:3px}aside{position:fixed;inset:0 auto 0 0;width:264px;background:#102c3b;color:#d9e9ee;overflow:auto;padding:28px 22px}
.brand{font-size:12px;letter-spacing:3px;color:#8abec4}.nav-title{font-size:22px;font-weight:700;line-height:1.5;margin:12px 0 10px}.nav-meta{font-size:13px;color:#a5bec7;margin-bottom:24px}
aside a{display:block;color:#d5e4e8;text-decoration:none;font-size:13px;line-height:1.6;padding:8px 0;border-bottom:1px solid #ffffff13}aside a:hover{color:white}
main{margin-left:264px;max-width:1264px;padding:36px 48px 90px}.top-note{font-size:12px;letter-spacing:2px;color:var(--accent)}
h1{font-size:34px;line-height:1.45;letter-spacing:-.5px;margin:12px 0 18px}h2{font-size:25px;line-height:1.5;margin:0 0 24px;padding-bottom:14px;border-bottom:2px solid var(--accent)}
h3{font-size:19px;line-height:1.65;margin:24px 0 12px}p{margin:10px 0 16px}li{margin-bottom:6px}strong{color:#123843}
.chapter{background:var(--paper);border:1px solid var(--line);border-radius:12px;padding:30px;margin:26px 0}.question{padding:8px 0 23px;border-bottom:1px solid var(--line)}.question:last-child{border-bottom:0;padding-bottom:0}.question h3{scroll-margin-top:110px}.answer p{color:#344853}
.toolbar{position:sticky;top:0;z-index:2;display:flex;gap:10px;align-items:center;flex-wrap:wrap;padding:14px 0;background:#f2f5f6f5;border-bottom:1px solid var(--line);backdrop-filter:blur(8px)}
input[type=search],select,button{font:inherit;font-size:14px;border:1px solid #bdcdd1;border-radius:7px;padding:8px 12px;background:white;color:var(--ink)}input[type=search]{flex:1;min-width:210px}button{cursor:pointer}button:hover{background:#e5f0f1}.count{font-size:12px;color:var(--muted);width:100%}
table{border-collapse:collapse;width:100%;font-size:14px;margin:20px 0;display:block;overflow-x:auto}th{background:#eaf3f4;text-align:left;color:#244f56}td,th{padding:12px;border:1px solid var(--line);min-width:110px;vertical-align:top}tr:nth-child(even){background:#fafcfc}
code{font-family:Consolas,"Microsoft YaHei",monospace;font-size:.92em;background:#edf3f4;border-radius:3px;padding:2px 5px;overflow-wrap:anywhere}input[type=checkbox]{accent-color:var(--accent);margin-right:8px}
pre{overflow-x:auto;padding:18px;background:#edf3f4;border-radius:8px;font-size:13px;line-height:1.7}pre code{background:none;padding:0;white-space:pre;overflow-wrap:normal}.problem{background:#f0f7f8;border-left:3px solid #6ca8ad;padding:10px 16px;margin:14px 0}.problem p{margin:0}
.practice .answer{display:none}.practice .question{padding-bottom:12px}.empty{padding:30px;background:white;border-radius:10px;border:1px solid var(--line)}[hidden]{display:none!important}.footer{font-size:12px;color:var(--muted);padding-top:12px}
.oral-answer{background:#edf7f4;border-left:3px solid #218371;padding:15px 18px;margin:14px 0}.oral-answer p{margin:4px 0 0;color:#173d39}.oral-label{font-size:12px;font-weight:700;letter-spacing:1px;color:#267361}.technical-details{border-top:1px dashed #c8d9da;margin-top:18px;padding-top:10px}.technical-details summary{cursor:pointer;font-size:13px;color:#52777d;padding:7px 0}.technical-details[open] summary{margin-bottom:12px}.practice .technical-details{display:none}
.site-breadcrumb{display:flex;gap:9px;flex-wrap:wrap;font-size:13px;color:var(--muted);margin-bottom:20px}.site-breadcrumb a{text-decoration:none}.home-link{display:block;margin-bottom:20px;color:#96d7d1!important;font-weight:bold}.question-links{font-size:12px;color:var(--muted);padding-top:12px}.reading-toc summary{cursor:pointer;color:var(--accent)}.chapter:has(#version-history) table{font-size:13px}h2,h3{scroll-margin-top:120px}
@media(min-width:1600px){main{margin-left:calc(264px + (100vw - 1600px)/2)}}
@media(max-width:950px){aside{display:none}main{margin:0;padding:24px 20px 60px}h1{font-size:28px}.chapter{padding:22px}table{font-size:13px}}
@media print{body{background:white;font-size:10pt;line-height:1.6}aside,.toolbar,.top-note,.empty{display:none!important}main{margin:0;max-width:none;padding:0}.chapter{border:0;padding:0;margin:20px 0;display:block!important}.question[hidden],.chapter[hidden]{display:block!important}.answer{display:block!important}h2{break-before:page;font-size:19pt}h3{break-after:avoid;font-size:12pt}p,li{orphans:3;widows:3}table{display:table;font-size:9pt}td,th{min-width:0;padding:6px}a{color:inherit}h1{font-size:24pt}}
@media print{.practice .technical-details{display:block!important}#intro[hidden]{display:block!important}.technical-details summary{font-size:9pt}.oral-answer{break-inside:avoid}}
'''

script = '''
const query=document.querySelector('#query'),priority=document.querySelector('#priority'),count=document.querySelector('#count');
const chapters=[...document.querySelectorAll('.chapter')],questions=[...document.querySelectorAll('.question')];
function filter(){
 const terms=query.value.trim().toLowerCase().split(/\\s+/).filter(Boolean),level=priority.value;let shown=0;
 questions.forEach(q=>{const content=q.textContent.toLowerCase();const ok=terms.every(t=>/^q\\d{3}$/.test(t)?q.querySelector('h3').id.toLowerCase()===t:content.includes(t))&&(!level||q.dataset.priority===level);q.hidden=!ok;if(ok)shown++});
 const active=terms.length>0||!!level;
 chapters.forEach(c=>{const qs=[...c.querySelectorAll('.question')];c.hidden=active&&(qs.length===0||qs.every(q=>q.hidden))});
 document.querySelector('#intro').hidden=active;
 count.textContent=`显示 ${shown} / ${questions.length} 道题 · 关键词检索覆盖问题与答案 · 可按题号检索`;
 document.querySelector('#empty').hidden=shown!==0;
}
query.addEventListener('input',filter);priority.addEventListener('change',filter);
document.querySelector('#toggle').addEventListener('click',()=>{const active=document.body.classList.toggle('practice');document.querySelector('#toggle').textContent=active?'显示期望答复':'隐藏答复，开始自测';document.querySelector('#toggle').setAttribute('aria-pressed',String(active))});
document.querySelector('#expand').addEventListener('click',()=>{const ds=[...document.querySelectorAll('.technical-details')];const expand=ds.some(d=>!d.open);ds.forEach(d=>d.open=expand);document.querySelector('#expand').textContent=expand?'收起全部深入复习':'展开全部深入复习';document.querySelector('#expand').setAttribute('aria-pressed',String(expand))});
let printState=[];
window.addEventListener('beforeprint',()=>{printState=[...document.querySelectorAll('details')].map(d=>[d,d.open]);printState.forEach(([d])=>d.open=true)});
window.addEventListener('afterprint',()=>printState.forEach(([d,open])=>d.open=open));
document.querySelector('#print').addEventListener('click',()=>window.print());
document.querySelectorAll('aside a').forEach(a=>a.addEventListener('click',()=>{query.value='';priority.value='';filter()}));
filter();
function revealHash(){const id=decodeURIComponent(location.hash.slice(1));const target=document.getElementById(id);if(!target)return;query.value='';priority.value='';filter();let p=target.parentElement;while(p){if(p.tagName==='DETAILS')p.open=true;p=p.parentElement}requestAnimationFrame(()=>target.scrollIntoView({block:'start',behavior:'instant'}));}
window.addEventListener('hashchange',revealHash);if(location.hash)revealHash();
function notifyReader(){if(window.parent!==window){window.parent.postMessage({type:'handbook-loaded',file:decodeURIComponent(location.pathname.split('/').pop()),fragment:location.hash,title:document.title},'*');}}
notifyReader();window.addEventListener('hashchange',notifyReader);
'''

# In-document checkboxes are deliberately non-persistent: no candidate assessment is stored.
content = '\n'.join(chapters)
content = content.replace('<li>[ ] ', '<li><input type="checkbox" aria-label="复习完成"> ')
document = f'''<!doctype html><html lang="zh-CN"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>{html.escape(metadata['title'])}</title><style>{style}</style></head><body>
<aside><a class="home-link" href="index.html" target="_top">← 面经聚合 · 总入口</a><div class="brand">MECHANICAL ENGINEERING</div><div class="nav-title">{nav_title}</div><div class="nav-meta">{question_count} 道题 · {config['current_version']}<br>{nav_topics}</div>{''.join(navigation)}<div class="footer"><a href="00-工作总结与编辑交接.html" target="_top">编辑交接与维护说明</a></div></aside>
<main><nav class="site-breadcrumb" aria-label="手册导航"><a href="index.html" target="_top">统一入口</a><span>/</span><a href="{html.escape(config['master'].replace('.md','.html'))}">主手册</a><span>/</span><span>{html.escape(metadata['label'])}</span><a href="#version-history">版本记录</a></nav><div class="top-note">ORAL INTERVIEW FIELD GUIDE</div><div id="intro">{intro}</div><div class="toolbar"><input id="query" type="search" placeholder="{search_hint}" aria-label="搜索题库"><select id="priority" aria-label="筛选优先级"><option value="">全部优先级</option><option value="P0">P0 · 必须掌握</option><option value="P1">P1 · 工程进阶</option></select><button id="toggle" aria-pressed="false">隐藏答复，开始自测</button><button id="expand" aria-pressed="false">展开全部深入复习</button><button id="print">打印</button><div class="count" id="count" aria-live="polite"></div></div><p class="empty" id="empty" hidden>没有匹配的问题，请更换关键词或优先级。</p>{content}<p class="footer">口头先讲判断、依据和条件；详细计算供追问或线下复习。数字不替代受控设计要求，例题不替代真实经历。</p></main><script>{script}</script></body></html>'''
target = source.with_suffix('.html')
target.write_text(document, encoding='utf-8')
print(f'Created {target}\nQuestions: {document.count("class=\"question\"")}\nCheckboxes: {document.count("type=\"checkbox\"")}')
