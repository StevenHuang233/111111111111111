param(
    [int]$MaxMB = 50
)

$limit = $MaxMB * 1MB
$staged = git diff --cached --name-only --diff-filter=ACM
$blocked = @()

foreach ($path in $staged) {
    if (-not (Test-Path -LiteralPath $path)) {
        continue
    }
    $item = Get-Item -LiteralPath $path
    if ($item.Length -gt $limit) {
        $blocked += [PSCustomObject]@{
            Path = $path
            MB = [math]::Round($item.Length / 1MB, 2)
        }
    }
}

if ($blocked.Count -gt 0) {
    Write-Host "Blocked large staged files. Do not commit videos, frames, model outputs, or archives." -ForegroundColor Red
    Write-Host "阻止提交大文件。不要把视频、抽帧、模型输出或压缩包提交到 Git。" -ForegroundColor Red
    $blocked | Format-Table -AutoSize
    exit 1
}

exit 0

