
const PROVINSI = [{"nama": "Aceh", "pulau": "Sumatera", "kode": "11", "ibukota": "Banda Aceh", "slug": "aceh", "cx": 58.7, "cy": 63.6}, {"nama": "Bali", "pulau": "Bali-Nusa Tenggara", "kode": "51", "ibukota": "Denpasar", "slug": "bali", "cx": 434.0, "cy": 363.3}, {"nama": "Banten", "pulau": "Jawa", "kode": "36", "ibukota": "Serang", "slug": "banten", "cx": 245.3, "cy": 313.8}, {"nama": "Bengkulu", "pulau": "Sumatera", "kode": "17", "ibukota": "Bengkulu", "slug": "bengkulu", "cx": 169.5, "cy": 245.2}, {"nama": "DKI Jakarta", "pulau": "Jawa", "kode": "31", "ibukota": "Jakarta", "slug": "dki-jakarta", "cx": 259.8, "cy": 308.1}, {"nama": "Daerah Istimewa Yogyakarta", "pulau": "Jawa", "kode": "34", "ibukota": "Yogyakarta", "slug": "daerah-istimewa-yogyakarta", "cx": 336.2, "cy": 348.0}, {"nama": "Gorontalo", "pulau": "Sulawesi", "kode": "75", "ibukota": "Gorontalo", "slug": "gorontalo", "cx": 589.0, "cy": 142.8}, {"nama": "Jambi", "pulau": "Sumatera", "kode": "15", "ibukota": "Jambi", "slug": "jambi", "cx": 171.2, "cy": 201.4}, {"nama": "Jawa Barat", "pulau": "Jawa", "kode": "32", "ibukota": "Bandung", "slug": "jawa-barat", "cx": 277.4, "cy": 323.8}, {"nama": "Jawa Tengah", "pulau": "Jawa", "kode": "33", "ibukota": "Semarang", "slug": "jawa-tengah", "cx": 334.0, "cy": 335.0}, {"nama": "Jawa Timur", "pulau": "Jawa", "kode": "35", "ibukota": "Surabaya", "slug": "jawa-timur", "cx": 380.5, "cy": 347.5}, {"nama": "Kalimantan Barat", "pulau": "Kalimantan", "kode": "61", "ibukota": "Pontianak", "slug": "kalimantan-barat", "cx": 350.4, "cy": 159.0}, {"nama": "Kalimantan Selatan", "pulau": "Kalimantan", "kode": "63", "ibukota": "Banjarmasin", "slug": "kalimantan-selatan", "cx": 446.3, "cy": 221.4}, {"nama": "Kalimantan Tengah", "pulau": "Kalimantan", "kode": "62", "ibukota": "Palangka Raya", "slug": "kalimantan-tengah", "cx": 400.1, "cy": 194.9}, {"nama": "Kalimantan Timur", "pulau": "Kalimantan", "kode": "64", "ibukota": "Samarinda", "slug": "kalimantan-timur", "cx": 459.0, "cy": 150.1}, {"nama": "Kalimantan Utara", "pulau": "Kalimantan", "kode": "65", "ibukota": "Tanjung Selor", "slug": "kalimantan-utara", "cx": 464.9, "cy": 89.0}, {"nama": "Kepulauan Bangka Belitung", "pulau": "Sumatera", "kode": "19", "ibukota": "Pangkal Pinang", "slug": "kepulauan-bangka-belitung", "cx": 241.4, "cy": 212.7}, {"nama": "Kepulauan Riau", "pulau": "Sumatera", "kode": "21", "ibukota": "Tanjung Pinang", "slug": "kepulauan-riau", "cx": 289.4, "cy": 66.8}, {"nama": "Lampung", "pulau": "Sumatera", "kode": "18", "ibukota": "Bandar Lampung", "slug": "lampung", "cx": 218.2, "cy": 278.5}, {"nama": "Maluku", "pulau": "Maluku", "kode": "81", "ibukota": "Ambon", "slug": "maluku", "cx": 731.3, "cy": 237.3}, {"nama": "Maluku Utara", "pulau": "Maluku", "kode": "82", "ibukota": "Sofifi", "slug": "maluku-utara", "cx": 708.8, "cy": 139.6}, {"nama": "Nusa Tenggara Barat", "pulau": "Bali-Nusa Tenggara", "kode": "52", "ibukota": "Mataram", "slug": "nusa-tenggara-barat", "cx": 499.3, "cy": 366.9}, {"nama": "Nusa Tenggara Timur", "pulau": "Bali-Nusa Tenggara", "kode": "53", "ibukota": "Kupang", "slug": "nusa-tenggara-timur", "cx": 570.5, "cy": 365.8}, {"nama": "Papua", "pulau": "Papua", "kode": "91", "ibukota": "Jayapura", "slug": "papua", "cx": 931.8, "cy": 233.0}, {"nama": "Papua Barat", "pulau": "Papua", "kode": "92", "ibukota": "Manokwari", "slug": "papua-barat", "cx": 829.0, "cy": 228.1}, {"nama": "Papua Barat Daya", "pulau": "Papua", "kode": "92", "ibukota": "Sorong", "slug": "papua-barat-daya", "cx": 797.0, "cy": 193.2}, {"nama": "Papua Pegunungan", "pulau": "Papua", "kode": "91", "ibukota": "Wamena", "slug": "papua-pegunungan", "cx": 946.0, "cy": 258.4}, {"nama": "Papua Selatan", "pulau": "Papua", "kode": "91", "ibukota": "Merauke", "slug": "papua-selatan", "cx": 944.1, "cy": 307.1}, {"nama": "Papua Tengah", "pulau": "Papua", "kode": "91", "ibukota": "Nabire", "slug": "papua-tengah", "cx": 890.1, "cy": 245.2}, {"nama": "Riau", "pulau": "Sumatera", "kode": "14", "ibukota": "Pekanbaru", "slug": "riau", "cx": 148.2, "cy": 144.3}, {"nama": "Sulawesi Barat", "pulau": "Sulawesi", "kode": "76", "ibukota": "Mamuju", "slug": "sulawesi-barat", "cx": 525.3, "cy": 215.4}, {"nama": "Sulawesi Selatan", "pulau": "Sulawesi", "kode": "73", "ibukota": "Makassar", "slug": "sulawesi-selatan", "cx": 544.3, "cy": 245.2}, {"nama": "Sulawesi Tengah", "pulau": "Sulawesi", "kode": "72", "ibukota": "Palu", "slug": "sulawesi-tengah", "cx": 562.0, "cy": 176.9}, {"nama": "Sulawesi Tenggara", "pulau": "Sulawesi", "kode": "74", "ibukota": "Kendari", "slug": "sulawesi-tenggara", "cx": 581.7, "cy": 251.3}, {"nama": "Sulawesi Utara", "pulau": "Sulawesi", "kode": "71", "ibukota": "Manado", "slug": "sulawesi-utara", "cx": 630.2, "cy": 134.3}, {"nama": "Sumatera Barat", "pulau": "Sumatera", "kode": "13", "ibukota": "Padang", "slug": "sumatera-barat", "cx": 127.9, "cy": 169.1}, {"nama": "Sumatera Selatan", "pulau": "Sumatera", "kode": "16", "ibukota": "Palembang", "slug": "sumatera-selatan", "cx": 201.7, "cy": 234.7}, {"nama": "Sumatera Utara", "pulau": "Sumatera", "kode": "12", "ibukota": "Medan", "slug": "sumatera-utara", "cx": 97.0, "cy": 102.8}];

const ISLAND_COLORS = {
  "Sumatera": "#ffc53d", "Jawa": "#5ea8ff", "Kalimantan": "#3ddc97",
  "Sulawesi": "#ff7ab8", "Bali-Nusa Tenggara": "#b79cff",
  "Maluku": "#ff6b6b", "Papua": "#4dd8ff"
};

const svg = document.getElementById("map");
const gDots = document.getElementById("dots");
const tooltip = document.getElementById("tooltip");
const preview = document.querySelector(".float-card");
const paths = [...document.querySelectorAll("path.province")];
const strip = document.getElementById("pulau");

const infoKicker = document.getElementById("infoKicker");
const infoNama = document.getElementById("infoNama");
const infoSub = document.getElementById("infoSub");
const infoPulau = document.getElementById("infoPulau");
const infoKode = document.getElementById("infoKode");
const infoIbukota = document.getElementById("infoIbukota");
const detailNama = document.getElementById("detailNama");
const detailSub = document.getElementById("detailSub");
const detailProv = document.getElementById("detailProv");
const detailPulau = document.getElementById("detailPulau");
const detailIbukota = document.getElementById("detailIbukota");
const searchInput = document.getElementById("search");
const islandBox = document.getElementById("islandFilters");
const chipsBox = document.getElementById("chips");
const legendBox = document.getElementById("legend");

let selected = null, activeIsland = "Semua", showDots = false;

/* ===== EVENT UTAMA: hover 1 provinsi -> ubah warna + kartu pratinjau ikut cursor ===== */
function fillPreview(el){
  infoKicker.textContent = "Pratinjau • " + el.dataset.pulau;
  infoNama.textContent = el.dataset.nama;
  infoSub.textContent = "Ibu kota " + (el.dataset.ibukota || "—") + ". Klik untuk kunci pilihan.";
  infoPulau.textContent = el.dataset.pulau;
  infoPulau.style.background = ISLAND_COLORS[el.dataset.pulau] || "#fff";
  infoKode.textContent = el.dataset.kode || "—";
  infoIbukota.textContent = el.dataset.ibukota || "—";
}
function movePreview(x, y){
  // tampil di dekat cursor, otomatis flip kalau mepet tepi layar
  const pad = 16, w = preview.offsetWidth || 270, h = preview.offsetHeight || 180;
  let left = x + pad, top = y + pad;
  if(left + w > innerWidth - 8) left = x - w - pad;
  if(top + h > innerHeight - 8) top = y - h - pad;
  preview.style.left = Math.max(8, left) + "px";
  preview.style.top = Math.max(8, top) + "px";
}
function onProvinceHover(el, x, y){
  fillPreview(el);
  preview.classList.add("show");
  if(x !== undefined && y !== undefined) movePreview(x, y);
  else {
    // tanpa posisi mouse (keyboard / search): tempel di samping provinsinya
    const r = el.getBoundingClientRect();
    movePreview(r.left + r.width / 2, r.top);
  }
}
function onProvinceLeave(){
  preview.classList.remove("show");
  tooltip.style.display = "none";
  document.querySelectorAll(".hover-js").forEach(x => x.classList.remove("hover-js"));
}
function onProvinceSelect(el){
  if(selected) selected.classList.remove("selected");
  selected = el;
  el.classList.add("selected");
  onProvinceHover(el);
  infoKicker.textContent = "Terpilih • " + el.dataset.pulau;
  detailNama.textContent = el.dataset.nama;
  detailSub.textContent = "Pulau " + el.dataset.pulau + " — ibu kota " + (el.dataset.ibukota || "—") + ".";
  detailProv.textContent = el.dataset.nama;
  detailPulau.textContent = el.dataset.pulau;
  detailIbukota.textContent = el.dataset.ibukota || "—";
}

paths.forEach(p => {
  p.setAttribute("tabindex", "0");
  p.addEventListener("mouseenter", e => onProvinceHover(p, e.clientX, e.clientY));
  p.addEventListener("mouseleave", onProvinceLeave);
  p.addEventListener("mousemove", e => movePreview(e.clientX, e.clientY));
  p.addEventListener("click", e => { onProvinceSelect(p); e.stopPropagation(); });
  p.addEventListener("focus", () => onProvinceHover(p));
  p.addEventListener("blur", onProvinceLeave);
  p.addEventListener("keydown", e => { if(e.key === "Enter" || e.key === " "){ e.preventDefault(); onProvinceSelect(p); } });
});
svg.addEventListener("click", () => { if(selected){ selected.classList.remove("selected"); selected = null; } });

function applyIsland(name){
  activeIsland = name;
  document.querySelectorAll(".pill").forEach(x => x.classList.toggle("active", x.dataset.island === name));
  document.querySelectorAll(".isle").forEach(x => x.classList.toggle("active", x.dataset.island === name));
  paths.forEach(p => p.classList.toggle("dimmed", !(name === "Semua" || p.dataset.pulau === name)));
}

const islands = ["Semua", ...Object.keys(ISLAND_COLORS)];
islands.forEach(name => {
  const b = document.createElement("button");
  b.className = "pill" + (name === "Semua" ? " active" : "");
  b.dataset.island = name;
  b.innerHTML = name === "Semua"
    ? '<span class="dot" style="background:conic-gradient(#ffc53d,#5ea8ff,#3ddc97,#ff7ab8,#b79cff,#ff6b6b,#4dd8ff)"></span>Semua'
    : '<span class="dot" style="background:' + ISLAND_COLORS[name] + '"></span>' + name;
  b.onclick = () => applyIsland(name);
  islandBox.appendChild(b);
});

const counts = {};
paths.forEach(p => counts[p.dataset.pulau] = (counts[p.dataset.pulau] || 0) + 1);
Object.entries(ISLAND_COLORS).forEach(([k, v]) => {
  const s = document.createElement("button");
  s.className = "isle"; s.dataset.island = k;
  s.innerHTML = "<b><i style='background:" + v + "'></i>" + k + "</b><small>" + (counts[k] || 0) + " provinsi • klik untuk filter</small>";
  s.onclick = () => { applyIsland(k); document.getElementById("peta").scrollIntoView({behavior:"smooth"}); };
  strip.appendChild(s);
  const l = document.createElement("span");
  l.innerHTML = "<i style='background:" + v + "'></i>" + k;
  legendBox.appendChild(l);
});

PROVINSI.slice().sort((a,b) => a.nama.localeCompare(b.nama, "id")).forEach(item => {
  const c = document.createElement("button");
  c.className = "chip";
  c.innerHTML = item.nama + "<small>" + item.pulau + "</small>";
  const target = document.getElementById("prov-" + item.slug);
  c.addEventListener("mouseenter", e => { if(target){ target.classList.add("hover-js"); onProvinceHover(target, e.clientX, e.clientY); } });
  c.addEventListener("mousemove", e => movePreview(e.clientX, e.clientY));
  c.addEventListener("mouseleave", onProvinceLeave);
  c.addEventListener("click", () => { if(target){ applyIsland("Semua"); onProvinceSelect(target); document.getElementById("peta").scrollIntoView({behavior:"smooth", block:"center"}); } });
  chipsBox.appendChild(c);
});

searchInput.addEventListener("input", () => {
  const q = searchInput.value.trim().toLowerCase();
  paths.forEach(p => p.classList.remove("match", "hover-js"));
  if(!q) return;
  paths.forEach(p => { if(p.dataset.nama.toLowerCase().includes(q)) p.classList.add("match"); });
  const first = paths.find(p => p.dataset.nama.toLowerCase().includes(q));
  if(first){ first.classList.add("hover-js"); onProvinceHover(first); }
});

document.getElementById("resetBtn").onclick = () => {
  searchInput.value = ""; applyIsland("Semua");
  paths.forEach(p => p.classList.remove("match", "hover-js", "selected"));
  selected = null; tooltip.style.display = "none";
  preview.classList.remove("show");
  vb = { ...VB_BASE }; applyVB();
  infoKicker.textContent = "Pratinjau provinsi";
  infoNama.textContent = "Arahkan kursor";
  infoSub.textContent = "Hover peta — warna provinsi berubah. Klik untuk kunci.";
  infoPulau.textContent = "—"; infoKode.textContent = "—"; infoIbukota.textContent = "—";
};
document.getElementById("clearBtn").onclick = () => {
  if(selected) selected.classList.remove("selected");
  selected = null;
  detailNama.textContent = "Belum ada pilihan";
  detailSub.textContent = "Klik salah satu provinsi di peta hero.";
  detailProv.textContent = "—"; detailPulau.textContent = "—"; detailIbukota.textContent = "—";
};
/* ===== ZOOM MURNI: hanya mengubah tampilan, data/warna/filter tak tersentuh ===== */
const VB_BASE = { x: 0, y: 0, w: 1000, h: 440 };
const VB_MIN_W = VB_BASE.w / 8; // maksimal 8x zoom
let vb = { ...VB_BASE };
function applyVB(){
  svg.setAttribute("viewBox", vb.x + " " + vb.y + " " + vb.w + " " + vb.h);
}
function svgPoint(clientX, clientY){
  const pt = new DOMPoint(clientX, clientY);
  return pt.matrixTransform(svg.getScreenCTM().inverse());
}
function zoomAt(sx, sy, factor){
  const w2 = Math.min(VB_BASE.w, Math.max(VB_MIN_W, vb.w * factor));
  const k = w2 / vb.w;
  vb.x = sx - (sx - vb.x) * k;
  vb.y = sy - (sy - vb.y) * k;
  vb.w = w2;
  vb.h = vb.h * k;
  applyVB();
}
function zoomCenter(factor){
  zoomAt(vb.x + vb.w / 2, vb.y + vb.h / 2, factor);
}
document.getElementById("zoomInBtn").onclick = () => zoomCenter(1 / 1.4);
document.getElementById("zoomOutBtn").onclick = () => zoomCenter(1.4);
document.getElementById("zoomResetBtn").onclick = () => { vb = { ...VB_BASE }; applyVB(); };
svg.addEventListener("wheel", e => {
  if(!e.ctrlKey) return; // tanpa Ctrl: biarkan halaman scroll normal
  e.preventDefault();
  const p = svgPoint(e.clientX, e.clientY);
  zoomAt(p.x, p.y, Math.exp(e.deltaY * 0.0015));
}, { passive: false });
svg.addEventListener("dblclick", e => {
  const p = svgPoint(e.clientX, e.clientY);
  zoomAt(p.x, p.y, 1 / 1.6);
});
// seret untuk geser (drag pan) + cubit untuk zoom (pinch), klik tetap untuk pilih
const pointers = new Map();
let pinchDist = 0, dragMoved = 0, suppressClick = false;
svg.addEventListener("pointerdown", e => {
  pointers.set(e.pointerId, { x: e.clientX, y: e.clientY });
  if(pointers.size === 2){
    const [a, b] = [...pointers.values()];
    pinchDist = Math.hypot(a.x - b.x, a.y - b.y);
  }
  dragMoved = 0;
  svg.classList.add("grabbing");
});
svg.addEventListener("pointermove", e => {
  if(!pointers.has(e.pointerId)) return;
  const prev = pointers.get(e.pointerId);
  pointers.set(e.pointerId, { x: e.clientX, y: e.clientY });
  if(pointers.size === 1 && e.buttons){
    const ctm = svg.getScreenCTM();
    const dx = (e.clientX - prev.x) / ctm.a;
    const dy = (e.clientY - prev.y) / ctm.d;
    dragMoved += Math.abs(e.clientX - prev.x) + Math.abs(e.clientY - prev.y);
    vb.x -= dx; vb.y -= dy;
    applyVB();
  } else if(pointers.size === 2){
    const [a, b] = [...pointers.values()];
    const d = Math.hypot(a.x - b.x, a.y - b.y);
    if(pinchDist > 0 && d > 0){
      const mx = (a.x + b.x) / 2, my = (a.y + b.y) / 2;
      const p = svgPoint(mx, my);
      zoomAt(p.x, p.y, pinchDist / d);
    }
    pinchDist = d;
    dragMoved = 99; // cubit selalu dianggap gesture, bukan klik
  }
});
function endPointer(e){
  pointers.delete(e.pointerId);
  if(pointers.size < 2) pinchDist = 0;
  if(pointers.size === 0){
    svg.classList.remove("grabbing");
    if(dragMoved > 6) suppressClick = true; // habis seret: jangan pilih provinsi
  }
}
svg.addEventListener("pointerup", endPointer);
svg.addEventListener("pointercancel", endPointer);
svg.addEventListener("click", e => {
  if(suppressClick){ e.stopPropagation(); suppressClick = false; }
}, true);
document.getElementById("toggleDotsBtn").onclick = (e) => {
  showDots = !showDots;
  e.target.classList.toggle("sun", showDots);
  gDots.innerHTML = "";
  if(!showDots) return;
  PROVINSI.forEach(item => {
    const c = document.createElementNS("http://www.w3.org/2000/svg", "circle");
    c.setAttribute("cx", item.cx); c.setAttribute("cy", item.cy); c.setAttribute("r", 2.4);
    c.setAttribute("fill", "#060b1c"); c.setAttribute("stroke", "#fff"); c.setAttribute("stroke-width", "1");
    c.style.pointerEvents = "none";
    gDots.appendChild(c);
  });
};

/* --- TravelFit: tombol cari per provinsi + daftar hasil sesi (<=20 baris) --- */
(function(){
  var panel = document.querySelector(".panel.detail") || document.body;
  var link = document.createElement("a");
  link.id = "cari-wisata"; link.className = "btn-cari"; link.style.display = "none";
  panel.appendChild(link);
  document.querySelectorAll("path.province").forEach(function(p){
    p.addEventListener("click", function(){
      link.style.display = "";
      link.href = "/?wilayah=" + encodeURIComponent(p.dataset.nama);
      link.textContent = "Cari wisata di " + p.dataset.nama + " ->";
    });
  });
  var raw = document.getElementById("hasil-data"), box = document.getElementById("daftar-hasil");
  if (raw && box) {
    var hasil = JSON.parse(raw.textContent);
    box.innerHTML = hasil.length
      ? "<h3>Hasil rekomendasi terakhir</h3>" + hasil.map(function(x, i){
          return "<div class='hasil-item'>" + (i + 1) + ". " + x.nama +
            " <small>(skor " + Number(x.vi).toFixed(4) + ")</small></div>";
        }).join("")
      : "<h3>Belum ada rekomendasi</h3><p>Isi form di <a href='/'>Beranda</a>.</p>";
  }
})();
