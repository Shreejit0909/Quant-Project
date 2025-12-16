import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '../components/ui/card';
import { Button } from '../components/ui/button';
import { Input } from '../components/ui/input';
import { Label } from '../components/ui/label';
import { api } from '../services/api'; // Changed import
import { Save, CheckCircle2 } from 'lucide-react';
import { toast } from '../hooks/use-toast';

const Settings = () => {
    const [config, setConfig] = useState({
        zscore_entry_threshold: 2.0,
        zscore_exit_threshold: 0.5,
        min_correlation: 0.7,
    });
    const [loading, setLoading] = useState(true);
    const [saving, setSaving] = useState(false);
    const [saved, setSaved] = useState(false);

    useEffect(() => {
        loadConfig();
    }, []);

    const loadConfig = async () => {
        try {
            const data = await api.getConfig();
            setConfig(data);
            setLoading(false);
        } catch (error) {
            console.error('Error loading config:', error);
            setLoading(false);
            toast({
                title: "Error",
                description: "Failed to load configuration.",
                variant: "destructive",
            });
        }
    };

    const handleSave = async () => {
        // Validate before sending
        if (config.zscore_entry_threshold <= config.zscore_exit_threshold) {
            toast({
                title: "Validation Error",
                description: "Entry threshold must be strictly greater than Exit threshold.",
                variant: "destructive",
            });
            return;
        }
        if (config.min_correlation < 0 || config.min_correlation > 1) {
            toast({
                title: "Validation Error",
                description: "Correlation must be between 0.0 and 1.0",
                variant: "destructive",
            });
            return;
        }

        try {
            setSaving(true);
            await api.saveConfig(config);
            setSaving(false);
            setSaved(true);
            toast({
                title: "Configuration Saved",
                description: "Your trading parameters have been updated.",
                duration: 3000,
            });
            setTimeout(() => setSaved(false), 3000);
        } catch (error) {
            console.error('Error saving config:', error);
            setSaving(false);
            toast({
                title: "Error",
                description: "Failed to save configuration. Please try again.",
                variant: "destructive",
                duration: 3000,
            });
        }
    };

    const handleChange = (field, value) => {
        setConfig((prev) => ({
            ...prev,
            [field]: parseFloat(value) || 0,
        }));
    };

    if (loading) {
        return (
            <div className="max-w-4xl mx-auto px-6 py-8">
                <div className="h-96 bg-[#0E1621] rounded-lg animate-pulse" />
            </div>
        );
    }

    return (
        <div className="max-w-4xl mx-auto px-6 py-8">
            <h1 className="text-3xl font-bold text-white mb-8">Settings</h1>

            <Card className="bg-[#0E1621] border-gray-800">
                <CardHeader>
                    <CardTitle className="text-xl font-semibold text-white">Trading Configuration</CardTitle>
                    <CardDescription className="text-gray-400">
                        Adjust parameters for your quantitative trading strategy
                    </CardDescription>
                </CardHeader>
                <CardContent className="space-y-6">
                    {/* Z-Score Entry Threshold */}
                    <div className="space-y-2">
                        <Label htmlFor="zscore_entry" className="text-sm font-medium text-gray-300">
                            Z-Score Entry Threshold
                        </Label>
                        <Input
                            id="zscore_entry"
                            type="number"
                            step="0.1"
                            value={config.zscore_entry_threshold}
                            onChange={(e) => handleChange('zscore_entry_threshold', e.target.value)}
                            className="bg-[#0B0F14] border-gray-700 text-white focus:border-emerald-500 focus:ring-emerald-500"
                        />
                        <p className="text-xs text-gray-500">
                            Trigger trading signal when Z-score exceeds this absolute value (default: 2.0).
                        </p>
                    </div>

                    {/* Z-Score Exit Threshold */}
                    <div className="space-y-2">
                        <Label htmlFor="zscore_exit" className="text-sm font-medium text-gray-300">
                            Z-Score Exit / Reset Threshold
                        </Label>
                        <Input
                            id="zscore_exit"
                            type="number"
                            step="0.1"
                            value={config.zscore_exit_threshold}
                            onChange={(e) => handleChange('zscore_exit_threshold', e.target.value)}
                            className="bg-[#0B0F14] border-gray-700 text-white focus:border-emerald-500 focus:ring-emerald-500"
                        />
                        <p className="text-xs text-gray-500">
                            Close position when Z-score reverts to this absolute value (default: 0.5).
                        </p>
                    </div>

                    {/* Minimum Correlation */}
                    <div className="space-y-2">
                        <Label htmlFor="min_correlation" className="text-sm font-medium text-gray-300">
                            Minimum Correlation
                        </Label>
                        <Input
                            id="min_correlation"
                            type="number"
                            step="0.01"
                            min="0"
                            max="1"
                            value={config.min_correlation}
                            onChange={(e) => handleChange('min_correlation', e.target.value)}
                            className="bg-[#0B0F14] border-gray-700 text-white focus:border-emerald-500 focus:ring-emerald-500"
                        />
                        <p className="text-xs text-gray-500">
                            Only generate alerts if rolling correlation is above this value (0.0 - 1.0).
                        </p>
                    </div>

                    {/* Save Button */}
                    <div className="pt-4 flex items-center space-x-3">
                        <Button
                            onClick={handleSave}
                            disabled={saving || saved}
                            className={`${saved
                                ? 'bg-emerald-600 hover:bg-emerald-600'
                                : 'bg-emerald-500 hover:bg-emerald-600'
                                } text-white transition-all duration-200`}
                        >
                            {saved ? (
                                <>
                                    <CheckCircle2 className="w-4 h-4 mr-2" />
                                    Saved
                                </>
                            ) : (
                                <>
                                    <Save className="w-4 h-4 mr-2" />
                                    {saving ? 'Saving...' : 'Save Configuration'}
                                </>
                            )}
                        </Button>
                        {saved && (
                            <span className="text-sm text-emerald-500 animate-fade-in">
                                Configuration updated successfully
                            </span>
                        )}
                    </div>
                </CardContent>
            </Card>

            {/* Information Card */}
            <Card className="bg-[#0E1621] border-gray-800 mt-6">
                <CardHeader>
                    <CardTitle className="text-lg font-semibold text-white">About These Settings</CardTitle>
                </CardHeader>
                <CardContent className="space-y-3 text-sm text-gray-400">
                    <p>
                        <strong className="text-white">Z-Score Threshold:</strong> When the Z-score exceeds
                        this value, a trading signal is generated. Higher values mean fewer but stronger signals.
                    </p>
                    <p>
                        <strong className="text-white">Reset Threshold:</strong> The Z-score level at which to
                        close positions and reset. This helps lock in profits when spread reverts to mean.
                    </p>
                    <p>
                        <strong className="text-white">Minimum Correlation:</strong> Only trade pairs with
                        correlation above this threshold. Higher values ensure stronger statistical relationships.
                    </p>
                </CardContent>
            </Card>
        </div>
    );
};

export default Settings;
