import React from "react";
import { Composition, Series } from "remotion";
import { FPS, HEIGHT, WIDTH } from "./theme";
import {
  Brand,
  CTA,
  Extras,
  Hook,
  Method,
  Problem,
  Stats,
  Step1,
  Step2,
  Step3,
} from "./scenes";

// Durasi tiap scene dalam frame (30 fps). Total 1500 frame = 50 detik.
const SCENES: { C: React.FC<{ d: number }>; d: number }[] = [
  { C: Hook, d: 120 },
  { C: Problem, d: 135 },
  { C: Brand, d: 120 },
  { C: Stats, d: 195 },
  { C: Step1, d: 165 },
  { C: Step2, d: 165 },
  { C: Step3, d: 210 },
  { C: Method, d: 165 },
  { C: Extras, d: 120 },
  { C: CTA, d: 105 },
];

const TOTAL = SCENES.reduce((a, s) => a + s.d, 0);

export const PromoReel: React.FC = () => (
  <Series>
    {SCENES.map(({ C, d }, i) => (
      <Series.Sequence key={i} durationInFrames={d}>
        <C d={d} />
      </Series.Sequence>
    ))}
  </Series>
);

export const MyComposition = () => (
  <Composition
    id="TravelFitReel"
    component={PromoReel}
    durationInFrames={TOTAL}
    fps={FPS}
    width={WIDTH}
    height={HEIGHT}
  />
);
