import React from "react";
import { AbsoluteFill, interpolate, spring, useCurrentFrame, useVideoConfig } from "remotion";

export const TituloCinetico: React.FC<{ text: string; color: string; bg: string }> = ({ text, color, bg }) => {
  const frame = useCurrentFrame();
  const { fps, durationInFrames } = useVideoConfig();
  const words = text.split(" ");
  const out = interpolate(frame, [durationInFrames - 15, durationInFrames], [1, 0], { extrapolateLeft: "clamp" });
  return (
    <AbsoluteFill style={{ backgroundColor: bg, justifyContent: "center", alignItems: "center", flexDirection: "column", opacity: out }}>
      {words.map((w, i) => {
        const s = spring({ frame: frame - i * 6, fps, config: { damping: 10, mass: 0.5 } });
        return (
          <div key={i} style={{ fontFamily: "DejaVu Sans, Inter, sans-serif", fontWeight: 900, fontSize: 150, lineHeight: 1.05,
            color: i % 2 ? "#fff" : color, transform: `scale(${s}) rotate(${(1 - s) * -10}deg)`, textTransform: "uppercase" }}>{w}</div>
        );
      })}
    </AbsoluteFill>
  );
};
