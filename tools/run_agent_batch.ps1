# 分批跑代理版图解页，进程意外退出就接着跑，直到没有待做页面。

param([string]$Flags = '--missing')

$ErrorActionPreference = 'Stop'
Set-Location -Path (Split-Path -Parent $PSScriptRoot)

function Get-AgentCount {
    python -c "import json;m=json.load(open('data/explainers/manifest.json',encoding='utf-8'));print(len([1 for v in m['entries'].values() if v.get('generator')=='agent']))"
}

$round = 0
while ($round -lt 40) {
    $round++
    $before = [int](Get-AgentCount)
    $stamp = Get-Date -Format 'HH:mm:ss'
    Write-Output "== 第 $round 轮 $stamp 已有 $before 篇 =="
    python tools\agent_explainers.py $Flags --concurrency 6 *>> logs\agent-supervisor.log
    $code = $LASTEXITCODE
    Start-Sleep -Seconds 3
    Get-Process claude -ErrorAction SilentlyContinue | Where-Object { $_.StartTime -gt (Get-Date).AddHours(-12) } | Stop-Process -Force -ErrorAction SilentlyContinue
    $after = [int](Get-AgentCount)
    Write-Output "   退出码 $code，本轮新增 $($after - $before) 篇，累计 $after 篇"
    if ($code -eq 0) { Write-Output '全部完成'; break }
    if ($after -le $before) { Write-Output '本轮无进展，停止'; break }
}
