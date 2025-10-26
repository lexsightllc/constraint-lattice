#!/usr/bin/env pwsh
param([Parameter(ValueFromRemainingArguments=$true)][string[]]$Args)
$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
& "$ScriptDir/dev" @Args
exit $LASTEXITCODE
