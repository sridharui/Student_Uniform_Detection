param(
    [Parameter(ValueFromRemainingArguments = $true)]
    [String[]]
    $Args
)

# PowerShell runner: run uniform detector system from current directory
$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Definition
Set-Location -Path $scriptDir

# Run python with any passed arguments
python.exe uniform_detector_system.py @Args
