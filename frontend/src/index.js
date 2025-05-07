import React from 'react';
import ReactDOM from 'react-dom/client';
import './assets/styles/index.css';
import "@fortawesome/fontawesome-free/css/all.min.css";
import App from './App';
import reportWebVitals from './reportWebVitals';
import * as Sentry from "@sentry/react";
import { BrowserTracing } from "@sentry/tracing";

// Initialize Sentry
// Only initialize if REACT_APP_SENTRY_DSN is set
if (process.env.REACT_APP_SENTRY_DSN) {
  Sentry.init({
    dsn: process.env.REACT_APP_SENTRY_DSN,
    integrations: [new BrowserTracing()],
    
    // We recommend adjusting this in production, for now capture all transactions
    tracesSampleRate: 1.0,
    
    // Only enable in production
    enabled: process.env.NODE_ENV === 'production',
    
    // Capture user interaction like clicks, navigation, etc.
    autoSessionTracking: true,
    
    // Set environment
    environment: process.env.NODE_ENV
  });
  console.log(`Sentry initialized in ${process.env.NODE_ENV} mode`);
} else {
  console.warn("Sentry DSN not found. Sentry integration disabled.");
}

const root = ReactDOM.createRoot(document.getElementById('root'));
root.render(
  <React.StrictMode>
    <Sentry.ErrorBoundary fallback={<p>An error has occurred. Our team has been notified.</p>}>
      <App />
    </Sentry.ErrorBoundary>
  </React.StrictMode>
);

// If you want to start measuring performance in your app, pass a function
// to log results (for example: reportWebVitals(console.log))
// or send to an analytics endpoint. Learn more: https://bit.ly/CRA-vitals
reportWebVitals();
