import type { HeatSummary, Observation, RankingItem } from "./types";

export class ApiError extends Error {
  constructor(
    readonly status: number,
    message: string,
  ) {
    super(message);
    this.name = "ApiError";
  }
}

async function get<T>(path: string, signal?: AbortSignal): Promise<T> {
  const response = await fetch(`/api${path}`, { signal });

  if (!response.ok) {
    const body = (await response.json().catch(() => null)) as { detail?: string } | null;
    throw new ApiError(response.status, body?.detail ?? response.statusText);
  }

  return (await response.json()) as T;
}

export const api = {
  rankings: (signal?: AbortSignal) =>
    get<RankingItem[]>("/rankings/hottest?limit=200", signal),
  summary: (slug: string, signal?: AbortSignal) =>
    get<HeatSummary>(`/cities/${slug}/heat-summary?days=7`, signal),
  temperature: (slug: string, signal?: AbortSignal) =>
    get<Observation[]>(`/cities/${slug}/temperature?limit=72`, signal),
};
