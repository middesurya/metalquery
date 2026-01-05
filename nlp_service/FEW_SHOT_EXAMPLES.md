# Few-Shot Examples Documentation

This document lists all few-shot examples added to `prompts_v2.py` for the MetalQuery NLP-to-SQL system.

**Total Examples: ~365+**  
**Last Updated: 2026-01-05**

---

## Table of Contents

1. [Original Examples (TYPE 1-10)](#original-examples-type-1-10)
2. [Cycle Time Examples (TYPE 11-19)](#cycle-time-examples-type-11-19)
3. [OEE Examples (TYPE 20-29)](#oee-examples-type-20-29)
4. [KPI Tables (TYPE 30-47)](#kpi-tables-type-30-47)
5. [Core Process Tables (TYPE 48-50)](#core-process-tables-type-48-50)
6. [Log & Config Tables (TYPE 51-52)](#log--config-tables-type-51-52)

---

## Original Examples (TYPE 1-10)

### TYPE 1: Simple Aggregation (12 examples)
| Question | SQL |
|----------|-----|
| Average OEE for all furnaces | `SELECT AVG(oee_percentage) as average_oee FROM kpi_overall_equipment_efficiency_data` |
| Average OEE for Furnace 1 | `SELECT AVG(oee_percentage) FROM kpi_overall_equipment_efficiency_data WHERE furnace_no = 1` |
| Average OEE for Furnace 1 last 30 days | `SELECT AVG(oee_percentage) FROM kpi_overall_equipment_efficiency_data WHERE furnace_no = 1 AND date >= CURRENT_DATE - INTERVAL '30 days'` |
| Average OEE by furnace | `SELECT furnace_no, AVG(oee_percentage) as avg_oee FROM kpi_overall_equipment_efficiency_data GROUP BY furnace_no ORDER BY avg_oee DESC` |
| Total downtime by furnace | `SELECT furnace_no, SUM(downtime_hours) as total_downtime FROM kpi_downtime_data GROUP BY furnace_no ORDER BY total_downtime DESC` |
| Total energy consumption by furnace | `SELECT furnace_no, SUM(energy_used) as total_energy FROM kpi_energy_used_data GROUP BY furnace_no ORDER BY total_energy DESC` |
| Which furnace has highest OEE? | `SELECT furnace_no, AVG(oee_percentage) as avg_oee FROM kpi_overall_equipment_efficiency_data GROUP BY furnace_no ORDER BY avg_oee DESC LIMIT 1` |
| Total quantity produced by furnace | `SELECT furnace_no, SUM(quantity_produced) as total_qty FROM kpi_quantity_produced_data GROUP BY furnace_no ORDER BY total_qty DESC` |
| Average yield for Furnace 2 | `SELECT AVG(yield_percentage) FROM kpi_yield_data WHERE furnace_no = 2` |
| Total downtime last year | `SELECT SUM(downtime_hours) as total_downtime FROM kpi_downtime_data WHERE date >= CURRENT_DATE - INTERVAL '1 year'` |
| Average downtime per furnace | `SELECT furnace_no, AVG(downtime_hours) as avg_downtime FROM kpi_downtime_data GROUP BY furnace_no` |
| Total production for Furnace 1 last month | `SELECT SUM(quantity_produced) as total_production FROM kpi_quantity_produced_data WHERE furnace_no = 1 AND date >= CURRENT_DATE - INTERVAL '30 days'` |

### TYPE 2: Trend Analysis - No Aggregation (11 examples)
| Question | SQL |
|----------|-----|
| Show OEE trend for Furnace 2 | `SELECT date, oee_percentage FROM kpi_overall_equipment_efficiency_data WHERE furnace_no = 2 ORDER BY date DESC LIMIT 100` |
| Display downtime trend last 30 days | `SELECT date, furnace_no, downtime_hours FROM kpi_downtime_data WHERE date >= CURRENT_DATE - INTERVAL '30 days' ORDER BY date DESC` |
| Recent defect rate data | `SELECT date, shift_id, furnace_no, defect_rate FROM kpi_defect_rate_data ORDER BY date DESC LIMIT 50` |
| Show OEE trend last week | `SELECT date, furnace_no, oee_percentage FROM kpi_overall_equipment_efficiency_data WHERE date >= CURRENT_DATE - INTERVAL '7 days' ORDER BY date DESC` |
| List all furnaces | `SELECT furnace_no, furnace_description, is_active FROM furnace_furnaceconfig ORDER BY furnace_no` |
| Show downtime events for Furnace 1 | `SELECT obs_start_dt, obs_end_dt, downtime_hours FROM log_book_furnace_down_time_event WHERE furnace_no = 1 ORDER BY obs_start_dt DESC LIMIT 50` |
| Recent tap production data | `SELECT tap_id, cast_weight, energy, tap_production_datetime FROM core_process_tap_production ORDER BY tap_production_datetime DESC LIMIT 20` |
| Show yield data for last month | `SELECT date, furnace_no, yield_percentage FROM kpi_yield_data WHERE date >= CURRENT_DATE - INTERVAL '30 days' ORDER BY date DESC` |
| Display energy efficiency trend | `SELECT date, furnace_no, energy_efficiency FROM kpi_energy_efficiency_data ORDER BY date DESC LIMIT 100` |
| Show MTTR data for Furnace 2 | `SELECT date, mttr_hours FROM kpi_mean_time_to_repair_data WHERE furnace_no = 2 ORDER BY date DESC LIMIT 100` |
| List recent quality issues | `SELECT date, furnace_no, defect_rate FROM kpi_defect_rate_data ORDER BY date DESC LIMIT 100` |

### TYPE 3: Comparative Analysis (10 examples)
| Question | SQL |
|----------|-----|
| Compare OEE between Furnace 1 and 2 | `SELECT furnace_no, AVG(oee_percentage) as avg_oee FROM kpi_overall_equipment_efficiency_data WHERE furnace_no IN (1, 2) GROUP BY furnace_no ORDER BY avg_oee DESC` |
| Which shift has highest yield? | `SELECT shift_id, AVG(yield_percentage) as avg_yield FROM kpi_yield_data GROUP BY shift_id ORDER BY avg_yield DESC LIMIT 1` |
| Compare all furnaces by OEE | `SELECT furnace_no, AVG(oee_percentage) as avg_oee, MAX(oee_percentage) as max_oee, MIN(oee_percentage) as min_oee FROM kpi_overall_equipment_efficiency_data GROUP BY furnace_no ORDER BY avg_oee DESC` |
| Rank furnaces by defect rate | `SELECT furnace_no, AVG(defect_rate) as avg_defect FROM kpi_defect_rate_data GROUP BY furnace_no ORDER BY avg_defect DESC` |
| Compare downtime between machines | `SELECT machine_id, SUM(downtime_hours) as total_downtime FROM kpi_downtime_data GROUP BY machine_id ORDER BY total_downtime DESC` |
| Which product type has highest yield? | `SELECT product_type_id, AVG(yield_percentage) as avg_yield FROM kpi_yield_data GROUP BY product_type_id ORDER BY avg_yield DESC LIMIT 1` |
| Compare energy efficiency by furnace | `SELECT furnace_no, AVG(energy_efficiency) as avg_efficiency FROM kpi_energy_efficiency_data GROUP BY furnace_no ORDER BY avg_efficiency` |
| Production efficiency by shift | `SELECT shift_id, AVG(production_efficiency_percentage) as avg_efficiency FROM kpi_production_efficiency_data GROUP BY shift_id ORDER BY avg_efficiency DESC` |
| Compare MTBF by furnace | `SELECT furnace_no, AVG(mtbf_hours) as avg_mtbf FROM kpi_mean_time_between_failures_data GROUP BY furnace_no ORDER BY avg_mtbf DESC` |
| Best and worst shift by OEE | `SELECT shift_id, AVG(oee_percentage) as avg_oee FROM kpi_overall_equipment_efficiency_data GROUP BY shift_id ORDER BY avg_oee DESC` |

### TYPE 4-10: Multi-Table Joins, Temporal, Threshold, Ranking, Statistical, Time-Series, Anomaly Detection
*(~50 additional examples covering advanced query patterns)*

---

## Cycle Time Examples (TYPE 11-19)

**Table: `kpi_cycle_time_data`**  
**Columns:** record_id, date, shift_id, cycle_time, furnace_no, machine_id, plant_id, product_type_id, workshop_id, material_id, supplier_id

### TYPE 11: Quick Lookups (5 examples)
| Question | SQL |
|----------|-----|
| What is the cycle time for FURNACE on 2024-01-07? | `SELECT date, shift_id, cycle_time, furnace_no FROM kpi_cycle_time_data WHERE machine_id = 'FURNACE' AND date = '2024-01-07' ORDER BY shift_id` |
| Show all cycle time records for 2024-01-08 | `SELECT date, shift_id, cycle_time, furnace_no, machine_id FROM kpi_cycle_time_data WHERE date = '2024-01-08' ORDER BY shift_id` |
| What was the cycle time for shift 12 on 2024-01-09? | `SELECT date, shift_id, cycle_time, furnace_no, machine_id FROM kpi_cycle_time_data WHERE shift_id = '12' AND date = '2024-01-09'` |
| List cycle times for machine CAST_BAY | `SELECT date, shift_id, cycle_time, furnace_no FROM kpi_cycle_time_data WHERE machine_id = 'CAST_BAY' ORDER BY date DESC LIMIT 100` |
| Show cycle time for furnace 888 on 2024-01-07 | `SELECT date, shift_id, cycle_time, machine_id FROM kpi_cycle_time_data WHERE furnace_no = 888 AND date = '2024-01-07' ORDER BY shift_id` |

### TYPE 12: Aggregations (6 examples)
| Question | SQL |
|----------|-----|
| What is the average cycle time overall? | `SELECT AVG(cycle_time) as average_cycle_time FROM kpi_cycle_time_data` |
| What is the total cycle time per day? | `SELECT date, SUM(cycle_time) as total_cycle_time FROM kpi_cycle_time_data GROUP BY date ORDER BY date DESC` |
| What is the average cycle time per shift? | `SELECT shift_id, AVG(cycle_time) as avg_cycle_time FROM kpi_cycle_time_data GROUP BY shift_id ORDER BY avg_cycle_time DESC` |
| Which day had the highest average cycle time? | `SELECT date, AVG(cycle_time) as avg_cycle_time FROM kpi_cycle_time_data GROUP BY date ORDER BY avg_cycle_time DESC LIMIT 1` |
| Give me the min, max, and average cycle time for 2024-01-07 | `SELECT MIN(cycle_time) as min_cycle_time, MAX(cycle_time) as max_cycle_time, AVG(cycle_time) as avg_cycle_time FROM kpi_cycle_time_data WHERE date = '2024-01-07'` |
| Average cycle time by furnace | `SELECT furnace_no, AVG(cycle_time) as avg_cycle_time FROM kpi_cycle_time_data GROUP BY furnace_no ORDER BY avg_cycle_time DESC` |

### TYPE 13: Shift Analysis (5 examples)
| Question | SQL |
|----------|-----|
| Which shift has the highest average cycle time? | `SELECT shift_id, AVG(cycle_time) as avg_cycle_time FROM kpi_cycle_time_data GROUP BY shift_id ORDER BY avg_cycle_time DESC LIMIT 1` |
| Compare cycle time between shifts 4, 12, and 20 | `SELECT shift_id, AVG(cycle_time) as avg_cycle_time, MIN(cycle_time) as min_cycle_time, MAX(cycle_time) as max_cycle_time FROM kpi_cycle_time_data WHERE shift_id IN ('4', '12', '20') GROUP BY shift_id ORDER BY avg_cycle_time DESC` |
| Show cycle time trend by shift over time | `SELECT date, shift_id, AVG(cycle_time) as avg_cycle_time FROM kpi_cycle_time_data GROUP BY date, shift_id ORDER BY date DESC, shift_id` |
| On 2024-01-08, which shift was slowest? | `SELECT shift_id, AVG(cycle_time) as avg_cycle_time FROM kpi_cycle_time_data WHERE date = '2024-01-08' GROUP BY shift_id ORDER BY avg_cycle_time DESC LIMIT 1` |
| What's the average cycle time for shift 20 across all days? | `SELECT AVG(cycle_time) as avg_cycle_time FROM kpi_cycle_time_data WHERE shift_id = '20'` |

### TYPE 14: Machine Performance (5 examples)
| Question | SQL |
|----------|-----|
| Which machine has the highest average cycle time? | `SELECT machine_id, AVG(cycle_time) as avg_cycle_time FROM kpi_cycle_time_data GROUP BY machine_id ORDER BY avg_cycle_time DESC LIMIT 1` |
| Show top 5 machines by cycle time | `SELECT machine_id, AVG(cycle_time) as avg_cycle_time FROM kpi_cycle_time_data GROUP BY machine_id ORDER BY avg_cycle_time DESC LIMIT 5` |
| Which machine had cycle time above 90? | `SELECT DISTINCT machine_id, date, shift_id, cycle_time FROM kpi_cycle_time_data WHERE cycle_time > 90 ORDER BY cycle_time DESC` |
| Compare cycle time for FURNACE vs ELECTROD | `SELECT machine_id, AVG(cycle_time) as avg_cycle_time, MIN(cycle_time) as min_cycle_time, MAX(cycle_time) as max_cycle_time FROM kpi_cycle_time_data WHERE machine_id IN ('FURNACE', 'ELECTROD') GROUP BY machine_id ORDER BY avg_cycle_time DESC` |
| For UNKWN_EQ, what's the average cycle time by shift? | `SELECT shift_id, AVG(cycle_time) as avg_cycle_time FROM kpi_cycle_time_data WHERE machine_id = 'UNKWN_EQ' GROUP BY shift_id ORDER BY avg_cycle_time DESC` |

### TYPE 15: Furnace Comparisons (5 examples)
| Question | SQL |
|----------|-----|
| Compare average cycle time between furnace 1 and furnace 888 | `SELECT furnace_no, AVG(cycle_time) as avg_cycle_time FROM kpi_cycle_time_data WHERE furnace_no IN (1, 888) GROUP BY furnace_no ORDER BY avg_cycle_time DESC` |
| Which furnace has more cycle time spikes? | `SELECT furnace_no, COUNT(*) as spike_count FROM kpi_cycle_time_data WHERE cycle_time > (SELECT AVG(cycle_time) + STDDEV(cycle_time) FROM kpi_cycle_time_data) GROUP BY furnace_no ORDER BY spike_count DESC` |
| Show cycle time distribution for furnace 888 | `SELECT MIN(cycle_time) as min_cycle_time, MAX(cycle_time) as max_cycle_time, AVG(cycle_time) as avg_cycle_time, STDDEV(cycle_time) as stddev_cycle_time, COUNT(*) as total_records FROM kpi_cycle_time_data WHERE furnace_no = 888` |
| What is the max cycle time for furnace 1? | `SELECT MAX(cycle_time) as max_cycle_time FROM kpi_cycle_time_data WHERE furnace_no = 1` |
| Cycle time statistics by furnace | `SELECT furnace_no, AVG(cycle_time) as avg_cycle_time, MIN(cycle_time) as min_cycle_time, MAX(cycle_time) as max_cycle_time, STDDEV(cycle_time) as stddev_cycle_time FROM kpi_cycle_time_data GROUP BY furnace_no ORDER BY avg_cycle_time DESC` |

### TYPE 16: Product-Based (5 examples)
| Question | SQL |
|----------|-----|
| What is the average cycle time for product M004? | `SELECT AVG(cycle_time) as avg_cycle_time FROM kpi_cycle_time_data WHERE product_type_id = 'M004'` |
| Which product_type_id has the highest cycle time? | `SELECT product_type_id, AVG(cycle_time) as avg_cycle_time FROM kpi_cycle_time_data GROUP BY product_type_id ORDER BY avg_cycle_time DESC LIMIT 1` |
| Compare cycle time for MET30 vs MET32 | `SELECT product_type_id, AVG(cycle_time) as avg_cycle_time, MIN(cycle_time) as min_cycle_time, MAX(cycle_time) as max_cycle_time FROM kpi_cycle_time_data WHERE product_type_id IN ('MET30', 'MET32') GROUP BY product_type_id ORDER BY avg_cycle_time DESC` |
| Show cycle time by product_type_id for each day | `SELECT date, product_type_id, AVG(cycle_time) as avg_cycle_time FROM kpi_cycle_time_data GROUP BY date, product_type_id ORDER BY date DESC, product_type_id` |
| Which products have cycle time above 80 on 2024-01-07? | `SELECT DISTINCT product_type_id, cycle_time FROM kpi_cycle_time_data WHERE cycle_time > 80 AND date = '2024-01-07' ORDER BY cycle_time DESC` |

### TYPE 17: Trend Analysis (5 examples)
| Question | SQL |
|----------|-----|
| Is cycle time increasing from Jan 7 to Jan 9? | `SELECT date, AVG(cycle_time) as avg_cycle_time FROM kpi_cycle_time_data WHERE date BETWEEN '2024-01-07' AND '2024-01-09' GROUP BY date ORDER BY date` |
| Show the cycle time trend per machine across days | `SELECT date, machine_id, AVG(cycle_time) as avg_cycle_time FROM kpi_cycle_time_data GROUP BY date, machine_id ORDER BY date DESC, machine_id` |
| Which machine improved the most between Jan 7 and Jan 9? | `SELECT machine_id, AVG(CASE WHEN date = '2024-01-07' THEN cycle_time END) as jan7_avg, AVG(CASE WHEN date = '2024-01-09' THEN cycle_time END) as jan9_avg, AVG(CASE WHEN date = '2024-01-07' THEN cycle_time END) - AVG(CASE WHEN date = '2024-01-09' THEN cycle_time END) as improvement FROM kpi_cycle_time_data WHERE date IN ('2024-01-07', '2024-01-09') GROUP BY machine_id ORDER BY improvement DESC LIMIT 1` |
| Which shift shows the biggest cycle time variation? | `SELECT shift_id, STDDEV(cycle_time) as cycle_time_variation, AVG(cycle_time) as avg_cycle_time FROM kpi_cycle_time_data GROUP BY shift_id ORDER BY cycle_time_variation DESC LIMIT 1` |
| Daily cycle time trend | `SELECT date, AVG(cycle_time) as avg_cycle_time, MIN(cycle_time) as min_cycle_time, MAX(cycle_time) as max_cycle_time FROM kpi_cycle_time_data GROUP BY date ORDER BY date DESC` |

### TYPE 18: Exceptions & Alerts (5 examples)
| Question | SQL |
|----------|-----|
| Show records where cycle time is greater than 90 | `SELECT date, shift_id, cycle_time, furnace_no, machine_id FROM kpi_cycle_time_data WHERE cycle_time > 90 ORDER BY cycle_time DESC LIMIT 100` |
| Which machines crossed the cycle time threshold on Jan 8? | `SELECT DISTINCT machine_id, cycle_time, shift_id FROM kpi_cycle_time_data WHERE date = '2024-01-08' AND cycle_time > 90 ORDER BY cycle_time DESC` |
| List the top 10 highest cycle time incidents | `SELECT date, shift_id, cycle_time, furnace_no, machine_id FROM kpi_cycle_time_data ORDER BY cycle_time DESC LIMIT 10` |
| Which machine had the lowest cycle time and when? | `SELECT machine_id, date, shift_id, cycle_time FROM kpi_cycle_time_data ORDER BY cycle_time ASC LIMIT 1` |
| Cycle time anomalies above normal | `SELECT date, shift_id, cycle_time, furnace_no, machine_id FROM kpi_cycle_time_data WHERE cycle_time > (SELECT AVG(cycle_time) + 2 * STDDEV(cycle_time) FROM kpi_cycle_time_data) ORDER BY cycle_time DESC` |

### TYPE 19: Chatbot Style Questions (5 examples)
| Question | SQL |
|----------|-----|
| What are the slowest machines today? | `SELECT machine_id, AVG(cycle_time) as avg_cycle_time FROM kpi_cycle_time_data WHERE date = CURRENT_DATE GROUP BY machine_id ORDER BY avg_cycle_time DESC LIMIT 5` |
| Where are we spending the most time in the process? | `SELECT machine_id, SUM(cycle_time) as total_cycle_time, AVG(cycle_time) as avg_cycle_time FROM kpi_cycle_time_data GROUP BY machine_id ORDER BY total_cycle_time DESC LIMIT 5` |
| Which area should I investigate first for long cycle times? | `SELECT machine_id, furnace_no, AVG(cycle_time) as avg_cycle_time, COUNT(*) as record_count FROM kpi_cycle_time_data WHERE cycle_time > (SELECT AVG(cycle_time) FROM kpi_cycle_time_data) GROUP BY machine_id, furnace_no ORDER BY avg_cycle_time DESC LIMIT 5` |
| What changed on Jan 8 that caused higher cycle time? | `SELECT machine_id, shift_id, AVG(cycle_time) as avg_cycle_time, COUNT(*) as record_count FROM kpi_cycle_time_data WHERE date = '2024-01-08' GROUP BY machine_id, shift_id ORDER BY avg_cycle_time DESC` |
| Show me cycle time bottlenecks | `SELECT machine_id, furnace_no, AVG(cycle_time) as avg_cycle_time, MAX(cycle_time) as max_cycle_time FROM kpi_cycle_time_data GROUP BY machine_id, furnace_no HAVING AVG(cycle_time) > (SELECT AVG(cycle_time) FROM kpi_cycle_time_data) ORDER BY avg_cycle_time DESC` |

---

## OEE Examples (TYPE 20-29)

**Table: `kpi_overall_equipment_efficiency_data`**  
**Columns:** record_id, date, shift_id, oee_percentage, furnace_no, machine_id, plant_id, product_type_id, workshop_id, material_id_id, supplier_id

### TYPE 20: Quick Lookups (5 examples)
| Question | SQL |
|----------|-----|
| What is the OEE for FURNACE on 2024-01-07? | `SELECT date, shift_id, oee_percentage, furnace_no FROM kpi_overall_equipment_efficiency_data WHERE machine_id = 'FURNACE' AND date = '2024-01-07' ORDER BY shift_id` |
| Show all OEE records for 2024-01-08 | `SELECT date, shift_id, oee_percentage, furnace_no, machine_id FROM kpi_overall_equipment_efficiency_data WHERE date = '2024-01-08' ORDER BY shift_id` |
| What was the OEE for shift 12 on 2024-01-09? | `SELECT date, shift_id, oee_percentage, furnace_no, machine_id FROM kpi_overall_equipment_efficiency_data WHERE shift_id = '12' AND date = '2024-01-09'` |
| List OEE for machine CAST_BAY | `SELECT date, shift_id, oee_percentage, furnace_no FROM kpi_overall_equipment_efficiency_data WHERE machine_id = 'CAST_BAY' ORDER BY date DESC LIMIT 100` |
| Show OEE for furnace 888 on 2024-01-07 | `SELECT date, shift_id, oee_percentage, machine_id FROM kpi_overall_equipment_efficiency_data WHERE furnace_no = 888 AND date = '2024-01-07' ORDER BY shift_id` |

### TYPE 21-29: Aggregations, Shift Analysis, Machine Performance, Furnace Comparisons, Product & Material, Supplier & Workshop, Trend Analysis, Exceptions & Alerts, Chatbot Style
*(46 additional examples following the same pattern as Cycle Time)*

---

## KPI Tables (TYPE 30-47)

### TYPE 30: Defect Rate (10 examples)
**Table: `kpi_defect_rate_data`** | **Value Column: `defect_rate`**

| Question | SQL |
|----------|-----|
| What is the average defect rate? | `SELECT AVG(defect_rate) as avg_defect_rate FROM kpi_defect_rate_data` |
| Show defect rate for furnace 1 | `SELECT date, shift_id, defect_rate FROM kpi_defect_rate_data WHERE furnace_no = 1 ORDER BY date DESC LIMIT 100` |
| Which furnace has highest defect rate? | `SELECT furnace_no, AVG(defect_rate) as avg_defect_rate FROM kpi_defect_rate_data GROUP BY furnace_no ORDER BY avg_defect_rate DESC LIMIT 1` |
| Defect rate by shift | `SELECT shift_id, AVG(defect_rate) as avg_defect_rate FROM kpi_defect_rate_data GROUP BY shift_id ORDER BY avg_defect_rate DESC` |
| Show defect rate trend last 30 days | `SELECT date, AVG(defect_rate) as avg_defect_rate FROM kpi_defect_rate_data WHERE date >= CURRENT_DATE - INTERVAL '30 days' GROUP BY date ORDER BY date DESC` |
| Which products have high defect rates? | `SELECT product_type_id, AVG(defect_rate) as avg_defect_rate FROM kpi_defect_rate_data GROUP BY product_type_id ORDER BY avg_defect_rate DESC LIMIT 5` |
| Defect rate above 5 percent | `SELECT date, shift_id, furnace_no, defect_rate FROM kpi_defect_rate_data WHERE defect_rate > 5 ORDER BY defect_rate DESC LIMIT 100` |
| Compare defect rate between shifts 4 and 12 | `SELECT shift_id, AVG(defect_rate) as avg_defect_rate FROM kpi_defect_rate_data WHERE shift_id IN ('4', '12') GROUP BY shift_id` |
| Quality issues by machine | `SELECT machine_id, AVG(defect_rate) as avg_defect_rate FROM kpi_defect_rate_data GROUP BY machine_id ORDER BY avg_defect_rate DESC` |
| Defect rate statistics | `SELECT MIN(defect_rate) as min_defect, MAX(defect_rate) as max_defect, AVG(defect_rate) as avg_defect, STDDEV(defect_rate) as stddev_defect FROM kpi_defect_rate_data` |

### TYPE 31: Energy Efficiency (10 examples)
**Table: `kpi_energy_efficiency_data`** | **Value Column: `energy_efficiency`**

| Question | SQL |
|----------|-----|
| What is the average energy efficiency? | `SELECT AVG(energy_efficiency) as avg_energy_efficiency FROM kpi_energy_efficiency_data` |
| Energy efficiency for furnace 1 | `SELECT date, shift_id, energy_efficiency FROM kpi_energy_efficiency_data WHERE furnace_no = 1 ORDER BY date DESC LIMIT 100` |
| Which furnace is most energy efficient? | `SELECT furnace_no, AVG(energy_efficiency) as avg_efficiency FROM kpi_energy_efficiency_data GROUP BY furnace_no ORDER BY avg_efficiency ASC LIMIT 1` |
| Energy efficiency by shift | `SELECT shift_id, AVG(energy_efficiency) as avg_efficiency FROM kpi_energy_efficiency_data GROUP BY shift_id ORDER BY avg_efficiency` |
| Show energy efficiency trend | `SELECT date, AVG(energy_efficiency) as avg_efficiency FROM kpi_energy_efficiency_data GROUP BY date ORDER BY date DESC LIMIT 30` |
| Compare energy efficiency between furnaces | `SELECT furnace_no, AVG(energy_efficiency) as avg_efficiency, MIN(energy_efficiency) as min_eff, MAX(energy_efficiency) as max_eff FROM kpi_energy_efficiency_data GROUP BY furnace_no ORDER BY avg_efficiency` |
| Which machines have poor energy efficiency? | `SELECT machine_id, AVG(energy_efficiency) as avg_efficiency FROM kpi_energy_efficiency_data GROUP BY machine_id ORDER BY avg_efficiency DESC LIMIT 5` |
| Energy efficiency by product type | `SELECT product_type_id, AVG(energy_efficiency) as avg_efficiency FROM kpi_energy_efficiency_data GROUP BY product_type_id ORDER BY avg_efficiency` |
| Energy efficiency above threshold | `SELECT date, furnace_no, energy_efficiency FROM kpi_energy_efficiency_data WHERE energy_efficiency > 500 ORDER BY energy_efficiency DESC LIMIT 100` |
| kWh per ton statistics | `SELECT MIN(energy_efficiency) as min_kwh, MAX(energy_efficiency) as max_kwh, AVG(energy_efficiency) as avg_kwh FROM kpi_energy_efficiency_data` |

### TYPE 32: Energy Used (10 examples)
**Table: `kpi_energy_used_data`** | **Value Column: `energy_used`** | **Aggregation: SUM**

| Question | SQL |
|----------|-----|
| What is the total energy used? | `SELECT SUM(energy_used) as total_energy_used FROM kpi_energy_used_data` |
| Total energy consumption by furnace | `SELECT furnace_no, SUM(energy_used) as total_energy FROM kpi_energy_used_data GROUP BY furnace_no ORDER BY total_energy DESC` |
| Energy used today | `SELECT furnace_no, SUM(energy_used) as total_energy FROM kpi_energy_used_data WHERE date = CURRENT_DATE GROUP BY furnace_no` |
| Daily energy consumption | `SELECT date, SUM(energy_used) as daily_energy FROM kpi_energy_used_data GROUP BY date ORDER BY date DESC LIMIT 30` |
| Energy used by shift | `SELECT shift_id, SUM(energy_used) as total_energy FROM kpi_energy_used_data GROUP BY shift_id ORDER BY total_energy DESC` |
| Monthly energy consumption | `SELECT DATE_TRUNC('month', date)::DATE as month, SUM(energy_used) as monthly_energy FROM kpi_energy_used_data GROUP BY DATE_TRUNC('month', date) ORDER BY month DESC` |
| Which machine uses most energy? | `SELECT machine_id, SUM(energy_used) as total_energy FROM kpi_energy_used_data GROUP BY machine_id ORDER BY total_energy DESC LIMIT 1` |
| Energy consumption last 7 days | `SELECT date, SUM(energy_used) as daily_total FROM kpi_energy_used_data WHERE date >= CURRENT_DATE - INTERVAL '7 days' GROUP BY date ORDER BY date` |
| Compare energy used between furnaces | `SELECT furnace_no, SUM(energy_used) as total, AVG(energy_used) as avg_per_record FROM kpi_energy_used_data GROUP BY furnace_no ORDER BY total DESC` |
| High energy consumption events | `SELECT date, shift_id, furnace_no, energy_used FROM kpi_energy_used_data WHERE energy_used > (SELECT AVG(energy_used) + STDDEV(energy_used) FROM kpi_energy_used_data) ORDER BY energy_used DESC LIMIT 50` |

### TYPE 33: Downtime (10 examples)
**Table: `kpi_downtime_data`** | **Value Column: `downtime_hours`** | **Aggregation: SUM**

| Question | SQL |
|----------|-----|
| What is the total downtime? | `SELECT SUM(downtime_hours) as total_downtime FROM kpi_downtime_data` |
| Total downtime by furnace | `SELECT furnace_no, SUM(downtime_hours) as total_downtime FROM kpi_downtime_data GROUP BY furnace_no ORDER BY total_downtime DESC` |
| Downtime today | `SELECT furnace_no, SUM(downtime_hours) as downtime FROM kpi_downtime_data WHERE date = CURRENT_DATE GROUP BY furnace_no` |
| Daily downtime trend | `SELECT date, SUM(downtime_hours) as daily_downtime FROM kpi_downtime_data GROUP BY date ORDER BY date DESC LIMIT 30` |
| Downtime by shift | `SELECT shift_id, SUM(downtime_hours) as total_downtime FROM kpi_downtime_data GROUP BY shift_id ORDER BY total_downtime DESC` |
| Which machine has most downtime? | `SELECT machine_id, SUM(downtime_hours) as total_downtime FROM kpi_downtime_data GROUP BY machine_id ORDER BY total_downtime DESC LIMIT 1` |
| Downtime last week | `SELECT date, furnace_no, SUM(downtime_hours) as downtime FROM kpi_downtime_data WHERE date >= CURRENT_DATE - INTERVAL '7 days' GROUP BY date, furnace_no ORDER BY date DESC` |
| Average downtime per day | `SELECT date, AVG(downtime_hours) as avg_downtime FROM kpi_downtime_data GROUP BY date ORDER BY date DESC` |
| Furnaces with high downtime | `SELECT furnace_no, SUM(downtime_hours) as total_downtime FROM kpi_downtime_data GROUP BY furnace_no HAVING SUM(downtime_hours) > 10 ORDER BY total_downtime DESC` |
| Compare downtime across workshops | `SELECT workshop_id, SUM(downtime_hours) as total_downtime FROM kpi_downtime_data GROUP BY workshop_id ORDER BY total_downtime DESC` |

### TYPE 34-47: MTBF, MTTR, MTBS, Yield, First Pass Yield, Rework Rate, Capacity Utilization, Quantity Produced, Output Rate, Production Efficiency, On-Time Delivery, Maintenance Compliance, Planned Maintenance, Safety Incidents
*(~100 additional examples following similar patterns)*

---

## Core Process Tables (TYPE 48-50)

### TYPE 48: Tap Production (10 examples)
**Table: `core_process_tap_production`**

| Question | SQL |
|----------|-----|
| What is the total cast weight? | `SELECT SUM(cast_weight) as total_cast_weight FROM core_process_tap_production` |
| Cast weight by plant | `SELECT plant_id, SUM(cast_weight) as total_cast_weight FROM core_process_tap_production GROUP BY plant_id ORDER BY total_cast_weight DESC` |
| Daily tap production | `SELECT DATE_TRUNC('day', tap_production_datetime)::DATE as production_date, COUNT(DISTINCT tap_id) as tap_count, SUM(cast_weight) as total_weight FROM core_process_tap_production GROUP BY DATE_TRUNC('day', tap_production_datetime) ORDER BY production_date DESC LIMIT 30` |
| Recent tap production | `SELECT tap_id, cast_weight, liquid_weight, energy, tap_production_datetime FROM core_process_tap_production ORDER BY tap_production_datetime DESC LIMIT 20` |
| Average energy per tap | `SELECT AVG(energy) as avg_energy FROM core_process_tap_production` |
| Tap production energy efficiency | `SELECT AVG(energy_efficiency) as avg_energy_efficiency FROM core_process_tap_production` |
| Total liquid weight produced | `SELECT SUM(liquid_weight) as total_liquid_weight FROM core_process_tap_production` |
| Slag weight by plant | `SELECT plant_id, SUM(casting_slag_weight) as total_slag FROM core_process_tap_production GROUP BY plant_id ORDER BY total_slag DESC` |
| Recycling metal statistics | `SELECT SUM(recycling_metal_weight) as total_recycled FROM core_process_tap_production` |
| Ladle weight analysis | `SELECT AVG(ladle_weight_before_tapping) as avg_before, AVG(ladle_weight_after_tapping) as avg_after FROM core_process_tap_production` |

### TYPE 49: Tap Process (8 examples)
**Table: `core_process_tap_process`**

| Question | SQL |
|----------|-----|
| How many taps today? | `SELECT COUNT(DISTINCT tap_id) as tap_count FROM core_process_tap_process WHERE DATE(tap_datetime) = CURRENT_DATE` |
| Taps by furnace | `SELECT furnace_no, COUNT(DISTINCT tap_id) as tap_count FROM core_process_tap_process GROUP BY furnace_no ORDER BY tap_count DESC` |
| Tap status summary | `SELECT tap_status, COUNT(*) as count FROM core_process_tap_process GROUP BY tap_status ORDER BY count DESC` |
| Recent tap processes | `SELECT tap_id, furnace_no, tap_datetime, tap_status, tap_progress FROM core_process_tap_process ORDER BY tap_datetime DESC LIMIT 20` |
| Tap progress distribution | `SELECT tap_progress, COUNT(*) as count FROM core_process_tap_process GROUP BY tap_progress ORDER BY count DESC` |
| Taps by tap hole | `SELECT tap_hole_id, COUNT(*) as tap_count FROM core_process_tap_process GROUP BY tap_hole_id ORDER BY tap_count DESC` |
| Target materials used | `SELECT target_material, COUNT(*) as count FROM core_process_tap_process GROUP BY target_material ORDER BY count DESC` |
| Daily tap count trend | `SELECT DATE_TRUNC('day', tap_datetime)::DATE as tap_date, COUNT(DISTINCT tap_id) as tap_count FROM core_process_tap_process GROUP BY DATE_TRUNC('day', tap_datetime) ORDER BY tap_date DESC LIMIT 30` |

### TYPE 50: Tap Grading (6 examples)
**Table: `core_process_tap_grading`**

| Question | SQL |
|----------|-----|
| Show all allocated grades | `SELECT allocated_grade, COUNT(*) as count FROM core_process_tap_grading GROUP BY allocated_grade ORDER BY count DESC` |
| Grade quality distribution | `SELECT allocated_grade_quality, COUNT(*) as count FROM core_process_tap_grading GROUP BY allocated_grade_quality ORDER BY count DESC` |
| Grade priority breakdown | `SELECT allocated_grade_priority, COUNT(*) as count FROM core_process_tap_grading GROUP BY allocated_grade_priority ORDER BY count DESC` |
| Grading by cast process | `SELECT cast_process_code, COUNT(*) as count FROM core_process_tap_grading GROUP BY cast_process_code ORDER BY count DESC` |
| Bulk pile allocations | `SELECT allocated_grade_bulk_pile, COUNT(*) as count FROM core_process_tap_grading GROUP BY allocated_grade_bulk_pile ORDER BY count DESC` |
| Recent grading records | `SELECT tap_id, allocated_grade, allocated_grade_quality, allocated_grade_priority FROM core_process_tap_grading ORDER BY id DESC LIMIT 50` |

---

## Log & Config Tables (TYPE 51-52)

### TYPE 51: Downtime Events Log (10 examples)
**Table: `log_book_furnace_down_time_event`**

| Question | SQL |
|----------|-----|
| Total downtime from events | `SELECT SUM(downtime_hours) as total_downtime FROM log_book_furnace_down_time_event` |
| Downtime events by furnace | `SELECT furnace_no, SUM(downtime_hours) as total_downtime, COUNT(*) as event_count FROM log_book_furnace_down_time_event GROUP BY furnace_no ORDER BY total_downtime DESC` |
| Recent downtime events | `SELECT furnace_no, obs_start_dt, obs_end_dt, downtime_hours FROM log_book_furnace_down_time_event ORDER BY obs_start_dt DESC LIMIT 20` |
| Downtime by reason | `SELECT reason_id, SUM(downtime_hours) as total_downtime, COUNT(*) as event_count FROM log_book_furnace_down_time_event GROUP BY reason_id ORDER BY total_downtime DESC` |
| Downtime by type | `SELECT downtime_type_id, SUM(downtime_hours) as total_downtime, COUNT(*) as event_count FROM log_book_furnace_down_time_event GROUP BY downtime_type_id ORDER BY total_downtime DESC` |
| Long downtime events | `SELECT furnace_no, obs_start_dt, obs_end_dt, downtime_hours FROM log_book_furnace_down_time_event WHERE downtime_hours > 4 ORDER BY downtime_hours DESC LIMIT 50` |
| Downtime events last 7 days | `SELECT furnace_no, obs_start_dt, downtime_hours FROM log_book_furnace_down_time_event WHERE obs_start_dt >= CURRENT_DATE - INTERVAL '7 days' ORDER BY obs_start_dt DESC` |
| Daily downtime event summary | `SELECT DATE_TRUNC('day', obs_start_dt)::DATE as event_date, SUM(downtime_hours) as total_downtime, COUNT(*) as event_count FROM log_book_furnace_down_time_event GROUP BY DATE_TRUNC('day', obs_start_dt) ORDER BY event_date DESC LIMIT 30` |
| Downtime by equipment | `SELECT equipment_id, SUM(downtime_hours) as total_downtime, COUNT(*) as event_count FROM log_book_furnace_down_time_event GROUP BY equipment_id ORDER BY total_downtime DESC` |
| Downtime events by plant | `SELECT plant_id, SUM(downtime_hours) as total_downtime, COUNT(*) as event_count FROM log_book_furnace_down_time_event GROUP BY plant_id ORDER BY total_downtime DESC` |

### TYPE 52: Furnace Config & Master Data (8 examples)
**Tables: `furnace_furnaceconfig`, `furnace_config_parameters`, `plant_plant`, `log_book_reasons`, `log_book_downtime_type_master`**

| Question | SQL |
|----------|-----|
| List all furnaces | `SELECT furnace_no, furnace_description, is_active FROM furnace_furnaceconfig ORDER BY furnace_no` |
| Active furnaces | `SELECT furnace_no, furnace_description FROM furnace_furnaceconfig WHERE is_active = true ORDER BY furnace_no` |
| Furnaces by workshop | `SELECT workshop_id, COUNT(*) as furnace_count FROM furnace_furnaceconfig GROUP BY workshop_id ORDER BY furnace_count DESC` |
| Furnace configuration parameters | `SELECT furnace_config_id, crucible_diameter, crucible_depth, target_energy_efficiency FROM furnace_config_parameters ORDER BY furnace_config_id` |
| Show all plants | `SELECT id, plant_code, plant_name FROM plant_plant ORDER BY id` |
| Downtime reasons list | `SELECT id, reason_name, reason_code FROM log_book_reasons ORDER BY id` |
| Downtime types list | `SELECT id, name, down_time_type_code FROM log_book_downtime_type_master ORDER BY id` |
| Furnace energy targets | `SELECT furnace_config_id, target_energy_efficiency, target_availability, target_furnace_load FROM furnace_config_parameters ORDER BY furnace_config_id` |

---

## Summary Statistics

| Category | Tables Covered | Examples |
|----------|---------------|----------|
| Original Examples (TYPE 1-10) | Multiple | ~75 |
| Cycle Time (TYPE 11-19) | 1 | 46 |
| OEE (TYPE 20-29) | 1 | 51 |
| KPI Tables (TYPE 30-47) | 18 | ~160 |
| Core Process (TYPE 48-50) | 3 | 24 |
| Log & Config (TYPE 51-52) | 5 | 18 |
| **TOTAL** | **29** | **~365+** |

---

## Notes

1. **VARCHAR Columns**: `shift_id`, `machine_id`, `product_type_id` are VARCHAR - use quotes: `WHERE shift_id = '4'`
2. **INTEGER Columns**: `furnace_no`, `plant_id`, `record_id` are INTEGER - no quotes: `WHERE furnace_no = 1`
3. **Date Filtering**: Use `CURRENT_DATE - INTERVAL 'X days'` for relative dates
4. **Aggregation Rules**:
   - Percentages (OEE, yield, defect_rate) → `AVG()`
   - Quantities (energy_used, downtime_hours, quantity_produced) → `SUM()`
   - Counts → `COUNT()`
