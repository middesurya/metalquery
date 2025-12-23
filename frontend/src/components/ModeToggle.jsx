import React from 'react';
import './ModeToggle.css';

/**
 * ModeToggle Component
 * Toggle between NLP-SQL (Data) and RAG (Documentation) modes.
 */
const ModeToggle = ({ mode, onModeChange, disabled = false }) => {
    const modes = [
        { id: 'auto', label: 'Auto', icon: '🔄', description: 'Auto-detect query type' },
        { id: 'nlp-sql', label: 'Data', icon: '📊', description: 'Query database for metrics' },
        { id: 'rag', label: 'Docs', icon: '📚', description: 'Search BRD documents' },
    ];

    return (
        <div className="mode-toggle-container">
            <span className="mode-toggle-label">Query Mode:</span>
            <div className={`mode-toggle ${disabled ? 'disabled' : ''}`}>
                {modes.map((m) => (
                    <button
                        key={m.id}
                        className={`mode-btn ${mode === m.id ? 'active' : ''}`}
                        onClick={() => !disabled && onModeChange(m.id)}
                        disabled={disabled}
                        title={m.description}
                    >
                        <span className="mode-icon">{m.icon}</span>
                        <span className="mode-label">{m.label}</span>
                    </button>
                ))}
            </div>
        </div>
    );
};

export default ModeToggle;
