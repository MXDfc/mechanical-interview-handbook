"""Refresh derived reading navigation and end-of-document version tables."""
import re,json
from pathlib import Path
from site_common import ROOT,catalog,headings,html_name

def main():
    cfg=catalog();docs=cfg['documents']
    history=json.loads((ROOT/'maintenance/releases.json').read_text(encoding='utf-8'))
    for doc in docs:
        path=ROOT/doc['file'];text=path.read_text(encoding='utf-8')
        text=re.sub(r'\n<!-- NAV_START -->.*?<!-- NAV_END -->\s*','\n',text,flags=re.S)
        text=re.sub(r'\n<!-- VERSIONS_START -->.*?<!-- VERSIONS_END -->\s*','\n',text,flags=re.S)
        h=headings(text)
        nav=['<!-- NAV_START -->','## 阅读导航','',f'[统一入口](index.html) · [主手册]({cfg["master"].replace(".md",".html")}) · [本册版本记录]({html_name(doc)}#version-history)','',
             '**本册目录**','', '| 板块 | 阅读内容 |','|---|---|']
        for title,anchor in h:
            if title in ['版本记录','阅读导航']:continue
            label=title.split('：')[0]
            nav.append(f'| [{label}]({html_name(doc)}#{anchor}) | {title} |')
        nav+=['','**五个阅读板块**','', '| 板块 | 定位 |','|---|---|']
        for related in sorted(docs,key=lambda d:d['order']):
            if related.get('kind')!='category':continue
            mark='（当前）' if related['id']==doc['id'] else ''
            nav.append(f'| [{related["label"]}]({html_name(related)}){mark} | {related["description"]} |')
        nav+=['','五板块按主要主题分配题目；原题号保持不变。完整主手册及原专题链接仍可查阅。','<!-- NAV_END -->','']
        pos=text.index('\n## ')
        text=text[:pos]+'\n\n'+'\n'.join(nav)+text[pos:]
        version=['','<!-- VERSIONS_START -->','## 版本记录','',
                 '版本号按项目记录统一编排；v1.x为历史阶段的回溯标签，日期统一记为资料整理日，不代表当时曾发布同名版本。版本表只记录编辑沿革，技术参数的来源与适用条件仍见正文。','',
                 '| 版本 | 日期 | 变更内容 | 对本册的影响 |','|---|---|---|---|']
        for release in history['releases']:
            impact=release['impact'].get(doc['id'])
            if impact:version.append(f'| {release["version"]} | {release["date"]} | {release["change"]} | {impact} |')
        version+=['','<!-- VERSIONS_END -->','']
        path.write_text(text.rstrip()+'\n'+'\n'.join(version),encoding='utf-8')
        print('Navigation and versions:',path.name)

if __name__=='__main__':main()
