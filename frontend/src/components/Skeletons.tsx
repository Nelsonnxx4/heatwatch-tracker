interface SkeletonBarProps {
  className?: string;
}

export function SkeletonBar({ className = "" }: SkeletonBarProps) {
  return <span className={`skeleton-bar ${className}`} aria-hidden="true" />;
}

export function RankingListSkeleton() {
  return (
    <div className="ranking-skeleton" aria-busy="true" aria-label="Loading city rankings">
      {Array.from({ length: 7 }, (_, index) => (
        <div className="ranking-skeleton__row" key={index} aria-hidden="true">
          <SkeletonBar className="skeleton-bar--rank" />
          <SkeletonBar className="skeleton-bar--dot" />
          <span className="ranking-skeleton__name">
            <SkeletonBar className="skeleton-bar--city" />
            <SkeletonBar className="skeleton-bar--meta" />
          </span>
          <SkeletonBar className="skeleton-bar--value" />
        </div>
      ))}
    </div>
  );
}

export function MapSkeleton() {
  return (
    <div className="map-skeleton" role="status" aria-label="Loading global heat map">
      <div className="map-skeleton__land map-skeleton__land--americas" aria-hidden="true" />
      <div className="map-skeleton__land map-skeleton__land--eurasia" aria-hidden="true" />
      <div className="map-skeleton__land map-skeleton__land--africa" aria-hidden="true" />
      <div className="map-skeleton__land map-skeleton__land--oceania" aria-hidden="true" />
      <span className="map-skeleton__label">Loading map</span>
    </div>
  );
}

export function ConditionsSkeleton() {
  return (
    <div className="conditions-skeleton" aria-busy="true" aria-label="Loading current conditions">
      <div className="detail__lead">
        <div>
          <span className="metric__label">Current temperature</span>
          <SkeletonBar className="skeleton-bar--temperature" />
        </div>
        <div className="detail__risk">
          <SkeletonBar className="skeleton-bar--pill" />
          <SkeletonBar className="skeleton-bar--feels" />
        </div>
      </div>
      <dl className="stats">
        {["Humidity", "Wind", "High today", "Wind direction"].map((label) => (
          <div className="stat" key={label}>
            <dt>{label}</dt>
            <dd><SkeletonBar className="skeleton-bar--stat" /></dd>
          </div>
        ))}
      </dl>
      <SkeletonBar className="skeleton-bar--note" />
      <SkeletonBar className="skeleton-bar--updated" />
    </div>
  );
}

export function ChartSkeleton() {
  return (
    <div className="chart chart-skeleton" role="status" aria-label="Loading temperature trend">
      <span className="chart-skeleton__line chart-skeleton__line--top" aria-hidden="true" />
      <span className="chart-skeleton__line chart-skeleton__line--middle" aria-hidden="true" />
      <span className="chart-skeleton__line chart-skeleton__line--bottom" aria-hidden="true" />
      <span className="chart-skeleton__plot" aria-hidden="true" />
    </div>
  );
}
