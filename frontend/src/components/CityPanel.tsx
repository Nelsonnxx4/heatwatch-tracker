import {
  HEAT_LEVELS,
  formatDegrees,
  formatTime,
  formatWindDirection,
  formatWindSpeed,
} from "@/lib/heat";
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
      <div className="detail__lead">
        <div>
          <span className="metric__label">Current temperature</span>
          <p className="detail__temp">{formatDegrees(current.temperature_c)}</p>
        </div>
        <div className="detail__risk">
          <span className="pill" style={{ background: level.color }}>
            {level.label}
          </span>
          <span>Feels like {formatDegrees(current.heat_index_c)}</span>
        </div>
      </div>
      <dl className="stats">
        <div className="stat">
          <dt>Humidity</dt>
          <dd>{current.humidity_pct === null ? "Unknown" : `${Math.round(current.humidity_pct)}%`}</dd>
        </div>
        <div className="stat">
          <dt>Wind</dt>
          <dd>
            {current.wind_speed_kmh == null
              ? "—"
              : formatWindSpeed(current.wind_speed_kmh)}
          </dd>
        </div>
        <div className="stat">
          <dt>High today</dt>
          <dd>{todaysHigh === undefined ? "Unknown" : formatDegrees(todaysHigh)}</dd>
        </div>
        <div className="stat">
          <dt>Wind direction</dt>
          <dd>
            {current.wind_direction_deg == null
              ? "—"
              : `${formatWindDirection(current.wind_direction_deg)} ${Math.round(current.wind_direction_deg)}°`}
          </dd>
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
    <section className="detail" aria-label={`${city.name} conditions`}>
      <div className="detail__top">
        <div>
          <p className="detail__back">Global heat map</p>
          <h1>{city.name}</h1>
          <p>{city.state}, {city.country}</p>
        </div>
        <button type="button" className="icon-button" aria-label="Close" onClick={onClose}>
          <span aria-hidden>×</span>
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
        <section className="trend">
          <div className="trend__header">
            <div>
              <h3>72-hour trend</h3>
              <p>Temperature and how hot it felt</p>
            </div>
            <div className="trend__legend" aria-label="Chart legend">
              <span><i style={{ background: accent }} /> Feels like</span>
              <span><i className="trend__legend-muted" /> Temperature</span>
            </div>
          </div>
          <TrendChart observations={trend.data} accent={accent} scheme={scheme} />
        </section>
      )}
    </section>
  );
}
