import React from 'react';
import ViolationsTable from './ViolationsTable';
import PaginationControls from './PaginationControls';
import useViolationList from '../hooks/useViolationList';

export default function ViolationList() {
  const {
    violations,
    loading,
    error,
    page,
    perPage,
    totalPages,
    totalItems,
    dateFilter,
    handlePageChange,
    handlePerPageChange,
    handleDateFilterChange,
    refreshViolations
  } = useViolationList();

  if (loading) return (
    <div className="p-4 flex justify-center">
      <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-500"></div>
    </div>
  );
  
  if (error) return (
    <div className="p-4 text-red-600 bg-red-100 border border-red-400 rounded p-3">
      {error}
      <button 
        onClick={refreshViolations} 
        className="ml-4 bg-red-500 hover:bg-red-700 text-white font-bold py-1 px-2 rounded text-sm"
      >
        Retry
      </button>
    </div>
  );
  
  if (!violations.length) return (
    <div className="p-4 text-gray-600 bg-gray-100 border border-gray-300 rounded p-3">
      No violations found matching the current filters.
      <button 
        onClick={() => {
          // Reset filters and refresh
          handleDateFilterChange('');
          refreshViolations();
        }} 
        className="ml-4 bg-gray-500 hover:bg-gray-700 text-white font-bold py-1 px-2 rounded text-sm"
      >
        Clear Filters
      </button>
    </div>
  );

  return (
    <div className="p-4">
      <div className="flex justify-between items-center mb-4">
        <h2 className="text-2xl font-bold">Violations</h2>
        <button 
          onClick={refreshViolations}
          className="bg-blue-500 hover:bg-blue-700 text-white font-bold py-2 px-4 rounded flex items-center"
          disabled={loading}
        >
          <i className="fas fa-sync-alt mr-2"></i> Refresh
        </button>
      </div>
      
      {/* Filters and Controls */}
      <div className="flex flex-wrap gap-4 mb-4 items-center">
        <div className="flex items-center">
          <label htmlFor="dateFilter" className="mr-2 text-sm font-medium">Date Filter:</label>
          <select
            id="dateFilter"
            value={dateFilter}
            onChange={(e) => handleDateFilterChange(e.target.value)}
            className="border rounded px-2 py-1 text-sm"
          >
            <option value="">All Time</option>
            <option value="last7days">Last 7 Days</option>
            <option value="last30days">Last 30 Days</option>
          </select>
        </div>
        <div className="flex items-center">
          <label htmlFor="perPage" className="mr-2 text-sm font-medium">Show:</label>
          <select
            id="perPage"
            value={perPage}
            onChange={handlePerPageChange}
            className="border rounded px-2 py-1 text-sm"
          >
            <option value="5">5</option>
            <option value="10">10</option>
            <option value="25">25</option>
            <option value="50">50</option>
          </select>
        </div>
        <div className="text-sm text-gray-500">
          Showing {violations.length} of {totalItems} violations
        </div>
      </div>
      <ViolationsTable violations={violations} />
      <PaginationControls page={page} totalPages={totalPages} handlePageChange={handlePageChange} />
    </div>
  );
} 