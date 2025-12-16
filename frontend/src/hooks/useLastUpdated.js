import { useState, useEffect } from 'react';

export const useLastUpdated = () => {
    const [lastUpdated, setLastUpdated] = useState(null);
    const [timeAgo, setTimeAgo] = useState('');

    const updateTimestamp = () => {
        setLastUpdated(new Date());
    };

    useEffect(() => {
        if (!lastUpdated) return;

        const updateTimeAgo = () => {
            const now = new Date();
            const diffSeconds = Math.floor((now - lastUpdated) / 1000);

            if (diffSeconds < 5) {
                setTimeAgo('just now');
            } else if (diffSeconds < 60) {
                setTimeAgo(`${diffSeconds}s ago`);
            } else {
                const diffMinutes = Math.floor(diffSeconds / 60);
                setTimeAgo(`${diffMinutes}m ago`);
            }
        };

        updateTimeAgo();
        const interval = setInterval(updateTimeAgo, 1000);

        return () => clearInterval(interval);
    }, [lastUpdated]);

    return { timeAgo, updateTimestamp };
};
