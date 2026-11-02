param([string]$DeckRoot = (Split-Path $PSScriptRoot -Parent))
$ErrorActionPreference='Stop'
$repoRoot=Split-Path $DeckRoot -Parent
$fontRoot=Join-Path $repoRoot 'runtime/pitch-build/fonts'
Add-Type @'
using System;
using System.Runtime.InteropServices;
public class PitchFonts {
 [DllImport("gdi32.dll", CharSet=CharSet.Unicode)] public static extern int AddFontResourceEx(string name, uint flags, IntPtr reserved);
 [DllImport("gdi32.dll", CharSet=CharSet.Unicode)] public static extern bool RemoveFontResourceEx(string name, uint flags, IntPtr reserved);
 [DllImport("user32.dll",CharSet=CharSet.Unicode)] public static extern IntPtr SendMessageTimeout(IntPtr hwnd,uint msg,IntPtr wparam,IntPtr lparam,uint flags,uint timeout,out IntPtr result);
}
'@
$fonts=Get-ChildItem $fontRoot -Filter '*.ttf'
$registered=@()
foreach($font in $fonts){ $count=[PitchFonts]::AddFontResourceEx($font.FullName,0,[IntPtr]::Zero); if($count -lt 1){throw "Font registration failed: $($font.Name)"}; $registered += $font.FullName }
$dummy=[IntPtr]::Zero
[PitchFonts]::SendMessageTimeout([IntPtr]0xffff,0x001D,[IntPtr]::Zero,[IntPtr]::Zero,2,1000,[ref]$dummy) | Out-Null
$app=$null;$deck=$null
try {
 $app=New-Object -ComObject PowerPoint.Application
 $deck=$app.Presentations.Open((Join-Path $DeckRoot 'STEPLOCK_Speedrun_SR008.pptx'),0,0,0)
 $report=@();$overflow=@()
 for($i=1;$i -le $deck.Slides.Count;$i++){
  $slide=$deck.Slides.Item($i)
  $slide.SlideShowTransition.EntryEffect=1793
  $slide.SlideShowTransition.AdvanceOnClick=-1
  $slide.Export((Join-Path $DeckRoot ('previews/slide-{0:D2}.png' -f $i)),'PNG',1920,1080)
  $nativeText=0;$charts=0;$tables=0;$images=0
  for($j=1;$j -le $slide.Shapes.Count;$j++){
   $shape=$slide.Shapes.Item($j)
   if($shape.Type -eq 13){$images++}
   if($shape.HasChart -eq -1){$charts++}
   if($shape.HasTable -eq -1){$tables++}
   if($shape.HasTextFrame -eq -1 -and $shape.TextFrame.HasText -eq -1){
    $nativeText++
    $range=$shape.TextFrame.TextRange
    if($range.BoundHeight -gt ($shape.Height+3)){$overflow += @{slide=$i;shape=$j;text=$range.Text;bound=[math]::Round($range.BoundHeight,2);height=[math]::Round($shape.Height,2)}}
   }
  }
  $report += @{slide=$i;native_text_shapes=$nativeText;native_charts=$charts;native_tables=$tables;image_shapes=$images;shapes=$slide.Shapes.Count}
 }
 $deck.Save()
 $deck.SaveAs((Join-Path $DeckRoot 'STEPLOCK_Speedrun_SR008.pdf'),32)
 @{renderer='Microsoft PowerPoint 16 via COM';slides=$deck.Slides.Count;width_pt=$deck.PageSetup.SlideWidth;height_pt=$deck.PageSetup.SlideHeight;render_px=@(1920,1080);font_registration='Session-only GDI from existing Fontsource subsets; no standalone fonts distributed';slides_report=$report;text_height_warnings=$overflow} | ConvertTo-Json -Depth 8 | Set-Content -Encoding utf8 (Join-Path $repoRoot 'runtime/pitch-build/powerpoint-render.json')
 Write-Output ('Rendered '+$deck.Slides.Count+' slides; text-height warnings: '+$overflow.Count)
} finally {
 if($deck){$deck.Close();[Runtime.InteropServices.Marshal]::ReleaseComObject($deck)|Out-Null}
 if($app){[Runtime.InteropServices.Marshal]::ReleaseComObject($app)|Out-Null}
 foreach($font in $registered){[PitchFonts]::RemoveFontResourceEx($font,0,[IntPtr]::Zero)|Out-Null}
}
