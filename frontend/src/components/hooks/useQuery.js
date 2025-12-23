import { useState, useCallback } from 'react';
import config, { getEndpointUrl } from '../../config';

/**
 * useQuery Hook
 * Custom hook for making API queries with loading/error state management.
 */
const useQuery = () => {
    const [isLoading, setIsLoading] = useState(false);
    const [error, setError] = useState(null);
    const [data, setData] = useState(null);

    /**
     * Execute a chat query
     * @param {string} question - The user's question
     * @param {string} mode - Query mode: 'auto', 'nlp-sql', or 'rag'
     * @returns {Promise<Object>} The response data
     */
    const executeQuery = useCallback(async (question, mode = 'auto') => {
        setIsLoading(true);
        setError(null);
        setData(null);

        try {
            const url = getEndpointUrl('chat');

            const response = await fetch(url, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    question,
                    mode: mode !== 'auto' ? mode : undefined,
                }),
            });

            const result = await response.json();

            if (!response.ok) {
                throw new Error(result.error || `HTTP error ${response.status}`);
            }

            if (!result.success) {
                throw new Error(result.error || 'Query failed');
            }

            setData(result);
            return result;
        } catch (err) {
            const errorMessage = err.message || 'An error occurred';
            setError(errorMessage);
            throw err;
        } finally {
            setIsLoading(false);
        }
    }, []);

    /**
     * Execute a dual query (auto-routes to NLP or RAG)
     * @param {string} question - The user's question
     * @param {string} forceMode - Force specific mode: 'nlp-sql' or 'rag'
     * @returns {Promise<Object>} The response data
     */
    const executeDualQuery = useCallback(async (question, forceMode = null) => {
        setIsLoading(true);
        setError(null);
        setData(null);

        try {
            const url = getEndpointUrl('dualQuery');

            const body = { question };
            if (forceMode) {
                body.mode = forceMode;
            }

            const response = await fetch(url, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(body),
            });

            const result = await response.json();

            if (!response.ok) {
                throw new Error(result.error || `HTTP error ${response.status}`);
            }

            setData(result);
            return result;
        } catch (err) {
            const errorMessage = err.message || 'An error occurred';
            setError(errorMessage);
            throw err;
        } finally {
            setIsLoading(false);
        }
    }, []);

    /**
     * Check API health status
     * @returns {Promise<Object>} Health status
     */
    const checkHealth = useCallback(async () => {
        try {
            const url = getEndpointUrl('health');
            const response = await fetch(url);
            return await response.json();
        } catch (err) {
            return { status: 'error', error: err.message };
        }
    }, []);

    /**
     * Fetch database schema
     * @returns {Promise<Object>} Schema information
     */
    const fetchSchema = useCallback(async () => {
        try {
            const url = getEndpointUrl('schema');
            const response = await fetch(url);
            return await response.json();
        } catch (err) {
            return { success: false, error: err.message };
        }
    }, []);

    /**
     * Reset the hook state
     */
    const reset = useCallback(() => {
        setIsLoading(false);
        setError(null);
        setData(null);
    }, []);

    return {
        // State
        isLoading,
        error,
        data,

        // Actions
        executeQuery,
        executeDualQuery,
        checkHealth,
        fetchSchema,
        reset,

        // Config
        queryModes: config.queryModes,
    };
};

export default useQuery;
