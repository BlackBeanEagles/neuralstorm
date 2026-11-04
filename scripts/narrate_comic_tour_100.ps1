param([Parameter(Mandatory = $true)][string]$OutputDirectory)

$ErrorActionPreference = 'Stop'
Add-Type -AssemblyName System.Runtime.WindowsRuntime
New-Item -ItemType Directory -Force -Path $OutputDirectory | Out-Null

$voiceType = [Windows.Media.SpeechSynthesis.SpeechSynthesizer,Windows.Media.SpeechSynthesis,ContentType=WindowsRuntime]
$streamType = [Windows.Media.SpeechSynthesis.SpeechSynthesisStream,Windows.Media.SpeechSynthesis,ContentType=WindowsRuntime]
$synth = [Activator]::CreateInstance($voiceType)
$voice = $voiceType::AllVoices | Where-Object DisplayName -eq 'Microsoft Heera' | Select-Object -First 1
if (-not $voice) {
  $voice = $voiceType::AllVoices | Where-Object DisplayName -eq 'Microsoft Zira' | Select-Object -First 1
}
if (-not $voice) { throw 'No supported English Windows speech voice is installed.' }
$synth.Voice = $voice
$synth.Options.SpeakingRate = 1.10
$synth.Options.AudioVolume = 0.95

$asTask = [System.WindowsRuntimeSystemExtensions].GetMethods() | Where-Object {
  $_.Name -eq 'AsTask' -and $_.IsGenericMethodDefinition -and
  $_.GetGenericArguments().Count -eq 1 -and $_.GetParameters().Count -eq 1
} | Select-Object -First 1
$asTask = $asTask.MakeGenericMethod($streamType)

$lines = @(Get-Content (Join-Path $PSScriptRoot 'comic_tour_100_narration.txt') -Encoding UTF8 |
  Where-Object { $_.Trim() })
if ($lines.Count -ne 16) { throw 'Expected exactly 16 narration lines.' }

try {
  for ($i = 0; $i -lt $lines.Count; $i++) {
    $operation = $synth.SynthesizeTextToStreamAsync($lines[$i])
    $task = $asTask.Invoke($null, @($operation))
    $task.Wait()
    $stream = $task.Result
    $reader = [System.IO.WindowsRuntimeStreamExtensions]::AsStreamForRead($stream)
    $target = Join-Path $OutputDirectory ('voice-{0:D2}.wav' -f $i)
    $output = [System.IO.File]::Create($target)
    try { $reader.CopyTo($output) }
    finally { $output.Dispose(); $reader.Dispose(); $stream.Dispose() }
    Write-Host ('Narrated scene {0}/16 with {1}' -f ($i + 1), $voice.DisplayName)
  }
}
finally { $synth.Dispose() }
