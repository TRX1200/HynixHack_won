"""Local text extraction and literal retrieval; no OCR, embeddings or network.

An extraction is an inspectable derivative, not proof of correct PDF reading order.
"""
from __future__ import annotations
import json
import re
import zipfile
import xml.etree.ElementTree as ET
from pathlib import Path
from typing import Any
from .core import checked_file, file_hash, parse_json, write_new, MAX_BYTES

MAX_CHUNK_CHARS = 200_000


def extract_units(path: str | Path, encoding: str = 'utf-8-sig') -> list[dict]:
    p = checked_file(path)
    suffix = p.suffix.lower()
    units = []
    if suffix in {'.txt', '.md', '.csv', '.tsv', '.json', '.jsonl', '.py', '.js', '.html'}:
        text = p.read_text(encoding=encoding)
        units = [{'locator': 'text', 'text': text, 'warning': None}]
    elif suffix == '.pdf':
        try: import fitz
        except ImportError as e: raise ValueError('PDF extraction needs PyMuPDF. Use an existing approved installation or the manual path.') from e
        with fitz.open(p) as doc:
            if doc.needs_pass: raise ValueError('Encrypted PDF requires authorized access; no password guessing.')
            for page_num, page in enumerate(doc, 1):
                text = page.get_text('text', sort=True)
                warning = 'Reading order/table structure must be checked against the rendered page.'
                if not text.strip(): warning = 'NO_TEXT_LAYER: inspect page visually; no OCR performed.'
                units.append({'locator': f'page:{page_num}', 'text': text, 'warning': warning})
    elif suffix == '.docx':
        with zipfile.ZipFile(p) as archive:
            member = archive.getinfo('word/document.xml')
            if member.file_size > MAX_BYTES: raise ValueError('DOCX expanded XML exceeds resource limit.')
            root = ET.fromstring(archive.read(member))
        ns = {'w': 'http://schemas.openxmlformats.org/wordprocessingml/2006/main'}
        prefix = '{' + ns['w'] + '}'
        separators = {prefix + 'tab': '\t', prefix + 'br': '\n', prefix + 'cr': '\n'}
        for number, paragraph in enumerate(root.findall('.//w:p', ns), 1):
            text = ''.join((node.text or '') if node.tag == prefix + 't' else separators.get(node.tag, '')
                           for node in paragraph.iter())
            units.append({'locator': f'body-paragraph:{number}', 'text': text,
                          'warning': 'Main document paragraphs only; table geometry, images, notes and headers not represented.'})
    else:
        raise ValueError('Unsupported input. Use TXT/MD/CSV/TSV/JSON/JSONL/PDF/DOCX; never claim unextracted content was read.')
    sha = file_hash(p)
    for u in units:
        u.update({'source_file': p.name, 'source_sha256': sha})
    return units


def chunk_units(units: list[dict], lines_per_chunk: int = 35, overlap: int = 3) -> list[dict]:
    if not 1 <= lines_per_chunk <= 200 or not 0 <= overlap < lines_per_chunk:
        raise ValueError('Chunk size 1..200 and 0 <= overlap < size required.')
    chunks = []
    for u in units:
        lines = u['text'].splitlines()
        if not lines:
            lines = ['']
        start = 0
        while start < len(lines):
            stop = min(start + lines_per_chunk, len(lines))
            content = '\n'.join(lines[start:stop])
            if len(content) > MAX_CHUNK_CHARS:
                raise ValueError('Individual chunk exceeds text limit; reduce chunk size or partition long lines explicitly.')
            chunks.append({
                'id': f"{u['source_sha256'][:16]}:{u['locator']}:{start+1}-{stop}",
                'source_file': u['source_file'], 'source_sha256': u['source_sha256'],
                'locator': u['locator'], 'line_start': start + 1, 'line_end': stop,
                'text': content, 'warning': u['warning'], 'trusted_instruction': False,
            })
            if stop == len(lines): break
            start = stop - overlap
    return chunks


def extract_to_index(paths: list[str], output: str, lines: int = 35, overlap: int = 3, encoding: str = 'utf-8-sig') -> dict:
    if len(paths) > 200: raise ValueError('At most 200 explicit files per batch.')
    if Path(output).resolve() in [Path(p).resolve() for p in paths]:
        raise ValueError('Output cannot replace an input.')
    result, seen = [], set()
    for p in paths:
        for chunk in chunk_units(extract_units(p, encoding), lines, overlap):
            if chunk['id'] in seen: continue  # identical content source, dedup index IDs only
            seen.add(chunk['id']); result.append(chunk)
    text = '\n'.join(json.dumps(c, ensure_ascii=False) for c in result)
    if len(text.encode('utf-8')) > MAX_BYTES: raise ValueError('Extracted index exceeds size limit.')
    write_new(output, text)
    return {'index': output, 'input_files': len(paths), 'chunks': len(result),
            'warnings': sorted(set(c['warning'] for c in result if c['warning'])),
            'note': 'Line numbers refer to extracted text, not printed source line numbers. Same-content sources share an index identity.'}


def load_index(path: str | Path) -> list[dict]:
    data, ids = [], set()
    for lineno, line in enumerate(checked_file(path).read_text(encoding='utf-8').splitlines(), 1):
        if not line.strip(): continue
        record = parse_json(line)
        if not isinstance(record, dict) or not all(isinstance(record.get(k), str) for k in ['id', 'text', 'source_file', 'source_sha256', 'locator']):
            raise ValueError(f'Invalid index record {lineno}.')
        if len(record['text']) > MAX_CHUNK_CHARS: raise ValueError('Individual chunk exceeds text limit.')
        if record['id'] in ids: raise ValueError('Duplicate index ID.')
        ids.add(record['id']); data.append(record)
        if len(data) > 100_000: raise ValueError('Too many chunks.')
    return data


def search_chunks(chunks: list[dict], query: str, limit: int = 5, source: str | None = None) -> dict:
    if not isinstance(query, str) or not query.strip() or len(query) > 2000:
        raise ValueError('A nonempty query of at most 2000 characters is required.')
    if isinstance(limit, bool) or not isinstance(limit, int) or not 1 <= limit <= 20:
        raise ValueError('limit must be an integer from 1 to 20.')
    if source is not None and not isinstance(source, str): raise ValueError('source must be a string.')
    terms = list(dict.fromkeys(re.findall(r'[\w-]+', query.casefold())))
    if not terms: raise ValueError('Query must contain letters or digits.')
    hits = []
    for c in chunks:
        if source is not None and c['source_file'] != source: continue
        text = c['text'].casefold()
        n = sum(1 for t in terms if t in text)
        if n:
            # Mechanical score is a sorting aid, never calibrated confidence.
            score = n * 10 + min(sum(text.count(t) for t in terms), 20)
            pos = min(text.find(t) for t in terms if t in text)
            # Case folding can expand characters (for example, sharp-s to ss).
            # Convert the match offset back to source-text coordinates.
            folded_offset = 0
            original_pos = 0
            for original_pos, character in enumerate(c['text']):
                folded_offset += len(character.casefold())
                if folded_offset > pos:
                    break
            snippet = c['text'][max(0, original_pos - 120):original_pos + 600]
            hits.append({'id': c['id'], 'source_file': c['source_file'], 'locator': c['locator'],
                         'line_start': c.get('line_start'), 'line_end': c.get('line_end'),
                         'source_sha256': c['source_sha256'], 'matched_terms': n,
                         'rank_score_not_confidence': score, 'snippet': snippet,
                         'warning': c.get('warning'), 'untrusted_source_data': True})
    hits.sort(key=lambda x: (-x['rank_score_not_confidence'], x['id']))
    return {'hits': hits[:limit], 'matching_chunks': len(hits), 'indexed_chunks': len(chunks),
            'method': 'Case-insensitive literal term OR search; not semantic search, BM25 or proof of absence.',
            'source_version': 'Snapshot at extraction. Re-extract after source changes.'}


def get_chunk(chunks: list[dict], chunk_id: str, max_chars: int = 12000) -> dict:
    if not isinstance(chunk_id, str): raise ValueError('chunk_id must be a string.')
    if isinstance(max_chars, bool) or not isinstance(max_chars, int) or not 100 <= max_chars <= 20000:
        raise ValueError('max_chars must be an integer 100..20000.')
    for c in chunks:
        if c['id'] == chunk_id:
            return {**c, 'text': c['text'][:max_chars], 'truncated': len(c['text']) > max_chars,
                    'untrusted_source_data': True}
    raise ValueError('Unknown chunk ID. No arbitrary file reads are supported.')
