import React from "react";
import {
  AbsoluteFill,
  Easing,
  interpolate,
  useCurrentFrame,
} from "remotion";
import { C, SANS, SERIF } from "./theme";
import {
  Chip,
  Crop,
  Eyebrow,
  JavaMap,
  Logo,
  PaperBg,
  Phone,
  Rise,
  Scene,
  Title,
  useIn,
} from "./ui";

const PAD = 96;

/* 1. Hook ---------------------------------------------------------------- */
export const Hook: React.FC<{ d: number }> = ({ d }) => {
  const frame = useCurrentFrame();
  const lines = ["Mau liburan", "ke Jawa,", "tapi bingung", "mulai dari mana?"];
  const underline = interpolate(frame, [62, 82], [0, 1], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
    easing: Easing.out(Easing.cubic),
  });
  return (
    <Scene duration={d}>
      <PaperBg />
      <AbsoluteFill
        style={{ justifyContent: "center", padding: PAD, gap: 10 }}
      >
        {lines.map((l, i) => {
          const t = useIn(6 + i * 11, 14);
          const accent = i === 3;
          return (
            <div
              key={l}
              style={{
                fontFamily: SERIF,
                fontSize: accent ? 100 : 132,
                whiteSpace: "nowrap",
                lineHeight: 1.1,
                color: accent ? C.teal : C.ink,
                fontStyle: accent ? "italic" : "normal",
                opacity: t,
                transform: `translateY(${(1 - t) * 90}px) rotate(${(1 - t) * -4}deg)`,
                position: "relative",
                alignSelf: "flex-start",
              }}
            >
              {l}
              {accent && (
                <div
                  style={{
                    position: "absolute",
                    left: 0,
                    bottom: -6,
                    height: 16,
                    width: `${underline * 100}%`,
                    background: C.mustard,
                    zIndex: -1,
                    borderRadius: 8,
                  }}
                />
              )}
            </div>
          );
        })}
      </AbsoluteFill>
    </Scene>
  );
};

/* 2. Masalah ------------------------------------------------------------- */
export const Problem: React.FC<{ d: number }> = ({ d }) => {
  const items = [
    { q: "Budget pas-pasan?", tilt: -3 },
    { q: "Pilihan wisata kebanyakan?", tilt: 2 },
    { q: "Takut nggak sesuai selera?", tilt: -2 },
  ];
  return (
    <Scene duration={d}>
      <PaperBg />
      <AbsoluteFill
        style={{ justifyContent: "center", padding: PAD, gap: 56 }}
      >
        {items.map((it, i) => {
          const t = useIn(8 + i * 20, 12);
          return (
            <div
              key={it.q}
              style={{
                alignSelf: i === 1 ? "flex-end" : "flex-start",
                background: i === 1 ? C.teal : C.card,
                color: i === 1 ? "#fff" : C.ink,
                border: `3px solid ${i === 1 ? C.teal : C.border}`,
                borderRadius: 40,
                padding: "44px 56px",
                fontFamily: SERIF,
                fontSize: 76,
                lineHeight: 1.1,
                maxWidth: 820,
                boxShadow: "0 24px 50px rgba(24,59,54,0.12)",
                opacity: t,
                transform: `scale(${0.6 + t * 0.4}) rotate(${it.tilt * t}deg)`,
              }}
            >
              {it.q}
            </div>
          );
        })}
        <Rise delay={78}>
          <div
            style={{
              fontFamily: SANS,
              fontSize: 52,
              color: C.muted,
              textAlign: "center",
              marginTop: 40,
            }}
          >
            Tenang, ada solusinya
            <span style={{ color: C.teal, fontWeight: 700 }}> →</span>
          </div>
        </Rise>
      </AbsoluteFill>
    </Scene>
  );
};

/* 3. Brand reveal -------------------------------------------------------- */
export const Brand: React.FC<{ d: number }> = ({ d }) => {
  const logo = useIn(4, 12);
  return (
    <Scene duration={d} bg={C.ink}>
      <PaperBg dark />
      <AbsoluteFill
        style={{ justifyContent: "center", alignItems: "center", gap: 70 }}
      >
        <div
          style={{
            opacity: logo,
            transform: `scale(${0.7 + logo * 0.3})`,
          }}
        >
          <Logo size={150} color="#fff" />
        </div>
        <JavaMap width={880} delay={16} />
        <Rise delay={40}>
          <Title
            size={92}
            color="#fff"
            style={{ textAlign: "center", padding: `0 ${PAD}px` }}
          >
            Perjalanan yang{" "}
            <span style={{ color: C.mustard, fontStyle: "italic" }}>pas.</span>
            <br />
            Mulai dari Jawa.
          </Title>
        </Rise>
      </AbsoluteFill>
    </Scene>
  );
};

/* 4. Angka --------------------------------------------------------------- */
export const Stats: React.FC<{ d: number }> = ({ d }) => {
  const frame = useCurrentFrame();
  const count = Math.round(
    interpolate(frame, [8, 50], [0, 443], {
      extrapolateLeft: "clamp",
      extrapolateRight: "clamp",
      easing: Easing.out(Easing.cubic),
    }),
  );
  const boxes = [
    { n: "6", l: "provinsi\ndi Pulau Jawa" },
    { n: "6", l: "kategori\nwisata" },
    { n: "137", l: "destinasi\ngratis tiket" },
  ];
  const cats = ["Alam", "Bahari", "Budaya", "Hiburan", "Belanja", "Religi"];
  return (
    <Scene duration={d}>
      <PaperBg />
      <AbsoluteFill style={{ padding: PAD, paddingTop: 220, gap: 30 }}>
        <Rise delay={0}>
          <Eyebrow>Satu pulau, banyak pilihan</Eyebrow>
        </Rise>
        <div
          style={{
            fontFamily: SERIF,
            fontSize: 330,
            lineHeight: 1,
            color: C.teal,
            letterSpacing: -10,
          }}
        >
          {count}
        </div>
        <Rise delay={20}>
          <Title size={84}>destinasi wisata siap kamu jelajahi.</Title>
        </Rise>
        <div style={{ display: "flex", gap: 24, marginTop: 50 }}>
          {boxes.map((b, i) => {
            const t = useIn(55 + i * 10, 14);
            return (
              <div
                key={b.l}
                style={{
                  flex: 1,
                  background: i === 2 ? C.mustard : C.card,
                  border: `3px solid ${i === 2 ? C.mustard : C.border}`,
                  borderRadius: 32,
                  padding: "36px 28px",
                  opacity: t,
                  transform: `translateY(${(1 - t) * 80}px)`,
                }}
              >
                <div
                  style={{ fontFamily: SERIF, fontSize: 100, color: C.ink, lineHeight: 1 }}
                >
                  {b.n}
                </div>
                <div
                  style={{
                    fontFamily: SANS,
                    fontSize: 36,
                    color: C.muted,
                    whiteSpace: "pre-line",
                    marginTop: 14,
                    lineHeight: 1.25,
                  }}
                >
                  {b.l}
                </div>
              </div>
            );
          })}
        </div>
        <div style={{ display: "flex", flexWrap: "wrap", gap: 18, marginTop: 40 }}>
          {cats.map((c, i) => {
            const t = useIn(90 + i * 6, 14);
            return (
              <div
                key={c}
                style={{ opacity: t, transform: `scale(${0.5 + t * 0.5})` }}
              >
                <Chip bg={i % 2 ? C.soft : C.teal} color={i % 2 ? C.ink : "#fff"} size={44}>
                  {c}
                </Chip>
              </div>
            );
          })}
        </div>
        <Rise delay={120} style={{ marginTop: 30 }}>
          <div style={{ fontFamily: SANS, fontSize: 40, color: C.muted }}>
            Dari Banten sampai Jawa Timur.
          </div>
        </Rise>
      </AbsoluteFill>
    </Scene>
  );
};

/* 5–7. Langkah pemakaian ------------------------------------------------- */
const StepHeader: React.FC<{ n: number; title: React.ReactNode; sub: string }> = ({
  n,
  title,
  sub,
}) => {
  const badge = useIn(2, 10);
  return (
    <div style={{ padding: `140px ${PAD}px 0`, display: "flex", flexDirection: "column", gap: 18 }}>
      <div style={{ display: "flex", alignItems: "center", gap: 24 }}>
        <div
          style={{
            width: 84,
            height: 84,
            borderRadius: 42,
            background: C.teal,
            color: "#fff",
            fontFamily: SERIF,
            fontSize: 52,
            display: "flex",
            alignItems: "center",
            justifyContent: "center",
            transform: `scale(${badge})`,
          }}
        >
          {n}
        </div>
        <Rise delay={4} distance={30}>
          <Eyebrow>Langkah {n} dari 3</Eyebrow>
        </Rise>
      </div>
      <Rise delay={8}>
        <Title size={88}>{title}</Title>
      </Rise>
      <Rise delay={14}>
        <div style={{ fontFamily: SANS, fontSize: 44, color: C.muted, lineHeight: 1.3 }}>
          {sub}
        </div>
      </Rise>
    </div>
  );
};

const PhoneIn: React.FC<{
  src: string;
  d: number;
  originY?: string;
  top?: number;
}> = ({ src, d, originY, top = 640 }) => {
  const t = useIn(10, 18);
  return (
    <div
      style={{
        position: "absolute",
        top: top + (1 - t) * 500,
        left: "50%",
        transform: `translateX(-50%) rotate(${(1 - t) * 6}deg)`,
        opacity: t,
      }}
    >
      <Phone src={src} width={600} duration={d} originY={originY} />
    </div>
  );
};

export const Step1: React.FC<{ d: number }> = ({ d }) => (
  <Scene duration={d}>
    <PaperBg />
    <StepHeader
      n={1}
      title={
        <>
          Atur <em style={{ color: C.teal }}>budget</em> & tujuanmu
        </>
      }
      sub="Budget tiket, kota asal, dan provinsi tujuan."
    />
    <PhoneIn src="shots/form.png" d={d} />
    <Callout delay={50} top={1120} left={40} text="Rp 50.000 / orang" />
    <Callout delay={68} top={1420} right={40} text="Surabaya → Yogyakarta" />
  </Scene>
);

const Callout: React.FC<{
  delay: number;
  top: number;
  left?: number;
  right?: number;
  text: string;
}> = ({ delay, top, left, right, text }) => {
  const t = useIn(delay, 11);
  return (
    <div
      style={{
        position: "absolute",
        top,
        left,
        right,
        opacity: t,
        transform: `scale(${0.4 + t * 0.6})`,
        background: C.mustard,
        color: C.ink,
        fontFamily: SANS,
        fontWeight: 700,
        fontSize: 44,
        padding: "22px 34px",
        borderRadius: 24,
        boxShadow: "0 18px 40px rgba(24,59,54,0.25)",
      }}
    >
      {text}
    </div>
  );
};

export const Step2: React.FC<{ d: number }> = ({ d }) => {
  const profiles = [
    { n: "Seimbang", s: "pilihan responden" },
    { n: "Hemat", s: "harga tiket" },
    { n: "Kualitas", s: "rating" },
    { n: "Petualang", s: "jelajah jauh" },
  ];
  return (
    <Scene duration={d}>
      <PaperBg />
      <StepHeader
        n={2}
        title={
          <>
            Pilih <em style={{ color: C.teal }}>minat</em> & prioritas
          </>
        }
        sub="13 hobi, 6 kategori, dan 4 profil prioritas."
      />
      <PhoneIn src="shots/profil.png" d={d} originY="20%" />
      <div
        style={{
          position: "absolute",
          top: 1180,
          left: 0,
          right: 0,
          display: "flex",
          flexDirection: "column",
          alignItems: "center",
          gap: 22,
        }}
      >
        {profiles.map((p, i) => {
          const t = useIn(48 + i * 9, 12);
          return (
            <div
              key={p.n}
              style={{
                opacity: t,
                transform: `translateX(${(1 - t) * (i % 2 ? 300 : -300)}px)`,
                background: i === 0 ? C.teal : C.card,
                color: i === 0 ? "#fff" : C.ink,
                border: `3px solid ${C.teal}`,
                borderRadius: 26,
                padding: "20px 40px",
                fontFamily: SANS,
                fontSize: 42,
                minWidth: 620,
                display: "flex",
                justifyContent: "space-between",
                boxShadow: "0 16px 36px rgba(24,59,54,0.18)",
              }}
            >
              <b>{p.n}</b>
              <span style={{ opacity: 0.8 }}>{p.s}</span>
            </div>
          );
        })}
      </div>
    </Scene>
  );
};

export const Step3: React.FC<{ d: number }> = ({ d }) => {
  const top = [
    { n: "Desa Wisata Rumah Domes", k: "Hiburan" },
    { n: "Candi Donotirto", k: "Budaya" },
    { n: "Bukit Paralayang Watugupit", k: "Alam" },
  ];
  return (
    <Scene duration={d}>
      <PaperBg />
      <StepHeader
        n={3}
        title={
          <>
            Dapat <em style={{ color: C.teal }}>Top 10</em> rekomendasi
          </>
        }
        sub="Diurutkan khusus sesuai preferensimu."
      />
      <PhoneIn src="shots/hasil.png" d={d} originY="60%" />
      <div
        style={{
          position: "absolute",
          top: 1160,
          left: 0,
          right: 0,
          display: "flex",
          flexDirection: "column",
          alignItems: "center",
          gap: 22,
        }}
      >
        {top.map((r, i) => {
          const t = useIn(50 + i * 14, 12);
          return (
            <div
              key={r.n}
              style={{
                opacity: t,
                transform: `translateY(${(1 - t) * 120}px) scale(${0.85 + t * 0.15})`,
                width: 860,
                background: C.card,
                borderRadius: 30,
                padding: "26px 32px",
                display: "flex",
                alignItems: "center",
                gap: 28,
                borderLeft: `14px solid ${i === 0 ? C.mustard : C.teal}`,
                boxShadow: "0 22px 46px rgba(24,59,54,0.22)",
              }}
            >
              <div
                style={{
                  fontFamily: SERIF,
                  fontSize: 76,
                  color: C.teal,
                  width: 70,
                  textAlign: "center",
                }}
              >
                {i + 1}
              </div>
              <div>
                <div style={{ fontFamily: SANS, fontSize: 30, color: C.muted, letterSpacing: 3, textTransform: "uppercase", fontWeight: 700 }}>
                  {r.k}
                </div>
                <div style={{ fontFamily: SERIF, fontSize: 46, color: C.ink }}>{r.n}</div>
              </div>
            </div>
          );
        })}
      </div>
    </Scene>
  );
};

/* 8. Metode -------------------------------------------------------------- */
export const Method: React.FC<{ d: number }> = ({ d }) => {
  const frame = useCurrentFrame();
  // Bobot profil Seimbang (README: C5 26,04%, C6 23,19%, C1 16,13%, C2 13,51%, C4 13,23%, C3 7,90%)
  const bars = [
    { l: "Kecocokan kategori", v: 26 },
    { l: "Kecocokan hobi", v: 23 },
    { l: "Harga tiket", v: 16 },
    { l: "Rating", v: 14 },
    { l: "Fasilitas", v: 13 },
    { l: "Jarak", v: 8 },
  ];
  return (
    <Scene duration={d} bg={C.ink}>
      <PaperBg dark />
      <AbsoluteFill style={{ padding: PAD, paddingTop: 200, gap: 26 }}>
        <Rise>
          <Eyebrow color={C.mustard}>Metode AHP + TOPSIS</Eyebrow>
        </Rise>
        <Rise delay={6}>
          <Title size={112} color="#fff">
            Dihitung,
            <br />
            <span style={{ color: C.mustard, fontStyle: "italic" }}>bukan ditebak.</span>
          </Title>
        </Rise>
        <Rise delay={14}>
          <div style={{ fontFamily: SANS, fontSize: 44, color: "rgba(255,255,255,0.75)", lineHeight: 1.3 }}>
            Setiap destinasi ditimbang dengan 6 kriteria sekaligus.
          </div>
        </Rise>
        <div style={{ display: "flex", flexDirection: "column", gap: 30, marginTop: 50 }}>
          {bars.map((b, i) => {
            const t = interpolate(frame - 30 - i * 7, [0, 24], [0, 1], {
              extrapolateLeft: "clamp",
              extrapolateRight: "clamp",
              easing: Easing.out(Easing.cubic),
            });
            return (
              <div key={b.l} style={{ opacity: Math.min(1, t * 3) }}>
                <div
                  style={{
                    display: "flex",
                    justifyContent: "space-between",
                    fontFamily: SANS,
                    fontSize: 40,
                    color: "#fff",
                    marginBottom: 10,
                  }}
                >
                  <span>{b.l}</span>
                  <span style={{ fontFamily: SERIF, color: C.mustard }}>
                    {Math.round(b.v * t)}%
                  </span>
                </div>
                <div style={{ height: 26, borderRadius: 13, background: "rgba(255,255,255,0.12)" }}>
                  <div
                    style={{
                      height: "100%",
                      width: `${(b.v / 26) * 100 * t}%`,
                      borderRadius: 13,
                      background: i < 2 ? C.mustard : "#7fc4b4",
                    }}
                  />
                </div>
              </div>
            );
          })}
        </div>
        <Rise delay={80} style={{ marginTop: 40 }}>
          <div style={{ fontFamily: SANS, fontSize: 38, color: "rgba(255,255,255,0.7)", lineHeight: 1.35 }}>
            Bobot default dari kuesioner <b style={{ color: "#fff" }}>28 responden</b>.
            <br />
            Mau atur sendiri? Geser saja slidernya.
          </div>
        </Rise>
      </AbsoluteFill>
    </Scene>
  );
};

/* 9. Fitur tambahan ------------------------------------------------------ */
export const Extras: React.FC<{ d: number }> = ({ d }) => {
  const feats = [
    "Peta interaktif Pulau Jawa",
    "Langsung buka Google Maps & rute",
    "Estimasi biaya bensin perjalanan",
  ];
  const card = useIn(12, 16);
  return (
    <Scene duration={d}>
      <PaperBg />
      <AbsoluteFill style={{ padding: PAD, paddingTop: 180, gap: 26 }}>
        <Rise>
          <Eyebrow>Masih ada lagi</Eyebrow>
        </Rise>
        <Rise delay={4}>
          <Title size={96}>
            Dari rekomendasi
            <br />
            sampai <em style={{ color: C.teal }}>rute.</em>
          </Title>
        </Rise>
        <div
          style={{
            marginTop: 40,
            opacity: card,
            transform: `translateY(${(1 - card) * 100}px) rotate(${(1 - card) * -3}deg)`,
            alignSelf: "center",
            background: C.card,
            borderRadius: 40,
            padding: 22,
            boxShadow: "0 30px 60px rgba(24,59,54,0.22)",
          }}
        >
          <Crop src="shots/hasil2.png" x={40} y={1075} w={820} h={400} width={840} />
        </div>
        <div style={{ display: "flex", flexDirection: "column", gap: 24, marginTop: 40 }}>
          {feats.map((f, i) => {
            const t = useIn(34 + i * 10, 12);
            return (
              <div
                key={f}
                style={{
                  opacity: t,
                  transform: `translateX(${(1 - t) * -120}px)`,
                  display: "flex",
                  alignItems: "center",
                  gap: 26,
                  fontFamily: SANS,
                  fontSize: 46,
                  color: C.ink,
                }}
              >
                <div
                  style={{
                    width: 56,
                    height: 56,
                    borderRadius: 28,
                    background: C.teal,
                    color: "#fff",
                    fontSize: 34,
                    display: "flex",
                    alignItems: "center",
                    justifyContent: "center",
                    flexShrink: 0,
                  }}
                >
                  ✓
                </div>
                {f}
              </div>
            );
          })}
        </div>
      </AbsoluteFill>
    </Scene>
  );
};

/* 10. Ajakan ------------------------------------------------------------- */
export const CTA: React.FC<{ d: number }> = ({ d }) => {
  const frame = useCurrentFrame();
  const btn = useIn(30, 10);
  const pulse = 1 + Math.sin(Math.max(0, frame - 45) / 5) * 0.025;
  return (
    <Scene duration={d + 12} bg={C.teal}>
      <PaperBg dark />
      <AbsoluteFill
        style={{ justifyContent: "center", alignItems: "center", gap: 64, padding: PAD }}
      >
        <Rise>
          <Logo size={120} color="#fff" />
        </Rise>
        <Rise delay={10}>
          <Title size={104} color="#fff" style={{ textAlign: "center" }}>
            Temukan perjalanan
            <br />
            yang <span style={{ color: C.mustard, fontStyle: "italic" }}>pas</span> untukmu.
          </Title>
        </Rise>
        <div
          style={{
            opacity: btn,
            transform: `scale(${(0.6 + btn * 0.4) * pulse})`,
            background: C.mustard,
            color: C.ink,
            fontFamily: SANS,
            fontWeight: 700,
            fontSize: 54,
            padding: "36px 70px",
            borderRadius: 999,
            boxShadow: "0 24px 50px rgba(0,0,0,0.25)",
          }}
        >
          Coba TravelFit sekarang ↗
        </div>
        <Rise delay={44}>
          <JavaMap width={620} delay={44} stagger={3} />
        </Rise>
      </AbsoluteFill>
    </Scene>
  );
};
