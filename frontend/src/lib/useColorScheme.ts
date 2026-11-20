import { useSyncExternalStore } from "react";

export type ColorScheme = "light" | "dark";

const QUERY = "(prefers-color-scheme: dark)";

function subscribe(onChange: () => void): () => void {
  const media = window.matchMedia(QUERY);
  media.addEventListener("change", onChange);
  return () => media.removeEventListener("change", onChange);
}

/** Follows the OS appearance setting, like the rest of the UI. */
export function useColorScheme(): ColorScheme {
  return useSyncExternalStore(
    subscribe,
    () => (window.matchMedia(QUERY).matches ? "dark" : "light"),
    () => "light",
  );
}

export const prefersReducedMotion = (): boolean =>
  window.matchMedia("(prefers-reduced-motion: reduce)").matches;
