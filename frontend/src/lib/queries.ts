import { useQuery } from "@tanstack/react-query";

import { api } from "./api";

const FIVE_MINUTES = 5 * 60_000;

export const queryKeys = {
  rankings: ["rankings"] as const,
  summary: (slug: string) => ["summary", slug] as const,
  temperature: (slug: string) => ["temperature", slug] as const,
};

export const useRankings = () =>
  useQuery({
    queryKey: queryKeys.rankings,
    queryFn: ({ signal }) => api.rankings(signal),
    refetchInterval: FIVE_MINUTES,
  });

export const useHeatSummary = (slug: string) =>
  useQuery({
    queryKey: queryKeys.summary(slug),
    queryFn: ({ signal }) => api.summary(slug, signal),
  });

export const useTemperature = (slug: string) =>
  useQuery({
    queryKey: queryKeys.temperature(slug),
    queryFn: ({ signal }) => api.temperature(slug, signal),
  });
