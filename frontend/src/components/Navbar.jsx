import React from 'react';
import { Link, useLocation } from 'react-router-dom';
import { BarChart3, TrendingUp, Settings } from 'lucide-react';
import { useConnectionStatus } from '../hooks/useConnectionStatus';

const Navbar = () => {
    const location = useLocation();
    const { isConnected } = useConnectionStatus();

    const navItems = [
        { path: '/', label: 'Dashboard', icon: BarChart3 },
        { path: '/analytics', label: 'Analytics', icon: TrendingUp },
        { path: '/settings', label: 'Settings', icon: Settings },
    ];

    return (
        <nav className="fixed top-0 left-0 right-0 z-50 bg-[#0E1621] border-b border-gray-800">
            <div className="max-w-7xl mx-auto px-6">
                <div className="flex items-center justify-between h-16">
                    <div className="flex items-center space-x-2">
                        <BarChart3 className="w-6 h-6 text-emerald-500" />
                        <span className="text-xl font-semibold text-white">Quant Analytics Dashboard</span>
                    </div>

                    <div className="flex items-center space-x-6">
                        <div className="flex items-center space-x-1">
                            {navItems.map((item) => {
                                const Icon = item.icon;
                                const isActive = location.pathname === item.path;
                                return (
                                    <Link
                                        key={item.path}
                                        to={item.path}
                                        className={`flex items-center space-x-2 px-4 py-2 rounded-lg transition-all duration-200 ${isActive
                                                ? 'bg-emerald-500/10 text-emerald-500'
                                                : 'text-gray-400 hover:text-white hover:bg-white/5'
                                            }`}
                                    >
                                        <Icon className="w-4 h-4" />
                                        <span className="font-medium">{item.label}</span>
                                    </Link>
                                );
                            })}
                        </div>

                        {/* Connection Status Indicator */}
                        <div className="flex items-center space-x-2 px-3 py-1 rounded-md bg-[#0B0F14] border border-gray-800">
                            <div
                                className={`w-2 h-2 rounded-full transition-colors duration-300 ${isConnected ? 'bg-emerald-500' : 'bg-red-500'
                                    }`}
                            />
                            <span className="text-xs text-gray-400">
                                {isConnected ? 'Connected' : 'Disconnected'}
                            </span>
                        </div>
                    </div>
                </div>
            </div>
        </nav>
    );
};

export default Navbar;
