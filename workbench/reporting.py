"""Render a user-supplied evidence report to Markdown or static HTML.

No facts, tests, images or metrics are invented. HTML is escaped, contains no
JavaScript, remote assets, font downloads or active links.
"""
from __future__ import annotations
import html
from typing import Any
from .core import write_new

SECTIONS = [('summary','결론과 제안'),('scope','범위와 입력'),('findings','확인된 결과'),
            ('method','방법과 선택 이유'),('validation','검증'),('limitations','한계와 미확인 사항'),
            ('next_actions','다음 조치'),('sources','근거 목록')]


def normalize_report(data: dict) -> dict:
    if not isinstance(data,dict) or not isinstance(data.get('title'),str) or not data['title'].strip():
        raise ValueError('A nonempty report title is required.')
    for key,_ in SECTIONS:
        if key in data and not isinstance(data[key],(list,str)):
            raise ValueError(f'{key} must be text or a list.')
    validation = data.get('validation', [])
    if not isinstance(validation, list):
        raise ValueError('validation must be a list of checks with explicit status.')
    for row in validation:
        if not isinstance(row,dict) or row.get('status') not in ['pass','fail','not_run','blocked']:
            raise ValueError('Every validation item requires explicit pass/fail/not_run/blocked status.')
        for k in ['check','expected','actual']:
            if not isinstance(row.get(k),str): raise ValueError(f'Validation {k} text required.')
        evidence = row.get('evidence')
        if row['status'] in ['pass','fail'] and (not isinstance(evidence, str) or not evidence.strip()):
            raise ValueError('Executed checks require an evidence location; do not claim unexecuted checks.')
    return data


def text_item(value: Any) -> str:
    if isinstance(value,str): return value
    if isinstance(value,dict):
        return ' | '.join(f'{k}: {v}' for k,v in value.items())
    return str(value)


def markdown_report(data: dict) -> str:
    normalize_report(data)
    lines=['# '+data['title'],'','> 본문 값은 입력한 보고서 데이터입니다. 자동 렌더링은 사실성 검증을 대신하지 않습니다.','']
    for key,title in SECTIONS:
        lines.extend(['## '+title,''])
        section=data.get(key,[])
        if not section: lines.extend(['미작성 / 확인 필요','']); continue
        if isinstance(section,str): lines.extend([section,'']); continue
        for row in section:
            lines.append('- '+text_item(row).replace('\n',' '))
        lines.append('')
    return '\n'.join(lines)


def html_report(data: dict) -> str:
    normalize_report(data)
    esc=html.escape
    sections=[]
    for key,title in SECTIONS:
        section=data.get(key,[])
        if not section: body='<p class="pending">미작성 / 확인 필요</p>'
        elif isinstance(section,str): body='<p>'+esc(section).replace('\n','<br>')+'</p>'
        elif key=='validation':
            header='<tr><th>검사</th><th>기대값</th><th>실제값</th><th>상태</th><th>근거</th></tr>'
            rows=['<tr>'+''.join('<td>'+esc(str(r.get(k,'')))+'</td>' for k in ['check','expected','actual','status','evidence'])+'</tr>' for r in section]
            body='<div class="table"><table>'+header+''.join(rows)+'</table></div>'
        else:
            body='<ul>'+''.join('<li>'+esc(text_item(v))+'</li>' for v in section)+'</ul>'
        sections.append('<section><h2>'+esc(title)+'</h2>'+body+'</section>')
    css='''body{font:16px/1.7 system-ui,sans-serif;max-width:980px;margin:36px auto;padding:0 24px;color:#1d2733;background:#fff}h1{font-size:30px;line-height:1.35}h2{font-size:21px;border-bottom:1px solid #cbd2da;padding-bottom:6px}section{margin:30px 0}li{margin:8px 0;overflow-wrap:anywhere}table{border-collapse:collapse;width:100%;font-size:14px}th,td{border:1px solid #ccd4dc;padding:9px;text-align:left;vertical-align:top;overflow-wrap:anywhere}.table{overflow-x:auto}.note,.pending{color:#546170}@media print{body{margin:0;max-width:none;font-size:11pt}h2{break-after:avoid}tr{break-inside:avoid}.table{overflow:visible}section{margin:18px 0}}'''
    return '<!doctype html><html lang="ko"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><meta http-equiv="Content-Security-Policy" content="default-src \'none\'; style-src \'unsafe-inline\'"><title>'+esc(data['title'])+'</title><style>'+css+'</style></head><body><h1>'+esc(data['title'])+'</h1><p class="note">제공된 보고서 데이터를 정리한 문서입니다. 출력 형식의 정상 여부와 내용의 정확성은 별개입니다.</p>'+''.join(sections)+'</body></html>'


def render_report(data: dict, output: str, format: str) -> dict:
    if format not in ['md','html']: raise ValueError('Use md or html.')
    text=markdown_report(data) if format=='md' else html_report(data)
    write_new(output,text)
    return {'output':output,'format':format,'semantic_verification_performed':False}
