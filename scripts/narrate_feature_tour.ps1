param([Parameter(Mandatory = $true)][string]$OutputDirectory)

Add-Type -AssemblyName System.Speech
New-Item -ItemType Directory -Force -Path $OutputDirectory | Out-Null
$voice = New-Object System.Speech.Synthesis.SpeechSynthesizer
$voice.SelectVoice('Microsoft Zira Desktop')
$voice.Rate = 2
$voice.Volume = 95
$lines = @(
  'Meet the bottle with an identity crisis. Blue bin? Green bin? Even the bins look confused.',
  'BinWise starts with one clear photo. One item at a time, please. No group selfies for garbage.',
  'The app suggests a material. Here, a real cardboard photo becomes a dry waste sorting step after the preparation check.',
  'Photo too dark, tiny, or blurry? BinWise asks for another shot. The camera does not get a participation trophy.',
  'If the material is uncertain, you choose it yourself. No confident match means no automatic bin advice.',
  'Before dry waste advice, answer two little questions. Empty? Free of food and liquid? If unsure, check locally first.',
  'No camera? Type the item or tap a common choice. The typed route sends no photo at all.',
  'A battery is not an ordinary bin guest. BinWise points it to special care guidance, with local handover rules.',
  'Switch to Hindi, and press read aloud. Sorting help should be easy to hear as well as read.',
  'The guide can create a QR card for sharing. Use a reachable link when you want phones to open it.',
  'Spot a mistake? Mark it correct, change the material, or report a different local rule. Feedback saves no photo or name.',
  'BinWise gives India wide guidance. Example site profiles show how rules can vary. Your local collector decides the exact bin or pickup point. Check the signs, then sort with confidence.'
)

for ($i = 0; $i -lt $lines.Count; $i++) {
  $target = Join-Path $OutputDirectory ('voice-{0:D2}.wav' -f $i)
  $voice.SetOutputToWaveFile($target)
  $voice.Speak($lines[$i])
  $voice.SetOutputToNull()
}
$voice.Dispose()
