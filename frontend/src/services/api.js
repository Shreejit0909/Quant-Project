import axios from 'axios';

const API_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';

// Axios instance with timeout
const apiClient = axios.create({
    baseURL: API_URL,
    timeout: 5000,
    headers: {
        'Content-Type': 'application/json',
    },
});

export const api = {
    // Health check
    async getHealth() {
        try {
            const response = await apiClient.get('/health');
            return response.data;
        } catch (error) {
            throw error;
        }
    },

    // Analytics endpoints
    async getAnalyticsLatest() {
        const response = await apiClient.get('/analytics/latest');
        return response.data;
    },

    async getAnalyticsHistory() {
        const response = await apiClient.get('/analytics/history');
        return response.data;
    },

    async getAnalyticsStats() {
        const response = await apiClient.get('/analytics/stats');
        return response.data;
    },

    getStatsCsvUrl() {
        return `${API_URL}/analytics/stats/csv`;
    },

    // Alerts
    async getLatestAlert() {
        const response = await apiClient.get('/alerts/latest');
        return response.data;
    },

    // Config
    async getConfig() {
        const response = await apiClient.get('/config');
        return response.data;
    },

    async saveConfig(config) {
        const response = await apiClient.post('/config', config);
        return response.data;
    },
};
