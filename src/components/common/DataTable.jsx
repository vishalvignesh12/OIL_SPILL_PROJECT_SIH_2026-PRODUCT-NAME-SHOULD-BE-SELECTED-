import React, { useState, useMemo } from 'react';

/**
 * DataTable Component
 * Zebra-striped government table with column sorting, filtering, and row clicks
 */
export default function DataTable({
  columns,
  data,
  onRowClick,
  emptyMessage = 'No records found matching criteria',
  pageSize = 10,
  className = ''
}) {
  const [sortKey, setSortKey] = useState(null);
  const [sortDirection, setSortDirection] = useState('asc');
  const [currentPage, setCurrentPage] = useState(1);

  const handleSort = (key) => {
    if (sortKey === key) {
      setSortDirection(sortDirection === 'asc' ? 'desc' : 'asc');
    } else {
      setSortKey(key);
      setSortDirection('asc');
    }
  };

  const sortedData = useMemo(() => {
    if (!sortKey) return data;
    return [...data].sort((a, b) => {
      let aVal = a[sortKey];
      let bVal = b[sortKey];
      if (typeof aVal === 'string') aVal = aVal.toLowerCase();
      if (typeof bVal === 'string') bVal = bVal.toLowerCase();
      if (aVal < bVal) return sortDirection === 'asc' ? -1 : 1;
      if (aVal > bVal) return sortDirection === 'asc' ? 1 : -1;
      return 0;
    });
  }, [data, sortKey, sortDirection]);

  const totalPages = Math.ceil(sortedData.length / pageSize) || 1;
  const paginatedData = useMemo(() => {
    const start = (currentPage - 1) * pageSize;
    return sortedData.slice(start, start + pageSize);
  }, [sortedData, currentPage, pageSize]);

  return (
    <div className={`w-full bg-surface-container-lowest border border-outline-variant rounded overflow-hidden flex flex-col ${className}`}>
      <div className="overflow-x-auto w-full">
        <table className="w-full text-left border-collapse">
          <thead>
            <tr className="bg-surface-container-low border-b border-outline-variant">
              {columns.map((col) => (
                <th
                  key={col.key || col.header}
                  onClick={() => col.sortable !== false && col.key && handleSort(col.key)}
                  className={`py-3.5 px-4 text-label-md font-bold text-primary tracking-wide ${
                    col.sortable !== false && col.key ? 'cursor-pointer hover:bg-surface-container-high transition-colors select-none' : ''
                  }`}
                  style={{ width: col.width }}
                >
                  <div className="flex items-center gap-1.5">
                    <span>{col.header}</span>
                    {col.sortable !== false && col.key && (
                      <span className="material-symbols-outlined text-[14px] text-outline">
                        {sortKey === col.key
                          ? sortDirection === 'asc'
                            ? 'arrow_upward'
                            : 'arrow_downward'
                          : 'unfold_more'}
                      </span>
                    )}
                  </div>
                </th>
              ))}
            </tr>
          </thead>
          <tbody className="divide-y divide-outline-variant/60 font-body-md text-on-surface">
            {paginatedData.length === 0 ? (
              <tr>
                <td colSpan={columns.length} className="py-12 text-center text-on-surface-variant font-body-md">
                  <span className="material-symbols-outlined text-[36px] text-outline mb-2 block">folder_off</span>
                  {emptyMessage}
                </td>
              </tr>
            ) : (
              paginatedData.map((row, idx) => (
                <tr
                  key={row.id || idx}
                  onClick={() => onRowClick && onRowClick(row)}
                  className={`transition-colors ${
                    idx % 2 === 1 ? 'bg-surface-container-low/50' : 'bg-surface-container-lowest'
                  } ${onRowClick ? 'cursor-pointer hover:bg-surface-container-high' : ''}`}
                >
                  {columns.map((col) => (
                    <td key={col.key || col.header} className="py-3 px-4 text-label-md">
                      {col.render ? col.render(row[col.key], row) : row[col.key]}
                    </td>
                  ))}
                </tr>
              ))
            )}
          </tbody>
        </table>
      </div>

      {/* Pagination Footer */}
      {totalPages > 1 && (
        <div className="px-4 py-3 bg-surface-container-low border-t border-outline-variant flex items-center justify-between text-label-sm text-on-surface-variant">
          <span>
            Showing <strong className="text-on-surface">{(currentPage - 1) * pageSize + 1}</strong> to{' '}
            <strong className="text-on-surface">{Math.min(currentPage * pageSize, sortedData.length)}</strong> of{' '}
            <strong className="text-on-surface">{sortedData.length}</strong> results
          </span>

          <div className="flex items-center gap-1">
            <button
              onClick={() => setCurrentPage(p => Math.max(1, p - 1))}
              disabled={currentPage === 1}
              className="p-1.5 rounded border border-outline-variant bg-surface-container-lowest hover:bg-surface-container disabled:opacity-40 disabled:cursor-not-allowed transition-colors"
            >
              <span className="material-symbols-outlined text-[16px]">chevron_left</span>
            </button>
            <span className="px-3 font-semibold text-primary">
              {currentPage} / {totalPages}
            </span>
            <button
              onClick={() => setCurrentPage(p => Math.min(totalPages, p + 1))}
              disabled={currentPage === totalPages}
              className="p-1.5 rounded border border-outline-variant bg-surface-container-lowest hover:bg-surface-container disabled:opacity-40 disabled:cursor-not-allowed transition-colors"
            >
              <span className="material-symbols-outlined text-[16px]">chevron_right</span>
            </button>
          </div>
        </div>
      )}
    </div>
  );
}
