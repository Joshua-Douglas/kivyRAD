Param(
    [ValidateScript({
        if(-Not (Test-Path $_)){
            throw "Path does not exist"
        } elseif (-Not (Test-Path $_ -PathType 'Container')){
            throw "Path is not a directory"
        }
    })]
    [System.IO.FileInfo]
    $Path = $PSScriptRoot,
    [string]
    $Name = "kivyrad",
    [switch]
    $Regenerate
)

$venvPath = Join-Path $Path $Name
if (-not (Test-Path $venvPath) ) {
    python -m venv $venvPath
}
$activatePath = Join-Path $venvPath "Scripts" "Activate.ps1"
Invoke-Expression $activatePath

$srcPath = Join-Path $PSScriptRoot "kivydesigner"
python -m pip install --upgrade pip 
if ($Regenerate) {
    python -m pip install pipreqs
    pipreqs $srcPath --force
}
$reqsPath = Join-Path $srcPath "requirements.txt"
python -m pip install -r $reqsPath