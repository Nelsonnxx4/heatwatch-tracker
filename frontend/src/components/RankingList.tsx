import { HEAT_LEVELS, formatDegrees } from "@/lib/heat";
import type { RankingItem } from "@/lib/types";

interface Props {
  items: RankingItem[];
  selected: string | null;
  onSelect: (slug: string) => void;
}

export function RankingList({ items, selected, onSelect }: Props) {
  return (
    <ul className="ranking">
      {items.map(({ city, heat_index_max_c, heat_category }) => {
        const level = HEAT_LEVELS[heat_category];
        return (
          <li key={city.slug}>
            <button
              type="button"
              className="ranking__row"
              aria-current={selected === city.slug}
              onClick={() => onSelect(city.slug)}
            >
              <span className="dot" style={{ background: level.color }} aria-hidden />
              <span className="ranking__name">
                <span className="ranking__city">{city.name}</span>
                <span className="ranking__meta">
                  {city.state}, {level.label}
                </span>
              </span>
              <span className="ranking__value">{formatDegrees(heat_index_max_c)}</span>
            </button>
          </li>
        );
      })}
    </ul>
  );
}
