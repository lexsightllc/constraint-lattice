#!/usr/bin/env pwsh
param([Parameter(ValueFromRemainingArguments=$true)][string[]]$Args)
$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
& "$ScriptDir/typecheck" @Args
exit $LASTEXITCODE
