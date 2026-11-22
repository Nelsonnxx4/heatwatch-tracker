"use client";

import { LineChart } from "echarts/charts";
import { GridComponent, TooltipComponent } from "echarts/components";
import * as echarts from "echarts/core";
import type { ECharts, EChartsCoreOption } from "echarts/core";
import { CanvasRenderer } from "echarts/renderers";
import { useEffect, useRef } from "react";

import { parseUtc } from "@/lib/heat";
import type { Observation } from "@/lib/types";
import { prefersReducedMotion, type ColorScheme } from "@/lib/useColorScheme";

echarts.use([LineChart, GridComponent, TooltipComponent, CanvasRenderer]);

interface Props {
  observations: Observation[];
  accent: string;
  scheme: ColorScheme;
}

const toSeries = (observations: Observation[], pick: (o: Observation) => number) =>
  observations.map((o) => [parseUtc(o.observed_at).getTime(), pick(o)]);

function buildOption(
  { observations, accent }: Pick<Props, "observations" | "accent">,
  colors: { text: string; muted: string; grid: string; surface: string },
): EChartsCoreOption {
  const line = (name: string, color: string, data: number[][], width: number) => ({
    name,
    data,
    type: "line" as const,
    smooth: false,
    showSymbol: false,
    lineStyle: { width, color },
    itemStyle: { color },
  });

  return {
    animation: !prefersReducedMotion(),
    grid: { left: 0, right: 6, top: 12, bottom: 0, containLabel: true },
    tooltip: {
      trigger: "axis",
      backgroundColor: colors.surface,
      borderWidth: 1,
      borderColor: colors.grid,
      textStyle: { color: colors.text, fontSize: 13 },
      valueFormatter: (value: unknown) => `${Number(value).toFixed(1)}°C`,
    },
    xAxis: {
      type: "time",
      axisLine: { show: false },
      axisTick: { show: false },
      axisLabel: { color: colors.muted, hideOverlap: true },
    },
    yAxis: {
      type: "value",
      scale: true,
      splitNumber: 4,
      splitLine: { lineStyle: { color: colors.grid } },
      axisLabel: { color: colors.muted, formatter: "{value}°" },
    },
    series: [
      line("Feels like", accent, toSeries(observations, (o) => o.heat_index_c), 3),
      line("Temperature", colors.muted, toSeries(observations, (o) => o.temperature_c), 2),
    ],
  };
}

export function TrendChart({ observations, accent, scheme }: Props) {
  const containerRef = useRef<HTMLDivElement>(null);
  const chartRef = useRef<ECharts | null>(null);

  useEffect(() => {
    const element = containerRef.current;
    if (!element) return;
    const chart = echarts.init(element);
    chartRef.current = chart;
    const observer = new ResizeObserver(() => chart.resize());
    observer.observe(element);
    return () => {
      observer.disconnect();
      chart.dispose();
      chartRef.current = null;
    };
  }, []);

  useEffect(() => {
    const chart = chartRef.current;
    const element = containerRef.current;
    if (!chart || !element) return;
    const styles = getComputedStyle(element);
    const read = (name: string) => styles.getPropertyValue(name).trim();
    chart.setOption(
      buildOption(
        { observations, accent },
        {
          text: read("--text"),
          muted: read("--text-secondary"),
          grid: read("--hairline"),
          surface: read("--surface"),
        },
      ),
      true,
    );
  }, [observations, accent, scheme]);

  return (
    <div
      ref={containerRef}
      className="chart"
      role="img"
      aria-label="Temperature and heat index over the last 72 hours"
    />
  );
}
