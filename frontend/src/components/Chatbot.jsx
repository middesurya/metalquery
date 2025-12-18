import React, { useState, useRef, useEffect } from 'react';
import './Chatbot.css';

// NLP Service API URL
// Backend API URL
const API_URL = process.env.REACT_APP_API_URL || 'http://127.0.0.1:8002';

/**
 * ChatMessage Component
 * Renders a single chat message with appropriate styling
 */
const ChatMessage = ({ message, isUser }) => {
    return (
        <div className={`chat-message ${isUser ? 'user' : 'bot'}`}>
            <div className="message-avatar">
                {isUser ? '👤' : '🔩'}
            </div>
            <div className="message-content">
                <div className="message-bubble">
                    {message.text}
                </div>
                {message.sql && (
                    <div className="message-sql">
                        <details>
                            <summary>View SQL Query</summary>
                            <pre><code>{message.sql}</code></pre>
                        </details>
                    </div>
                )}
                {message.results && message.results.length > 0 && (
                    <div className="message-results">
                        <details>
                            <summary>View Data ({message.results.length} rows)</summary>
                            <div className="results-table-wrapper">
                                <table className="results-table">
                                    <thead>
                                        <tr>
                                            {Object.keys(message.results[0]).map(key => (
                                                <th key={key}>{key}</th>
                                            ))}
                                        </tr>
                                    </thead>
                                    <tbody>
                                        {message.results.slice(0, 20).map((row, idx) => (
                                            <tr key={idx}>
                                                {Object.values(row).map((val, i) => (
                                                    <td key={i}>{val !== null ? String(val) : '-'}</td>
                                                ))}
                                            </tr>
                                        ))}
                                    </tbody>
                                </table>
                                {message.results.length > 20 && (
                                    <p className="more-rows">... and {message.results.length - 20} more rows</p>
                                )}
                            </div>
                        </details>
                    </div>
                )}
                <div className="message-time">
                    {new Date(message.timestamp).toLocaleTimeString()}
                </div>
            </div>
        </div>
    );
};

/**
 * TypingIndicator Component
 * Shows animated dots when bot is thinking
 */
const TypingIndicator = () => (
    <div className="chat-message bot">
        <div className="message-avatar">🔩</div>
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
 * Chatbot Component
 * Main chatbot UI for NLP-to-SQL queries on Metallurgy Database
 */
const Chatbot = () => {
    const [messages, setMessages] = useState([
        {
            id: 1,
            text: "Hello! I'm your Metallurgy Database Assistant. Ask me anything about materials, properties, and specifications. For example: 'What steel has the highest tensile strength?' or 'Show me aluminum alloys'.",
            isUser: false,
            timestamp: new Date().toISOString()
        }
    ]);
    const [inputValue, setInputValue] = useState('');
    const [isLoading, setIsLoading] = useState(false);
    const [isOpen, setIsOpen] = useState(true);
    const messagesEndRef = useRef(null);
    const inputRef = useRef(null);

    // Auto-scroll to bottom when new messages arrive
    const scrollToBottom = () => {
        messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
    };

    useEffect(() => {
        scrollToBottom();
    }, [messages]);

    // Focus input when chat opens
    useEffect(() => {
        if (isOpen) {
            inputRef.current?.focus();
        }
    }, [isOpen]);

    /**
     * Send message to NLP Service API
     */
    const sendMessage = async () => {
        if (!inputValue.trim() || isLoading) return;

        const userMessage = {
            id: Date.now(),
            text: inputValue,
            isUser: true,
            timestamp: new Date().toISOString()
        };

        setMessages(prev => [...prev, userMessage]);
        const questionText = inputValue;
        setInputValue('');
        setIsLoading(true);

        try {
            // Call the chat endpoint which executes the query and returns results
            const response = await fetch(`${API_URL}/api/chatbot/chat/`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ question: questionText })
            });

            const data = await response.json();

            if (!data.success) {
                throw new Error(data.error || 'Failed to process question');
            }

            // Create bot message with response, SQL, and results
            const botMessage = {
                id: Date.now() + 1,
                text: data.response,
                isUser: false,
                sql: data.sql,
                results: data.results,
                row_count: data.row_count,
                timestamp: new Date().toISOString()
            };

            setMessages(prev => [...prev, botMessage]);

        } catch (error) {
            console.error('Chat error:', error);
            setMessages(prev => [...prev, {
                id: Date.now() + 1,
                text: `Sorry, I couldn't process that: ${error.message}. Please try rephrasing your question.`,
                isUser: false,
                timestamp: new Date().toISOString()
            }]);
        } finally {
            setIsLoading(false);
        }
    };

    /**
     * Handle Enter key press
     */
    const handleKeyPress = (e) => {
        if (e.key === 'Enter' && !e.shiftKey) {
            e.preventDefault();
            sendMessage();
        }
    };

    /**
     * Quick suggestion buttons - Metallurgy focused
     */
    const suggestions = [
        "What steel has highest strength?",
        "Show aluminum alloys",
        "Compare hardness of steels",
        "Find materials with density < 3000"
    ];

    return (
        <div className={`chatbot-container ${isOpen ? 'open' : 'closed'}`}>
            {/* Floating Toggle Button */}
            <button
                className="chatbot-toggle"
                onClick={() => setIsOpen(!isOpen)}
                aria-label={isOpen ? 'Close chat' : 'Open chat'}
            >
                {isOpen ? '✕' : '🔩'}
            </button>

            {/* Chat Window */}
            {isOpen && (
                <div className="chatbot-window">
                    {/* Header */}
                    <div className="chatbot-header">
                        <div className="header-info">
                            <span className="header-icon">🔩</span>
                            <div>
                                <h3>Metallurgy Assistant</h3>
                                <span className="status online">Online</span>
                            </div>
                        </div>
                    </div>

                    {/* Messages Container */}
                    <div className="chatbot-messages">
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

                    {/* Suggestions */}
                    {messages.length === 1 && (
                        <div className="chatbot-suggestions">
                            <p>Try asking:</p>
                            <div className="suggestion-chips">
                                {suggestions.map((suggestion, idx) => (
                                    <button
                                        key={idx}
                                        className="suggestion-chip"
                                        onClick={() => {
                                            setInputValue(suggestion);
                                            inputRef.current?.focus();
                                        }}
                                    >
                                        {suggestion}
                                    </button>
                                ))}
                            </div>
                        </div>
                    )}

                    {/* Input Area */}
                    <div className="chatbot-input">
                        <input
                            ref={inputRef}
                            type="text"
                            value={inputValue}
                            onChange={(e) => setInputValue(e.target.value)}
                            onKeyPress={handleKeyPress}
                            placeholder="Ask about materials..."
                            disabled={isLoading}
                        />
                        <button
                            onClick={sendMessage}
                            disabled={!inputValue.trim() || isLoading}
                            className="send-button"
                        >
                            {isLoading ? '...' : '➤'}
                        </button>
                    </div>
                </div>
            )}
        </div>
    );
};

export default Chatbot;
