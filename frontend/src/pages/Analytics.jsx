import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '../components/ui/card';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer, ReferenceLine } from 'recharts';
import { api } from '../services/api';
import { RefreshCw, Download } from 'lucide-react';
import { Button } from '../components/ui/button';
import { Badge } from '../components/ui/badge';
import { useLastUpdated } from '../hooks/useLastUpdated';
import { formatChartTime, formatTableTime } from '../utils/dateUtils';

const Analytics = () => {
    const [zscoreData, setZscoreData] = useState([]);
    const [spreadData, setSpreadData] = useState([]);
    const [correlationData, setCorrelationData] = useState([]);
    const [statsRows, setStatsRows] = useState([]);
    const [loading, setLoading] = useState(true);
    const [refreshing, setRefreshing] = useState(false);
    const [error, setError] = useState(false);
    const { timeAgo, updateTimestamp } = useLastUpdated();

    useEffect(() => {
        loadAnalyticsData();
        const interval = setInterval(loadAnalyticsData, 10000); // Refresh every 10 seconds
        return () => clearInterval(interval);
    }, []);

    const loadAnalyticsData = async () => {
        try {
            setRefreshing(true);
            const [history, stats] = await Promise.all([
                api.getAnalyticsHistory(),
                api.getAnalyticsStats()
            ]);

            if (!history || !history.series) {
                // Empty state handling
                setZscoreData([]);
                setSpreadData([]);
                setCorrelationData([]);
                setStatsRows([]);
                setLoading(false);
                setRefreshing(false);
                return;
            }

            if (stats && stats.rows) {
                setStatsRows(stats.rows);
            }

            // Format data for Recharts
            // series: [{ timestamp, zscore, spread, correlation }, ...]
            const series = history.series;

            const formattedZScore = series.map((item) => ({
                time: formatChartTime(item.timestamp),
                zscore: parseFloat(item.zscore?.toFixed(3) || 0),
                upper: 2.0, // Hardcoded per config default or could fetch config
                lower: -2.0,
            }));

            const formattedSpread = series.map((item) => ({
                time: formatChartTime(item.timestamp),
                spread: parseFloat(item.spread?.toFixed(2) || 0),
            }));

            const formattedCorr = series.map((item) => ({
                time: formatChartTime(item.timestamp),
                correlation: parseFloat((item.correlation * 100).toFixed(1) || 0),
            }));

            setZscoreData(formattedZScore);
            setSpreadData(formattedSpread);
            setCorrelationData(formattedCorr);
            setLoading(false);
            setRefreshing(false);
            updateTimestamp();
        } catch (error) {
            console.error('Error loading analytics data:', error);
            setLoading(false);
            setRefreshing(false);
            // Optionally set error state to show "Backend unavailable"
            setError(true);
        }
    };

    const CustomTooltip = ({ active, payload, label }) => {
        if (active && payload && payload.length) {
            return (
                <div className="bg-[#0E1621] border border-gray-700 rounded-lg p-3 shadow-lg">
                    <p className="text-gray-400 text-xs mb-1">{label}</p>
                    {payload.map((entry, index) => (
                        <p key={index} className="text-sm" style={{ color: entry.color }}>
                            {entry.name}: <span className="font-bold">{entry.value}</span>
                        </p>
                    ))}
                </div>
            );
        }
        return null;
    };

    const handleDownload = () => {
        const url = api.getStatsCsvUrl();
        const link = document.createElement('a');
        link.href = url;
        link.setAttribute('download', 'analytics_stats.csv'); // distinct logic for download
        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);
    };

    if (loading) {
        return (
            <div className="max-w-7xl mx-auto px-6 py-8">
                <div className="space-y-6">
                    {[1, 2, 3].map((i) => (
                        <div key={i} className="h-80 bg-[#0E1621] rounded-lg animate-pulse" />
                    ))}
                </div>
            </div>
        );
    }

    return (
        <div className="max-w-7xl mx-auto px-6 py-8">
            <div className="flex items-center justify-between mb-8">
                <h1 className="text-3xl font-bold text-white">Analytics</h1>
                <Button
                    onClick={loadAnalyticsData}
                    disabled={refreshing}
                    className="bg-emerald-500 hover:bg-emerald-600 text-white"
                >
                    <RefreshCw className={`w-4 h-4 mr-2 ${refreshing ? 'animate-spin' : ''}`} />
                    Refresh Data
                </Button>
            </div>

            <div className="space-y-6">
                {/* Z-Score Chart */}
                <Card className="bg-[#0E1621] border-gray-800">
                    <CardHeader>
                        <CardTitle className="text-lg font-semibold text-white">Z-Score Over Time</CardTitle>
                        <p className="text-sm text-gray-400">Tracking deviation from mean with threshold lines</p>
                    </CardHeader>
                    <CardContent>
                        <ResponsiveContainer width="100%" height={300}>
                            <LineChart data={zscoreData}>
                                <CartesianGrid strokeDasharray="3 3" stroke="#1f2937" />
                                <XAxis dataKey="time" stroke="#6b7280" style={{ fontSize: '12px' }} />
                                <YAxis stroke="#6b7280" style={{ fontSize: '12px' }} />
                                <Tooltip content={<CustomTooltip />} />
                                <Legend wrapperStyle={{ color: '#9ca3af' }} />
                                <ReferenceLine y={2} stroke="#ef4444" strokeDasharray="3 3" label="Upper" />
                                <ReferenceLine y={-2} stroke="#ef4444" strokeDasharray="3 3" label="Lower" />
                                <ReferenceLine y={0} stroke="#6b7280" strokeDasharray="3 3" />
                                <Line
                                    type="monotone"
                                    dataKey="zscore"
                                    stroke="#10b981"
                                    strokeWidth={2}
                                    dot={false}
                                    name="Z-Score"
                                />
                            </LineChart>
                        </ResponsiveContainer>
                    </CardContent>
                </Card>

                {/* Spread Chart */}
                <Card className="bg-[#0E1621] border-gray-800">
                    <CardHeader>
                        <CardTitle className="text-lg font-semibold text-white">Spread Time Series</CardTitle>
                        <p className="text-sm text-gray-400">Historical spread between trading pairs</p>
                    </CardHeader>
                    <CardContent>
                        <ResponsiveContainer width="100%" height={300}>
                            <LineChart data={spreadData}>
                                <CartesianGrid strokeDasharray="3 3" stroke="#1f2937" />
                                <XAxis dataKey="time" stroke="#6b7280" style={{ fontSize: '12px' }} />
                                <YAxis stroke="#6b7280" style={{ fontSize: '12px' }} />
                                <Tooltip content={<CustomTooltip />} />
                                <Legend wrapperStyle={{ color: '#9ca3af' }} />
                                <Line
                                    type="monotone"
                                    dataKey="spread"
                                    stroke="#3b82f6"
                                    strokeWidth={2}
                                    dot={false}
                                    name="Spread ($)"
                                />
                            </LineChart>
                        </ResponsiveContainer>
                    </CardContent>
                </Card>

                {/* Correlation Chart */}
                <Card className="bg-[#0E1621] border-gray-800">
                    <CardHeader>
                        <CardTitle className="text-lg font-semibold text-white">Rolling Correlation</CardTitle>
                        <p className="text-sm text-gray-400">Correlation coefficient over time (percentage)</p>
                    </CardHeader>
                    <CardContent>
                        <ResponsiveContainer width="100%" height={300}>
                            <LineChart data={correlationData}>
                                <CartesianGrid strokeDasharray="3 3" stroke="#1f2937" />
                                <XAxis dataKey="time" stroke="#6b7280" style={{ fontSize: '12px' }} />
                                <YAxis stroke="#6b7280" style={{ fontSize: '12px' }} domain={[0, 100]} />
                                <Tooltip content={<CustomTooltip />} />
                                <Legend wrapperStyle={{ color: '#9ca3af' }} />
                                <ReferenceLine y={70} stroke="#f59e0b" strokeDasharray="3 3" label="Min" />
                                <Line
                                    type="monotone"
                                    dataKey="correlation"
                                    stroke="#8b5cf6"
                                    strokeWidth={2}
                                    dot={false}
                                    name="Correlation (%)"
                                />
                            </LineChart>
                        </ResponsiveContainer>
                    </CardContent>
                </Card>

                {/* Stats Table */}
                <Card className="bg-[#0E1621] border-gray-800">
                    <CardHeader className="flex flex-row items-center justify-between">
                        <div>
                            <CardTitle className="text-lg font-semibold text-white">Time-Series Statistics</CardTitle>
                            <p className="text-sm text-gray-400">Detailed numerical data</p>
                        </div>
                        <Button
                            onClick={handleDownload}
                            disabled={error || loading}
                            variant="outline"
                            className="bg-[#0B0F14] text-emerald-500 border-emerald-500/50 hover:bg-emerald-500/10 hover:text-emerald-400"
                        >
                            <Download className="w-4 h-4 mr-2" />
                            Download CSV
                        </Button>
                    </CardHeader>
                    <CardContent>
                        <div className="overflow-x-auto">
                            <table className="w-full text-sm text-left text-gray-400">
                                <thead className="text-xs text-gray-500 uppercase bg-[#0B0F14] border-b border-gray-800">
                                    <tr>
                                        <th className="px-4 py-3">Time</th>
                                        <th className="px-4 py-3">Z-Score</th>
                                        <th className="px-4 py-3">Spread</th>
                                        <th className="px-4 py-3">Correlation</th>
                                        <th className="px-4 py-3">Stationary</th>
                                        <th className="px-4 py-3">Alert</th>
                                    </tr>
                                </thead>
                                <tbody>
                                    {statsRows.length > 0 ? (
                                        statsRows.map((row, index) => (
                                            <tr key={index} className="border-b border-gray-800 hover:bg-[#0B0F14]/50 transition-colors">
                                                <td className="px-4 py-3 font-medium text-white">{formatTableTime(row.timestamp)}</td>
                                                <td className={`px-4 py-3 ${Math.abs(row.zscore) > 2 ? 'text-red-400 font-bold' : ''}`}>
                                                    {row.zscore.toFixed(3)}
                                                </td>
                                                <td className="px-4 py-3 text-white">
                                                    {row.spread.toFixed(2)}
                                                </td>
                                                <td className="px-4 py-3">
                                                    {(row.correlation * 100).toFixed(1)}%
                                                </td>
                                                <td className="px-4 py-3">
                                                    {row.is_stationary ? (
                                                        <Badge className="bg-emerald-500/20 text-emerald-500 border-emerald-500/30">YES</Badge>
                                                    ) : (
                                                        <Badge className="bg-red-500/20 text-red-500 border-red-500/30">NO</Badge>
                                                    )}
                                                </td>
                                                <td className="px-4 py-3">
                                                    {row.alert === 'LONG' ? (
                                                        <Badge className="bg-emerald-500/20 text-emerald-500 border-emerald-500/30">LONG</Badge>
                                                    ) : row.alert === 'SHORT' ? (
                                                        <Badge className="bg-red-500/20 text-red-500 border-red-500/30">SHORT</Badge>
                                                    ) : (
                                                        <Badge className="bg-gray-500/20 text-gray-400 border-gray-500/30">NONE</Badge>
                                                    )}
                                                </td>
                                            </tr>
                                        ))
                                    ) : (
                                        <tr>
                                            <td colSpan="6" className="text-center py-8 text-gray-500">
                                                No analytics data available yet
                                            </td>
                                        </tr>
                                    )}
                                </tbody>
                            </table>
                        </div>
                    </CardContent>
                </Card>
            </div>
        </div>
    );
};

export default Analytics;
