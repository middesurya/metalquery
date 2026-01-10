import React, { useState, useRef, useEffect } from 'react';
import './App.css';
import config from './config';
import ChartRenderer from './components/charts/ChartRenderer';

// Django Backend API URL (React → Django → NLP → LLM)
// Security: React calls Django, which owns the database
// AI service never touches the database directly
const API_URL = config.API_URL;

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
 * Image Lightbox Modal Component
 */
const ImageLightbox = ({ images, currentIndex, onClose, onNavigate }) => {
    const currentImage = images[currentIndex];

    useEffect(() => {
        const handleKeyDown = (e) => {
            if (e.key === 'Escape') onClose();
            if (e.key === 'ArrowLeft' && currentIndex > 0) onNavigate(currentIndex - 1);
            if (e.key === 'ArrowRight' && currentIndex < images.length - 1) onNavigate(currentIndex + 1);
        };
        document.addEventListener('keydown', handleKeyDown);
        document.body.style.overflow = 'hidden';
        return () => {
            document.removeEventListener('keydown', handleKeyDown);
            document.body.style.overflow = 'auto';
        };
    }, [currentIndex, images.length, onClose, onNavigate]);

    return (
        <div className="lightbox-overlay" onClick={onClose}>
            <div className="lightbox-content" onClick={(e) => e.stopPropagation()}>
                <button className="lightbox-close" onClick={onClose}>
                    &times;
                </button>

                {images.length > 1 && currentIndex > 0 && (
                    <button
                        className="lightbox-nav lightbox-prev"
                        onClick={() => onNavigate(currentIndex - 1)}
                    >
                        &#8249;
                    </button>
                )}

                <img
                    src={currentImage.data}
                    alt={`BRD Screenshot ${currentIndex + 1}`}
                    className="lightbox-image"
                />

                {images.length > 1 && currentIndex < images.length - 1 && (
                    <button
                        className="lightbox-nav lightbox-next"
                        onClick={() => onNavigate(currentIndex + 1)}
                    >
                        &#8250;
                    </button>
                )}

                <div className="lightbox-info">
                    <span className="lightbox-source">{currentImage.source || 'BRD Document'}</span>
                    {images.length > 1 && (
                        <span className="lightbox-counter">{currentIndex + 1} / {images.length}</span>
                    )}
                </div>
            </div>
        </div>
    );
};

/**
 * Score Badge Component
 */
const ScoreBadge = ({ label, score }) => {
    if (score === undefined || score === null) return null;

    let color = '#4caf50'; // Green
    if (score < 50) color = '#f44336'; // Red
    else if (score < 80) color = '#ff9800'; // Orange

    return (
        <div style={{
            display: 'inline-flex',
            alignItems: 'center',
            fontSize: '11px',
            backgroundColor: 'rgba(255,255,255,0.05)',
            padding: '2px 8px',
            borderRadius: '12px',
            border: `1px solid ${color}`,
            color: '#ccc'
        }}>
            <span style={{ marginRight: '4px', color: '#888' }}>{label}:</span>
            <span style={{ color: color, fontWeight: 'bold' }}>{score}%</span>
        </div>
    );
};

/**
 * Image Gallery Component for BRD Images
 */
const ImageGallery = ({ images }) => {
    const [selectedImage, setSelectedImage] = useState(null);

    if (!images || images.length === 0) return null;

    // NLP service URL for images
    const NLP_URL = process.env.REACT_APP_NLP_URL || 'http://localhost:8003';

    return (
        <div className="image-gallery">
            <div className="image-gallery-header">
                <span className="gallery-icon">📷</span>
                <span>Related Images ({images.length})</span>
            </div>
            <div className="image-grid">
                {images.map((img, idx) => (
                    <div
                        key={idx}
                        className="image-item"
                        onClick={() => setSelectedImage(img)}
                    >
                        <img
                            src={`${NLP_URL}${img.url}`}
                            alt={`From ${img.source}`}
                            loading="lazy"
                        />
                        <div className="image-caption">
                            {img.source} (p.{img.page + 1})
                        </div>
                    </div>
                ))}
            </div>

            {/* Lightbox Modal */}
            {selectedImage && (
                <div
                    className="image-lightbox"
                    onClick={() => setSelectedImage(null)}
                >
                    <div className="lightbox-content" onClick={e => e.stopPropagation()}>
                        <button
                            className="lightbox-close"
                            onClick={() => setSelectedImage(null)}
                        >
                            ×
                        </button>
                        <img
                            src={`${NLP_URL}${selectedImage.url}`}
                            alt={`From ${selectedImage.source}`}
                        />
                        <div className="lightbox-caption">
                            Source: {selectedImage.source} | Page {selectedImage.page + 1}
                        </div>
                    </div>
                </div>
            )}
        </div>
    );
};

/**
 * Chat Message Component
 */
const ChatMessage = ({ message, isUser, onEdit, onImageClick }) => {
    return (
        <div className={`message ${isUser ? 'user-message' : 'bot-message'}`}>
            {!isUser && (
                <div className="message-avatar">
                    <span>🔩</span>
                </div>
            )}
            <div className="message-content">
                <div className="message-text">
                    {message.text}
                    {isUser && onEdit && (
                        <button
                            onClick={() => onEdit(message.id, message.text)}
                            title="Edit this question"
                            style={{
                                marginLeft: '12px',
                                padding: '4px 10px',
                                background: 'rgba(255,255,255,0.1)',
                                border: '1px solid rgba(255,255,255,0.3)',
                                borderRadius: '4px',
                                cursor: 'pointer',
                                fontSize: '12px',
                                color: '#fff'
                            }}
                        >
                            ✏️ Edit
                        </button>
                    )}
                </div>

                {/* Chart Visualization - shown if chart_config is available */}
                {message.chart_config && message.results && message.results.length > 0 && (
                    <ChartRenderer
                        config={message.chart_config}
                        data={message.results}
                    />
                )}

                {/* Results Table - shown below chart or standalone */}
                {message.results && message.results.length > 0 && (
                    <ResultsTable results={message.results} />
                )}

                {message.images && message.images.length > 0 && (
                    <ImageGallery images={message.images} />
                )}

                {message.sql && (
                    <SQLDisplay sql={message.sql} />
                )}


                <div className="message-time">
                    {new Date(message.timestamp).toLocaleTimeString()}
                </div>
                {!isUser && message.confidence_score !== undefined && (
                    <div className="message-scores" style={{ marginTop: '8px', display: 'flex', gap: '8px' }}>
                        <ScoreBadge label="Confidence" score={message.confidence_score} />
                        <ScoreBadge label="Relevance" score={message.relevance_score} />
                    </div>
                )}
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

    const [editingMessageId, setEditingMessageId] = useState(null);
    const [lightboxData, setLightboxData] = useState(null);
    const messagesEndRef = useRef(null);
    const inputRef = useRef(null);

    // Lightbox handlers
    const openLightbox = (images, index) => {
        setLightboxData({ images, currentIndex: index });
    };

    const closeLightbox = () => {
        setLightboxData(null);
    };

    const navigateLightbox = (index) => {
        setLightboxData(prev => ({ ...prev, currentIndex: index }));
    };

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
            // Get auth token from localStorage (set during login)
            const token = localStorage.getItem('authToken');

            // Call Django backend (which calls NLP service internally)
            const response = await fetch(`${API_URL}/api/chatbot/chat/`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    ...(token && { 'Authorization': `Bearer ${token}` }),
                },
                body: JSON.stringify({ question: text })
            });

            // Handle auth errors
            if (response.status === 401) {
                setMessages(prev => [...prev, {
                    id: Date.now() + 1,
                    text: "Session expired or not authenticated. Please log in to access the chatbot.",
                    isUser: false,
                    timestamp: new Date().toISOString()
                }]);
                setIsLoading(false);
                return;
            }

            if (response.status === 403) {
                const errorData = await response.json();
                setMessages(prev => [...prev, {
                    id: Date.now() + 1,
                    text: `Access denied: ${errorData.error || 'Your role may not have permission for this data.'}`,
                    isUser: false,
                    timestamp: new Date().toISOString()
                }]);
                setIsLoading(false);
                return;
            }

            const data = await response.json();

            const botMessage = {
                id: Date.now() + 1,
                text: data.success
                    ? data.response
                    : `Sorry, I couldn't process that: ${data.error}`,
                isUser: false,
                sql: data.sql,
                results: data.results,
                chart_config: data.chart_config,  // Visualization config from backend
                row_count: data.row_count,
                images: data.images || [],  // Multimodal: images from BRD
                confidence_score: data.confidence_score,
                relevance_score: data.relevance_score,
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
            text: "Chat cleared. How can I help you explore the IGNIS database?",
            isUser: false,
            timestamp: new Date().toISOString()
        }]);
        setEditingMessageId(null);
    };

    /**
     * Handle edit message - populate input with message text
     */
    const handleEditMessage = (messageId, messageText) => {
        setEditingMessageId(messageId);
        setInputValue(messageText);
        inputRef.current?.focus();
    };

    /**
     * Cancel editing
     */
    const handleCancelEdit = () => {
        setEditingMessageId(null);
        setInputValue('');
    };

    /**
     * Submit edited message
     */
    const handleSubmitEdit = async () => {
        if (!inputValue.trim() || isLoading) return;

        // Remove messages from the edited one onwards
        const editIndex = messages.findIndex(m => m.id === editingMessageId);
        if (editIndex !== -1) {
            setMessages(prev => prev.slice(0, editIndex));
        }

        setEditingMessageId(null);
        await sendMessage();
    };

    return (
        <div className="app">
            {/* Sidebar */}
            <aside className="sidebar">
                <div className="sidebar-header">
                    <div className="logo">
                        <span className="logo-icon">🔩</span>
                        <div className="logo-text">
                            <h1>IGNIS</h1>
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
                                onEdit={msg.isUser ? handleEditMessage : null}
                                onImageClick={openLightbox}
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
                    {editingMessageId && (
                        <div style={{
                            padding: '8px 16px',
                            background: 'rgba(99, 102, 241, 0.2)',
                            borderRadius: '8px',
                            marginBottom: '8px',
                            display: 'flex',
                            alignItems: 'center',
                            justifyContent: 'space-between'
                        }}>
                            <span style={{ color: '#a5b4fc' }}>✏️ Editing question...</span>
                            <button
                                onClick={handleCancelEdit}
                                style={{
                                    background: 'transparent',
                                    border: 'none',
                                    color: '#f87171',
                                    cursor: 'pointer'
                                }}
                            >
                                ✕ Cancel
                            </button>
                        </div>
                    )}
                    <div className="input-wrapper">
                        <input
                            ref={inputRef}
                            type="text"
                            value={inputValue}
                            onChange={(e) => setInputValue(e.target.value)}
                            onKeyPress={handleKeyPress}
                            placeholder={editingMessageId ? "Edit your question..." : "Ask about furnace, OEE, production..."}
                            disabled={isLoading}
                            className="chat-input"
                        />
                        <button
                            onClick={editingMessageId ? handleSubmitEdit : () => sendMessage()}
                            disabled={!inputValue.trim() || isLoading}
                            className="send-button"
                        >
                            {isLoading ? (
                                <span className="loading-spinner"></span>
                            ) : editingMessageId ? (
                                <span>✓ Update</span>
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

            {/* Image Lightbox Modal */}
            {lightboxData && (
                <ImageLightbox
                    images={lightboxData.images}
                    currentIndex={lightboxData.currentIndex}
                    onClose={closeLightbox}
                    onNavigate={navigateLightbox}
                />
            )}
        </div>
    );
}

export default App;
