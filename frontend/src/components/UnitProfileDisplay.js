import React from 'react';
import { Link } from 'react-router-dom';

// Helper to display boolean values nicely
const YesNo = ({ value }) => (
  <span className={value ? 'text-green-600 font-semibold' : 'text-red-600 font-semibold'}>
    {value ? 'Yes' : 'No'}
  </span>
);

// Helper to format dates (could be moved to utils)
const formatDate = (dateString) => {
  if (!dateString) return 'N/A';
  try {
    return new Date(dateString).toLocaleDateString();
  } catch {
    return dateString;
  }
};

export default function UnitProfileDisplay({ unitData, violationSummary }) {
  if (!unitData) return null; // Or some placeholder

  const renderViolationCounts = () => {
    if (!violationSummary?.violation_counts_last_5_years) return <p>No violation history available.</p>;
    const years = Object.keys(violationSummary.violation_counts_last_5_years).sort().reverse();
    if (years.length === 0) return <p>No violations in the last 5 years.</p>;
    
    return (
      <ul className="list-disc pl-5">
        {years.map(year => (
          <li key={year}>{year}: {violationSummary.violation_counts_last_5_years[year]} violation(s)</li>
        ))}
      </ul>
    );
  };

  const renderOutstandingViolations = () => {
    if (!violationSummary?.outstanding_violations || violationSummary.outstanding_violations.length === 0) {
      return <p>No outstanding violations.</p>;
    }
    return (
      <ul className="list-disc pl-5 space-y-1">
        {violationSummary.outstanding_violations.map(v => (
          <li key={v.id}>
            <Link to={`/violations/public/${v.public_id}`} className="text-blue-600 hover:underline">
              {v.reference}
            </Link> - {v.category} ({v.status}, Created: {formatDate(v.created_at)})
          </li>
        ))}
      </ul>
    );
  };

  return (
    <div className="bg-white shadow-md rounded-lg p-6 space-y-6">

      {/* Owner Information Section */} 
      <section className="border-b pb-4">
        <h3 className="text-xl font-semibold text-gray-700 mb-3">Owner Information</h3>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-x-6 gap-y-2 text-sm">
          <div><strong className="text-gray-600">Unit Number:</strong> {unitData.unit_number}</div>
          <div><strong className="text-gray-600">Strata Lot:</strong> {unitData.strata_lot_number || 'N/A'}</div>
          <div><strong className="text-gray-600">Name:</strong> {unitData.owner_first_name} {unitData.owner_last_name}</div>
          <div><strong className="text-gray-600">Email:</strong> {unitData.owner_email}</div>
          <div><strong className="text-gray-600">Telephone:</strong> {unitData.owner_telephone}</div>
          <div className="md:col-span-2"><strong className="text-gray-600">Mailing Address:</strong> {unitData.owner_mailing_address || 'N/A'}</div>
        </div>
      </section>

      {/* Storage & Pet Information Section */} 
      <section className="border-b pb-4">
         <h3 className="text-xl font-semibold text-gray-700 mb-3">Storage & Pets</h3>
         <div className="grid grid-cols-1 md:grid-cols-2 gap-x-6 gap-y-2 text-sm">
            <div><strong className="text-gray-600">Parking Stalls:</strong> {unitData.parking_stall_numbers || 'N/A'}</div>
            <div><strong className="text-gray-600">Bike Storage:</strong> {unitData.bike_storage_numbers || 'N/A'}</div>
            <div><strong className="text-gray-600">Has Dog:</strong> <YesNo value={unitData.has_dog} /></div>
            <div><strong className="text-gray-600">Has Cat:</strong> <YesNo value={unitData.has_cat} /></div>
         </div>
      </section>
      
      {/* Rental Information Section */} 
      <section className="border-b pb-4">
        <h3 className="text-xl font-semibold text-gray-700 mb-3">Rental Information</h3>
        <div className="text-sm mb-3"><strong className="text-gray-600">Is Rented:</strong> <YesNo value={unitData.is_rented} /></div>
        {unitData.is_rented && (
            <div className="grid grid-cols-1 md:grid-cols-2 gap-x-6 gap-y-2 text-sm pl-4 border-l-2 border-gray-200">
              <div><strong className="text-gray-600">Tenant Name:</strong> {unitData.tenant_first_name || ''} {unitData.tenant_last_name || ''}</div>
              <div><strong className="text-gray-600">Tenant Email:</strong> {unitData.tenant_email || 'N/A'}</div>
              <div><strong className="text-gray-600">Tenant Telephone:</strong> {unitData.tenant_telephone || 'N/A'}</div>
            </div>
        )}
      </section>

      {/* Violation Summary Section */} 
      <section>
          <h3 className="text-xl font-semibold text-gray-700 mb-3">Violation History</h3>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6 text-sm">
            <div>
                <h4 className="font-semibold text-gray-600 mb-2">Violations Last 5 Years:</h4>
                {renderViolationCounts()}
            </div>
            <div>
                <h4 className="font-semibold text-gray-600 mb-2">Outstanding Violations:</h4>
                {renderOutstandingViolations()}
            </div>
            <div>
                 <h4 className="font-semibold text-gray-600 mb-2">Fines Levied:</h4>
                 <p>{violationSummary?.total_fines_levied ? `$${violationSummary.total_fines_levied}` : '$0.00'}</p>
                 {/* TODO: Display list of fines if API provides it */}
             </div>
          </div>
      </section>

       {/* Audit Info */}
       <div className="mt-4 pt-4 border-t text-xs text-gray-500">
          Last updated: {formatDate(unitData.updated_at)} by {unitData.updater_email || 'System'}
       </div>

    </div>
  );
} 