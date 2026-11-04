param([Parameter(Mandatory = $true)][string]$OutputDirectory)

Add-Type -AssemblyName System.Speech
New-Item -ItemType Directory -Force -Path $OutputDirectory | Out-Null
$voice = New-Object System.Speech.Synthesis.SpeechSynthesizer
$voice.SelectVoice('Microsoft Zira Desktop')
$voice.Rate = 2
$voice.Volume = 100
$lines = @(
  'One bottle. Two bins. A tiny identity crisis.',
  'Snap one clear item. BinWise looks for the material.',
  'Too dark or blurry? Retake. Even robots need glasses.',
  'Cardboard? Check it is clean. Then follow the dry waste guide.',
  'When unsure, BinWise asks you. No risky bin guess.',
  'No camera? Type or tap a common item. No photo is sent.',
  'Battery says: I am special! Keep it out of regular bins.',
  'Hindi guidance? Yes. And the app can read it aloud.',
  'Share the sourced guide with a QR card and a reachable link.',
  'A wrong answer? Report the material or local rule.',
  'India wide guidance is a start. Your local signs have the final word.',
  'BinWise: know where it goes. Built by Hridya Jain. No battery tantrums, please.'
)

for ($i = 0; $i -lt $lines.Count; $i++) {
  $target = Join-Path $OutputDirectory ('voice-{0:D2}.wav' -f $i)
  $voice.SetOutputToWaveFile($target)
  $voice.Speak($lines[$i])
  $voice.SetOutputToNull()
}
$voice.Dispose()
