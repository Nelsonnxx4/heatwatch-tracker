"use client";

import "maplibre-gl/dist/maplibre-gl.css";

import { useCallback, useEffect, useMemo, useRef } from "react";
import MapGL, { Marker, NavigationControl, type MapRef } from "react-map-gl/maplibre";

import { HEAT_LEVELS, markerSize } from "@/lib/heat";
import type { RankingItem } from "@/lib/types";
import { prefersReducedMotion, useColorScheme } from "@/lib/useColorScheme";

const BASEMAPS = {
  light: "https://basemaps.cartocdn.com/gl/positron-gl-style/style.json",
  dark: "https://basemaps.cartocdn.com/gl/dark-matter-gl-style/style.json",
} as const;

const WORLD_VIEW = { longitude: 10, latitude: 22, zoom: 1.15 };
const SELECTED_MIN_ZOOM = 6.5;
const FLY_DURATION_MS = 900;

interface Props {
  items: RankingItem[];
  selected: string | null;
  onSelect: (slug: string) => void;
}

export function MapView({ items, selected, onSelect }: Props) {
  const scheme = useColorScheme();
  const mapRef = useRef<MapRef>(null);

  const selectedCity = useMemo(
    () => items.find((item) => item.city.slug === selected)?.city ?? null,
    [items, selected],
  );

  const fitOverview = useCallback(() => {
    const map = mapRef.current;
    if (!map || items.length === 0) return;

    const longitudes = items.map(({ city }) => city.longitude);
    const latitudes = items.map(({ city }) => city.latitude);
    const compact = window.innerWidth <= 900;

    map.fitBounds(
      [
        [Math.min(...longitudes), Math.min(...latitudes)],
        [Math.max(...longitudes), Math.max(...latitudes)],
      ],
      {
        padding: compact
          ? { top: 70, right: 42, bottom: Math.min(470, window.innerHeight * 0.5), left: 42 }
          : { top: 80, right: 80, bottom: 80, left: 80 },
        duration: 0,
        maxZoom: compact ? 4.2 : 6,
      },
    );
  }, [items]);

  useEffect(() => {
    if (!selected) fitOverview();
  }, [fitOverview, selected]);

  useEffect(() => {
    const map = mapRef.current;
    if (!map || !selectedCity) return;
    map.flyTo({
      center: [selectedCity.longitude, selectedCity.latitude],
      zoom: Math.max(map.getZoom(), SELECTED_MIN_ZOOM),
      offset: window.innerWidth <= 900 ? [0, -Math.min(140, window.innerHeight * 0.18)] : [0, 0],
      duration: prefersReducedMotion() ? 0 : FLY_DURATION_MS,
    });
  }, [selectedCity]);

  return (
    <div className="map">
      <MapGL
        ref={mapRef}
        initialViewState={WORLD_VIEW}
        mapStyle={BASEMAPS[scheme]}
        attributionControl={{ compact: true }}
        onLoad={fitOverview}
        style={{ width: "100%", height: "100%" }}
      >
        <NavigationControl position="bottom-right" showCompass={false} />
        {items.map(({ city, heat_index_max_c, heat_category }, index) => {
          const size = markerSize(heat_index_max_c);
          return (
            <Marker key={city.slug} longitude={city.longitude} latitude={city.latitude} anchor="top">
              <button
                type="button"
                className="pin"
                aria-pressed={selected === city.slug}
                aria-label={`${city.name}, ${HEAT_LEVELS[heat_category].label}`}
                onClick={() => onSelect(city.slug)}
              >
                <span
                  className="pin__dot"
                  style={{ width: size, height: size, background: HEAT_LEVELS[heat_category].color }}
                />
                <span className={`pin__label${index >= 8 ? " pin__label--secondary" : ""}`}>
                  {city.name}
                </span>
              </button>
            </Marker>
          );
        })}
      </MapGL>
    </div>
  );
}
