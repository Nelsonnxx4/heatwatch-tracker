import { HEAT_LEVELS, formatDegrees, formatTime } from "@/lib/heat";
import { useHeatSummary, useTemperature } from "@/lib/queries";
import type { City, HeatSummary } from "@/lib/types";
import { useColorScheme } from "@/lib/useColorScheme";

import { StateMessage } from "./StateMessage";
import { TrendChart } from "./TrendChart";

interface Props {
  city: City;
  onClose: () => void;
}

function describeAnomaly(anomalyC: number | null): string {
  if (anomalyC === null) return "There isn't enough history yet to compare with recent days.";
  if (Math.abs(anomalyC) < 0.5) return "About the same as the recent average.";
  const direction = anomalyC > 0 ? "warmer" : "cooler";
  return `${Math.abs(anomalyC).toFixed(1)}° ${direction} than the recent average.`;
}

function Conditions({ summary }: { summary: HeatSummary }) {
  const { current, days, anomaly_c } = summary;
  const level = HEAT_LEVELS[current.heat_category];
  const todaysHigh = days.at(-1)?.temp_max_c;

  return (
    <>
      <p className="detail__temp">{formatDegrees(current.temperature_c)}</p>
      <div className="detail__feels">
        <span>Feels like {formatDegrees(current.heat_index_c)}</span>
        <span className="pill" style={{ background: level.color }}>
          {level.label}
        </span>
      </div>
      <dl className="stats">
        <div className="stat">
          <dt>Humidity</dt>
          <dd>{current.humidity_pct === null ? "Unknown" : `${Math.round(current.humidity_pct)}%`}</dd>
        </div>
        <div className="stat">
          <dt>High today</dt>
          <dd>{todaysHigh === undefined ? "Unknown" : formatDegrees(todaysHigh)}</dd>
        </div>
      </dl>
      <p className="detail__note">{describeAnomaly(anomaly_c)}</p>
      <p className="updated">Updated {formatTime(current.observed_at)}</p>
    </>
  );
}

export function CityPanel({ city, onClose }: Props) {
  const scheme = useColorScheme();
  const summary = useHeatSummary(city.slug);
  const trend = useTemperature(city.slug);
  const accent = summary.data ? HEAT_LEVELS[summary.data.current.heat_category].color : "#0a84ff";

  return (
    <section className="panel panel--right" aria-label={`${city.name} conditions`}>
      <div className="detail__top">
        <div>
          <h2 className="panel__title">{city.name}</h2>
          <p className="panel__subtitle">{city.state}</p>
        </div>
        <button type="button" className="icon-button" aria-label="Close" onClick={onClose}>
          ×
        </button>
      </div>

      {summary.isError ? (
        <StateMessage
          title="Can't load this city"
          body="The conditions for this city didn't load. Check your connection and try again."
          actionLabel="Try again"
          onAction={() => void summary.refetch()}
        />
      ) : summary.data ? (
        <Conditions summary={summary.data} />
      ) : (
        <div aria-busy="true">
          <div className="skeleton" style={{ height: 72, margin: "20px 0 0" }} />
          <div className="skeleton" style={{ margin: "12px 0 0" }} />
        </div>
      )}

      {trend.data && trend.data.length > 0 && (
        <>
          <h3 className="detail__chart-title">Last 72 hours</h3>
          <TrendChart observations={trend.data} accent={accent} scheme={scheme} />
        </>
      )}
    </section>
  );
}
