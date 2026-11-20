"use client";

import "maplibre-gl/dist/maplibre-gl.css";

import { useEffect, useMemo, useRef } from "react";
import MapGL, { Marker, NavigationControl, type MapRef } from "react-map-gl/maplibre";

import { HEAT_LEVELS, markerSize } from "@/lib/heat";
import type { RankingItem } from "@/lib/types";
import { prefersReducedMotion, useColorScheme } from "@/lib/useColorScheme";

const BASEMAPS = {
  light: "https://basemaps.cartocdn.com/gl/positron-gl-style/style.json",
  dark: "https://basemaps.cartocdn.com/gl/dark-matter-gl-style/style.json",
} as const;

const NIGERIA_VIEW = { longitude: 8.7, latitude: 9.1, zoom: 5.3 };
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

  useEffect(() => {
    const map = mapRef.current;
    if (!map || !selectedCity) return;
    map.flyTo({
      center: [selectedCity.longitude, selectedCity.latitude],
      zoom: Math.max(map.getZoom(), SELECTED_MIN_ZOOM),
      duration: prefersReducedMotion() ? 0 : FLY_DURATION_MS,
    });
  }, [selectedCity]);

  return (
    <div className="map">
      <MapGL
        ref={mapRef}
        initialViewState={NIGERIA_VIEW}
        mapStyle={BASEMAPS[scheme]}
        attributionControl={{ compact: true }}
        style={{ width: "100%", height: "100%" }}
      >
        <NavigationControl position="bottom-right" showCompass={false} />
        {items.map(({ city, heat_index_max_c, heat_category }) => {
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
                <span className="pin__label">{city.name}</span>
              </button>
            </Marker>
          );
        })}
      </MapGL>
    </div>
  );
}
