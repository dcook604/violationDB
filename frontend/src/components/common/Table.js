import React from 'react';

export default function Table({ columns, data, renderCell }) {
  return (
    <div className="overflow-x-auto">
      <table className="min-w-full bg-white border border-gray-200 rounded-lg">
        <thead>
          <tr>
            {columns.map(col => (
              <th key={col.accessor} className="px-4 py-2 border-b text-left font-semibold">{col.label}</th>
            ))}
          </tr>
        </thead>
        <tbody>
          {data.map((row, i) => (
            <tr key={row.id || i} className="hover:bg-gray-50">
              {columns.map(col => (
                <td key={col.accessor} className="px-4 py-2 border-b">
                  {renderCell ? renderCell(row, col) : row[col.accessor]}
                </td>
              ))}
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
} 