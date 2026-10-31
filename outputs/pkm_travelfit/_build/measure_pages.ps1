param([Parameter(Mandatory=$true)][string]$DocumentPath,
      [Parameter(Mandatory=$true)][string]$PagesJson,
      [string]$PdfPath = '')
# Ukur nomor halaman judul bab/subbab, judul gambar/tabel dan lampiran dengan Word,
# lalu (opsional) ekspor PDF untuk pemeriksaan visual. Dokumen tidak disimpan ulang.
$ErrorActionPreference = 'Stop'
$wordApp = $null
$wordDoc = $null
try {
    $wordApp = New-Object -ComObject Word.Application
    $wordApp.Visible = $false
    $wordApp.DisplayAlerts = 0
    $wordApp.AutomationSecurity = 3
    $wordDoc = $wordApp.Documents.Open($DocumentPath, $false, $true)
    $wordDoc.Repaginate()
    $pages = [ordered]@{}
    $pattern = '^(BAB \d+\. |\d+\.\d+ |DAFTAR PUSTAKA$|LAMPIRAN$|Lampiran \d+\. |Gambar \d+\. |Tabel \d+\. )'
    foreach ($paragraph in $wordDoc.Paragraphs) {
        $text = $paragraph.Range.Text.Trim([char]13, [char]7, ' ')
        if ($text.Contains("`t") -or -not ($text -match $pattern)) { continue }
        if (-not $pages.Contains($text)) {
            # 1 = wdActiveEndAdjustedPageNumber (mengikuti penomoran per section)
            $pages[$text] = [int]$paragraph.Range.Information(1)
        }
    }
    $json = $pages | ConvertTo-Json
    [IO.File]::WriteAllText($PagesJson, $json, (New-Object Text.UTF8Encoding($false)))
    Write-Output ('HEADINGS_MEASURED: ' + $pages.Count)
    Write-Output ('PAGES_TOTAL: ' + $wordDoc.ComputeStatistics(2))
    if ($PdfPath) { $wordDoc.ExportAsFixedFormat($PdfPath, 17); Write-Output ('PDF: ' + $PdfPath) }
} finally {
    if ($null -ne $wordDoc) { $wordDoc.Close(0); [void][Runtime.InteropServices.Marshal]::ReleaseComObject($wordDoc) }
    if ($null -ne $wordApp) { $wordApp.Quit(); [void][Runtime.InteropServices.Marshal]::ReleaseComObject($wordApp) }
}
