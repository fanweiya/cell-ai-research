"""Finish a daily update; keep failed build/publish work pending for the next run."""
import json


def mark_site_pending(pending_path, needs_build=True):
    pending_path.parent.mkdir(parents=True, exist_ok=True)
    temporary = pending_path.with_suffix('.tmp')
    temporary.write_text(json.dumps({'needs_build': needs_build}), encoding='utf-8')
    temporary.replace(pending_path)


def update_site(evidence, changed, project, pending_path, run, build_command):
    evidence['publish_status'] = '未执行（页面无变化）'
    if changed:
        mark_site_pending(pending_path)
    if not pending_path.exists():
        return
    state = json.loads(pending_path.read_text(encoding='utf-8'))
    if state.get('needs_build', True):
        try:
            result = run(build_command, timeout=900)
            if result.returncode:
                raise RuntimeError((result.stderr or result.stdout or '非零退出码')[-500:])
        except Exception as exc:
            evidence['index_status'] = '失败'
            evidence['publish_status'] = '未执行（生成失败）'
            evidence['errors'].append(f'网页生成失败，已保留待重试状态：{exc}')
            return
        evidence['index_status'] = '已更新'
        mark_site_pending(pending_path, False)
    else:
        evidence['index_status'] = '复用上次已生成页面'
    try:
        result = run(['bash', str(project / 'publish_cf_pages.sh')], timeout=600)
        if result.returncode:
            raise RuntimeError((result.stderr or result.stdout or '非零退出码')[-500:])
    except Exception as exc:
        evidence['publish_status'] = '失败（下次重试）'
        evidence['errors'].append(f'Cloudflare 发布失败，研究数据已保留：{exc}')
        return
    evidence['publish_status'] = '已发布'
    evidence['site_updated'] = True
    pending_path.unlink()
