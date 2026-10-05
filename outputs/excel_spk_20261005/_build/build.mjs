import fs from 'node:fs/promises';
import path from 'node:path';
import { Workbook, SpreadsheetFile } from '@oai/artifact-tool';
const dir=path.dirname(new URL(import.meta.url).pathname.replace(/^\/(.:)/,'$1'));
const src=JSON.parse(await fs.readFile(path.join(dir,'snapshot.json'),'utf8'));
const wb=Workbook.create();
const names=['Hasil','Input','AHP','Perhitungan','TOPSIS','Data443','Verifikasi'];
const sheets=Object.fromEntries(names.map(n=>[n,wb.worksheets.add(n)]));
const col=n=>{let s='';for(n++;n;n=Math.floor((n-1)/26))s=String.fromCharCode(65+(n-1)%26)+s;return s;};
const set=(s,r,c,v)=>s.getCell(r-1,c-1).values=[[v]];
const formula=(s,r,c,v)=>s.getCell(r-1,c-1).formulas=[[v]];
const title=(s,text,end='I',last=35)=>{
 s.showGridLines=false;
 s.getRange(`A1:${end}${last}`).format.font={name:'Arial',size:10,color:'#24334A'};
 s.getRange(`A1:${end}${last}`).format.rowHeight=23;
 s.getRange(`A1:${end}${last}`).format.verticalAlignment='center';
 s.getRange(`A1:${end}${last}`).format.columnWidth=18;
 set(s,2,1,text);s.getRange('A2').format.font={name:'Arial',size:16,bold:true,color:'#233E62'};
 s.getRange(`A3:${end}3`).format.borders={bottom:{style:'thin',color:'#BBC7D6'}};
};
const head=(s,row,labels,start=1)=>{
 s.getRangeByIndexes(row-1,start-1,1,labels.length).values=[labels];
 s.getRangeByIndexes(row-1,start-1,1,labels.length).format={fill:'#233E62',font:{name:'Arial',size:10,bold:true,color:'#FFFFFF'},wrapText:true,horizontalAlignment:'center',verticalAlignment:'center',rowHeight:38};
};
const num=(s,range,fmt='0.000000000000')=>s.getRange(range).setNumberFormat(fmt);
const band=(s,row,text,end='I')=>{set(s,row,1,text);s.getRange(`A${row}:${end}${row}`).format.fill='#EAF0F7';s.getRange(`A${row}`).format.font.bold=true;};
const records=src.master.filter(x=>x.provinsi===src.baseline.inputs.wilayah);
const count=records.length, first=9,last=first+count-1;
const masterIndex=new Map(src.master.map((r,i)=>[r.source_id,i+9]));
const tags=['belanja','berenang','budaya','camping','diving','edukasi','fotografi','hiking','kuliner','rekreasi_keluarga','religi','sejarah','snorkeling'];
const criteria=['Harga tiket','Rating perhitungan','Jarak garis lurus','Fasilitas','Kecocokan kategori','Kecocokan hobi'];
const raw=sheets.Data443;
title(raw,'Data sumber aktif — 437 Kaggle + 6 kurasi Jawa','AD',451);
set(raw,4,1,'Sumber: database aplikasi (Destination), data/processed/destinations_clean_java443.csv; snapshot '+src.timestamp);
set(raw,5,1,'Kaggle: https://www.kaggle.com/datasets/aprabowo/indonesia-tourism-destination | Kurasi: data/review/gabungan_jawa/Dokumentasi.md');
set(raw,6,1,'Tarif/rating adalah snapshot, bukan jaminan nilai terkini. Fasilitas & tag merupakan heuristik deskripsi. Rating imputasi ditandai.');
const dh=['Place_Id','Nama destinasi','Kota','Provinsi','Kategori','Harga tiket (Rp)','Rating asli','Rating model','Rating imputasi','Latitude','Longitude','Toilet','Parkir','Warung','Tempat ibadah','Aksesibilitas','Pusat informasi','Tag aktivitas','Cluster','Sumber dataset','Haversine Bandung (km)','Metode jarak','Waktu snapshot','Sumber tiket / URL','Sumber rating / URL','Catatan tarif','Catatan kualitas','Deskripsi','Sumber lokasi','Fingerprint'];
head(raw,8,dh);
const flagKeys=['fas_toilet','fas_parkir','fas_warung','fas_mushola','fas_accessibility','fas_information_center'];
raw.getRange(`A9:AD451`).values=src.master.map(d=>[d.source_id,d.nama,d.kota,d.provinsi,d.kategori,d.harga_tiket,d.rating,d.calculation_rating,d.rating_imputed?1:0,d.latitude,d.longitude,...flagKeys.map(k=>d[k]?1:0),d.tag_aktivitas,d.cluster_label,d.sumber_data,d.great_circle_km,'Haversine (garis lurus; bukan jalan)',src.timestamp,d.provenance?.ticket_source_url??'',d.provenance?.rating_source_url??'',d.provenance?.tariff_note??'',JSON.stringify(d.data_quality),d.description,d.provenance?.coordinate_source??'',d.pipeline_fingerprint]);
raw.getRange('B9:B451').format.columnWidth=48;
raw.getRange('R9:R451').format.columnWidth=42;
raw.getRange('X9:AD451').format.columnWidth=52;
num(raw,'F9:F451','"Rp "#,##0');num(raw,'G9:H451','0.0');num(raw,'J9:K451','0.0000000');num(raw,'U9:U451','0.000000000000');
num(raw,'W9:W451','yyyy-mm-dd hh:mm:ss');
raw.freezePanes.freezeRows(8);raw.freezePanes.freezeColumns(2);
raw.tables.add('A8:AD451',true,'MasterDestinasi443');

const inp=sheets.Input;
title(inp,'Input contoh dan aturan aplikasi','J',39);inp.tabColor='#496488';
inp.getRange('A5:A29').format.columnWidth=32;inp.getRange('B5:B29').format.columnWidth=28;
const iv={5:['Kota asal (snapshot tetap)','Bandung'],6:['Provinsi tujuan (tetap)','Jawa Barat'],7:['Budget tiket (Rp/orang)',1000000],9:['Profil AHP','hemat'],10:['Kategori utama','alam'],11:['Kategori sekunder','budaya'],14:['Latitude asal',src.origin[0]],15:['Longitude asal',src.origin[1]],22:['Radius bumi (km)',6371],23:['Skor kategori utama',1],24:['Skor kategori sekunder',0.5],25:['Skor kategori lain',0],26:['Pembagi fasilitas',6]};
for(const [r,a] of Object.entries(iv)){set(inp,+r,1,a[0]);set(inp,+r,2,a[1]);}
head(inp,13,['Hobi tersedia','Dipilih: 1/0'],6);
inp.getRange('F14:G26').values=tags.map(t=>[t,src.baseline.inputs.hobi.includes(t)?1:0]);
set(inp,28,1,'Jumlah hobi terpilih');formula(inp,28,2,'=SUM(G14:G26)');
head(inp,30,['Kode','Kriteria','Tipe'],6);inp.getRange('F31:H36').values=criteria.map((c,i)=>['C'+(i+1),c,[0,2].includes(i)?'cost':'benefit']);
inp.getRange('G30:G36').format.columnWidth=30;
inp.getRange('B7').format.fill='#FFF0C2';inp.getRange('B9:B11').format.fill='#FFF0C2';inp.getRange('G14:G26').format.fill='#FFF0C2';
inp.getRange('B9').dataValidation={rule:{type:'list',values:Object.keys(src.profiles)}};
for(const r of [10,11])inp.getRange(`B${r}`).dataValidation={rule:{type:'list',values:['alam','bahari','budaya','hiburan','belanja','religi']}};
inp.getRange('G14:G26').dataValidation={rule:{type:'whole',operator:'between',formula1:0,formula2:1}};
inp.getRange('B7').dataValidation={rule:{type:'whole',operator:'greaterThanOrEqual',formula1:0}};
num(inp,'B7','"Rp "#,##0');
set(inp,32,1,'Kuning: preferensi dapat diubah. Contoh tetap Bandung–Jawa Barat; koordinat asal dipakai formula Haversine.');
set(inp,34,1,'Budget hanya tiket satu destinasi/orang; tidak termasuk transport, makan atau penginapan. Rp0 menerima tiket gratis.');
set(inp,36,1,'C3: formula Haversine dari koordinat; garis lurus bukan jarak jalan. Acuan: recommender/spk/geo.py.');
set(inp,38,1,'Harga/rating memakai snapshot Data443. Jika sumber berubah, buat snapshot Excel baru untuk perbandingan setara.');

const ahp=sheets.AHP;
title(ahp,'AHP — dari perbandingan berpasangan ke bobot','L',52);
set(ahp,4,1,'Profil aktif');formula(ahp,4,2,'=Input!B9');
set(ahp,5,1,'Metode website: normalisasi per kolom, lalu rata-rata baris (bukan iterasi eigenvector).');
band(ahp,7,'1. Matriks perbandingan berpasangan','L');
head(ahp,8,['Kriteria','C1','C2','C3','C4','C5','C6']);
for(let i=0;i<6;i++){
 set(ahp,9+i,1,'C'+(i+1));
 for(let j=0;j<6;j++)formula(ahp,9+i,2+j,`=INDEX($B$47:$AK$50,MATCH(Input!$B$9,$A$47:$A$50,0),${i*6+j+1})`);
}
set(ahp,15,1,'Jumlah kolom');for(let j=0;j<6;j++)formula(ahp,15,2+j,`=SUM(${col(j+1)}9:${col(j+1)}14)`);
band(ahp,17,'2. Normalisasi AHP dan rata-rata baris','L');
head(ahp,18,['Kriteria','C1','C2','C3','C4','C5','C6','Bobot w','A × w','λ per baris']);
for(let i=0;i<6;i++){
 set(ahp,19+i,1,'C'+(i+1));
 for(let j=0;j<6;j++)formula(ahp,19+i,2+j,`=${col(j+1)}${9+i}/${col(j+1)}$15`);
 formula(ahp,19+i,8,`=AVERAGE(B${19+i}:G${19+i})`);
 formula(ahp,19+i,9,`=SUMPRODUCT(B${9+i}:G${9+i},$H$19:$H$24)`);
 // SUMPRODUCT requires equally oriented arrays: separate six visible terms.
 formula(ahp,19+i,9,`=B${9+i}*$H$19+C${9+i}*$H$20+D${9+i}*$H$21+E${9+i}*$H$22+F${9+i}*$H$23+G${9+i}*$H$24`);
 formula(ahp,19+i,10,`=I${19+i}/H${19+i}`);
}
set(ahp,25,1,'Jumlah bobot');formula(ahp,25,8,'=SUM(H19:H24)');
band(ahp,27,'3. Pemeriksaan konsistensi','L');
for(const [r,label] of [[29,'n kriteria'],[30,'λ maksimum'],[31,'Consistency Index (CI)'],[32,'Random Index (RI) n=6'],[33,'Consistency Ratio (CR)'],[34,'Ambang CR'],[35,'Status konsistensi']])set(ahp,r,1,label);
formula(ahp,29,2,'=ROWS(H19:H24)');formula(ahp,30,2,'=AVERAGE(J19:J24)');formula(ahp,31,2,'=(B30-B29)/(B29-1)');set(ahp,32,2,1.24);formula(ahp,33,2,'=B31/B32');set(ahp,34,2,0.1);formula(ahp,35,2,'=IF(B33<B34,"Konsisten","Tidak konsisten")');
num(ahp,'B9:G15');num(ahp,'B19:J25');num(ahp,'B30:B34');
set(ahp,38,1,'Bobot profil merupakan preset pengembang; bukan hasil survei responden.');
set(ahp,40,1,'Sumber metode/RI: recommender/spk/ahp.py; matriks preset: recommender/spk/profiles.py.');
band(ahp,44,'Sumber matriks preset — urutan C1C1, C1C2, …, C6C6','L');
head(ahp,46,['Profil',...Array.from({length:36},(_,i)=>`C${Math.floor(i/6)+1}/C${i%6+1}`)]);
Object.entries(src.matrices).forEach(([key,m],i)=>{
 set(ahp,47+i,1,key);
 for(let a=0;a<6;a++)for(let b=0;b<6;b++){
  const c=2+a*6+b;
  if(a<b)set(ahp,47+i,c,m[a][b]);
  else if(a===b)formula(ahp,47+i,c,'=1');
  else formula(ahp,47+i,c,`=1/${col(1+b*6+a)}${47+i}`);
 }
});
ahp.getRange('A9:A50').format.columnWidth=31;
ahp.getRange('B9:G24').format.columnWidth=18;
ahp.getRange('H19:J24').format.columnWidth=21;
ahp.getRange('B47:AK50').format.columnWidth=16;

const calc=sheets.Perhitungan;
title(calc,'Pembentukan C1–C6 dan seleksi budget','AI',last+3);
set(calc,4,1,'C1 = harga tiket asli. Budget menyaring tiket <= batas. C4 = jumlah indikator/6. C6 = irisan hobi ÷ gabungan tag.');
set(calc,5,1,'Semua 124 destinasi Jawa Barat ditampilkan; yang di luar budget tidak masuk normalisasi TOPSIS.');
head(calc,8,['Place_Id','Nama alternatif','Kategori','Tiket (Rp)','C2 Rating','C3 Jarak (km)','Haversine (km)','Rating imputasi 1/0','Koordinat review 1/0','Sumber dataset','C1 Tiket (Rp)','Sisa alokasi tiket (Rp)','Lolos? 1/0','Indikator fasilitas','C4 Fasilitas','C5 Kategori','Irisan hobi','Jumlah tag','Gabungan tag','C6 Jaccard','Status']);
head(calc,8,tags.map(t=>'Tag: '+t),23);
records.forEach((d,i)=>{
 const r=first+i,m=masterIndex.get(d.source_id),f=(c,x)=>formula(calc,r,c,x);
 ['A','B','E','F','H'].forEach((c,j)=>f(j+1,`=Data443!${c}${m}`));f(6,`=G${r}`);
 f(7,`=2*Input!$B$22*ASIN(SQRT(SIN(RADIANS(Data443!J${m}-Input!$B$14)/2)^2+COS(RADIANS(Input!$B$14))*COS(RADIANS(Data443!J${m}))*SIN(RADIANS(Data443!K${m}-Input!$B$15)/2)^2))`);
 f(8,`=Data443!I${m}`);set(calc,r,9,d.data_quality?.coordinate_review_required?1:0);f(10,`=Data443!T${m}`);
 f(11,`=D${r}`);f(12,`=Input!$B$7-K${r}`);
 f(13,`=IF(D${r}<=Input!$B$7,1,0)`);
 f(14,`=SUM(Data443!L${m}:Q${m})`);f(15,`=N${r}/Input!$B$26`);
 f(16,`=IF(C${r}=Input!$B$10,Input!$B$23,IF(C${r}=Input!$B$11,Input!$B$24,Input!$B$25))`);
 tags.forEach((t,j)=>f(23+j,`=IF(ISNUMBER(SEARCH("|"&Input!$F$${14+j}&"|","|"&Data443!R${m}&"|")),1,0)`));
 f(17,'=SUM('+tags.map((t,j)=>`Input!$G$${14+j}*${col(22+j)}${r}`).join(',')+')');
 f(18,`=IF(Data443!R${m}="",0,LEN(Data443!R${m})-LEN(SUBSTITUTE(Data443!R${m},"|",""))+1)`);
 f(19,`=Input!$B$28+R${r}-Q${r}`);f(20,`=IF(Input!$B$28=0,0,IF(S${r}=0,0,Q${r}/S${r}))`);
 f(21,`=IF(M${r}=1,"Dinilai","Di luar budget")`);
});
num(calc,`D9:D${last}`,'"Rp "#,##0');num(calc,`E9:G${last}`,'0.000000');num(calc,`H9:I${last}`,'0');num(calc,`K9:L${last}`,'"Rp "#,##0');num(calc,`O9:P${last}`);num(calc,`T9:T${last}`);
calc.getRange(`B8:B${last}`).format.columnWidth=46;calc.getRange(`H8:L${last}`).format.columnWidth=25;
calc.freezePanes.freezeRows(8);calc.freezePanes.freezeColumns(2);

const ts=sheets.TOPSIS;
title(ts,'TOPSIS — matriks sampai skor dan ranking','AL',last+5);
set(ts,4,1,'Tipe kriteria');for(let j=0;j<6;j++)formula(ts,4,3+j,`=Input!H${31+j}`);
set(ts,5,1,'Bobot AHP');for(let j=0;j<6;j++)formula(ts,5,3+j,`=AHP!H${19+j}`);
set(ts,6,10,'Penyebut √Σx²');
for(let j=0;j<6;j++)formula(ts,6,11+j,`=SQRT(SUMPRODUCT(${col(2+j)}$9:${col(2+j)}$${last},${col(2+j)}$9:${col(2+j)}$${last},$I$9:$I$${last}))`);
set(ts,5,17,'Ideal positif A+');set(ts,6,17,'Ideal negatif A−');
for(let j=0;j<6;j++){
 const v=col(17+j),type=col(2+j)+'$4',rng=`${v}$9:${v}$${last}`,minimum=`${col(31+j)}$9:${col(31+j)}$${last}`;
 formula(ts,5,18+j,`=IF(SUM($I$9:$I$${last})=0,0,IF(${type}="cost",MIN(${minimum}),MAX(${rng})))`);
 formula(ts,6,18+j,`=IF(SUM($I$9:$I$${last})=0,0,IF(${type}="cost",MAX(${rng}),MIN(${minimum})))`);
}
head(ts,8,['Place_Id','Nama alternatif','C1 Tiket','C2 Rating','C3 Jarak','C4 Fasilitas','C5 Kategori','C6 Hobi','Lolos 1/0']);
head(ts,8,['R1','R2','R3','R4','R5','R6'],11);head(ts,8,['V1','V2','V3','V4','V5','V6'],18);
head(ts,8,['D+','D−','Vi','Ranking','Vi website (%)','Tiket web (Rp)','Jarak web (km)'],25);
set(ts,8,38,'Sisa alokasi tiket (Rp)');num(ts,`AL9:AL${last}`,'"Rp "#,##0');
head(ts,8,['V1 untuk MIN','V2 untuk MIN','V3 untuk MIN','V4 untuk MIN','V5 untuk MIN','V6 untuk MIN'],32);
set(ts,last+3,1,'Helper MIN (AF–AK): kandidat tidak lolos diberi 1, karena 0 ≤ nilai V ≤ bobot ≤ 1. Dengan demikian kandidat gugur tidak mengubah minimum.');
for(let i=0;i<count;i++){
 const r=first+i,f=(c,x)=>formula(ts,r,c,x);
 f(1,`=Perhitungan!A${r}`);f(2,`=Perhitungan!B${r}`);
 ['K','E','F','O','P','T'].forEach((c,j)=>f(3+j,`=Perhitungan!${c}${r}`));f(9,`=Perhitungan!M${r}`);
 for(let j=0;j<6;j++){
  f(11+j,`=IF(AND($I${r}=1,${col(10+j)}$6<>0),${col(2+j)}${r}/${col(10+j)}$6,0)`);
  f(18+j,`=${col(10+j)}${r}*${col(2+j)}$5`);
  f(32+j,`=IF($I${r}=1,${col(17+j)}${r},1)`);
 }
 const distance=ideal=>'=IF(I'+r+'=1,SQRT('+Array.from({length:6},(_,j)=>`(${col(17+j)}${r}-${col(17+j)}$${ideal})^2`).join('+')+'),"")';
 f(25,distance(5));f(26,distance(6));f(27,`=IF(I${r}=1,IF(Y${r}+Z${r}=0,1,Z${r}/(Y${r}+Z${r})),"")`);
 f(28,`=IF(I${r}=1,COUNTIF($AA$9:$AA$${last},">"&AA${r})+COUNTIF($AA$9:AA${r},AA${r}),"")`);
 f(38,`=IF(I${r}=1,Input!$B$7-C${r},"")`);
 f(29,`=IF(I${r}=1,ROUND(AA${r}*100,2),"")`);f(30,`=IF(I${r}=1,INT(C${r}),"")`);f(31,`=IF(I${r}=1,ROUND(E${r},1),"")`);
}
num(ts,`C9:H${last}`);num(ts,`K5:W${last}`);num(ts,`Y9:AA${last}`);num(ts,`AB9:AB${last}`,'0');num(ts,`AC9:AC${last}`,'0.00');num(ts,`AD9:AD${last}`,'"Rp "#,##0');num(ts,`AE9:AE${last}`,'0.0');
ts.getRange(`B8:B${last}`).format.columnWidth=46;ts.getRange(`C8:H${last}`).format.columnWidth=23;ts.getRange(`K8:W${last}`).format.columnWidth=22;
ts.freezePanes.freezeRows(8);ts.freezePanes.freezeColumns(2);

const out=sheets.Hasil;
title(out,'TravelFit — bukti perhitungan AHP–TOPSIS','I',39);out.tabColor='#233E62';
set(out,4,1,'Kota asal');formula(out,4,3,'=Input!B5');set(out,5,1,'Wilayah tujuan');formula(out,5,3,'=Input!B6');set(out,6,1,'Profil');formula(out,6,3,'=Input!B9');
set(out,4,5,'Budget (Rp/orang)');formula(out,4,7,'=Input!B7');set(out,5,5,'Alternatif lolos');formula(out,5,7,`=SUM(Perhitungan!M9:M${last})`);
set(out,6,5,'Alternatif dinilai sebelum Top 10');set(out,6,7,count);
head(out,9,['Rank','Place_Id','Nama alternatif','Vi (presisi penuh)','Skor website','Sisa alokasi tiket (Rp)','Tiket web (Rp)','Garis lurus (km)','Jarak web (km)']);
for(let r=10;r<=19;r++){
 set(out,r,1,r-9);
 for(const [c,target] of [[2,'A'],[3,'B'],[4,'AA'],[5,'AC'],[6,'AL'],[7,'AD'],[8,'E'],[9,'AE']]){
  formula(out,r,c,`=IF($A${r}<=$G$5,INDEX(TOPSIS!$${target}$9:$${target}$${last},MATCH($A${r},TOPSIS!$AB$9:$AB$${last},0)),"")`);
 }
}
num(out,'D10:D19');num(out,'E10:E19','0.00"%"');num(out,'F10:F19','"Rp "#,##0');num(out,'G10:G19','"Rp "#,##0');num(out,'G4','"Rp "#,##0');num(out,'H10:H19','0.000000');num(out,'I10:I19','0.0');
out.getRange('A4:A19').format.columnWidth=23;out.getRange('B9:B19').format.columnWidth=14;out.getRange('C4:C23').format.columnWidth=48;out.getRange('D9:F19').format.columnWidth=24;out.getRange('G9:I19').format.columnWidth=22;
band(out,22,'Alternatif terbaik');formula(out,23,3,'=IF(G5>0,C10,"Tidak ada alternatif yang lolos budget")');out.getRange('C23').format.font.bold=true;
set(out,26,1,'Urutan proses: Data443 → Perhitungan C1–C6 & budget → AHP → TOPSIS → Hasil.');
set(out,28,1,'Normalisasi TOPSIS memakai norma vektor, bukan Z-score atau P99 K-Means. Semua kandidat lolos dinilai sebelum mengambil Top 10.');
set(out,30,1,'Tiket web memakai INT; harga sumber tetap utuh. Skor website = ROUND(Vi × 100, 2). Sisa hanya alokasi tiket.');
set(out,32,1,'Jika skor tepat sama, ranking mengikuti urutan kandidat asli, seperti stable sort pada Python.');
set(out,34,1,'Kesetaraan berlaku untuk input dan data yang sama. Excel dan website menghitung Haversine, tanpa layanan routing.');
set(out,36,1,'C4 dan tag aktivitas tidak berarti audit fasilitas lapangan. Harga dari Kaggle tidak otomatis merupakan tarif resmi terkini.');
set(out,38,1,'K-Means memberi konteks kelompok destinasi; pada kode saat ini, label cluster tidak digunakan untuk menyaring ranking TOPSIS.');

const audit=sheets.Verifikasi;
title(audit,'Verifikasi terhadap eksekusi view website','R',last+7);
set(audit,4,1,'Snapshot (UTC)');set(audit,4,3,new Date(src.timestamp));num(audit,'C4','yyyy-mm-dd hh:mm:ss');
const inputChecks=[`Input!B5="Bandung"`,`Input!B6="Jawa Barat"`,`Input!B7=1000000`,`Input!B9="hemat"`,`Input!B10="alam"`,`Input!B11="budaya"`,...tags.map((t,i)=>`Input!G${14+i}=${src.baseline.inputs.hobi.includes(t)?1:0}`)];
set(audit,5,1,'Baseline masih aktif?');formula(audit,5,3,`=AND(${inputChecks.join(',')})`);set(audit,6,1,'Batas beda numerik');set(audit,6,3,1e-12);
head(audit,8,['Place_Id','Nama','Vi website mentah','Vi Excel','|Selisih Vi|','Rank website penuh','Rank Excel','Tiket web referensi','Tiket web Excel','Max beda C1–C6','Status baseline']);
const expected=src.baseline.calculation;
const ranks=new Map(expected.rank.map((r,i)=>[r.idx,i+1]));
records.forEach((d,i)=>{
 const r=first+i;set(audit,r,1,d.source_id);set(audit,r,2,d.nama);set(audit,r,3,expected.rank.find(x=>x.idx===i).vi);formula(audit,r,4,`=TOPSIS!AA${r}`);formula(audit,r,5,`=ABS(C${r}-D${r})`);set(audit,r,6,ranks.get(i));formula(audit,r,7,`=TOPSIS!AB${r}`);set(audit,r,8,Math.trunc(expected.matrix[i][0]));formula(audit,r,9,`=TOPSIS!AD${r}`);
 expected.matrix[i].forEach((v,j)=>set(audit,r,13+j,v));
 formula(audit,r,10,'=MAX('+Array.from({length:6},(_,j)=>`ABS(${col(12+j)}${r}-TOPSIS!${col(2+j)}${r})`).join(',')+')');
 formula(audit,r,11,`=IF(NOT($C$5),"Input berbeda",IF(AND(E${r}<=$C$6,F${r}=G${r},H${r}=I${r},J${r}<=0.00000001),"Sesuai","Periksa"))`);
});
head(audit,8,['C1 referensi','C2 referensi','C3 referensi','C4 referensi','C5 referensi','C6 referensi'],13);
set(audit,last+3,1,'Referensi: eksekusi view Django asli tanpa mengubah perhitungan, data atau database. Seluruh 124 kandidat baseline dibandingkan.');
set(audit,last+5,1,'Perbandingan urutan dan tampilan harus tepat sama. Vi: toleransi 10⁻¹² karena operasi floating-point Python/Excel. C1–C6: toleransi 10⁻⁸.');
audit.getRange(`B8:B${last}`).format.columnWidth=46;audit.getRange(`C8:K${last}`).format.columnWidth=25;num(audit,`C9:E${last}`);num(audit,`H9:I${last}`,'"Rp "#,##0');num(audit,`J9:J${last}`,'0.00E+00');num(audit,'C6','0.00E+00');
audit.getRange(`K9:K${last}`).conditionalFormats.add('containsText',{text:'Periksa',format:{fill:'#FDE9E7',font:{color:'#9A2222',bold:true}}});
audit.freezePanes.freezeRows(8);audit.freezePanes.freezeColumns(2);

wb.recalculate();
console.log((await wb.inspect({kind:'table',range:'Hasil!A9:I19',include:'values,formulas',tableMaxRows:11,tableMaxCols:9,maxChars:3000})).ndjson);
console.log((await wb.inspect({kind:'match',searchTerm:'#REF!|#DIV/0!|#VALUE!|#NAME\\?|#N/A|#NUM!|#NULL!',options:{useRegex:true,maxResults:20},summary:'Formula errors',maxChars:2500})).ndjson);
const ranges={Hasil:'A1:I23',Input:'A1:H29',AHP:'A7:J35',Perhitungan:'A1:H15',TOPSIS:'R4:AE16',Data443:'A1:I15',Verifikasi:'A1:K15'};
for(const [name,range] of Object.entries(ranges)){
 const blob=await wb.render({sheetName:name,range,scale:1.4,format:'png'});
 await fs.writeFile(path.join(dir,`preview_${name}.png`),new Uint8Array(await blob.arrayBuffer()));
}
await (await SpreadsheetFile.exportXlsx(wb)).save(path.join(dir,'..','Perhitungan_AHP_TOPSIS_TravelFit.xlsx'));
console.log('Exported XLSX.');
