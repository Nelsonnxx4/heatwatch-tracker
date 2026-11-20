import type { HeatCategory } from "./types";

export const HEAT_LEVELS: Record<HeatCategory, { label: string; color: string }> = {
  normal: { label: "Comfortable", color: "#64d2ff" },
  caution: { label: "Caution", color: "#ffd60a" },
  extreme_caution: { label: "Extreme caution", color: "#ff9f0a" },
  danger: { label: "Danger", color: "#ff453a" },
  extreme_danger: { label: "Extreme danger", color: "#c8102e" },
};

export const formatDegrees = (celsius: number): string => `${Math.round(celsius)}°`;

/** The API returns naive UTC timestamps; make that explicit before parsing. */
export const parseUtc = (iso: string): Date => new Date(`${iso}Z`);

const timeFormat = new Intl.DateTimeFormat(undefined, { hour: "numeric", minute: "2-digit" });
export const formatTime = (iso: string): string => timeFormat.format(parseUtc(iso));

/** Dot diameter in px for a heat index, clamped so extremes stay readable. */
export const markerSize = (heatIndexC: number): number =>
  Math.min(32, Math.max(14, 14 + (heatIndexC - 25) * 0.6));
