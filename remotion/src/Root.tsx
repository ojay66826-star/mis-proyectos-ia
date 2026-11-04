import React from "react";
import { Composition } from "remotion";
import { Historia, historiaSchemaDefaults } from "./Historia";
import { TituloCinetico } from "./TituloCinetico";

// Composiciones disponibles. Se renderizan con:
//   npx remotion render src/index.ts Historia salida.mp4 --props=props.json
export const RemotionRoot: React.FC = () => (
  <>
    <Composition
      id="Historia"
      component={Historia}
      durationInFrames={30 * 12}
      fps={30}
      width={1280}
      height={720}
      defaultProps={historiaSchemaDefaults}
      calculateMetadata={({ props }) => ({
        durationInFrames: Math.max(30, Math.round(props.scenes.reduce((a, s) => a + s.seconds, 0) * 30)),
        width: props.vertical ? 720 : 1280,
        height: props.vertical ? 1280 : 720,
      })}
    />
    <Composition
      id="TituloCinetico"
      component={TituloCinetico}
      durationInFrames={30 * 5}
      fps={30}
      width={1080}
      height={1920}
      defaultProps={{ text: "Estudio de Animación IA", color: "#ff006e", bg: "#14121b" }}
    />
  </>
);
