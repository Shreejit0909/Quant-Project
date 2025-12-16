import React, { useState, useEffect } from 'react';
import { TrendingUp, TrendingDown, Activity, CheckCircle2, AlertTriangle, ChevronDown } from 'lucide-react';
import { Card, CardContent, CardHeader, CardTitle } from '../components/ui/card';
import { Badge } from '../components/ui/badge';
import {
    Select,
    SelectContent,
    SelectItem,
    SelectTrigger,
    SelectValue,
} from '../components/ui/select';
import { api } from '../services/api';
import { useLastUpdated } from '../hooks/useLastUpdated';
import { formatToLocal } from '../utils/dateUtils';

const Dashboard = () => {
    const [metrics, setMetrics] = useState(null);
    const [alert, setAlert] = useState(null);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(false);
    const [selectedPair, setSelectedPair] = useState('BTC-ETH');
    const { timeAgo, updateTimestamp } = useLastUpdated();

    useEffect(() => {
        loadDashboardData();
        const interval = setInterval(loadDashboardData, 5000);
        return () => clearInterval(interval);
    }, []);

    const loadDashboardData = async () => {
        try {
            const [analytics, alertData] = await Promise.all([
                api.getAnalyticsLatest(),
                api.getLatestAlert(),
            ]);

            // Validate Data Integrity
            if (
                typeof analytics.zscore !== 'number' ||
                typeof analytics.spread !== 'number' ||
                typeof analytics.correlation !== 'number'
            ) {
                console.warn('Invalid analytics data received', analytics);
                setMetrics(null);
                // Or set partial? Request Says: "Log warning + skip render" of invalid parts.
                // But for dashboard, if core metrics are missing, we should probably show 'Waiting'.
                // Let's setMetrics to null to trigger empty state.
                return;
            }

            // Should be non-negative spread
            if (analytics.spread < 0) {
                console.warn('Negative spread received', analytics.spread);
            }

            setMetrics({
                zscore: analytics.zscore,
                spread: analytics.spread,
                correlation: analytics.correlation,
                stationary: !!analytics.stationary, // Ensure boolean
            });

            // Validate Alert
            if (!alertData || typeof alertData.z_score !== 'number' || !alertData.timestamp) {
                console.warn('Invalid alert data', alertData);
                setAlert(null);
            } else {
                setAlert(alertData);
            }

            setLoading(false);
            setError(false);
            updateTimestamp(); // Keep the "Updated X ago" logic alive
        } catch (error) {
            console.error('Error loading dashboard data:', error);
            setError(true);
            setLoading(false);
        }
    };

    if (loading && !metrics) {
        return (
            <div className="max-w-7xl mx-auto px-6 py-8">
                <div className="mb-8">
                    <h1 className="text-3xl font-bold text-white mb-2">Dashboard Overview</h1>
                    <p className="text-sm text-gray-500">Waiting for market data...</p>
                </div>
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
                    {[1, 2, 3, 4].map((i) => (
                        <div key={i} className="h-32 bg-[#0E1621] rounded-lg animate-pulse border border-gray-800" />
                    ))}
                </div>
            </div>
        );
    }

    if (error && !metrics) {
        return (
            <div className="max-w-7xl mx-auto px-6 py-8">
                <div className="mb-8">
                    <h1 className="text-3xl font-bold text-white mb-2">Dashboard Overview</h1>
                    <p className="text-sm text-red-500">Backend unavailable. Retrying...</p>
                </div>
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
                    {[1, 2, 3, 4].map((i) => (
                        <Card key={i} className="bg-[#0E1621] border-gray-800 opacity-50">
                            <CardContent className="py-8 text-center">
                                <p className="text-gray-500 text-sm">Waiting...</p>
                            </CardContent>
                        </Card>
                    ))}
                </div>
            </div>
        );
    }

    const getZScoreColor = (zscore) => {
        if (typeof zscore !== 'number') return 'text-gray-500';
        if (Math.abs(zscore) > 2) return 'text-red-500';
        if (Math.abs(zscore) > 1.5) return 'text-yellow-500';
        return 'text-emerald-500';
    };

    return (
        <div className="max-w-7xl mx-auto px-6 py-8">
            <div className="flex items-center justify-between mb-8">
                <div>
                    <h1 className="text-3xl font-bold text-white mb-1">Dashboard Overview</h1>
                    {timeAgo && (
                        <p className="text-xs text-gray-500">Updated {timeAgo}</p>
                    )}
                </div>

                {/* Trading Pair Selector - Locked to BTC-ETH */}
                <div className="flex items-center space-x-3">
                    <span className="text-sm text-gray-400">Trading Pair:</span>
                    <Select value="BTC-ETH" disabled>
                        <SelectTrigger className="w-[180px] bg-[#0E1621] border-gray-800 text-white cursor-not-allowed opacity-80">
                            <SelectValue placeholder="BTC-ETH" />
                        </SelectTrigger>
                        <SelectContent className="bg-[#0E1621] border-gray-800">
                            <SelectItem value="BTC-ETH" className="text-white">
                                <div className="flex items-center justify-between w-full">
                                    <span>BTC-ETH</span>
                                    <Badge className="ml-2 bg-emerald-500/20 text-emerald-500 border-emerald-500/30 text-xs">
                                        Active
                                    </Badge>
                                </div>
                            </SelectItem>
                        </SelectContent>
                    </Select>
                </div>
            </div>

            {/* Metrics Cards */}
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
                {/* Z-Score */}
                <Card className="bg-[#0E1621] border-gray-800 hover:border-gray-700 transition-all duration-200">
                    <CardHeader className="pb-3">
                        <CardTitle className="text-sm font-medium text-gray-400 flex items-center justify-between">
                            Z-Score
                            <Activity className="w-4 h-4" />
                        </CardTitle>
                    </CardHeader>
                    <CardContent>
                        <div className={`text-3xl font-bold ${getZScoreColor(metrics?.zscore)}`}>
                            {metrics?.zscore?.toFixed(3) ?? '0.000'}
                        </div>
                        <p className="text-xs text-gray-500 mt-2">
                            {metrics?.zscore && Math.abs(metrics.zscore) > 2 ? 'Extreme deviation' : 'Within threshold'}
                        </p>
                    </CardContent>
                </Card>

                {/* Spread */}
                <Card className="bg-[#0E1621] border-gray-800 hover:border-gray-700 transition-all duration-200">
                    <CardHeader className="pb-3">
                        <CardTitle className="text-sm font-medium text-gray-400 flex items-center justify-between">
                            Current Spread
                            <TrendingUp className="w-4 h-4" />
                        </CardTitle>
                    </CardHeader>
                    <CardContent>
                        <div className="text-3xl font-bold text-white">
                            ${metrics?.spread?.toFixed(2) ?? '0.00'}
                        </div>
                        <p className="text-xs text-gray-500 mt-2">Latest spread value</p>
                    </CardContent>
                </Card>

                {/* Correlation */}
                <Card className="bg-[#0E1621] border-gray-800 hover:border-gray-700 transition-all duration-200">
                    <CardHeader className="pb-3">
                        <CardTitle className="text-sm font-medium text-gray-400 flex items-center justify-between">
                            Correlation
                            <TrendingDown className="w-4 h-4" />
                        </CardTitle>
                    </CardHeader>
                    <CardContent>
                        <div className="text-3xl font-bold text-white">
                            {((metrics?.correlation ?? 0) * 100).toFixed(1)}%
                        </div>
                        <p className="text-xs text-gray-500 mt-2">
                            {(metrics?.correlation ?? 0) > 0.8 ? 'Strong correlation' : 'Moderate correlation'}
                        </p>
                    </CardContent>
                </Card>

                {/* Stationarity */}
                <Card className="bg-[#0E1621] border-gray-800 hover:border-gray-700 transition-all duration-200">
                    <CardHeader className="pb-3">
                        <CardTitle className="text-sm font-medium text-gray-400 flex items-center justify-between">
                            Stationarity
                            {metrics?.stationary ? (
                                <CheckCircle2 className="w-4 h-4 text-emerald-500" />
                            ) : (
                                <AlertTriangle className="w-4 h-4 text-yellow-500" />
                            )}
                        </CardTitle>
                    </CardHeader>
                    <CardContent>
                        <div className={`text-2xl font-bold ${metrics?.stationary ? 'text-emerald-500' : 'text-yellow-500'}`}>
                            {metrics?.stationary ? 'Stationary' : 'Non-Stationary'}
                        </div>
                        <p className="text-xs text-gray-500 mt-2">ADF test status</p>
                    </CardContent>
                </Card>
            </div>

            {/* Alert Panel */}
            <Card className="bg-[#0E1621] border-gray-800">
                <CardHeader>
                    <CardTitle className="text-lg font-semibold text-white">Latest Trading Alert</CardTitle>
                </CardHeader>
                <CardContent>
                    {alert ? (
                        <div className="flex items-center justify-between p-4 rounded-lg bg-[#0B0F14] border border-gray-800">
                            <div className="flex items-center space-x-4">
                                <Badge
                                    className={`text-sm font-semibold px-3 py-1 ${alert.signal === 'LONG'
                                            ? 'bg-emerald-500/20 text-emerald-500 border-emerald-500/30'
                                            : alert.signal === 'SHORT'
                                                ? 'bg-red-500/20 text-red-500 border-red-500/30'
                                                : 'bg-gray-500/20 text-gray-400 border-gray-500/30'
                                        }`}
                                >
                                    {alert.signal || alert.type}
                                </Badge>
                                <div>
                                    <p className="text-white font-medium">{alert.reason}</p>
                                    <p className="text-xs text-gray-500 mt-1">
                                        {formatToLocal(alert.timestamp)}
                                    </p>
                                </div>
                            </div>
                            <div className="text-right">
                                <p className="text-sm text-gray-400">Z-Score</p>
                                <p className={`text-xl font-bold ${getZScoreColor(alert.z_score)}`}>
                                    {alert.z_score?.toFixed(3) ?? 'N/A'}
                                </p>
                            </div>
                        </div>
                    ) : (
                        <p className="text-gray-500 text-center py-4">Waiting for alerts...</p>
                    )}
                </CardContent>
            </Card>
        </div>
    );
};

export default Dashboard;
