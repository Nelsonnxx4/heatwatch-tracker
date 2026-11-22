import type { HeatCategory } from "./types";

export const HEAT_LEVELS: Record<HeatCategory, { label: string; color: string }> = {
  normal: { label: "Comfortable", color: "#64d2ff" },
  caution: { label: "Caution", color: "#ffd60a" },
  extreme_caution: { label: "Extreme caution", color: "#ff9f0a" },
  danger: { label: "Danger", color: "#ff453a" },
  extreme_danger: { label: "Extreme danger", color: "#c8102e" },
};

export const formatDegrees = (celsius: number): string => `${Math.round(celsius)}°`;

export const formatWindSpeed = (kilometresPerHour: number): string =>
  `${Math.round(kilometresPerHour)} km/h`;

const COMPASS_POINTS = ["N", "NE", "E", "SE", "S", "SW", "W", "NW"] as const;

export const formatWindDirection = (degrees: number): string => {
  const normalized = ((degrees % 360) + 360) % 360;
  return COMPASS_POINTS[Math.round(normalized / 45) % COMPASS_POINTS.length];
};

export const parseUtc = (iso: string): Date => new Date(`${iso}Z`);

const timeFormat = new Intl.DateTimeFormat(undefined, { hour: "numeric", minute: "2-digit" });
export const formatTime = (iso: string): string => timeFormat.format(parseUtc(iso));

export const markerSize = (heatIndexC: number): number =>
  Math.min(32, Math.max(14, 14 + (heatIndexC - 25) * 0.6));
