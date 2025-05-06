import { useState, useEffect } from 'react';
import API from '../api';

export default function useViolationList() {
  const [violations, setViolations] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [page, setPage] = useState(1);
  const [perPage, setPerPage] = useState(10);
  const [totalPages, setTotalPages] = useState(1);
  const [totalItems, setTotalItems] = useState(0);
  const [dateFilter, setDateFilter] = useState('');

  useEffect(() => {
    setLoading(true);
    let url = `/api/violations?page=${page}&per_page=${perPage}`;
    if (dateFilter) {
      url += `&date_filter=${dateFilter}`;
    }
    API.get(url)
      .then(res => {
        if (res.data.violations) {
          setViolations(res.data.violations);
          setTotalPages(res.data.pagination.pages);
          setTotalItems(res.data.pagination.total);
        } else {
          setViolations(res.data || []);
        }
        setLoading(false);
      })
      .catch(() => {
        setError('Failed to load violations');
        setLoading(false);
      });
  }, [page, perPage, dateFilter]);

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
    handleDateFilterChange
  };
} 