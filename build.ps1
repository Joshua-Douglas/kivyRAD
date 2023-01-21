Param(
    [ValidateScript({
        if(-Not (Test-Path $_)){
            throw "Path does not exist"
        } else if (-Not (Test-Path $_ -PathType 'Container')){
            throw "Path is not a directory"
        }
        })]
        Test-Path $_ -PathType ‘Container’
        })]
    [System.IO.FileInfo]
    $Path = $PSScriptRoot
    [string]
    $VenvName = "kivyrad"
)

# To-Do. Add option to clean venv. build venv from requirements. Add option to regenerate requirements using pipreqs. 
python -m pip install --upgrade pip 
python -m venv $VenvName