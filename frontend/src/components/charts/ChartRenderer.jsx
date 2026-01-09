import React from 'react';
import {
    LineChart, Line, BarChart, Bar, PieChart, Pie, AreaChart, Area,
    XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer, Cell
} from 'recharts';
import './Charts.css';

// DaVinci Design System Colors
const COLORS = {
    primary: '#3b82f6',
    secondary: '#f97316',
    success: '#22c55e',
    warning: '#f59e0b',
    danger: '#ef4444',
    purple: '#a855f7',
    palette: ['#3b82f6', '#f97316', '#22c55e', '#a855f7', '#f59e0b', '#ef4444', '#06b6d4', '#ec4899']
};

// Custom tooltip component
const CustomTooltip = ({ active, payload, label }) => {
    if (active && payload && payload.length) {
        return (
            <div className="chart-tooltip">
                <p className="tooltip-label">{label}</p>
                {payload.map((entry, index) => (
                    <p key={index} style={{ color: entry.color }}>
                        {entry.name}: {typeof entry.value === 'number' ? entry.value.toLocaleString() : entry.value}
                    </p>
                ))}
            </div>
        );
    }
    return null;
};

// Line Chart Component
const LineChartView = ({ config, data }) => {
    const options = config.options || {};
    const xKey = options.xAxis?.dataKey || Object.keys(data[0] || {})[0];
    const lines = options.lines || [{ dataKey: Object.keys(data[0] || {})[1], stroke: COLORS.primary }];

    return (
        <ResponsiveContainer width="100%" height={300}>
            <LineChart data={data} margin={{ top: 20, right: 30, left: 20, bottom: 20 }}>
                <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.1)" />
                <XAxis
                    dataKey={xKey}
                    stroke="#94a3b8"
                    tick={{ fill: '#94a3b8', fontSize: 12 }}
                />
                <YAxis
                    stroke="#94a3b8"
                    tick={{ fill: '#94a3b8', fontSize: 12 }}
                />
                <Tooltip content={<CustomTooltip />} />
                {options.legend && <Legend />}
                {lines.map((line, idx) => (
                    <Line
                        key={idx}
                        type="monotone"
                        dataKey={line.dataKey}
                        stroke={line.stroke || COLORS.palette[idx % COLORS.palette.length]}
                        strokeWidth={line.strokeWidth || 2}
                        dot={{ r: 4, fill: line.stroke || COLORS.palette[idx % COLORS.palette.length] }}
                        activeDot={{ r: 6 }}
                    />
                ))}
            </LineChart>
        </ResponsiveContainer>
    );
};

// Bar Chart Component
const BarChartView = ({ config, data }) => {
    const options = config.options || {};
    const xKey = options.xAxis?.dataKey || Object.keys(data[0] || {})[0];
    const bars = options.bars || [{ dataKey: Object.keys(data[0] || {})[1], fill: COLORS.primary }];

    return (
        <ResponsiveContainer width="100%" height={300}>
            <BarChart data={data} margin={{ top: 20, right: 30, left: 20, bottom: 20 }}>
                <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.1)" />
                <XAxis
                    dataKey={xKey}
                    stroke="#94a3b8"
                    tick={{ fill: '#94a3b8', fontSize: 12 }}
                />
                <YAxis
                    stroke="#94a3b8"
                    tick={{ fill: '#94a3b8', fontSize: 12 }}
                />
                <Tooltip content={<CustomTooltip />} />
                {options.legend && <Legend />}
                {bars.map((bar, idx) => (
                    <Bar
                        key={idx}
                        dataKey={bar.dataKey}
                        fill={bar.fill || COLORS.palette[idx % COLORS.palette.length]}
                        radius={[4, 4, 0, 0]}
                    />
                ))}
            </BarChart>
        </ResponsiveContainer>
    );
};

// Pie Chart Component
const PieChartView = ({ config, data }) => {
    const options = config.options || {};
    const valueKey = options.dataKey || Object.keys(data[0] || {})[1];
    const nameKey = options.nameKey || Object.keys(data[0] || {})[0];

    return (
        <ResponsiveContainer width="100%" height={300}>
            <PieChart margin={{ top: 20, right: 30, left: 20, bottom: 20 }}>
                <Pie
                    data={data}
                    cx="50%"
                    cy="50%"
                    innerRadius={options.innerRadius || 60}
                    outerRadius={options.outerRadius || 100}
                    dataKey={valueKey}
                    nameKey={nameKey}
                    label={({ name, percent }) => `${name}: ${(percent * 100).toFixed(0)}%`}
                    labelLine={{ stroke: '#94a3b8' }}
                >
                    {data.map((entry, index) => (
                        <Cell key={`cell-${index}`} fill={COLORS.palette[index % COLORS.palette.length]} />
                    ))}
                </Pie>
                <Tooltip content={<CustomTooltip />} />
                {options.legend && <Legend />}
            </PieChart>
        </ResponsiveContainer>
    );
};

// Area Chart Component
const AreaChartView = ({ config, data }) => {
    const options = config.options || {};
    const xKey = options.xAxis?.dataKey || Object.keys(data[0] || {})[0];
    const yKey = options.lines?.[0]?.dataKey || Object.keys(data[0] || {})[1];

    return (
        <ResponsiveContainer width="100%" height={300}>
            <AreaChart data={data} margin={{ top: 20, right: 30, left: 20, bottom: 20 }}>
                <defs>
                    <linearGradient id="colorValue" x1="0" y1="0" x2="0" y2="1">
                        <stop offset="5%" stopColor={COLORS.primary} stopOpacity={0.3} />
                        <stop offset="95%" stopColor={COLORS.primary} stopOpacity={0} />
                    </linearGradient>
                </defs>
                <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.1)" />
                <XAxis
                    dataKey={xKey}
                    stroke="#94a3b8"
                    tick={{ fill: '#94a3b8', fontSize: 12 }}
                />
                <YAxis
                    stroke="#94a3b8"
                    tick={{ fill: '#94a3b8', fontSize: 12 }}
                />
                <Tooltip content={<CustomTooltip />} />
                <Area
                    type="monotone"
                    dataKey={yKey}
                    stroke={COLORS.primary}
                    strokeWidth={2}
                    fillOpacity={1}
                    fill="url(#colorValue)"
                />
            </AreaChart>
        </ResponsiveContainer>
    );
};

// Gauge Chart Component (Radial Progress)
const GaugeChart = ({ config, data }) => {
    const options = config.options || {};
    // Type-safe value extraction with Number() coercion
    const rawValue = config.data?.value ?? (data && data[0] ? Object.values(data[0])[0] : 0);
    const value = Number(rawValue) || 0;
    const max = Number(config.data?.max) || 100;
    const percentage = Math.min(Math.max((value / max) * 100, 0), 100); // Clamp between 0-100
    const unit = options.unit || '';
    const title = options.title || 'Value';

    // Determine color based on thresholds
    const thresholds = options.thresholds || {};
    let color = COLORS.primary;
    if (percentage < 50) color = thresholds.low?.color || COLORS.danger;
    else if (percentage < 80) color = thresholds.medium?.color || COLORS.warning;
    else color = thresholds.high?.color || COLORS.success;

    return (
        <div className="gauge-chart">
            <div className="gauge-title">{title}</div>
            <div className="gauge-container">
                <svg viewBox="0 0 100 60" className="gauge-svg">
                    {/* Background arc */}
                    <path
                        d="M 10 50 A 40 40 0 0 1 90 50"
                        fill="none"
                        stroke="rgba(255,255,255,0.1)"
                        strokeWidth="8"
                        strokeLinecap="round"
                    />
                    {/* Value arc */}
                    <path
                        d="M 10 50 A 40 40 0 0 1 90 50"
                        fill="none"
                        stroke={color}
                        strokeWidth="8"
                        strokeLinecap="round"
                        strokeDasharray={`${percentage * 1.26} 126`}
                        style={{ transition: 'stroke-dasharray 0.5s ease' }}
                    />
                </svg>
                <div className="gauge-value-container">
                    <span className="gauge-value" style={{ color }}>{value.toLocaleString()}</span>
                    <span className="gauge-unit">{unit}</span>
                </div>
            </div>
        </div>
    );
};

// KPI Card Component
const KPICard = ({ config, data }) => {
    const options = config.options || {};
    // Type-safe value extraction
    const rawValue = config.data?.value ?? (data && data[0] ? Object.values(data[0])[0] : 0);
    const value = typeof rawValue === 'number' ? rawValue : (Number(rawValue) || rawValue || 0);
    const unit = options.unit || '';
    const title = options.title || 'Metric';
    const trend = options.trend ? Number(options.trend) : null;
    const color = options.color || COLORS.primary;

    return (
        <div className="kpi-card" style={{ borderColor: color }}>
            <div className="kpi-label">{title}</div>
            <div className="kpi-value-container">
                <span className="kpi-value">{typeof value === 'number' ? value.toLocaleString() : value}</span>
                <span className="kpi-unit">{unit}</span>
            </div>
            {trend && (
                <div className={`kpi-trend ${trend > 0 ? 'up' : trend < 0 ? 'down' : 'stable'}`}>
                    {trend > 0 ? '↑' : trend < 0 ? '↓' : '→'} {Math.abs(trend)}%
                </div>
            )}
        </div>
    );
};

// Metric Grid Component
const MetricGrid = ({ config, data }) => {
    const metrics = config.data || [];
    const options = config.options || {};
    const columns = options.columns || Math.min(metrics.length, 4);

    return (
        <div className="metric-grid" style={{ gridTemplateColumns: `repeat(${columns}, 1fr)` }}>
            {metrics.map((metric, idx) => (
                <div key={idx} className="metric-item">
                    <div className="metric-value">
                        {typeof metric.value === 'number' ? metric.value.toLocaleString() : metric.value}
                        <span className="metric-unit">{metric.unit || ''}</span>
                    </div>
                    <div className="metric-label">{metric.label}</div>
                </div>
            ))}
        </div>
    );
};

/**
 * ChartErrorBoundary - Error boundary for chart rendering failures
 */
class ChartErrorBoundary extends React.Component {
    constructor(props) {
        super(props);
        this.state = { hasError: false, error: null };
    }

    static getDerivedStateFromError(error) {
        return { hasError: true, error };
    }

    componentDidCatch(error, errorInfo) {
        console.error('Chart rendering error:', error, errorInfo);
    }

    render() {
        if (this.state.hasError) {
            return (
                <div className="chart-error">
                    <p>Unable to render chart. Showing data table instead.</p>
                </div>
            );
        }
        return this.props.children;
    }
}

/**
 * ChartRenderer - Main chart dispatcher component
 * Renders the appropriate chart based on config type
 */
const ChartRenderer = ({ config, data }) => {
    if (!config || !config.type) {
        return null;
    }

    // Use data from config or props
    const chartData = config.data || data;

    // For certain chart types, we need array data
    const arrayData = Array.isArray(chartData) ? chartData : (data || []);

    // Skip rendering if no meaningful data
    if (!arrayData || (Array.isArray(arrayData) && arrayData.length === 0)) {
        if (config.type !== 'gauge' && config.type !== 'kpi_card') {
            return null;
        }
    }

    const chartComponents = {
        'line': LineChartView,
        'bar': BarChartView,
        'pie': PieChartView,
        'area': AreaChartView,
        'gauge': GaugeChart,
        'kpi_card': KPICard,
        'metric_grid': MetricGrid
    };

    const ChartComponent = chartComponents[config.type];

    if (!ChartComponent) {
        console.warn(`Unknown chart type: ${config.type}`);
        return null;
    }

    return (
        <ChartErrorBoundary>
            <div className="chart-container">
                {config.options?.title && config.type !== 'gauge' && config.type !== 'kpi_card' && (
                    <div className="chart-title">{config.options.title}</div>
                )}
                <ChartComponent config={config} data={arrayData} />
            </div>
        </ChartErrorBoundary>
    );
};

export default ChartRenderer;
