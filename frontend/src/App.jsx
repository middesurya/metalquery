import React, { useState, useRef, useEffect } from 'react';
import './App.css';
import ModeToggle from './components/ModeToggle';
import config from './config';

// Django Backend API URL (React → Django → NLP → LLM)
// Security: React calls Django, which owns the database
// AI service never touches the database directly
const API_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';

/**
 * Format number with commas and units
 */
const formatValue = (value, key) => {
    if (value === null || value === undefined) return '-';

    const numValue = parseFloat(value);
    if (isNaN(numValue)) return value;

    // Add units based on column name
    if (key?.includes('strength') || key?.includes('modulus')) {
        return `${numValue.toLocaleString()} MPa`;
    }
    if (key?.includes('density')) {
        return `${numValue.toLocaleString()} kg/m³`;
    }
    if (key?.includes('hardness') || key === 'bhn' || key === 'hv') {
        return numValue.toLocaleString();
    }
    if (key?.includes('ratio')) {
        return numValue.toFixed(3);
    }

    return typeof value === 'number' ? numValue.toLocaleString() : value;
};

/**
 * Results Table Component
 */
const ResultsTable = ({ results }) => {
    if (!results || results.length === 0) return null;

    const columns = Object.keys(results[0]);

    return (
        <div className="results-section">
            <div className="results-header">
                <span className="results-icon">📊</span>
                <span>Data Results ({results.length} rows)</span>
            </div>
            <div className="results-table-container">
                <table className="results-table">
                    <thead>
                        <tr>
                            {columns.map(col => (
                                <th key={col}>{col.replace(/_/g, ' ')}</th>
                            ))}
                        </tr>
                    </thead>
                    <tbody>
                        {results.map((row, idx) => (
                            <tr key={idx}>
                                {columns.map(col => (
                                    <td key={col}>{formatValue(row[col], col)}</td>
                                ))}
                            </tr>
                        ))}
                    </tbody>
                </table>
            </div>
        </div>
    );
};

/**
 * SQL Display Component
 */
const SQLDisplay = ({ sql }) => {
    const [copied, setCopied] = useState(false);

    const copySQL = () => {
        navigator.clipboard.writeText(sql);
        setCopied(true);
        setTimeout(() => setCopied(false), 2000);
    };

    return (
        <div className="sql-section">
            <div className="sql-header">
                <span className="sql-icon">🔍</span>
                <span>Generated SQL Query</span>
                <button className="copy-btn" onClick={copySQL}>
                    {copied ? '✓ Copied' : '📋 Copy'}
                </button>
            </div>
            <pre className="sql-code">{sql}</pre>
        </div>
    );
};

/**
 * Chat Message Component
 */
const ChatMessage = ({ message, isUser }) => {
    return (
        <div className={`message ${isUser ? 'user-message' : 'bot-message'}`}>
            {!isUser && (
                <div className="message-avatar">
                    <span>🔩</span>
                </div>
            )}
            <div className="message-content">
                <div className="message-text">{message.text}</div>

                {message.results && message.results.length > 0 && (
                    <ResultsTable results={message.results} />
                )}

                {message.sql && (
                    <SQLDisplay sql={message.sql} />
                )}

                <div className="message-time">
                    {new Date(message.timestamp).toLocaleTimeString()}
                </div>
            </div>
            {isUser && (
                <div className="message-avatar user-avatar">
                    <span>👤</span>
                </div>
            )}
        </div>
    );
};

/**
 * Typing Indicator
 */
const TypingIndicator = () => (
    <div className="message bot-message">
        <div className="message-avatar">
            <span>🔩</span>
        </div>
        <div className="message-content">
            <div className="typing-indicator">
                <span></span>
                <span></span>
                <span></span>
            </div>
        </div>
    </div>
);

/**
 * Suggestion Chip Component
 */
const SuggestionChip = ({ text, onClick }) => (
    <button className="suggestion-chip" onClick={() => onClick(text)}>
        {text}
    </button>
);

/**
 * Main App Component
 */
function App() {
    const [messages, setMessages] = useState([
        {
            id: 1,
            text: "Welcome to IGNIS Furnace Analytics! I can help you query furnace KPIs, analyze production data, or answer questions from BRD documents. What would you like to know?",
            isUser: false,
            timestamp: new Date().toISOString()
        }
    ]);
    const [inputValue, setInputValue] = useState('');
    const [isLoading, setIsLoading] = useState(false);
    const [queryMode, setQueryMode] = useState('auto');
    const messagesEndRef = useRef(null);
    const inputRef = useRef(null);

    // IGNIS-specific suggestions
    const suggestions = [
        "Show OEE by furnace for last week",
        "What is the total downtime for Furnace 1?",
        "Compare yield percentage across all furnaces",
        "Show MTBF and MTTR trends",
        "What is the energy consumption by furnace?",
        "How to configure furnace parameters?",
        "What is EHS?",
        "Show production efficiency for January"
    ];

    const scrollToBottom = () => {
        messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
    };

    useEffect(() => {
        scrollToBottom();
    }, [messages]);

    useEffect(() => {
        inputRef.current?.focus();
    }, []);

    const sendMessage = async (text = inputValue) => {
        if (!text.trim() || isLoading) return;

        const userMessage = {
            id: Date.now(),
            text: text,
            isUser: true,
            timestamp: new Date().toISOString()
        };

        setMessages(prev => [...prev, userMessage]);
        setInputValue('');
        setIsLoading(true);

        try {
            // Call Django backend (which calls NLP service internally)
            const response = await fetch(`${API_URL}/api/chatbot/chat/`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ question: text })
            });

            const data = await response.json();

            const botMessage = {
                id: Date.now() + 1,
                text: data.success
                    ? data.response
                    : `Sorry, I couldn't process that: ${data.error}`,
                isUser: false,
                sql: data.sql,
                results: data.results,
                row_count: data.row_count,
                timestamp: new Date().toISOString()
            };

            setMessages(prev => [...prev, botMessage]);
        } catch (error) {
            setMessages(prev => [...prev, {
                id: Date.now() + 1,
                text: `Connection error: ${error.message}. Please check if the server is running.`,
                isUser: false,
                timestamp: new Date().toISOString()
            }]);
        } finally {
            setIsLoading(false);
        }
    };

    const handleKeyPress = (e) => {
        if (e.key === 'Enter' && !e.shiftKey) {
            e.preventDefault();
            sendMessage();
        }
    };

    const handleSuggestionClick = (suggestion) => {
        sendMessage(suggestion);
    };

    const clearChat = () => {
        setMessages([{
            id: Date.now(),
            text: "Chat cleared. How can I help you explore the metallurgy database?",
            isUser: false,
            timestamp: new Date().toISOString()
        }]);
    };

    return (
        <div className="app">
            {/* Sidebar */}
            <aside className="sidebar">
                <div className="sidebar-header">
                    <div className="logo">
                        <span className="logo-icon">🔩</span>
                        <div className="logo-text">
                            <h1>MetalQuery</h1>
                            <span>AI Materials Assistant</span>
                        </div>
                    </div>
                </div>

                <div className="sidebar-content">
                    <div className="sidebar-section">
                        <h3>Quick Actions</h3>
                        <button className="sidebar-btn" onClick={clearChat}>
                            <span>🗑️</span> New Chat
                        </button>
                    </div>

                    <div className="sidebar-section">
                        <h3>Database Info</h3>
                        <div className="info-card">
                            <div className="info-item">
                                <span className="info-value">29</span>
                                <span className="info-label">KPI Tables</span>
                            </div>
                            <div className="info-item">
                                <span className="info-value">4</span>
                                <span className="info-label">Furnaces</span>
                            </div>
                            <div className="info-item">
                                <span className="info-value">33</span>
                                <span className="info-label">BRD Docs</span>
                            </div>
                        </div>
                    </div>

                    <div className="sidebar-section">
                        <h3>Available KPIs</h3>
                        <ul className="property-list">
                            <li>OEE / Health (%)</li>
                            <li>Downtime (hours)</li>
                            <li>Yield / Defect Rate</li>
                            <li>MTBF / MTTR / MTBS</li>
                            <li>Energy Consumption</li>
                            <li>Production Efficiency</li>
                        </ul>
                    </div>
                </div>

                <div className="sidebar-footer">
                    <div className="status-indicator">
                        <span className="status-dot online"></span>
                        <span>Connected</span>
                    </div>
                </div>
            </aside>

            {/* Main Chat Area */}
            <main className="main-content">
                {/* Chat Header */}
                <header className="chat-header">
                    <div className="header-left">
                        <h2>IGNIS Analytics Assistant</h2>
                        <p>Ask questions about furnace KPIs, production data, or BRD documentation</p>
                    </div>
                    <div className="header-right">
                        <ModeToggle
                            mode={queryMode}
                            onModeChange={setQueryMode}
                            disabled={isLoading}
                        />
                        <span className="badge">Groq LLM</span>
                    </div>
                </header>

                {/* Messages Area */}
                <div className="messages-container">
                    <div className="messages-wrapper">
                        {messages.map(msg => (
                            <ChatMessage
                                key={msg.id}
                                message={msg}
                                isUser={msg.isUser}
                            />
                        ))}
                        {isLoading && <TypingIndicator />}
                        <div ref={messagesEndRef} />
                    </div>
                </div>

                {/* Suggestions */}
                {messages.length <= 1 && (
                    <div className="suggestions-container">
                        <p className="suggestions-title">Try asking:</p>
                        <div className="suggestions-grid">
                            {suggestions.map((suggestion, idx) => (
                                <SuggestionChip
                                    key={idx}
                                    text={suggestion}
                                    onClick={handleSuggestionClick}
                                />
                            ))}
                        </div>
                    </div>
                )}

                {/* Input Area */}
                <div className="input-container">
                    <div className="input-wrapper">
                        <input
                            ref={inputRef}
                            type="text"
                            value={inputValue}
                            onChange={(e) => setInputValue(e.target.value)}
                            onKeyPress={handleKeyPress}
                            placeholder="Ask about materials, properties, or specifications..."
                            disabled={isLoading}
                            className="chat-input"
                        />
                        <button
                            onClick={() => sendMessage()}
                            disabled={!inputValue.trim() || isLoading}
                            className="send-button"
                        >
                            {isLoading ? (
                                <span className="loading-spinner"></span>
                            ) : (
                                <span>Send</span>
                            )}
                        </button>
                    </div>
                    <p className="input-hint">
                        Press Enter to send • Results limited to 50 rows
                    </p>
                </div>
            </main>
        </div>
    );
}

export default App;
