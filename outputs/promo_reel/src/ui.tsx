import React from "react";
import {
  AbsoluteFill,
  Img,
  interpolate,
  spring,
  staticFile,
  useCurrentFrame,
  useVideoConfig,
  Easing,
} from "remotion";
import { C, SANS, SERIF } from "./theme";
import { JAVA_PATHS, JAVA_VIEWBOX } from "./javaPaths";

/** Nilai 0..1 berbasis spring, mulai pada frame `delay`. */
export const useIn = (delay = 0, damping = 200, durationInFrames?: number) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  return spring({
    frame: frame - delay,
    fps,
    config: { damping },
    durationInFrames,
  });
};

/** Pembungkus scene: fade + sedikit zoom saat keluar. */
export const Scene: React.FC<{
  children: React.ReactNode;
  duration: number;
  bg?: string;
}> = ({ children, duration, bg = C.paper }) => {
  const frame = useCurrentFrame();
  const enter = interpolate(frame, [0, 8], [0, 1], {
    extrapolateRight: "clamp",
  });
  const exit = interpolate(frame, [duration - 10, duration], [1, 0], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
    easing: Easing.in(Easing.quad),
  });
  const scale = interpolate(frame, [duration - 10, duration], [1, 1.04], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
  });
  return (
    <AbsoluteFill style={{ backgroundColor: bg }}>
      <AbsoluteFill
        style={{ opacity: Math.min(enter, exit), transform: `scale(${scale})` }}
      >
        {children}
      </AbsoluteFill>
    </AbsoluteFill>
  );
};

/** Latar kertas dengan garis kontur yang bergerak pelan. */
export const PaperBg: React.FC<{ dark?: boolean }> = ({ dark }) => {
  const frame = useCurrentFrame();
  const stroke = dark ? "rgba(255,255,255,0.07)" : "rgba(8,104,92,0.07)";
  const rings = Array.from({ length: 9 }, (_, i) => i);
  return (
    <AbsoluteFill>
      <svg width="100%" height="100%" viewBox="0 0 1080 1920">
        {rings.map((i) => (
          <circle
            key={i}
            cx={900 + Math.sin(frame / 90) * 20}
            cy={260}
            r={120 + i * 110 + ((frame * 0.6) % 110)}
            fill="none"
            stroke={stroke}
            strokeWidth={3}
          />
        ))}
        {rings.map((i) => (
          <circle
            key={`b${i}`}
            cx={120}
            cy={1720 + Math.cos(frame / 80) * 20}
            r={80 + i * 120 + ((frame * 0.5) % 120)}
            fill="none"
            stroke={stroke}
            strokeWidth={3}
          />
        ))}
      </svg>
    </AbsoluteFill>
  );
};

export const Logo: React.FC<{ size?: number; color?: string }> = ({
  size = 64,
  color = C.ink,
}) => (
  <div
    style={{
      display: "flex",
      alignItems: "center",
      gap: size * 0.3,
      color,
      fontFamily: SANS,
      fontWeight: 700,
      fontSize: size,
      letterSpacing: -1,
    }}
  >
    <svg width={size * 1.1} height={size} viewBox="0 0 44 40">
      <path
        d="M4 36 L22 6 L40 36 Z M16 36 L24 22 L30 32"
        fill="none"
        stroke={color}
        strokeWidth={3.6}
        strokeLinejoin="round"
        strokeLinecap="round"
      />
    </svg>
    <span>
      Travel<span style={{ color: color === C.ink ? C.teal : C.mustard }}>Fit</span>
    </span>
  </div>
);

/** Peta Jawa (path diambil dari website), provinsi muncul berurutan. */
export const JavaMap: React.FC<{
  width: number;
  delay?: number;
  highlight?: string;
  stagger?: number;
}> = ({ width, delay = 0, highlight, stagger = 5 }) => {
  const frame = useCurrentFrame();
  const fills: Record<string, string> = {
    Banten: "#bdd3a8",
    "DKI Jakarta": "#edd79c",
    "Jawa Barat": "#a7c8ba",
    "Jawa Tengah": "#8bb3a5",
    "Daerah Istimewa Yogyakarta": "#d0b67c",
    "Jawa Timur": "#7a9c8a",
  };
  const order = [
    "Banten",
    "DKI Jakarta",
    "Jawa Barat",
    "Jawa Tengah",
    "Daerah Istimewa Yogyakarta",
    "Jawa Timur",
  ];
  return (
    <svg width={width} height={(width * 97) / 242} viewBox={JAVA_VIEWBOX}>
      {JAVA_PATHS.map((p) => {
        const i = order.indexOf(p.name);
        const t = interpolate(frame - delay - i * stagger, [0, 12], [0, 1], {
          extrapolateLeft: "clamp",
          extrapolateRight: "clamp",
          easing: Easing.out(Easing.cubic),
        });
        const isHi = highlight === p.name;
        return (
          <path
            key={p.name}
            d={p.d}
            fill={isHi ? C.teal : fills[p.name]}
            stroke="#fff"
            strokeWidth={1.2}
            style={{
              opacity: t,
              transform: `translateY(${(1 - t) * 6}px)`,
            }}
          />
        );
      })}
    </svg>
  );
};

export const Eyebrow: React.FC<{ children: React.ReactNode; color?: string }> = ({
  children,
  color = C.teal,
}) => (
  <div
    style={{
      fontFamily: SANS,
      fontWeight: 700,
      fontSize: 34,
      letterSpacing: 6,
      textTransform: "uppercase",
      color,
    }}
  >
    {children}
  </div>
);

export const Title: React.FC<{
  children: React.ReactNode;
  size?: number;
  color?: string;
  style?: React.CSSProperties;
}> = ({ children, size = 96, color = C.ink, style }) => (
  <div
    style={{
      fontFamily: SERIF,
      fontSize: size,
      lineHeight: 1.08,
      color,
      letterSpacing: -1,
      ...style,
    }}
  >
    {children}
  </div>
);

/** Muncul dari bawah dengan fade. */
export const Rise: React.FC<{
  delay?: number;
  children: React.ReactNode;
  distance?: number;
  style?: React.CSSProperties;
}> = ({ delay = 0, children, distance = 60, style }) => {
  const t = useIn(delay);
  return (
    <div
      style={{
        opacity: t,
        transform: `translateY(${(1 - t) * distance}px)`,
        ...style,
      }}
    >
      {children}
    </div>
  );
};

/** Mockup HP berisi screenshot asli website. */
export const Phone: React.FC<{
  src: string;
  width?: number;
  zoomFrom?: number;
  zoomTo?: number;
  duration: number;
  originY?: string;
}> = ({ src, width = 600, zoomFrom = 1, zoomTo = 1.06, duration, originY = "30%" }) => {
  const frame = useCurrentFrame();
  const z = interpolate(frame, [0, duration], [zoomFrom, zoomTo], {
    extrapolateRight: "clamp",
  });
  const bezel = 22;
  const h = width * 2;
  return (
    <div
      style={{
        width: width + bezel * 2,
        height: h + bezel * 2,
        borderRadius: 86,
        background: C.ink,
        padding: bezel,
        boxShadow: "0 50px 90px rgba(24,59,54,0.35)",
        position: "relative",
      }}
    >
      <div
        style={{
          width,
          height: h,
          borderRadius: 66,
          overflow: "hidden",
          background: C.paper,
          position: "relative",
        }}
      >
        <Img
          src={staticFile(src)}
          style={{
            width: "100%",
            height: "100%",
            objectFit: "cover",
            transform: `scale(${z})`,
            transformOrigin: `50% ${originY}`,
          }}
        />
      </div>
      <div
        style={{
          position: "absolute",
          top: bezel + 18,
          left: "50%",
          width: 150,
          height: 40,
          marginLeft: -75,
          borderRadius: 20,
          background: C.ink,
        }}
      />
    </div>
  );
};

/** Potongan area tertentu dari screenshot (koordinat piksel gambar 860×1720). */
export const Crop: React.FC<{
  src: string;
  x: number;
  y: number;
  w: number;
  h: number;
  width: number;
  style?: React.CSSProperties;
}> = ({ src, x, y, w, h, width, style }) => {
  const s = width / w;
  return (
    <div
      style={{
        width,
        height: h * s,
        overflow: "hidden",
        position: "relative",
        borderRadius: 28,
        ...style,
      }}
    >
      <Img
        src={staticFile(src)}
        style={{
          position: "absolute",
          width: 860 * s,
          height: 1720 * s,
          left: -x * s,
          top: -y * s,
          maxWidth: "none",
        }}
      />
    </div>
  );
};

export const Chip: React.FC<{
  children: React.ReactNode;
  bg?: string;
  color?: string;
  size?: number;
}> = ({ children, bg = C.soft, color = C.ink, size = 40 }) => (
  <div
    style={{
      background: bg,
      color,
      fontFamily: SANS,
      fontWeight: 600,
      fontSize: size,
      padding: `${size * 0.35}px ${size * 0.75}px`,
      borderRadius: 999,
      whiteSpace: "nowrap",
    }}
  >
    {children}
  </div>
);
