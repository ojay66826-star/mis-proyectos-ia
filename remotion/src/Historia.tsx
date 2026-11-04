import React from "react";
import { AbsoluteFill, Img, Sequence, interpolate, spring, staticFile, useCurrentFrame, useVideoConfig } from "remotion";

export type Escena = { image: string; caption: string; seconds: number };
export type HistoriaProps = { title: string; scenes: Escena[]; vertical?: boolean; accent?: string };

export const historiaSchemaDefaults: HistoriaProps = {
  title: "Mi historia animada",
  accent: "#6d28d9",
  scenes: [
    { image: "demo1.jpg", caption: "Había una vez…", seconds: 4 },
    { image: "demo2.jpg", caption: "…una gran aventura.", seconds: 4 },
  ],
};

const Panel: React.FC<{ scene: Escena; accent: string }> = ({ scene, accent }) => {
  const frame = useCurrentFrame();
  const { fps, durationInFrames } = useVideoConfig();
  // Ken Burns suave + entrada con resorte del subtítulo
  const zoom = interpolate(frame, [0, durationInFrames], [1, 1.12]);
  const fade = interpolate(frame, [0, 12, durationInFrames - 12, durationInFrames], [0, 1, 1, 0], { extrapolateLeft: "clamp", extrapolateRight: "clamp" });
  const pop = spring({ frame: frame - 8, fps, config: { damping: 12, mass: 0.6 } });
  const src = scene.image.startsWith("http") || scene.image.startsWith("/") ? scene.image : staticFile(scene.image);
  return (
    <AbsoluteFill style={{ opacity: fade, backgroundColor: "#000" }}>
      <Img src={src} style={{ width: "100%", height: "100%", objectFit: "cover", transform: `scale(${zoom})` }} />
      <div style={{ position: "absolute", left: "6%", right: "6%", bottom: "8%", transform: `translateY(${(1 - pop) * 80}px)`, opacity: pop,
        background: "rgba(0,0,0,.55)", borderLeft: `10px solid ${accent}`, borderRadius: 16, padding: "18px 26px",
        color: "#fff", fontFamily: "DejaVu Sans, Inter, sans-serif", fontWeight: 800, fontSize: 46 }}>
        {scene.caption}
      </div>
    </AbsoluteFill>
  );
};

export const Historia: React.FC<HistoriaProps> = ({ title, scenes, accent = "#6d28d9" }) => {
  const { fps } = useVideoConfig();
  const frame = useCurrentFrame();
  let from = 0;
  const titleIn = spring({ frame, fps, config: { damping: 14 } });
  return (
    <AbsoluteFill style={{ backgroundColor: "#0e0c14" }}>
      {scenes.map((s, i) => {
        const dur = Math.round(s.seconds * fps);
        const seq = (
          <Sequence key={i} from={from} durationInFrames={dur}>
            <Panel scene={s} accent={accent} />
          </Sequence>
        );
        from += dur;
        return seq;
      })}
      <Sequence durationInFrames={Math.round(2.2 * fps)}>
        <AbsoluteFill style={{ justifyContent: "flex-start", alignItems: "center", paddingTop: "7%" }}>
          <div style={{ transform: `scale(${titleIn})`, background: accent, color: "#fff", padding: "14px 34px", borderRadius: 999,
            fontFamily: "DejaVu Sans, Inter, sans-serif", fontWeight: 900, fontSize: 52 }}>{title}</div>
        </AbsoluteFill>
      </Sequence>
    </AbsoluteFill>
  );
};
