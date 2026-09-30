# Verifikasi integrasi Java443 — 30 September 2026

## Hasil implementasi dan pengujian

- Branch lokal `new`; delapan task implementasi memiliki commit terpisah: `437a5df`, `c07a0e0`, `72a092e`, `7da9c1f`, `1fa6116`, `400ef42`, `2f22dac`, `cca8ca2`.
- Full suite `manage.py test recommender.tests --noinput`: **184 tes lulus**, 56,448 detik, sesudah perbaikan review akhir. Pengujian memakai database sementara; tidak mengganti DB pengguna.
- `manage.py check`: tidak ada masalah; `makemigrations --check --dry-run`: tidak ada perubahan migration.
- Workflow tes meregenerasi output di direktori sementara, mengimpor 443 ID, melatih model, meminta rekomendasi, dan membuka peta. Tes menolak artefak usang serta memeriksa hash bukti dan notebook.
- Import ulang DB lokal: 443 input, 0 dibuat, 443 diperbarui, 0 dihapus; seluruh 443 label model dipertahankan. Sumber: 437 Kaggle dan 6 kurasi Jawa.
- Training aktual: 443 baris, k=2, silhouette 0,54302, anggota 414/29; bukan persentase akurasi. Tidak ada baris tambahan sintetis 1.900 dalam model aktif.
- Fingerprint preprocessing, laporan K-Means, dan DB cocok: `c3b2f4ead1b955ed41c4be8df4ee201a374a915a5eb10823f8f58c65ace25eac`.
- Hash 44 file sumber/bukti/DOCX diperiksa terhadap snapshot. `git cat-file --filters HEAD:<path>` juga menghasilkan seluruh hash yang sama: kebijakan checkout mempertahankan byte sumber.
- DOCX tidak diubah; SHA256 `34ee9ed27a65ce2233d0a58b04519119debf5411f42f2f4347ef81c2e7259304`.
- Backup sebelum migrasi `archive/local_backups/travelfit-before-java443-20260930T125839Z-120cd361.sqlite3`: `integrity_check=ok`, 2.337 baris destinasi. Backup diabaikan Git.
- Sebanyak 38 file lama diarsipkan dengan struktur relatif yang sama; lihat `docs/maintenance/java443-cleanup.md`. Tidak menghapus bukti sumber atau spreadsheet contoh SPK.

## Pemeriksaan browser nyata

Browser lokal `http://127.0.0.1:8000/`, bukan deployment publik. UI baru menggunakan arahan UI-UX Pro Max: hierarki editorial, formulir native, layout responsif, warna cream/teal, label dan fokus keyboard, serta pengurangan gerakan.

- Desktop 1.440 px, tablet 768 px, ponsel 375 px: tidak ada overflow horizontal.
- Submit AJAX: asal Serang, tujuan Banten, budget Rp20.000.000, profil Hemat, kategori alam/budaya → dua hasil, Tahura dan Museum Multatuli. Rincian komponen biaya dan sumber tiket terlihat; Tahura menampilkan rating model 4,5 dengan catatan imputasi, bukan rating Google palsu.
- Respons input tidak valid memberi pesan kesalahan, fokus ke ringkasan, dan tombol dapat dicoba kembali. Bobot profil dan slider khusus diuji; slider dapat dioperasikan keyboard.
- Link hasil menuju peta: daftar berisi 443 ID, 442 titik terlihat; Marina ID9 tetap di daftar dengan catatan konflik lokasi. Enam link provinsi diuji melalui keyboard; zoom, pan terbatas, drag ponsel, dan reset diuji.
- Tidak ada console error aplikasi dalam pemeriksaan akhir. Tangkapan layar hasil desktop dan peta ponsel diperiksa secara visual selama pengujian.
- Kemampuan browser yang tersedia tidak menyediakan emulasi JavaScript-disabled atau preferensi OS reduced-motion. Fallback POST server diuji otomatis; jangan menyebut keduanya sudah diuji manual pada OS.

## Keputusan pelaksanaan dan konsekuensi

1. Memakai checkout/branch pengguna tanpa worktree, sesuai permintaan. Konsekuensi: perubahan lain di checkout yang sama harus dipertahankan.
2. Menjalankan helper Bash dan tes di luar sandbox setelah kendala pipe/ACL Windows. Konsekuensi: cakupan eksekusi lebih luas; perintah tetap dibatasi repo dan pengujian lokal.
3. Menambah opsi importer `--backup-only` agar backup tersedia sebelum migration. Konsekuensi: ada satu opsi CLI tambahan, bukan perubahan isi data.
4. Menggunakan browser CUA yang tersedia karena agent-browser tidak tersedia; tidak memasang paket. Konsekuensi: emulasi media tertentu tidak tersedia.
5. Mempertahankan SVG lama dan memakai posisi titik pendekatan visual dengan label keterbatasan. Konsekuensi: peta tidak membuktikan batas administratif dan tidak cocok sebagai navigasi; koordinat data tidak diubah.
6. Mengarsipkan 38 path lama, bukan menghapus permanen, agar bukti sejarah dan fixture audit bisa dipulihkan. Konsekuensi: ukuran historis masih ada di repo.
7. Mengunci newline asli bukti melalui `.gitattributes`, termasuk receipt Nominatim CRLF. Konsekuensi: perubahan kebijakan harus disengaja saat bukti berubah.
8. Reviewer akhir menggunakan model warisan sesi karena aturan alat melarang override model tanpa permintaan pengguna. Konsekuensi: model reviewer tidak dipilih terpisah, tetapi konteks review tetap baru.

## Status review akhir

Review fresh-context read-only untuk range `36e166d..cca8ca2`: tidak ada temuan Critical; empat temuan Important diperbaiki dalam satu pass, masing-masing dibuktikan tes gagal dahulu lalu lulus. Tidak ada Minor yang ditangguhkan; tidak dilakukan review kedua.

| Temuan | Perbaikan dan bukti |
| --- | --- |
| POST/redirect dan error validasi kehilangan preferensi/bobot khusus | Simpan hanya field preferensi yang dideklarasikan (bukan CSRF), pertahankan hobi, profil, slider mentah dan penanda custom; dua tes regresi RED→GREEN |
| AJAX mengganti kartu tetapi tidak hasil peta inline | Kartu dan fragment rekomendasi peta berasal dari satu snapshot respons; tidak mengirim ulang seluruh 443 baris; tes fragment RED→GREEN dan browser menunjukkan hasil sama |
| Pencarian kosong menyisakan hasil lama | Kedua cabang filter membersihkan sesi dan fragment peta; tes normal/AJAX dan kedua filter RED→GREEN, browser budget0/10000 menunjukkan data peta `[]` |
| Label model tersimpan sebelum file laporan berhasil | Stage dan backup laporan sebelum mutasi; publication dalam transaksi, rollback dan restoration bila I/O atau exit transaksi gagal; tiga tes RED→GREEN, train lokal sukses ulang443 |

Tautan hasil peta dinamis memakai event delegation, sehingga hasil baru tetap membuka daftar dan memfokuskan ID438. Browser reload mempertahankan budget20.000.000/Serang/Hemat; console error kosong. `check` tetap bersih dan migration tidak berubah.

Perlindungan DB/file menangani error I/O/commit biasa; bukan transaksi dua fase yang menjamin atomicity lintas SQLite/filesystem saat listrik padam atau proses dibunuh. Jika restoration sendiri gagal, command menyebut lokasi backup dan berhenti; lakukan pemeriksaan sebelum menggunakan model.

Reviewer menyisihkan delapan area berikut; keputusan executor dan konsekuensinya tetap dicatat:

9. Tool arsip tidak dimodernisasi; inactive dan recovery/dependensi aktif diperiksa. Konsekuensi: reaktivasi perlu perbaikan path/dependensi.
10. GIS/batas provinsi presisi tetap tidak diklaim; koordinat asli dan label keterbatasan dipertahankan. Konsekuensi: peta bukan navigasi atau validasi batas.
11. Tidak memverifikasi ulang seluruh sumber eksternal secara live pada final code review; bukti tersimpan dan hash diperiksa. Konsekuensi: tarif/rating bisa berubah sesudah observasi.
12. Validitas survei/akurasi rekomendasi belum dibuktikan atau diklaim. Konsekuensi: masih perlu evaluasi empiris terhadap pengguna.
13. Semantik C4/aktivitas tetap heuristik yang disetujui dengan koreksi konteks teruji. Konsekuensi: false positive/negative masih mungkin.
14. DOCX tidak diperbarui karena di luar scope eksplisit. Konsekuensi: laporan lama belum mengikuti implementasi terbaru.
15. Deployment publik tidak dinilai; hanya development lokal. Konsekuensi: masih perlu hardening dan pemeriksaan release sebelum produksi.
16. Browser desktop/ponsel diuji, bukan eksekusi screen reader nyata atau jaminan uptime routing eksternal. Konsekuensi: perilaku assistive technology dan jaringan dapat berbeda.
17. Branch `new` dibiarkan lokal sesuai scope commit; tidak merge/push/deploy. Konsekuensi: remote belum diperbarui.
18. Scratch pelaksanaan dipindahkan secara recoverable ke `archive/local_backups/execution-java443-20260930` (diabaikan Git), bukan dihapus permanen. Konsekuensi: log audit masih memakai ruang disk lokal.

## Batasan data dan metode yang tetap berlaku

Kaggle adalah sumber komunitas, bukan seluruhnya data pemerintah. Enam tambahan menyimpan bukti tarif pemerintah, lokasi OSM, dan lima rating Google yang teramati. Tahura memakai median hanya untuk perhitungan; Marina mempertahankan koordinat sumber yang konflik. C4 adalah indikator penyebutan deskripsi, bukan audit kelengkapan fasilitas. Harga baseline dan parameter biaya perjalanan tidak diklaim sebagai harga terkini. Profil AHP belum hasil survei. Retensi 443 ID tidak membuktikan 443 objek unik atau cakupan merata seluruh Jawa.

Tidak dilakukan push, merge, PR, publikasi, atau perubahan laporan DOCX.
