import hashlib
import json
import os
import re


def export_evidence(papers, context_dir, output_dir):
    output_dir.mkdir(parents=True, exist_ok=True)
    manifest = {}
    for paper in papers:
        pid = paper.get('arxiv_id', '')
        if not isinstance(pid, str) or not re.fullmatch(r'[A-Za-z0-9._:-]+', pid):
            continue
        source = context_dir / f'{re.sub(r"v[0-9]+$", "", pid)}.txt'
        if not source.is_file():
            continue
        try:
            text = source.read_text(encoding='utf-8').strip()
        except (OSError, UnicodeDecodeError):
            continue
        if not text:
            continue
        chunks = []
        start = 0
        while start < len(text):
            end = min(start + 2000, len(text))
            if end < len(text):
                boundary = max(text.rfind('\n', start + 1200, end), text.rfind('. ', start + 1200, end))
                if boundary > start:
                    end = boundary + 1
            chunks.append({'id': f'C{len(chunks)+1:03}', 'text': text[start:end]})
            start = end
        payload = json.dumps({'version': 1, 'paper_id': pid, 'source': 'local_paper_text_cache',
                              'note': '原文提取缓存；历史采集可能只提取部分章节或截断长文，可能缺少图片或存在表格、公式提取误差，不代表已验证原文完整性。',
                              'characters': len(text), 'chunks': chunks}, ensure_ascii=False)
        digest = hashlib.sha256(payload.encode('utf-8')).hexdigest()[:24]
        name = f'{digest}.json'
        target = output_dir / name
        if not target.exists():
            temp_target = target.with_suffix(f'.tmp.{os.getpid()}')
            temp_target.write_text(payload, encoding='utf-8')
            temp_target.replace(target)
        manifest[pid] = f'data/evidence/{name}'
    return manifest
