# Query to Chart Type Mapping Guide

This document shows what chart type each query pattern will generate.

## Chart Type Legend
- 📊 **Bar Chart** - Comparing categories (furnaces, shifts, machines)
- 🥧 **Pie Chart** - Distribution/breakdown by category
- 📈 **Line Chart** - Trends over time
- 📉 **Area Chart** - Cumulative trends over time
- 📋 **Table** - Detailed multi-column data
- 🎯 **KPI Card** - Single metric value
- 📊 **Progress Bar** - Single percentage value
- 📊 **Metric Grid** - Multiple KPIs in grid

---

## 1. Simple Aggregation Queries → KPI Card / Bar Chart

| Query | Chart Type | Why |
|-------|-----------|-----|
| "What is the average oee for all furnaces" | 🎯 KPI Card | Single aggregated value |
| "What is the average oee for furnace 1" | 🎯 KPI Card | Single value for one furnace |
| "Show Average OEE by furnace" | 📊 Bar Chart | Comparing multiple furnaces |
| "Show OEE by furnace" | 📊 Bar Chart | Categorical comparison |
| "Show Total downtime by furnace" | 📊 Bar Chart | Comparing totals across furnaces |
| "Show Total energy consumption by furnace" | 📊 Bar Chart | Comparing energy by furnace |
| "Which furnace has highest OEE?" | 📊 Bar Chart | Ranking comparison |
| "Show Total quantity produced by furnace" | 📊 Bar Chart | Production comparison |

---

## 2. Trend Analysis Queries → Line/Area Chart

| Query | Chart Type | Why |
|-------|-----------|-----|
| "Show OEE trend for Furnace 2" | 📈 Line Chart | Time series for single furnace |
| "Display downtime trend last 30 days" | 📈 Line Chart | Trend over time period |
| "Show recent defect rate data" | 📈 Line Chart | Recent time series |
| "Show OEE trend last week" | 📈 Line Chart | Weekly trend |
| "Show yield data for last month" | 📈 Line Chart | Monthly trend |
| "Display energy efficiency trend" | 📈 Line Chart | Efficiency over time |
| "Show MTTR data for Furnace 2" | 📈 Line Chart | Maintenance trend |

---

## 3. Comparative Analysis → Bar Chart

| Query | Chart Type | Why |
|-------|-----------|-----|
| "Compare OEE between Furnace 1 and 2" | 📊 Bar Chart | Direct comparison |
| "Which shift has highest yield?" | 📊 Bar Chart | Shift comparison |
| "Compare all furnaces by OEE" | 📊 Bar Chart | Multi-furnace comparison |
| "Show rank furnaces by defect rate" | 📊 Bar Chart | Ranking |
| "Compare downtime between machines" | 📊 Bar Chart | Machine comparison |
| "Which product type has highest yield?" | 📊 Bar Chart | Product comparison |
| "Compare energy efficiency by furnace" | 📊 Bar Chart | Efficiency comparison |
| "Show production efficiency by shift" | 📊 Bar Chart | Shift efficiency |
| "Compare MTBF by furnace" | 📊 Bar Chart | Reliability comparison |
| "Best and worst shift by OEE" | 📊 Bar Chart | Shift ranking |

---

## 4. "By X" Pattern Queries → Bar Chart

| Query | Chart Type | Why |
|-------|-----------|-----|
| "Show production by furnace" | 📊 Bar Chart | "by furnace" = categorical breakdown |
| "Show production by shift" | 📊 Bar Chart | "by shift" = shift comparison |
| "Show downtime by furnace" | 📊 Bar Chart | Downtime comparison |
| "Show energy by furnace" | 📊 Bar Chart | Energy comparison |
| "Show yield by shift" | 📊 Bar Chart | Shift yield comparison |
| "Show OEE by shift" | 📊 Bar Chart | Shift OEE comparison |
| "Show OEE by plant" | 📊 Bar Chart | Plant comparison |

---

## 5. Threshold-Based Queries → Bar Chart / Table

| Query | Chart Type | Why |
|-------|-----------|-----|
| "Show OEE records above 90%" | 📋 Table | Filtered records |
| "Show downtime events exceeding 8 hours" | 📋 Table | Event details |
| "Show furnaces with low efficiency below 80%" | 📊 Bar Chart | Filtered comparison |
| "Show defect rate above 5 percent" | 📋 Table | Filtered records |
| "Show energy usage above average" | 📊 Bar Chart | Above-average comparison |
| "Show low yield furnaces below 85%" | 📊 Bar Chart | Low performers |

---

## 6. Ranking / Top-N Queries → Bar Chart

| Query | Chart Type | Why |
|-------|-----------|-----|
| "Show top 5 furnaces by production" | 📊 Bar Chart | Top performers |
| "Show bottom 3 furnaces by yield" | 📊 Bar Chart | Bottom performers |
| "Show top 10 shifts by output" | 📊 Bar Chart | Top shifts |
| "What is the worst furnace by OEE" | 📊 Bar Chart | Worst performer |
| "Show top 3 machines by energy" | 📊 Bar Chart | Top energy users |
| "What is the best shift by efficiency" | 📊 Bar Chart | Best shift |
| "What is the most reliable furnace" | 📊 Bar Chart | Reliability ranking |

---

## 7. Statistical Queries → Table / Metric Grid

| Query | Chart Type | Why |
|-------|-----------|-----|
| "Show oee statistics" | 📊 Metric Grid | Multiple statistics |
| "Show downtime statistics by furnace" | 📋 Table | Multi-column stats |
| "Show energy efficiency range" | 📊 Metric Grid | Min/max/avg |
| "Show yield statistics by furnace" | 📋 Table | Detailed stats |
| "Show production quantity statistics" | 📊 Metric Grid | Summary stats |

---

## 8. Time-Series Bucketing → Line/Area Chart

| Query | Chart Type | Why |
|-------|-----------|-----|
| "What is the average oee per day" | 📈 Line Chart | Daily trend |
| "What is the total production per week" | 📉 Area Chart | Weekly cumulative |
| "Show monthly energy by furnace" | 📈 Line Chart | Monthly trend |
| "Show daily downtime summary" | 📈 Line Chart | Daily trend |
| "Show weekly yield trend" | 📈 Line Chart | Weekly trend |
| "Show daily tap production" | 📉 Area Chart | Daily production |

---

## 9. Temporal Comparison → Bar Chart

| Query | Chart Type | Why |
|-------|-----------|-----|
| "Compare OEE January vs February 2025" | 📊 Bar Chart | Month comparison |
| "Show week over week downtime comparison" | 📊 Bar Chart | Week comparison |
| "Compare last 2 months of OEE" | 📊 Bar Chart | Period comparison |
| "Show monthly energy trend" | 📈 Line Chart | Monthly trend |
| "Show this month vs last month downtime" | 📊 Bar Chart | Period comparison |
| "Show year to date production" | 📉 Area Chart | YTD cumulative |

---

## 10. Distribution/Breakdown Queries → Pie Chart

| Query | Chart Type | Why |
|-------|-----------|-----|
| "Show breakdown of defects by type" | 🥧 Pie Chart | Category distribution |
| "Show distribution of downtime by reason" | 🥧 Pie Chart | Reason distribution |
| "Show grade distribution" | 🥧 Pie Chart | Grade breakdown |
| "What percentage of production by product" | 🥧 Pie Chart | Product distribution |

---

## Quick Reference: Query Keywords → Chart Type

### Bar Chart Keywords
- "by furnace", "by shift", "by machine", "by product"
- "compare", "versus", "between"
- "top 5", "bottom 3", "best", "worst"
- "rank", "highest", "lowest"
- "all furnaces", "each shift"

### Line Chart Keywords
- "trend", "over time", "last week", "last month"
- "historical", "recent data"
- "show data", "display trend"

### Pie Chart Keywords
- "breakdown", "distribution", "proportion"
- "percentage of", "share", "composition"
- "by type", "by category", "by reason"

### KPI Card Keywords
- "current", "total", "average" (single value)
- "what is the [metric]"
- Single furnace, single metric

### Table Keywords
- "show records", "list events"
- "above X", "below Y" (filtered data)
- Multiple columns needed
- More than 20 rows

---

## Chart Selection Priority

The system follows this priority order:

1. **Single Value** → KPI Card/Progress Bar
2. **"by X" Pattern** → Bar Chart
3. **"breakdown/distribution"** → Pie Chart
4. **Multiple Categories (3-20 rows)** → Bar Chart
5. **Time Series + Trend** → Line/Area Chart
6. **Complex Multi-column** → Table

---

## Examples by Chart Type

### 📊 Bar Charts (Most Common)
- Comparing furnaces, shifts, machines
- Rankings and top-N queries
- "by X" categorical breakdowns
- Performance comparisons

### 📈 Line Charts
- OEE trends over time
- Production trends
- Efficiency trends
- Historical data

### 🥧 Pie Charts
- Defect distribution by type
- Downtime by reason
- Grade distribution
- Product mix

### 🎯 KPI Cards
- Current OEE
- Total production today
- Average efficiency
- Single metric values

### 📋 Tables
- Detailed event logs
- Filtered records (>20 rows)
- Multi-column data
- Statistical breakdowns
