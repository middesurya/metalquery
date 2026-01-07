/**
 * API Configuration
 * Centralized configuration for API endpoints.
 */

// Environment-based API URL selection
const getApiUrl = () => {
    // Check for environment variable first
    if (process.env.REACT_APP_API_URL) {
        return process.env.REACT_APP_API_URL;
    }

    // Default to localhost in development
    if (process.env.NODE_ENV === 'development') {
        return 'http://localhost:8001';
    }

    // Production fallback
    return window.location.origin;
};

// API Configuration
const config = {
    // Base URL for Django backend
    API_URL: getApiUrl(),

    // API Endpoints
    endpoints: {
        chat: '/api/chatbot/chat/',
        dualQuery: '/api/chatbot/dual-query/',
        schema: '/api/chatbot/schema/',
        health: '/api/chatbot/health/',
    },

    // Request timeout in milliseconds
    timeout: 120000,

    // Query modes
    queryModes: {
        AUTO: 'auto',
        NLP_SQL: 'nlp-sql',
        RAG: 'rag',
    },

    // Default settings
    defaults: {
        queryMode: 'auto',
        maxResults: 50,
    }
};

/**
 * Build full URL for an endpoint
 * @param {string} endpoint - Endpoint key from config.endpoints
 * @returns {string} Full URL
 */
export const getEndpointUrl = (endpoint) => {
    const path = config.endpoints[endpoint] || endpoint;
    return `${config.API_URL}${path}`;
};

/**
 * Make API request with standard configuration
 * @param {string} endpoint - Endpoint key
 * @param {Object} options - Fetch options
 * @returns {Promise} Fetch promise
 */
export const apiRequest = async (endpoint, options = {}) => {
    const url = getEndpointUrl(endpoint);

    const defaultOptions = {
        headers: {
            'Content-Type': 'application/json',
        },
        timeout: config.timeout,
    };

    const mergedOptions = {
        ...defaultOptions,
        ...options,
        headers: {
            ...defaultOptions.headers,
            ...options.headers,
        },
    };

    try {
        const controller = new AbortController();
        const timeoutId = setTimeout(() => controller.abort(), config.timeout);

        const response = await fetch(url, {
            ...mergedOptions,
            signal: controller.signal,
        });

        clearTimeout(timeoutId);

        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }

        return await response.json();
    } catch (error) {
        if (error.name === 'AbortError') {
            throw new Error('Request timeout');
        }
        throw error;
    }
};

export default config;
