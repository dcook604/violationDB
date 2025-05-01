import React from "react";
import { Navigate } from "react-router-dom";
import { useAuth } from "../context/AuthContext";

export function PrivateRoute({ children }) {
  const { user } = useAuth();
  return user ? children : <Navigate to="/login" />;
}

export function AdminRoute({ children }) {
  const { user } = useAuth();
  return user && user.role === "admin" ? children : <Navigate to="/dashboard" />;
} 