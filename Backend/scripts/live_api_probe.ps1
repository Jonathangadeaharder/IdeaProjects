# Live API probe without GUI (PowerShell)
# - Checks /health
# - Logs in as admin/admin
# - Starts /process/chunk for Superstore episode (0-600s)
# - Polls /process/progress until completed or timeout
# - Fetches subtitles via /videos/subtitles and prints first lines

$ErrorActionPreference = 'Stop'

function Write-Section($title){
  Write-Host "`n=== $title ==="
}

$Base = 'http://localhost:8000'
$VideoRel = 'Superstore\Episode 1 Staffel 1 von Superstore S to - Serien Online gratis a.mp4'
$Start = 0
$End = 600

Write-Section 'Health'
try {
  $health = Invoke-RestMethod -Method GET -Uri "$Base/health" -TimeoutSec 5
  $health | ConvertTo-Json -Depth 4
} catch {
  Write-Error "Health check failed: $_"; exit 1
}

Write-Section 'Login'
try {
  $loginBody = @{ username = 'admin'; password = 'admin' } | ConvertTo-Json
  $auth = Invoke-RestMethod -Method POST -Uri "$Base/auth/login" -ContentType 'application/json' -Body $loginBody -TimeoutSec 15
  $token = $auth.token
  if (-not $token) { throw 'No token in response' }
  $headers = @{ Authorization = "Bearer $token" }
  "Token acquired"
} catch {
  Write-Error "Login failed: $_"; exit 1
}

Write-Section 'Start chunk 0-600'
try {
  $body = @{ video_path = $VideoRel; start_time = $Start; end_time = $End } | ConvertTo-Json
  $startResp = Invoke-RestMethod -Method POST -Uri "$Base/process/chunk" -Headers $headers -ContentType 'application/json' -Body $body -TimeoutSec 30
  $taskId = $startResp.task_id
  if (-not $taskId) { throw 'No task_id' }
  "Task ID: $taskId"
} catch {
  Write-Error "Start chunk failed: $_"; exit 1
}

Write-Section 'Poll progress'
$completed = $false
for ($i=0; $i -lt 90; $i++) { # up to ~90s
  Start-Sleep -Seconds 1
  try {
    $pr = Invoke-RestMethod -Method GET -Uri "$Base/process/progress/$taskId" -Headers $headers -TimeoutSec 15
    "status=$($pr.status) progress=$($pr.progress) step=$($pr.current_step)"
    if ($pr.subtitle_path) { "subtitle_path: $($pr.subtitle_path)" }
    if ($pr.translation_path) { "translation_path: $($pr.translation_path)" }
    if ($pr.status -eq 'completed') { $completed = $true; break }
  } catch {
    Write-Warning "Progress poll failed: $_"
  }
}
if (-not $completed) { Write-Error 'Task did not complete in time'; exit 1 }

Write-Section 'Fetch subtitles via API'
# Build relative chunk subtitle
$chunkRel = $VideoRel -replace '\\.mp4$', "_chunk_${Start}_${End}.srt"
$chunkRelUrl = $chunkRel -replace '\\', '/'
$encoded = [System.Uri]::EscapeDataString($chunkRelUrl)
try {
  $srtText = Invoke-RestMethod -Method GET -Uri "$Base/videos/subtitles/$encoded" -Headers $headers -TimeoutSec 20
  "Subtitle length: $($srtText.Length)"
  if ($srtText.Length -gt 0) {
    "First lines:"; $srtText -split "`n" | Select-Object -First 10
  } else {
    Write-Warning 'Subtitle response length is 0'
  }
} catch {
  Write-Error "Subtitle fetch failed: $_"; exit 1
}

Write-Section 'Done'
"Probe completed successfully."
