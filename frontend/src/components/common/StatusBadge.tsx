interface StatusBadgeProps {
  status: string;
}

const STATUS_MAP: Record<string, { containerClass: string; spinning?: boolean }> = {
  COMPLETED: { containerClass: 'bg-emerald-50 text-emerald-700 border border-emerald-200' },
  PROCESSING: { containerClass: 'bg-amber-50 text-amber-700 border border-amber-200', spinning: true },
  QUEUED: { containerClass: 'bg-sky-50 text-sky-700 border border-sky-200' },
  UPLOADED: { containerClass: 'bg-sky-50 text-sky-700 border border-sky-200' },
  FAILED: { containerClass: 'bg-red-50 text-red-700 border border-red-200' },
};

export default function StatusBadge({ status }: StatusBadgeProps) {
  const config = STATUS_MAP[status] ?? {
    containerClass: 'bg-slate-50 text-slate-600 border border-slate-200',
  };

  return (
    <span
      className={[
        'px-2 py-0.5 rounded text-xs font-medium inline-flex items-center gap-1',
        config.containerClass,
      ].join(' ')}
    >
      {config.spinning && (
        <span className="w-1.5 h-1.5 rounded-full bg-amber-500 animate-pulse" />
      )}
      {status.charAt(0) + status.slice(1).toLowerCase()}
    </span>
  );
}
