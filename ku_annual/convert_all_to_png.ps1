# 전체 HTML 슬라이드를 PNG로 변환

$slidesDir = "output\slides_v2"
$htmlFiles = Get-ChildItem -Path $slidesDir -Filter "*.html"

$total = $htmlFiles.Count
$current = 0

Write-Host "=" * 80
Write-Host "Chrome Headless PNG 변환 시작"
Write-Host "총 $total 개 파일"
Write-Host "=" * 80

foreach ($htmlFile in $htmlFiles) {
    $current++
    $htmlPath = (Resolve-Path $htmlFile.FullName).Path
    $pngPath = $htmlPath -replace '\.html$', '.png'
    
    Write-Host "[$current/$total] $($htmlFile.Name)..." -NoNewline
    
    & "C:\Program Files\Google\Chrome\Application\chrome.exe" `
        --headless=new `
        --screenshot="$pngPath" `
        --window-size=1920,1080 `
        "$htmlPath" 2>&1 | Out-Null
    
    if (Test-Path $pngPath) {
        $size = (Get-Item $pngPath).Length
        Write-Host " ✓ ($([math]::Round($size/1KB, 1))KB)"
    } else {
        Write-Host " ✗ 실패"
    }
}

Write-Host ""
Write-Host "=" * 80
Write-Host "PNG 변환 완료"
Write-Host "=" * 80
