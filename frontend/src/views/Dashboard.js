import React, { useState, useEffect } from "react";
import { useAuth } from "../context/AuthContext";
import API from "../api";
import { Link } from "react-router-dom";
import { fetchWithCache, invalidateCache } from "../utils/apiCache";

// Components
const StatCard = ({ title, value, icon, color, subtitle }) => (
  <div className="relative flex flex-col min-w-0 break-words bg-white rounded mb-6 xl:mb-0 shadow-lg">
    <div className="flex-auto p-4">
      <div className="flex flex-wrap">
        <div className="relative w-full pr-4 max-w-full flex-grow flex-1">
          <h5 className="text-blueGray-400 uppercase font-bold text-xs">
            {title}
            {subtitle && (
              <span className="block pt-1 text-xs">{subtitle}</span>
            )}
          </h5>
          <span className="font-semibold text-xl text-blueGray-700">
            {value}
          </span>
        </div>
        <div className="relative w-auto pl-4 flex-initial">
          <div className={`text-white p-3 text-center inline-flex items-center justify-center w-12 h-12 shadow-lg rounded-full ${color}`}>
            <i className={`${icon} text-lg`}></i>
          </div>
        </div>
      </div>
    </div>
  </div>
);

const RecentViolationsTable = ({ violations }) => (
  <div className="relative flex flex-col min-w-0 break-words bg-white w-full mb-6 shadow-lg rounded">
    <div className="rounded-t mb-0 px-4 py-3 border-0">
      <div className="flex flex-wrap items-center">
        <div className="relative w-full px-4 max-w-full flex-grow flex-1">
          <h3 className="font-semibold text-base text-blueGray-700">Recent Violations</h3>
        </div>
      </div>
    </div>
    <div className="block w-full overflow-x-auto">
      <table className="items-center w-full bg-transparent border-collapse">
        <thead>
          <tr>
            <th className="px-6 bg-blueGray-50 text-blueGray-500 align-middle border border-solid border-blueGray-100 py-3 text-xs uppercase border-l-0 border-r-0 whitespace-nowrap font-semibold text-left">Reference</th>
            <th className="px-6 bg-blueGray-50 text-blueGray-500 align-middle border border-solid border-blueGray-100 py-3 text-xs uppercase border-l-0 border-r-0 whitespace-nowrap font-semibold text-left">Unit No.</th>
            <th className="px-6 bg-blueGray-50 text-blueGray-500 align-middle border border-solid border-blueGray-100 py-3 text-xs uppercase border-l-0 border-r-0 whitespace-nowrap font-semibold text-left">Category</th>
            <th className="px-6 bg-blueGray-50 text-blueGray-500 align-middle border border-solid border-blueGray-100 py-3 text-xs uppercase border-l-0 border-r-0 whitespace-nowrap font-semibold text-left">Date</th>
            <th className="px-6 bg-blueGray-50 text-blueGray-500 align-middle border border-solid border-blueGray-100 py-3 text-xs uppercase border-l-0 border-r-0 whitespace-nowrap font-semibold text-left">Status</th>
            <th className="px-6 bg-blueGray-50 text-blueGray-500 align-middle border border-solid border-blueGray-100 py-3 text-xs uppercase border-l-0 border-r-0 whitespace-nowrap font-semibold text-left">Documents</th>
          </tr>
        </thead>
        <tbody>
          {violations.map((violation) => (
            <tr key={violation.id}>
              <th className="border-t-0 px-6 align-middle border-l-0 border-r-0 text-xs whitespace-nowrap p-4 text-left">
                <Link to={`/violations/public/${violation.public_id}`} className="text-blue-600 hover:underline">
                  {violation.reference}
                </Link>
              </th>
              <td className="border-t-0 px-6 align-middle border-l-0 border-r-0 text-xs whitespace-nowrap p-4">
                {violation.unit_number}
              </td>
              <td className="border-t-0 px-6 align-middle border-l-0 border-r-0 text-xs whitespace-nowrap p-4">
                {violation.category}
              </td>
              <td className="border-t-0 px-6 align-middle border-l-0 border-r-0 text-xs whitespace-nowrap p-4">
                {violation.created_at ? new Date(violation.created_at).toLocaleDateString() : 'Unknown date'}
              </td>
              <td className="border-t-0 px-6 align-middle border-l-0 border-r-0 text-xs whitespace-nowrap p-4">
                <span className="flex items-center">
                  <span className="inline-block w-3 h-3 rounded-full bg-emerald-500 mr-2"></span>
                  Active
                </span>
              </td>
              <td className="border-t-0 px-6 align-middle border-l-0 border-r-0 text-xs whitespace-nowrap p-4">
                <div className="flex space-x-3">
                {violation.html_path && (
                  <a 
                    href={`http://172.16.16.6:5004${violation.html_path}`} 
                    target="_blank" 
                    rel="noopener noreferrer" 
                      className="inline-block px-2 py-1 bg-green-100 text-green-800 rounded text-xs font-medium hover:bg-green-200"
                  >
                    HTML
                  </a>
                )}
                {violation.pdf_path && (
                  <a 
                    href={`http://172.16.16.6:5004${violation.pdf_path}`} 
                    target="_blank" 
                    rel="noopener noreferrer" 
                      className="inline-block px-2 py-1 bg-red-100 text-red-800 rounded text-xs font-medium hover:bg-red-200"
                  >
                    PDF
                  </a>
                )}
                  {!violation.html_path && !violation.pdf_path && (
                    <span className="text-gray-400">None</span>
                  )}
                </div>
              </td>
            </tr>
          ))}
          {violations.length === 0 && (
            <tr>
              <td colSpan="5" className="border-t-0 px-6 align-middle border-l-0 border-r-0 text-xs whitespace-nowrap p-4 text-center text-gray-500">
                No violations found
              </td>
            </tr>
          )}
        </tbody>
      </table>
    </div>
  </div>
);

export default function Dashboard() {
  const { user, loading: authLoading } = useAuth();
  const [stats, setStats] = useState({
    totalViolationsLastYear: 0,
    repeatOffenders: 0,
    activeViolations: 0,
    resolvedViolations: 0
  });
  const [recentViolations, setRecentViolations] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  // Cache duration constants
  const STATS_CACHE_DURATION = 5 * 60 * 1000; // 5 minutes
  const VIOLATIONS_CACHE_DURATION = 2 * 60 * 1000; // 2 minutes

  // Function to fetch dashboard data with caching
  const fetchDashboardData = async (forceFresh = false) => {
    if (!user) return; // Don't fetch if not authenticated
    
    setLoading(true);
    setError(null);
    
    try {
      // If forcing fresh data, invalidate the cache
      if (forceFresh) {
        invalidateCache('/api/stats', { method: 'GET', credentials: 'include' });
        invalidateCache('/api/violations?limit=5', { method: 'GET', credentials: 'include' });
      }

      // Fetch stats with caching
      const statsData = await fetchWithCache(
        '/api/stats',
        { method: 'GET', credentials: 'include' },
        STATS_CACHE_DURATION
      );
      
      // Fetch violations with caching
      const violationsData = await fetchWithCache(
        '/api/violations?limit=5',
        { method: 'GET', credentials: 'include' },
        VIOLATIONS_CACHE_DURATION
      );
      
      // Update stats
      setStats(statsData);
      
      // Handle both old and new API response formats for violations
      if (violationsData.violations) {
        setRecentViolations(violationsData.violations);
      } else {
        setRecentViolations(violationsData || []);
      }
    } catch (error) {
      console.error('Error fetching dashboard data:', error);
      setError('Failed to load dashboard data. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  // Initial data fetch
  useEffect(() => {
    if (!authLoading) {
      fetchDashboardData();
    }
  }, [user, authLoading]);

  // Function to manually refresh the dashboard
  const refreshDashboard = () => {
    fetchDashboardData(true);
  };

  if (authLoading || loading) {
    return (
      <div className="px-4 md:px-10 mx-auto w-full">
        <div className="flex justify-center items-center h-screen">
          <div className="animate-spin rounded-full h-32 w-32 border-b-2 border-lightBlue-500"></div>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="px-4 md:px-10 mx-auto w-full">
        <div className="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded relative" role="alert">
          <strong className="font-bold">Error!</strong>
          <span className="block sm:inline"> {error}</span>
          <button 
            onClick={refreshDashboard}
            className="mt-3 bg-red-500 hover:bg-red-700 text-white font-bold py-2 px-4 rounded"
          >
            Retry
          </button>
        </div>
      </div>
    );
  }

  return (
    <>
      <div className="relative md:pt-32 pb-32 pt-12">
        <div className="px-4 md:px-10 mx-auto w-full">
          <div className="flex justify-between items-center mb-4">
            <h1 className="text-2xl font-semibold">Dashboard</h1>
            <button 
              onClick={refreshDashboard}
              className="bg-blue-500 hover:bg-blue-700 text-white font-bold py-2 px-4 rounded flex items-center"
            >
              <i className="fas fa-sync-alt mr-2"></i> Refresh
            </button>
          </div>
          <div>
            <div className="flex flex-wrap">
              <div className="w-full lg:w-6/12 xl:w-3/12 px-4">
                <StatCard
                  title="Total Violations"
                  subtitle="(Last Year)"
                  value={stats.totalViolationsLastYear}
                  icon="fas fa-chart-bar"
                  color="bg-red-500"
                />
              </div>
              <div className="w-full lg:w-6/12 xl:w-3/12 px-4">
                <StatCard
                  title="Repeat Offenders"
                  value={stats.repeatOffenders}
                  icon="fas fa-exclamation-triangle"
                  color="bg-yellow-500"
                />
              </div>
              <div className="w-full lg:w-6/12 xl:w-3/12 px-4">
                <StatCard
                  title="Active Violations"
                  value={stats.activeViolations}
                  icon="fas fa-exclamation-circle"
                  color="bg-orange-500"
                />
              </div>
              <div className="w-full lg:w-6/12 xl:w-3/12 px-4">
                <StatCard
                  title="Resolved Violations"
                  value={stats.resolvedViolations}
                  icon="fas fa-check-circle"
                  color="bg-emerald-500"
                />
              </div>
            </div>
          </div>
        </div>
      </div>
      <div className="px-4 md:px-10 mx-auto w-full -m-24">
        <div className="flex flex-wrap">
          <div className="w-full mb-12 xl:mb-0 px-4">
            <RecentViolationsTable violations={recentViolations} />
          </div>
        </div>
      </div>
    </>
  );
} 