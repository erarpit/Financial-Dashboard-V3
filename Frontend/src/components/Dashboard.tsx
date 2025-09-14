// src/components/Dashboard.tsx

import React from 'react';
import { useDashboardData } from '../hooks/useApi';
import LoadingSpinner from './LoadingSpinner';
import ErrorMessage from './ErrorMessage';

// Lazy load components to avoid import errors if files are missing or to improve performance
const StockGrid = React.lazy(() => import('./StockGrid'));
const SignalsPanel = React.lazy(() => import('./SignalsPanel'));
const NewsPanel = React.lazy(() => import('./NewsPanel'));
const AIChat = React.lazy(() => import('./AIChat'));

interface DashboardProps {
  tickers: string[];
  onStockSelect: (ticker: string) => void;
}

const Dashboard: React.FC<DashboardProps> = ({ tickers, onStockSelect }) => {
  const { data, loading, error } = useDashboardData(tickers);

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-100 flex items-center justify-center">
        <LoadingSpinner size="large" />
      </div>
    );
  }

  if (error) {
    return (
      <div className="min-h-screen bg-gray-100 flex items-center justify-center p-4">
        <ErrorMessage message={error} onRetry={() => window.location.reload()} />
      </div>
    );
  }

  if (!data) {
    return (
      <div className="min-h-screen bg-gray-100 flex items-center justify-center p-4">
        <div className="text-center">
          <h2 className="text-2xl font-bold text-gray-900 mb-2">No Data Available</h2>
          <p className="text-gray-600">Please check your connection and try again.</p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-100">
      {/* Header */}
      <header className="bg-white shadow-sm border-b border-gray-200 p-4">
        <div className="max-w-7xl mx-auto flex justify-between items-center">
          <h1 className="text-2xl font-bold text-gray-900">AI Financial Dashboard</h1>
          <span className="text-sm text-gray-500">
            Last updated: {new Date(data.timestamp).toLocaleString()}
          </span>
        </div>
      </header>

      {/* Main Content */}
      <main className="max-w-7xl mx-auto p-4 grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Stock Grid */}
        <section className="lg:col-span-2 bg-white rounded-lg shadow p-4">
          <div className="flex justify-between items-center mb-4">
            <h2 className="text-xl font-semibold text-gray-900">Stock Portfolio</h2>
            <span className="text-sm text-gray-500">{data.stocks.length} stocks</span>
          </div>
          <StockGrid stocks={data.stocks} onSelect={onStockSelect} />
        </section>

        {/* Side Panel */}
        <aside className="space-y-6">
          <section className="bg-white rounded-lg shadow p-4">
            <h2 className="text-xl font-semibold text-gray-900 mb-3">AI Trading Signals</h2>
            <SignalsPanel signals={data.signals} />
          </section>
          <section className="bg-white rounded-lg shadow p-4">
            <h2 className="text-xl font-semibold text-gray-900 mb-3">Market Sentiment</h2>
            <NewsPanel news={data.news} />
          </section>
          <section className="bg-white rounded-lg shadow p-4">
            <h2 className="text-xl font-semibold text-gray-900 mb-3">AI Assistant</h2>
            <React.Suspense fallback={<LoadingSpinner />}>
              <AIChat />
            </React.Suspense>
          </section>
        </aside>
      </main>
    </div>
  );
};

export default Dashboard;
