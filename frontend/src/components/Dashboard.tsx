"use client";

import { useEffect, useMemo, useState } from "react";

import { useRankings } from "@/lib/queries";

import { CityPanel } from "./CityPanel";
import { MapView } from "./MapView";
import { RankingList } from "./RankingList";
import { StateMessage } from "./StateMessage";

export function Dashboard() {
  const { data, isPending, isError, refetch } = useRankings();
  const [selected, setSelected] = useState<string | null>(null);

  const items = useMemo(() => data ?? [], [data]);
  const selectedCity = items.find((item) => item.city.slug === selected)?.city ?? null;

  useEffect(() => {
    const onKeyDown = (event: KeyboardEvent) => {
      if (event.key === "Escape") setSelected(null);
    };
    window.addEventListener("keydown", onKeyDown);
    return () => window.removeEventListener("keydown", onKeyDown);
  }, []);

  return (
    <main className={`app${selectedCity ? " has-selection" : ""}`}>
      <MapView items={items} selected={selected} onSelect={setSelected} />

      <aside className="panel panel--left" aria-label="Hottest cities">
        <header className="panel__header">
          <h1 className="panel__title">HeatWatch</h1>
          <p className="panel__subtitle">Hottest cities, last 24 hours</p>
        </header>

        {isPending && (
          <div aria-busy="true">
            {Array.from({ length: 6 }, (_, index) => (
              <div key={index} className="skeleton" />
            ))}
          </div>
        )}
        {isError && (
          <StateMessage
            title="Can't reach the API"
            body="Make sure the HeatWatch backend is running, then try again."
            actionLabel="Try again"
            onAction={() => void refetch()}
          />
        )}
        {data && data.length === 0 && (
          <StateMessage
            title="No readings yet"
            body="Run the ingestion job to load the first temperatures: docker compose run --rm ingest"
          />
        )}
        {data && data.length > 0 && (
          <RankingList items={items} selected={selected} onSelect={setSelected} />
        )}
      </aside>

      {selectedCity && (
        <CityPanel key={selectedCity.slug} city={selectedCity} onClose={() => setSelected(null)} />
      )}
    </main>
  );
}
