param([Parameter(Mandatory=$true)][string]$DocumentPath,
      [Parameter(Mandatory=$true)][string]$PdfPath)
$ErrorActionPreference = 'Stop'
$wordApp = $null
$wordDoc = $null
try {
    $wordApp = New-Object -ComObject Word.Application
    $wordApp.Visible = $false
    $wordApp.DisplayAlerts = 0
    $wordApp.AutomationSecurity = 3
    $wordDoc = $wordApp.Documents.Open($DocumentPath, $false, $false)
    Write-Output ('WORD_OPEN: ' + $wordDoc.FullName + ' ReadOnly=' + $wordDoc.ReadOnly)
    $wordDoc.Fields.Update() | Out-Null
    foreach ($tocItem in $wordDoc.TablesOfContents) { $tocItem.Update() }
    foreach ($tocItem in $wordDoc.TablesOfContents) {
        $tocItem.Range.ParagraphFormat.SpaceBefore = 0
        $tocItem.Range.ParagraphFormat.SpaceAfter = 0
        $tocItem.Range.ParagraphFormat.LineSpacingRule = 5
        $tocItem.Range.ParagraphFormat.LineSpacing = 13.8
    }
    $wordDoc.Repaginate()
    foreach ($tocItem in $wordDoc.TablesOfContents) { $tocItem.UpdatePageNumbers() }
    $savedPath = [IO.Path]::Combine([IO.Path]::GetDirectoryName([IO.Path]::GetDirectoryName($DocumentPath)), 'Laporan_UTS_TravelFit.docx')
    $wordDoc.SaveAs2($savedPath, 16)
    Write-Output ('WORD_SAVED_AS: ' + $savedPath)
    $wordDoc.ExportAsFixedFormat($PdfPath, 17)
    Write-Output ('WORD_RENDER_PAGES: ' + $wordDoc.ComputeStatistics(2))
} finally {
    if ($null -ne $wordDoc) { $wordDoc.Close(0); [void][Runtime.InteropServices.Marshal]::ReleaseComObject($wordDoc) }
    if ($null -ne $wordApp) { $wordApp.Quit(); [void][Runtime.InteropServices.Marshal]::ReleaseComObject($wordApp) }
    [GC]::Collect()
    [GC]::WaitForPendingFinalizers()
}
