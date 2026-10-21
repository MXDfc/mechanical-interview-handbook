from pathlib import Path
import sys

root=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(root/'maintenance/vendor'))
import markdown

source=root/'00-工作总结与编辑交接.md'
body=markdown.markdown(source.read_text(encoding='utf-8'),extensions=['extra','toc','sane_lists'])
page='''<!doctype html><html lang="zh-CN"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>工作总结与编辑交接</title><style>
body{max-width:1120px;margin:35px auto;padding:0 24px;color:#213a45;background:#f5f8f9;font:16px/1.85 "Microsoft YaHei",system-ui,sans-serif}h1{font-size:32px}h2{margin-top:42px;border-bottom:2px solid #368883;padding-bottom:10px}h3{font-size:19px}a{color:#176c75}table{width:100%;border-collapse:collapse;display:block;overflow-x:auto;background:white;font-size:14px}th,td{border:1px solid #ccdce0;padding:10px;text-align:left;vertical-align:top;min-width:100px}th{background:#e5f1f2}pre{overflow:auto;background:#e6eef0;padding:16px;border-radius:8px}code{font:14px/1.8 Consolas,"Microsoft YaHei",monospace;overflow-wrap:anywhere}blockquote{border-left:4px solid #32887f;margin-left:0;padding:14px 20px;background:#e9f4ef}p,li{overflow-wrap:anywhere}@media print{body{background:white;font-size:10pt;margin:0}h2{break-after:avoid}table{display:table}th,td{min-width:0;font-size:9pt}pre{white-space:pre-wrap}}
</style></head><body>'''+body+'</body></html>'
source.with_suffix('.html').write_text(page,encoding='utf-8')
print(source.with_suffix('.html'))
