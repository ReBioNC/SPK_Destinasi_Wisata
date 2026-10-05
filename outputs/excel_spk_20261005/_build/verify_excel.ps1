$ErrorActionPreference = 'Stop'
$taskBuild = $PSScriptRoot
$taskSnapshot = Get-Content -LiteralPath (Join-Path $taskBuild 'snapshot.json') -Raw | ConvertFrom-Json
$taskPath = [System.IO.Path]::GetFullPath((Join-Path $taskBuild '../Perhitungan_AHP_TOPSIS_TravelFit.xlsx'))
$taskExcel = New-Object -ComObject Excel.Application
$taskBook = $null
$taskProof = [System.Collections.Generic.List[object]]::new()
try {
    $taskExcel.Visible = $false
    $taskExcel.DisplayAlerts = $false
    $taskExcel.AskToUpdateLinks = $false
    $taskBook = $taskExcel.Workbooks.Open($taskPath, 0, $false)
    $taskInputs = $taskBook.Worksheets.Item('Input')
    $taskResults = $taskBook.Worksheets.Item('Hasil')
    $taskTopsis = $taskBook.Worksheets.Item('TOPSIS')
    $taskAhp = $taskBook.Worksheets.Item('AHP')
    $taskCount = 124
    $taskTags = @('belanja','berenang','budaya','camping','diving','edukasi','fotografi','hiking','kuliner','rekreasi_keluarga','religi','sejarah','snorkeling')
    $taskCases = @($taskSnapshot.tests) + @($taskSnapshot.baseline)
    foreach ($taskCase in $taskCases) {
        $taskPrefs = $taskCase.inputs
        $taskInputs.Range('B7').Value2 = [double]$taskPrefs.budget
        $taskInputs.Range('B9').Value2 = [string]$taskPrefs.profil
        $taskInputs.Range('B10').Value2 = [string]$taskPrefs.kategori_utama
        $taskInputs.Range('B11').Value2 = [string]$taskPrefs.kategori_sekunder
        for ($taskI=0; $taskI -lt $taskTags.Count; $taskI++) {
            $taskInputs.Cells.Item(14+$taskI,7).Value2 = [double][int](@($taskPrefs.hobi) -contains $taskTags[$taskI])
        }
        $taskExcel.CalculateFullRebuild()
        $taskObservedCount = [int]$taskResults.Range('G5').Value2
        if ($taskObservedCount -ne $taskCase.candidate_count) { throw "Candidate count differs: $taskObservedCount / $($taskCase.candidate_count)" }
        $taskDisplay = $taskResults.Range('A10:I19').Value2
        Write-Output ([pscustomobject]@{profile=$taskPrefs.profil;observed_id=$taskDisplay[1,2];expected_id=$taskCase.results[0].source_id;ideal=$taskTopsis.Range('R5').Text;weight=$taskAhp.Range('H19').Text;score=$taskResults.Range('D10').Text;jaccard=$taskBook.Worksheets.Item('Perhitungan').Range('T64').Text} | ConvertTo-Json -Compress)
        $taskMaxDifference = 0.0
        for ($taskI=0; $taskI -lt @($taskCase.results).Count; $taskI++) {
            $taskExpected = $taskCase.results[$taskI]
            if ([int]$taskDisplay[($taskI+1),2] -ne $taskExpected.source_id) { throw "Ranking differs on $($taskPrefs.profil) at $taskI" }
            $taskDelta = [math]::Abs([double]$taskDisplay[($taskI+1),4] - $taskExpected.vi)
            $taskMaxDifference = [math]::Max($taskMaxDifference,$taskDelta)
            if ($taskDelta -gt 1e-12) { throw "Vi differs $taskDelta" }
            if ([double]$taskDisplay[($taskI+1),5] -ne $taskExpected.vi_pct) { throw 'Display percentage differs' }
            if ([double]$taskDisplay[($taskI+1),7] -ne $taskExpected.harga) { throw 'Display ticket differs' }
            if ([double]$taskDisplay[($taskI+1),6] -ne $taskExpected.sisa_budget) { throw 'Remaining ticket allocation differs' }
            if ([double]$taskDisplay[($taskI+1),9] -ne $taskExpected.jarak_km) { throw 'Display distance differs' }
        }
        $taskWeights = $taskAhp.Range('H19:H24').Value2
        for ($taskI=0; $taskI -lt 6; $taskI++) {
            $taskTarget = $taskSnapshot.profiles.($taskPrefs.profil).weights[$taskI]
            if ([math]::Abs($taskWeights[($taskI+1),1]-$taskTarget) -gt 1e-12) { throw 'Weight differs' }
        }
        if ($taskObservedCount -gt 0) {
            $taskMatrix = $taskTopsis.Range('C9:I132').Value2
            $taskJ=0
            for ($taskI=1; $taskI -le $taskCount; $taskI++) {
                if ($taskMatrix[$taskI,7] -eq 1) {
                    for ($taskK=1; $taskK -le 6; $taskK++) {
                        if ([math]::Abs($taskMatrix[$taskI,$taskK]-$taskCase.calculation.matrix[$taskJ][$taskK-1]) -gt 1e-8) { throw "Criterion C$taskK differs at $taskI" }
                    }
                    $taskJ++
                }
            }
        }
        $taskProof.Add([pscustomobject]@{profile=$taskPrefs.profil;budget=$taskPrefs.budget;hobbies=@($taskPrefs.hobi);candidates=$taskObservedCount;top10_order_display_exact=$true;max_vi_difference=$taskMaxDifference})
    }
    $taskAudit = $taskBook.Worksheets.Item('Verifikasi').Range('K9:K132').Value2
    for ($taskI=1; $taskI -le $taskCount; $taskI++) { if ($taskAudit[$taskI,1] -ne 'Sesuai') { throw "Baseline audit failed at $taskI" } }
    $taskBook.Save()
    $taskProof | ConvertTo-Json -Depth 8 | Set-Content -LiteralPath (Join-Path $taskBuild 'native_verification.json') -Encoding utf8
    [pscustomobject]@{engine=$taskExcel.Version;tested_cases=$taskProof.Count;all_124_baseline_rows_match=$true;winner=$taskResults.Range('C10').Value2;file=$taskPath} | ConvertTo-Json
} finally {
    if ($null -ne $taskBook) { $taskBook.Close($false); [System.Runtime.InteropServices.Marshal]::FinalReleaseComObject($taskBook) | Out-Null }
    $taskExcel.Quit()
    [System.Runtime.InteropServices.Marshal]::FinalReleaseComObject($taskExcel) | Out-Null
}
