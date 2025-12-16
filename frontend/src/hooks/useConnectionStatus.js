import { useState, useEffect } from 'react';
import { api } from '../services/api';

export const useConnectionStatus = () => {
    const [isConnected, setIsConnected] = useState(true);
    const [lastChecked, setLastChecked] = useState(null);

    useEffect(() => {
        const checkConnection = async () => {
            try {
                await api.getHealth();
                setIsConnected(true);
                setLastChecked(new Date());
            } catch (error) {
                setIsConnected(false);
                setLastChecked(new Date());
            }
        };

        // Initial check
        checkConnection();

        // Check every 5 seconds
        const interval = setInterval(checkConnection, 5000);

        return () => clearInterval(interval);
    }, []);

    return { isConnected, lastChecked };
};
