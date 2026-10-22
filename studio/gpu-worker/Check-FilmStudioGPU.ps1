# Read-only Windows GPU readiness report for Dan's consenting studio workstation.
# Never installs software, opens ports, changes firewall, gathers tokens, or starts jobs.
# PowerShell: Right click > Run with PowerShell, or:
# powershell -NoProfile -ExecutionPolicy Bypass -File .\Check-FilmStudioGPU.ps1
$ErrorActionPreference = 'Stop'
function Safe-Command($name) {
  $cmd = Get-Command $name -ErrorAction SilentlyContinue
  if ($null -eq $cmd) { return $null }
  return $cmd.Source
}
function Query-Gpu {
  if (-not (Safe-Command 'nvidia-smi.exe')) { return @() }
  $lines = @(& nvidia-smi.exe --query-gpu=name,memory.total,driver_version --format=csv,noheader,nounits 2>$null)
  $cards = @()
  foreach ($line in $lines) {
    $parts = $line -split '\s*,\s*'
    if ($parts.Count -ge 3) {
      $vram = 0
      [void][int]::TryParse(($parts[1] -replace '[^0-9]',''),[ref]$vram)
      $cards += [ordered]@{ model = $parts[0].Trim(); vram_mib = $vram; driver = $parts[2].Trim() }
    }
  }
  return ,$cards
}
$gpus = @(Query-Gpu)
$os = Get-CimInstance -ClassName Win32_OperatingSystem
$totalMemory = [math]::Round([double]$os.TotalVisibleMemorySize / 1MB,2)
$drive = Get-CimInstance -ClassName Win32_LogicalDisk -Filter "DeviceID='C:'"
$freeDisk = if ($drive) { [math]::Round([double]$drive.FreeSpace / 1GB,1) } else { $null }
$cuda = if ($gpus.Count -gt 0) { (& nvidia-smi.exe --query-gpu=compute_cap --format=csv,noheader 2>$null | Select-Object -First 1).Trim() } else { $null }
$report = [ordered]@{
  generated_utc = (Get-Date).ToUniversalTime().ToString('o')
  os_family = 'Windows'
  os_version = $os.Version
  cpu_logical_processors = [Environment]::ProcessorCount
  memory_gib = $totalMemory
  system_drive_free_gib = $freeDisk
  nvidia_gpus = $gpus
  cuda_compute_capability = $cuda
  python_present = [bool](Safe-Command 'python.exe')
  ffmpeg_present = [bool](Safe-Command 'ffmpeg.exe')
  blender_present = [bool](Safe-Command 'blender.exe')
  comfyui_present = [bool](Safe-Command 'ComfyUI.exe')
  information_only = $true
  installed_nothing = $true
}
$out = Join-Path $PSScriptRoot 'film-studio-gpu-readiness.json'
$report | ConvertTo-Json -Depth 6 | Set-Content -Encoding UTF8 -Path $out
Write-Host 'Film Studio GPU inspection complete. No software installed, no remote connection opened.' -ForegroundColor Green
Write-Host ('Report saved: ' + $out)
Write-Host ($report | ConvertTo-Json -Depth 6)
Write-Host 'Review before sharing. This report intentionally omits account names, PC hostname, IP addresses, passwords and unique device IDs.'
