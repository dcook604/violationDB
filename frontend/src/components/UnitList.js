import React from 'react';
import { Link } from 'react-router-dom';

export default function UnitList({ units }) {

  if (!units || units.length === 0) {
    return <div className="p-4 text-center text-gray-500">No unit profiles found.</div>;
  }

  return (
    <div className="overflow-x-auto bg-white rounded-lg shadow">
      <table className="min-w-full divide-y divide-gray-200">
        <thead className="bg-gray-50">
          <tr>
            <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Unit Number</th>
            <th scope="col" className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Owner Last Name</th>
            <th scope="col" className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">Actions</th>
          </tr>
        </thead>
        <tbody className="bg-white divide-y divide-gray-200">
          {units.map(unit => (
            <tr key={unit.id} className="hover:bg-gray-50">
              <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">{unit.unit_number}</td>
              <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">{unit.owner_last_name}</td>
              <td className="px-6 py-4 whitespace-nowrap text-right text-sm font-medium">
                <Link 
                  to={`/units/${unit.unit_number}`} 
                  className="text-indigo-600 hover:text-indigo-900 hover:underline"
                >
                  View Details
                </Link>
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
} 