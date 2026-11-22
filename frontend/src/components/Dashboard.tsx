"use client";

import { useCallback, useEffect, useMemo, useState } from "react";

import { useRankings } from "@/lib/queries";

import { CityPanel } from "./CityPanel";
import { MapView } from "./MapView";
import { RankingList } from "./RankingList";
import { StateMessage } from "./StateMessage";

export function Dashboard() {
  const { data, isPending, isError, refetch } = useRankings();
  const [selected, setSelected] = useState<string | null>(null);
  const [query, setQuery] = useState("");

  const items = useMemo(() => data ?? [], [data]);
  const visibleItems = useMemo(() => {
    const term = query.trim().toLocaleLowerCase();
    if (!term) return items;
    return items.filter(({ city }) =>
      `${city.name} ${city.state} ${city.country}`.toLocaleLowerCase().includes(term),
    );
  }, [items, query]);
  const selectedCity = items.find((item) => item.city.slug === selected)?.city ?? null;

  useEffect(() => {
    const syncSelectionFromUrl = () => {
      setSelected(new URLSearchParams(window.location.search).get("city"));
    };

    syncSelectionFromUrl();
    window.addEventListener("popstate", syncSelectionFromUrl);

    const onKeyDown = (event: KeyboardEvent) => {
      if (event.key === "Escape") {
        setSelected(null);
        window.history.pushState({}, "", window.location.pathname);
      }
    };
    window.addEventListener("keydown", onKeyDown);
    return () => {
      window.removeEventListener("popstate", syncSelectionFromUrl);
      window.removeEventListener("keydown", onKeyDown);
    };
  }, []);

  const selectCity = useCallback((slug: string) => {
    setSelected(slug);
    window.history.pushState({}, "", `?city=${encodeURIComponent(slug)}`);
  }, []);

  const closeCity = useCallback(() => {
    setSelected(null);
    window.history.pushState({}, "", window.location.pathname);
  }, []);

  return (
    <main className={`app${selectedCity ? " has-selection" : ""}`}>
      <header className="topbar">
        <div className="brand" aria-label="HeatWatch global weather monitor">
          <span className="brand__mark" aria-hidden><span /></span>
          <span>HeatWatch</span>
        </div>
        <p className="topbar__scope">Global · Live heat monitor</p>
        <span className="live-status"><span aria-hidden /> Latest observations</span>
      </header>

      <aside className="sidebar" aria-label="Hottest cities">
        <header className="sidebar__header">
          {selectedCity ? <h2>Heat around the world</h2> : <h1>Heat around the world</h1>}
          <p>Major cities ranked by peak heat index</p>
        </header>

        <div className="sidebar__list-heading">
          <span>Hottest now</span>
          {data && (
            <span>
              {visibleItems.length === data.length
                ? `${data.length} cities`
                : `${visibleItems.length} of ${data.length}`}
            </span>
          )}
        </div>

        {data && data.length > 0 && (
          <label className="city-search">
            <span>Find a city</span>
            <input
              type="search"
              value={query}
              placeholder="City, state, or country"
              onChange={(event) => setQuery(event.target.value)}
            />
          </label>
        )}

        {isPending && (
          <div className="skeleton-list" aria-busy="true" aria-label="Loading city rankings">
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
        {data && data.length > 0 && visibleItems.length === 0 && (
          <StateMessage
            title="No matching cities"
            body="Try another city, state, or country name."
          />
        )}
        {data && visibleItems.length > 0 && (
          <RankingList items={visibleItems} selected={selected} onSelect={selectCity} />
        )}
      </aside>

      <section className="workspace" aria-label="Global heat map">
        <MapView items={visibleItems} selected={selected} onSelect={selectCity} />

        <div className="map-key" aria-label="Heat risk legend">
          <span><i className="key-dot key-dot--normal" /> Comfortable</span>
          <span><i className="key-dot key-dot--caution" /> Caution</span>
          <span><i className="key-dot key-dot--danger" /> Danger</span>
        </div>

        {!isPending && !isError && items.length > 0 && !selectedCity && (
          <p className="map-hint">Select a city marker or ranking for details</p>
        )}

        {selectedCity && (
          <CityPanel key={selectedCity.slug} city={selectedCity} onClose={closeCity} />
        )}
      </section>
    </main>
  );
}
