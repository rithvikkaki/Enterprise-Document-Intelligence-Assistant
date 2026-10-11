import React from 'react';

interface StatusBadgeProps {
  status: string;
}

const STATUS_MAP: Record<string, { containerClass: string; dotClass?: string; spinning?: boolean }> = {
  COMPLETED: {
    containerClass: 'bg-emerald-50 text-emerald-700 border border-emerald-200/70',
    dotClass: 'bg-emerald-500',
  },
  PROCESSING: {
    containerClass: 'bg-amber-50 text-amber-700 border border-amber-200/70',
    dotClass: 'bg-amber-500',
    spinning: true,
  },
  QUEUED: {
    containerClass: 'bg-red-50 text-red-700 border border-red-200/70',
    dotClass: 'bg-red-500',
  },
  UPLOADED: {
    containerClass: 'bg-red-50 text-red-700 border border-red-200/70',
    dotClass: 'bg-red-500',
  },
  FAILED: {
    containerClass: 'bg-rose-50 text-rose-800 border border-rose-300/70',
    dotClass: 'bg-rose-600',
  },
};

export default function StatusBadge({ status }: StatusBadgeProps) {
  const config = STATUS_MAP[status] ?? {
    containerClass: 'bg-slate-50 text-slate-600 border border-slate-200',
    dotClass: 'bg-slate-400',
  };

  return (
    <span
      className={[
        'px-2.5 py-0.5 rounded-full text-xs font-semibold inline-flex items-center gap-1.5 shadow-2xs',
        config.containerClass,
      ].join(' ')}
    >
      <span
        className={[
          'w-1.5 h-1.5 rounded-full',
          config.dotClass,
          config.spinning ? 'animate-pulse' : '',
        ].join(' ')}
      />
      {status.charAt(0) + status.slice(1).toLowerCase()}
    </span>
  );
}
