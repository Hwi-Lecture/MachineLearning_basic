# ============================================================
#  머신러닝 수업 환경 자동 설치 스크립트
#  - Python 설치
#  - Visual Studio Code 설치 (+ Python/Jupyter 확장)
#  - 환경변수(PATH) 갱신
#  - requirements.txt 패키지 설치
#
#  이 스크립트는 여러 번 실행해도 안전합니다.
#  (이미 설치된 항목은 건너뜁니다)
# ============================================================

$ErrorActionPreference = "Stop"

# 오류가 나도 항상 이 로그 파일에 기록됩니다. 창이 닫혀도 이 파일을 열어서 확인할 수 있습니다.
$logPath = Join-Path $PSScriptRoot "setup_log.txt"
try { Start-Transcript -Path $logPath -Append | Out-Null } catch {}

function Write-Step($msg) {
    Write-Host ""
    Write-Host "==== $msg ====" -ForegroundColor Cyan
}

function Write-Ok($msg) {
    Write-Host "[완료] $msg" -ForegroundColor Green
}

function Write-Warn($msg) {
    Write-Host "[주의] $msg" -ForegroundColor Yellow
}

function Write-Err($msg) {
    Write-Host "[오류] $msg" -ForegroundColor Red
}

# --------------------------------------------------------------
# 0. 관리자 권한으로 재실행 (설치 프로그램은 관리자 권한이 필요합니다)
# --------------------------------------------------------------
$currentPrincipal = New-Object Security.Principal.WindowsPrincipal(
    [Security.Principal.WindowsIdentity]::GetCurrent()
)
$isAdmin = $currentPrincipal.IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)

if (-not $isAdmin) {
    Write-Warn "관리자 권한으로 다시 시작합니다. Windows에서 뜨는 권한 요청 창(사용자 계정 컨트롤)에서 반드시 '예'를 눌러주세요."
    $scriptPath = $MyInvocation.MyCommand.Path
    try {
        Start-Process powershell -Verb RunAs -ArgumentList @(
            "-NoProfile", "-ExecutionPolicy", "Bypass", "-File", $scriptPath
        ) -ErrorAction Stop
    } catch {
        Write-Err "관리자 권한 요청이 취소되었거나 실패했습니다: $($_.Exception.Message)"
        Write-Host "권한 요청 창에서 '예'를 눌러야 설치가 진행됩니다. setup.bat을 다시 실행한 뒤 '예'를 눌러주세요."
        Read-Host "아무 키나 누르면 창이 닫힙니다"
    }
    exit
}

# --------------------------------------------------------------
# 환경변수(PATH)를 현재 세션에 다시 불러오는 함수
# (설치 직후에는 새로 추가된 PATH가 현재 창에 바로 반영되지 않기 때문)
# --------------------------------------------------------------
function Update-SessionPath {
    $machinePath = [System.Environment]::GetEnvironmentVariable("Path", "Machine")
    $userPath    = [System.Environment]::GetEnvironmentVariable("Path", "User")
    $env:Path = "$machinePath;$userPath"
}

# Windows에는 실제 설치 없이도 "python" 명령이 Microsoft Store를 여는
# 가짜 실행 파일(App Execution Alias)이 기본으로 등록되어 있을 수 있습니다.
# 이런 경우를 실제 설치로 착각하지 않도록 걸러냅니다.
function Test-RealPython {
    $cmd = Get-Command python -ErrorAction SilentlyContinue
    if (-not $cmd) { return $false }
    if ($cmd.Source -match "WindowsApps") { return $false }
    return $true
}

try {

# --------------------------------------------------------------
# 1. winget(앱 설치 관리자) 확인
# --------------------------------------------------------------
Write-Step "1/5 winget(앱 설치 관리자) 확인"

$winget = Get-Command winget -ErrorAction SilentlyContinue
if (-not $winget) {
    Write-Err "winget을 찾을 수 없습니다."
    Write-Host "Microsoft Store에서 '앱 설치 관리자(App Installer)'를 설치한 뒤 다시 실행해주세요."
    throw "winget 없음"
}
Write-Ok "winget 확인됨"

# --------------------------------------------------------------
# 2. Python 설치
# --------------------------------------------------------------
Write-Step "2/5 Python 설치 확인"

if (Test-RealPython) {
    Write-Ok "Python이 이미 설치되어 있습니다. ($(python --version))"
} else {
    Write-Host "Python을 설치합니다. 잠시 기다려주세요..."
    winget install --id Python.Python.3.12 -e --source winget `
        --accept-package-agreements --accept-source-agreements --silent
    Update-SessionPath

    if (Test-RealPython) {
        Write-Ok "Python 설치 완료 ($(python --version))"
    } else {
        Write-Warn "Python 설치는 되었지만 이 창에서 바로 인식되지 않을 수 있습니다. 설치가 끝난 뒤 컴퓨터를 재시작하거나 새 터미널을 열어 다시 실행해주세요."
    }
}

# --------------------------------------------------------------
# 3. Visual Studio Code 설치
# --------------------------------------------------------------
Write-Step "3/5 Visual Studio Code 설치 확인"

$codeInstalled = Get-Command code -ErrorAction SilentlyContinue
if ($codeInstalled) {
    Write-Ok "Visual Studio Code가 이미 설치되어 있습니다."
} else {
    Write-Host "Visual Studio Code를 설치합니다. 잠시 기다려주세요..."
    winget install --id Microsoft.VisualStudioCode -e --source winget `
        --accept-package-agreements --accept-source-agreements --silent `
        --override '/VERYSILENT /MERGETASKS="!runcode,addcontextmenufiles,addcontextmenufolders,associatewithfiles,addtopath"'
    Update-SessionPath

    $codeInstalled = Get-Command code -ErrorAction SilentlyContinue
    if ($codeInstalled) {
        Write-Ok "Visual Studio Code 설치 완료"
    } else {
        Write-Warn "VS Code 설치는 되었지만 이 창에서 바로 인식되지 않을 수 있습니다. 컴퓨터를 재시작한 뒤 다시 실행해주세요."
    }
}

# VS Code 확장 설치 (Python, Jupyter)
if (Get-Command code -ErrorAction SilentlyContinue) {
    Write-Host "VS Code 확장(Python, Jupyter)을 설치합니다..."
    try {
        code --install-extension ms-python.python --force | Out-Null
        code --install-extension ms-toolsai.jupyter --force | Out-Null
        Write-Ok "VS Code 확장 설치 완료"
    } catch {
        Write-Warn "VS Code 확장 설치 중 문제가 발생했습니다: $_"
    }
}

# --------------------------------------------------------------
# 4. 환경변수(PATH) 최종 갱신
# --------------------------------------------------------------
Write-Step "4/5 환경변수 갱신"
Update-SessionPath
Write-Ok "환경변수 갱신 완료"

# --------------------------------------------------------------
# 5. requirements.txt 패키지 설치
# --------------------------------------------------------------
Write-Step "5/5 필요한 파이썬 패키지 설치 (requirements.txt)"

if (-not (Test-RealPython)) {
    Write-Err "Python을 찾을 수 없어 패키지를 설치할 수 없습니다. 컴퓨터를 재시작한 뒤 이 스크립트를 다시 실행해주세요."
    throw "Python 없음"
}

$reqPath = Join-Path $PSScriptRoot "requirements.txt"
if (-not (Test-Path $reqPath)) {
    Write-Err "requirements.txt 파일을 찾을 수 없습니다: $reqPath"
    throw "requirements.txt 없음"
}

python -m pip install --upgrade pip
if ($LASTEXITCODE -ne 0) { throw "pip 업그레이드 실패 (종료 코드 $LASTEXITCODE)" }

python -m pip install -r "$reqPath"
if ($LASTEXITCODE -ne 0) { throw "requirements.txt 설치 실패 (종료 코드 $LASTEXITCODE)" }

Write-Ok "필요한 패키지 설치 완료"

# --------------------------------------------------------------
# 완료
# --------------------------------------------------------------
Write-Step "설치가 모두 끝났습니다"
Write-Host "이제 Visual Studio Code를 열고 이 폴더의 .ipynb 노트북 파일을 실행해보세요." -ForegroundColor Green
Write-Host "만약 명령이 인식되지 않는다는 오류가 계속 보이면, 컴퓨터를 한 번 재시작한 뒤 다시 시도해주세요." -ForegroundColor Green

} catch {
    Write-Host ""
    Write-Err "설치 중 오류가 발생하여 중단되었습니다."
    Write-Host "오류 내용: $($_.Exception.Message)" -ForegroundColor Red
    Write-Host "위 오류 메시지와 함께 '$logPath' 로그 파일을 확인해주세요." -ForegroundColor Yellow
} finally {
    try { Stop-Transcript | Out-Null } catch {}
    Read-Host "아무 키나 누르면 창이 닫힙니다"
}
