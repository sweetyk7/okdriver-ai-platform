# Ensure we are in the script's directory
Set-Location -Path $PSScriptRoot

if (!(Test-Path ".\mediamtx.exe")) {
    Write-Host "MediaMTX not found. Downloading automatically..."
    Invoke-WebRequest -Uri "https://github.com/bluenviron/mediamtx/releases/download/v1.21.1/mediamtx_v1.21.1_windows_amd64.zip" -OutFile "mediamtx.zip"
    Expand-Archive -Path "mediamtx.zip" -DestinationPath "." -Force
    Remove-Item "mediamtx.zip"
    Write-Host "MediaMTX downloaded successfully!"
}

$env:MTX_API = "yes"
$env:MTX_APIADDRESS = ":9997"
$env:MTX_WEBRTCADDRESS = ":8889"
.\mediamtx.exe
