import { useState, useEffect, useCallback } from 'react';
import API from '../api';
import { fetchWithCache, invalidateCache } from '../utils/apiCache';

export default function useViolationList() {
  const [violations, setViolations] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [page, setPage] = useState(1);
  const [perPage, setPerPage] = useState(10);
  const [totalPages, setTotalPages] = useState(1);
  const [totalItems, setTotalItems] = useState(0);
  const [dateFilter, setDateFilter] = useState('');

  // Cache duration - 2 minutes
  const CACHE_DURATION = 2 * 60 * 1000;

  const fetchViolations = useCallback(async (forceFresh = false) => {
    setLoading(true);
    setError(null);

    let url = `/api/violations?page=${page}&per_page=${perPage}`;
    if (dateFilter) {
      url += `&date_filter=${dateFilter}`;
    }

    try {
      // If forceFresh is true, invalidate the cache first
      if (forceFresh) {
        invalidateCache(url, { method: 'GET', credentials: 'include' });
      }

      // Use fetchWithCache instead of API.get
      const data = await fetchWithCache(
        url, 
        { method: 'GET', credentials: 'include' },
        CACHE_DURATION
      );

      // Process the response data
      if (data.violations) {
        setViolations(data.violations);
        setTotalPages(data.pagination.pages);
        setTotalItems(data.pagination.total);
      } else {
        setViolations(data || []);
      }
    } catch (err) {
      console.error('Error fetching violations:', err);
      setError('Failed to load violations');
    } finally {
      setLoading(false);
    }
  }, [page, perPage, dateFilter]);

  // Initial fetch and when dependencies change
  useEffect(() => {
    fetchViolations();
  }, [fetchViolations]);

  const handlePageChange = (newPage) => {
    if (newPage > 0 && newPage <= totalPages) {
      setPage(newPage);
    }
  };

  const handlePerPageChange = (e) => {
    const value = parseInt(e.target.value, 10);
    setPerPage(value);
    setPage(1);
  };

  const handleDateFilterChange = (value) => {
    setDateFilter(value);
    setPage(1);
  };

  // Add function to force refresh data
  const refreshViolations = () => {
    fetchViolations(true);
  };

  return {
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
  };
} 