$ErrorActionPreference = 'Stop'
. "$PSScriptRoot\bootstrap-functions.ps1"
$html = @'
<a href="https://www.python.org/ftp/python/3.14.8/python-3.14.8-amd64.exe">stable</a>
<a href="https://www.python.org/ftp/python/3.15.0/python-3.15.0-amd64.exe">stable</a>
<a href="https://www.python.org/ftp/python/3.16.0/python-3.16.0a1-amd64.exe">alpha</a>
<a href="https://other.example/ftp/python/3.99.0/python-3.99.0-amd64.exe">untrusted</a>
<a href="https://www.python.org/ftp/python/3.15.0/python-3.15.0-arm64.exe">arm</a>
'@
if ((Get-PythonInstaller $html).Version -ne '3.15.0') { throw 'Stable version selection failed' }
if ((Get-PythonInstaller $html '3.14.8').Version -ne '3.14.8') { throw 'Explicit version failed' }
$failed = $false
try { Get-PythonInstaller '<html>unavailable</html>' | Out-Null } catch { $failed = $true }
if (-not $failed) { throw 'Missing installer was accepted' }
$failed = $false
try { Get-PythonInstaller $html '3.12.10' | Out-Null } catch { $failed = $true }
if (-not $failed) { throw 'Unavailable version was accepted' }
foreach ($file in @('setup.ps1', 'bootstrap-functions.ps1')) {
    $tokens = $null; $errors = $null
    [Management.Automation.Language.Parser]::ParseFile((Join-Path $PSScriptRoot $file), [ref]$tokens, [ref]$errors) | Out-Null
    if ($errors.Count) { throw ($errors | Out-String) }
}
Write-Host 'PASS: version selection, prerelease/host/architecture exclusion, missing releases, PowerShell syntax.'
