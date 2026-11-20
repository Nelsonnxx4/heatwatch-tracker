interface Props {
  title: string;
  body: string;
  actionLabel?: string;
  onAction?: () => void;
}

/** Empty and error states: say what happened and what to do next. */
export function StateMessage({ title, body, actionLabel, onAction }: Props) {
  return (
    <div className="message" role="status">
      <h2 className="message__title">{title}</h2>
      <p className="message__body">{body}</p>
      {actionLabel && onAction && (
        <button type="button" className="button" onClick={onAction}>
          {actionLabel}
        </button>
      )}
    </div>
  );
}
