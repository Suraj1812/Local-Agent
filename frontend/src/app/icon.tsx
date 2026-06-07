import { ImageResponse } from "next/og";

export const size = {
  width: 64,
  height: 64
};

export const contentType = "image/png";

export default function Icon() {
  return new ImageResponse(
    (
      <div
        style={{
          alignItems: "center",
          background: "#0d766c",
          color: "white",
          display: "flex",
          fontSize: 26,
          fontWeight: 800,
          height: "100%",
          justifyContent: "center",
          letterSpacing: 0,
          width: "100%"
        }}
      >
        AI
      </div>
    ),
    size
  );
}
