/**
 * Formats a UTC ISO-8601 string to local time.
 * @param {string} utcString - UTC timestamp, e.g., "2025-12-15T10:18:25+00:00"
 * @returns {string} - Formatted local string, e.g., "15 Dec 2025, 4:48:12 PM IST"
 */
export const formatToLocal = (utcString) => {
    if (!utcString) return 'N/A';
    try {
        const date = new Date(utcString);
        return new Intl.DateTimeFormat('en-IN', {
            year: 'numeric',
            month: 'short',
            day: 'numeric',
            hour: 'numeric',
            minute: 'numeric',
            second: 'numeric',
            timeZoneName: 'short',
        }).format(date);
    } catch (error) {
        console.error('Date formatting error:', error);
        return utcString;
    }
};

/**
 * Calculates relative time from now (e.g., "5m ago", "Just now").
 * @param {string} utcString - UTC timestamp
 * @returns {string} - Relative time string
 */
export const formatTimeAgo = (utcString) => {
    if (!utcString) return '';

    try {
        const date = new Date(utcString);
        const now = new Date();
        const diffInSeconds = Math.floor((now - date) / 1000);

        if (diffInSeconds < 60) {
            return 'Just now';
        }

        const minutes = Math.floor(diffInSeconds / 60);
        if (minutes < 60) {
            return `${minutes}m ago`;
        }

        const hours = Math.floor(minutes / 60);
        if (hours < 24) {
            return `${hours}h ago`;
        }

        return formatToLocal(utcString); // Fallback to full date for older items
    } catch (error) {
        return '';
    }
};

/**
 * Formats a UTC string for chart axis/tooltip (Time with milliseconds).
 * @param {string} utcString 
 * @returns {string} e.g. "10:30:15.123"
 */
export const formatChartTime = (utcString) => {
    if (!utcString) return '';
    try {
        const date = new Date(utcString);
        return new Intl.DateTimeFormat('en-IN', {
            hour: '2-digit',
            minute: '2-digit',
            second: '2-digit',
            fractionalSecondDigits: 3,
            hour12: false
        }).format(date);
    } catch (error) {
        return '';
    }
};

/**
 * Formats a UTC string for table display (Time HH:mm:ss).
 * @param {string} utcString 
 * @returns {string} e.g. "10:30:15"
 */
export const formatTableTime = (utcString) => {
    if (!utcString) return '';
    try {
        const date = new Date(utcString);
        return new Intl.DateTimeFormat('en-IN', {
            hour: '2-digit',
            minute: '2-digit',
            second: '2-digit',
            fractionalSecondDigits: 3,
            hour12: false
        }).format(date);
    } catch (error) {
        return '';
    }
};
