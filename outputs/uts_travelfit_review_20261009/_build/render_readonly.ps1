param([Parameter(Mandatory=$true)][string]$DocumentPath,
      [Parameter(Mandatory=$true)][string]$PdfPath)
$ErrorActionPreference = 'Stop'
$travelFitWord = $null
$travelFitDocument = $null
try {
    $travelFitWord = New-Object -ComObject Word.Application
    $travelFitWord.Visible = $false
    $travelFitWord.DisplayAlerts = 0
    $travelFitWord.AutomationSecurity = 3
    $travelFitDocument = $travelFitWord.Documents.Open($DocumentPath, $false, $true)
    $travelFitDocument.Repaginate()
    $travelFitDocument.ExportAsFixedFormat($PdfPath, 17)
    Write-Output ('RENDER_PAGES: ' + $travelFitDocument.ComputeStatistics(2))
} finally {
    if ($null -ne $travelFitDocument) { $travelFitDocument.Close(0); [void][Runtime.InteropServices.Marshal]::ReleaseComObject($travelFitDocument) }
    if ($null -ne $travelFitWord) { $travelFitWord.Quit(); [void][Runtime.InteropServices.Marshal]::ReleaseComObject($travelFitWord) }
    [GC]::Collect()
    [GC]::WaitForPendingFinalizers()
}
