
## Summary
- **Total Tests**: 372
- **Strict Matches**: 84
- **Functional Matches (Benign)**: 8 (Matches after ignoring LIMIT/ORDER BY)
- **Real Failures**: 280

**True Success Rate**: 24.7%

# NLP Test Failure Analysis

### [FAIL - Mismatch] Test #11
- **Q**: What is the average yield for furnace 2
- **Expected**: `SELECT AVG(yield_percentage) FROM kpi_yield_data WHERE furnace_no = 2`
- **Actual**: `SELECT AVG(yield_percentage) FROM kpi_yield_data WHERE furnace_no = '2'`

### [FAIL - Mismatch] Test #14
- **Q**: What is the total production for furnace 1 last month
- **Expected**: `SELECT SUM(quantity_produced) as total_production FROM kpi_quantity_produced_data WHERE furnace_no = 1 AND date >= CURRENT_DATE - INTERVAL '30 days'`
- **Actual**: `SELECT SUM(cast_weight) as total_production 
FROM core_process_tap_production 
WHERE tap_production_datetime >= CURRENT_DATE - INTERVAL '30 days' 
AND furnace_no = 1`

### [FAIL - Mismatch] Test #15
- **Q**: Show production by furnace
- **Expected**: `SELECT furnace_no, SUM(quantity_produced) as total_qty FROM kpi_quantity_produced_data GROUP BY furnace_no ORDER BY total_qty DESC`
- **Actual**: `SELECT 
  f.furnace_no, 
  SUM(cp.cast_weight) as total_production
FROM 
  core_process_tap_production cp
JOIN 
  furnace_furnaceconfig f ON cp.furnace_no = f.furnace_no
GROUP BY 
  f.furnace_no
ORDER BY 
  total_production DESC`

### [FAIL - Mismatch] Test #16
- **Q**: Show production by furnace
- **Expected**: `SELECT furnace_no, SUM(quantity_produced) as total_qty FROM kpi_quantity_produced_data GROUP BY furnace_no ORDER BY total_qty DESC`
- **Actual**: `SELECT 
  f.furnace_no, 
  SUM(p.cast_weight) as total_production
FROM 
  core_process_tap_production p
JOIN 
  furnace_furnaceconfig f ON p.tap_id = f.id
GROUP BY 
  f.furnace_no
ORDER BY 
  total_production DESC`

### [FAIL - Mismatch] Test #22
- **Q**: Display downtime trend last 30 days
- **Expected**: `SELECT date, furnace_no, downtime_hours FROM kpi_downtime_data WHERE date >= CURRENT_DATE - INTERVAL '30 days' ORDER BY date DESC`
- **Actual**: `SELECT date, downtime_hours 
FROM kpi_downtime_data 
WHERE date >= CURRENT_DATE - INTERVAL '30 days' 
ORDER BY date DESC 
LIMIT 100`

### [FAIL - Mismatch] Test #23
- **Q**: Show recent defect rate data
- **Expected**: `SELECT date, shift_id, furnace_no, defect_rate FROM kpi_defect_rate_data ORDER BY date DESC LIMIT 50`
- **Actual**: `SELECT record_id, date, shift_id, defect_rate, furnace_no, machine_id, plant_id, product_type_id 
FROM kpi_defect_rate_data 
WHERE furnace_no = 1 
ORDER BY date DESC 
LIMIT 100`

### [FAIL - Mismatch] Test #24
- **Q**: Show OEE trend last week
- **Expected**: `SELECT date, furnace_no, oee_percentage FROM kpi_overall_equipment_efficiency_data WHERE date >= CURRENT_DATE - INTERVAL '7 days' ORDER BY date DESC`
- **Actual**: `SELECT date, oee_percentage 
FROM kpi_overall_equipment_efficiency_data 
WHERE date >= CURRENT_DATE - INTERVAL '7 days' 
ORDER BY date DESC 
LIMIT 100`

### [FAIL - Mismatch] Test #25
- **Q**: List all furnaces
- **Expected**: `SELECT furnace_no, furnace_description, is_active FROM furnace_furnaceconfig ORDER BY furnace_no`
- **Actual**: `SELECT furnace_no, furnace_description FROM furnace_furnaceconfig ORDER BY created_at DESC LIMIT 100`

### [FAIL - Mismatch] Test #26
- **Q**: Show downtime events for Furnace 1
- **Expected**: `SELECT obs_start_dt, obs_end_dt, downtime_hours FROM log_book_furnace_down_time_event WHERE furnace_no = 1 ORDER BY obs_start_dt DESC LIMIT 50`
- **Actual**: `SELECT id, furnace_no, obs_start_dt, obs_end_dt, downtime_hours, equipment_id, reason_id, downtime_type_id 
FROM log_book_furnace_down_time_event 
WHERE furnace_no = 1 
ORDER BY obs_start_dt DESC 
LIMIT 100`

### [FAIL - Mismatch] Test #27
- **Q**: Show recent tap production data
- **Expected**: `SELECT tap_id, cast_weight, energy, tap_production_datetime FROM core_process_tap_production ORDER BY tap_production_datetime DESC LIMIT 20`
- **Actual**: `SELECT id, tap_id, tap_production_datetime, cast_weight, liquid_weight, energy, energy_efficiency, graded_cast_weight, downgrade_quantity, ladle_number_code 
FROM core_process_tap_production 
ORDER BY tap_production_datetime DESC 
LIMIT 100`

### [FAIL - Mismatch] Test #28
- **Q**: Show yield data for last month
- **Expected**: `SELECT date, furnace_no, yield_percentage FROM kpi_yield_data WHERE date >= CURRENT_DATE - INTERVAL '30 days' ORDER BY date DESC`
- **Actual**: `SELECT record_id, date, shift_id, yield_percentage, furnace_no, machine_id, plant_id, product_type_id 
FROM kpi_yield_data 
WHERE date >= CURRENT_DATE - INTERVAL '30 days' 
ORDER BY date DESC 
LIMIT 100`

### [FAIL - Mismatch] Test #29
- **Q**: Display energy efficiency trend
- **Expected**: `SELECT date, furnace_no, energy_efficiency FROM kpi_energy_efficiency_data ORDER BY date DESC LIMIT 100`
- **Actual**: `SELECT date, energy_efficiency FROM kpi_energy_efficiency_data ORDER BY date DESC LIMIT 100`

### [FAIL - Mismatch] Test #30
- **Q**: Show MTTR data for Furnace 2
- **Expected**: `SELECT date, mttr_hours FROM kpi_mean_time_to_repair_data WHERE furnace_no = 2 ORDER BY date DESC LIMIT 100`
- **Actual**: `SELECT record_id, date, shift_id, mttr_hours, furnace_no, machine_id, plant_id, product_type_id 
FROM kpi_mean_time_to_repair_data 
WHERE furnace_no = 2 
ORDER BY date DESC 
LIMIT 100`

### [FAIL - Mismatch] Test #31
- **Q**: List recent quality issues
- **Expected**: `SELECT date, furnace_no, defect_rate FROM kpi_defect_rate_data ORDER BY date DESC LIMIT 100`
- **Actual**: `SELECT record_id, date, shift_id, defect_rate, furnace_no, machine_id, plant_id, product_type_id 
FROM kpi_defect_rate_data 
WHERE date >= CURRENT_DATE - INTERVAL '30 days' 
ORDER BY date DESC 
LIMIT 100`

### [FAIL - Mismatch] Test #36
- **Q**: Show production by shift
- **Expected**: `SELECT shift_id, SUM(quantity_produced) as total_qty FROM kpi_quantity_produced_data GROUP BY shift_id ORDER BY total_qty DESC`
- **Actual**: `SELECT shift_id, SUM(cast_weight) as total_production FROM core_process_tap_production GROUP BY shift_id ORDER BY total_production DESC`

### [FAIL - Mismatch] Test #37
- **Q**: Show production by shift
- **Expected**: `SELECT shift_id, SUM(quantity_produced) as total_qty FROM kpi_quantity_produced_data GROUP BY shift_id ORDER BY total_qty DESC`
- **Actual**: `SELECT shift_id, SUM(cast_weight) as total_production FROM core_process_tap_production GROUP BY shift_id ORDER BY total_production DESC`

### [FAIL - Mismatch] Test #40
- **Q**: Compare all furnaces by OEE
- **Expected**: `SELECT furnace_no, AVG(oee_percentage) as avg_oee, MAX(oee_percentage) as max_oee, MIN(oee_percentage) as min_oee FROM kpi_overall_equipment_efficiency_data GROUP BY furnace_no ORDER BY avg_oee DESC`
- **Actual**: `SELECT furnace_no, AVG(oee_percentage) as avg_oee FROM kpi_overall_equipment_efficiency_data GROUP BY furnace_no ORDER BY avg_oee DESC`

### [FAIL - Mismatch] Test #41
- **Q**: Show rank furnaces by defect rate
- **Expected**: `SELECT furnace_no, AVG(defect_rate) as avg_defect FROM kpi_defect_rate_data GROUP BY furnace_no ORDER BY avg_defect DESC`
- **Actual**: `SELECT furnace_no, AVG(defect_rate) as avg_defect_rate
FROM kpi_defect_rate_data
GROUP BY furnace_no
ORDER BY avg_defect_rate DESC`

### [FAIL - Mismatch] Test #44
- **Q**: Compare energy efficiency by furnace
- **Expected**: `SELECT furnace_no, AVG(energy_efficiency) as avg_efficiency FROM kpi_energy_efficiency_data GROUP BY furnace_no ORDER BY avg_efficiency`
- **Actual**: `SELECT furnace_no, AVG(energy_efficiency) as avg_energy_efficiency 
FROM kpi_energy_efficiency_data 
GROUP BY furnace_no 
ORDER BY avg_energy_efficiency DESC`

### [FAIL - Mismatch] Test #45
- **Q**: Show production efficiency by shift
- **Expected**: `SELECT shift_id, AVG(production_efficiency_percentage) as avg_efficiency FROM kpi_production_efficiency_data GROUP BY shift_id ORDER BY avg_efficiency DESC`
- **Actual**: `SELECT shift_id, production_efficiency_percentage, date 
FROM kpi_production_efficiency_data 
ORDER BY date DESC 
LIMIT 100`
- **Diagnosis**: Missing GROUP BY

### [FAIL - Mismatch] Test #48
- **Q**: Show Average OEE by furnace with names
- **Expected**: `SELECT f.furnace_no, f.furnace_description, AVG(k.oee_percentage) as avg_oee FROM kpi_overall_equipment_efficiency_data k JOIN furnace_furnaceconfig f ON k.furnace_no = f.furnace_no GROUP BY f.furnace_no, f.furnace_description ORDER BY avg_oee DESC`
- **Actual**: `SELECT p.plant_name, f.furnace_no, AVG(k.oee_percentage) as avg_oee 
FROM kpi_overall_equipment_efficiency_data k
JOIN furnace_furnaceconfig f ON k.furnace_no = f.furnace_no
JOIN plant_plant p ON k.plant_id = p.plant_id
GROUP BY p.plant_name, f.furnace_no
ORDER BY avg_oee DESC`

### [FAIL - Mismatch] Test #49
- **Q**: Show tap production by tap status
- **Expected**: `SELECT t.tap_status, COUNT(t.tap_id) as tap_count, SUM(tp.cast_weight) as total_weight FROM core_process_tap_process t JOIN core_process_tap_production tp ON t.tap_id = tp.tap_id GROUP BY t.tap_status ORDER BY tap_count DESC`
- **Actual**: `SELECT tap_status, SUM(cast_weight) as total_cast_weight 
FROM core_process_tap_process 
JOIN core_process_tap_production ON core_process_tap_process.tap_id = core_process_tap_production.tap_id 
GROUP BY tap_status 
ORDER BY total_cast_weight DESC`

### [FAIL - Mismatch] Test #50
- **Q**: Show downtime events with reasons for furnace 1
- **Expected**: `SELECT d.obs_start_dt, d.obs_end_dt, d.downtime_hours, r.reason_name FROM log_book_furnace_down_time_event d LEFT JOIN log_book_reasons r ON d.reason_id = r.id WHERE d.furnace_no = 1 ORDER BY d.obs_start_dt DESC LIMIT 50`
- **Actual**: `SELECT id, furnace_no, obs_start_dt, obs_end_dt, downtime_hours, equipment_id, reason_id, downtime_type_id 
FROM log_book_furnace_down_time_event 
WHERE furnace_no = 1 
ORDER BY obs_start_dt DESC 
LIMIT 100`

### [FAIL - Mismatch] Test #51
- **Q**: Show oee and yield by furnace last month
- **Expected**: `SELECT f.furnace_no, f.furnace_description, AVG(k1.oee_percentage) as avg_oee, AVG(k2.yield_percentage) as avg_yield FROM kpi_overall_equipment_efficiency_data k1 JOIN kpi_yield_data k2 ON k1.furnace_no = k2.furnace_no AND k1.date = k2.date JOIN furnace_furnaceconfig f ON k1.furnace_no = f.furnace_no WHERE k1.date >= CURRENT_DATE - INTERVAL '30 days' GROUP BY f.furnace_no, f.furnace_description ORDER BY avg_oee DESC`
- **Actual**: `SELECT 
  f.furnace_no, 
  AVG(k.oee_percentage) as avg_oee, 
  AVG(y.yield_percentage) as avg_yield
FROM 
  kpi_overall_equipment_efficiency_data k
JOIN 
  kpi_yield_data y ON k.furnace_no = y.furnace_no AND k.date = y.date
JOIN 
  furnace_furnaceconfig f ON k.furnace_no = f.furnace_no
WHERE 
  k.date >= CURRENT_DATE - INTERVAL '30 days'
GROUP BY 
  f.furnace_no
ORDER BY 
  avg_oee DESC`

### [FAIL - Mismatch] Test #52
- **Q**: Show production with furnace details
- **Expected**: `SELECT f.furnace_no, f.furnace_description, SUM(tp.cast_weight) as total_weight, AVG(tp.energy_efficiency) as avg_efficiency FROM core_process_tap_production tp JOIN core_process_tap_process t ON tp.tap_id = t.tap_id JOIN furnace_furnaceconfig f ON t.furnace_no = f.furnace_no GROUP BY f.furnace_no, f.furnace_description ORDER BY total_weight DESC`
- **Actual**: `SELECT 
  p.furnace_no, 
  p.furnace_description, 
  t.tap_production_datetime, 
  t.cast_weight, 
  t.liquid_weight, 
  t.energy, 
  t.energy_efficiency, 
  t.graded_cast_weight, 
  t.downgrade_quantity, 
  t.ladle_number_code
FROM 
  core_process_tap_production t
JOIN 
  furnace_furnaceconfig p ON t.furnace_no = p.furnace_no
ORDER BY 
  t.tap_production_datetime DESC
LIMIT 100`
- **Diagnosis**: Missing GROUP BY

### [FAIL - Mismatch] Test #53
- **Q**: Show oee by plant
- **Expected**: `SELECT p.plant_name, AVG(k.oee_percentage) as avg_oee FROM kpi_overall_equipment_efficiency_data k JOIN plant_plant p ON k.plant_id = p.id GROUP BY p.id, p.plant_name ORDER BY avg_oee DESC`
- **Actual**: `SELECT p.plant_name, AVG(k.oee_percentage) as avg_oee 
FROM kpi_overall_equipment_efficiency_data k 
JOIN plant_plant p ON k.plant_id = p.id 
GROUP BY p.plant_name 
ORDER BY avg_oee DESC`

### [FAIL - Mismatch] Test #54
- **Q**: Show energy usage by furnace with config
- **Expected**: `SELECT f.furnace_no, f.furnace_description, SUM(k.energy_used) as total_energy FROM kpi_energy_used_data k JOIN furnace_furnaceconfig f ON k.furnace_no = f.furnace_no GROUP BY f.furnace_no, f.furnace_description ORDER BY total_energy DESC`
- **Actual**: `SELECT 
  f.furnace_no, 
  f.furnace_description, 
  fc.crucible_diameter, 
  fc.crucible_depth, 
  fc.energy_losses, 
  fc.joule_losses_coefficient, 
  k.energy_used
FROM 
  kpi_energy_used_data k
JOIN 
  furnace_furnaceconfig f ON k.furnace_no = f.furnace_no
JOIN 
  furnace_config_parameters fc ON f.id = fc.furnace_config_id
ORDER BY 
  k.date DESC
LIMIT 100`
- **Diagnosis**: Missing GROUP BY

### [FAIL - Mismatch] Test #55
- **Q**: Show tap grading with tap status
- **Expected**: `SELECT t.tap_status, COUNT(DISTINCT g.tap_id) as graded_taps FROM core_process_tap_grading g JOIN core_process_tap_process t ON g.tap_id = t.tap_id GROUP BY t.tap_status`
- **Actual**: `SELECT tap_id, tap_status, tap_hole_id, target_material, tap_progress 
FROM core_process_tap_process 
ORDER BY tap_datetime DESC 
LIMIT 100`
- **Diagnosis**: Missing GROUP BY

### [FAIL - Mismatch] Test #57
- **Q**: Show week over week downtime comparison
- **Expected**: `SELECT CASE WHEN date >= CURRENT_DATE - INTERVAL '7 days' THEN 'Current Week' ELSE 'Previous Week' END as period, SUM(downtime_hours) as total_downtime FROM kpi_downtime_data WHERE date >= CURRENT_DATE - INTERVAL '14 days' GROUP BY period`
- **Actual**: `SELECT 
    EXTRACT(WEEK FROM date) AS week_number,
    SUM(downtime_hours) AS total_downtime
FROM 
    kpi_downtime_data
WHERE 
    date >= CURRENT_DATE - INTERVAL '8 weeks'
GROUP BY 
    EXTRACT(WEEK FROM date)
ORDER BY 
    week_number DESC`

### [FAIL - Mismatch] Test #58
- **Q**: Compare last 2 months of OEE
- **Expected**: `SELECT DATE_TRUNC('month', date)::DATE as month, AVG(oee_percentage) as avg_oee FROM kpi_overall_equipment_efficiency_data WHERE date >= CURRENT_DATE - INTERVAL '60 days' GROUP BY DATE_TRUNC('month', date) ORDER BY month DESC`
- **Actual**: `SELECT AVG(oee_percentage) as avg_oee 
FROM kpi_overall_equipment_efficiency_data 
WHERE date >= CURRENT_DATE - INTERVAL '60 days' 
GROUP BY EXTRACT(MONTH FROM date) 
ORDER BY avg_oee DESC`

### [FAIL - Mismatch] Test #59
- **Q**: Show monthly energy trend
- **Expected**: `SELECT DATE_TRUNC('month', date)::DATE as month, SUM(energy_used) as monthly_total FROM kpi_energy_used_data GROUP BY DATE_TRUNC('month', date) ORDER BY month DESC`
- **Actual**: `SELECT 
    EXTRACT(MONTH FROM date) AS month, 
    SUM(energy_used) AS total_energy 
FROM 
    kpi_energy_used_data 
GROUP BY 
    EXTRACT(MONTH FROM date) 
ORDER BY 
    month DESC`

### [FAIL - Mismatch] Test #60
- **Q**: Show this month vs last month downtime
- **Expected**: `SELECT CASE WHEN date >= CURRENT_DATE - INTERVAL '30 days' THEN 'This Month' ELSE 'Last Month' END as period, SUM(downtime_hours) as total FROM kpi_downtime_data WHERE date >= CURRENT_DATE - INTERVAL '60 days' GROUP BY period`
- **Actual**: `SELECT 
    EXTRACT(MONTH FROM date) AS month,
    SUM(downtime_hours) AS total_downtime
FROM 
    kpi_downtime_data
WHERE 
    EXTRACT(YEAR FROM date) = EXTRACT(YEAR FROM CURRENT_DATE)
GROUP BY 
    EXTRACT(MONTH FROM date)
ORDER BY 
    month`

### [FAIL - Mismatch] Test #61
- **Q**: Show year to date production
- **Expected**: `SELECT DATE_TRUNC('month', tap_production_datetime)::DATE as month, SUM(cast_weight) as monthly_production FROM core_process_tap_production WHERE EXTRACT(YEAR FROM tap_production_datetime) = EXTRACT(YEAR FROM CURRENT_DATE) GROUP BY DATE_TRUNC('month', tap_production_datetime) ORDER BY month DESC`
- **Actual**: `SELECT tap_id, tap_production_datetime, cast_weight, liquid_weight, energy, energy_efficiency, graded_cast_weight, downgrade_quantity, ladle_number_code 
FROM core_process_tap_production 
WHERE tap_production_datetime >= CURRENT_DATE - INTERVAL '1 year' 
ORDER BY tap_production_datetime DESC 
LIMIT 100`
- **Diagnosis**: Missing GROUP BY

### [FAIL - Mismatch] Test #62
- **Q**: Show OEE records above 90%
- **Expected**: `SELECT date, furnace_no, shift_id, oee_percentage FROM kpi_overall_equipment_efficiency_data WHERE oee_percentage > 90 ORDER BY oee_percentage DESC LIMIT 100`
- **Actual**: `SELECT record_id, date, shift_id, oee_percentage, furnace_no, machine_id, plant_id, product_type_id 
FROM kpi_overall_equipment_efficiency_data 
WHERE oee_percentage > '90' 
ORDER BY date DESC 
LIMIT 100`

### [FAIL - Mismatch] Test #63
- **Q**: Show downtime events exceeding 8 hours
- **Expected**: `SELECT obs_start_dt, furnace_no, downtime_hours FROM log_book_furnace_down_time_event WHERE downtime_hours > 8 ORDER BY downtime_hours DESC`
- **Actual**: `SELECT * FROM log_book_furnace_down_time_event WHERE downtime_hours > 8 ORDER BY obs_start_dt DESC LIMIT 100`

### [FAIL - Mismatch] Test #64
- **Q**: Show furnaces with low efficiency below 80%
- **Expected**: `SELECT furnace_no, AVG(oee_percentage) as avg_oee FROM kpi_overall_equipment_efficiency_data GROUP BY furnace_no HAVING AVG(oee_percentage) < 80`
- **Actual**: `SELECT furnace_no, AVG(energy_efficiency) as avg_efficiency 
FROM kpi_energy_efficiency_data 
WHERE energy_efficiency < 80 
GROUP BY furnace_no 
ORDER BY avg_efficiency DESC`

### [FAIL - Mismatch] Test #65
- **Q**: Show defect rate above 5 percent
- **Expected**: `SELECT date, shift_id, furnace_no, defect_rate FROM kpi_defect_rate_data WHERE defect_rate > 5 ORDER BY defect_rate DESC LIMIT 100`
- **Actual**: `SELECT record_id, date, shift_id, defect_rate, furnace_no, machine_id, plant_id, product_type_id 
FROM kpi_defect_rate_data 
WHERE defect_rate > '5' 
ORDER BY date DESC 
LIMIT 100`

### [FAIL - Mismatch] Test #66
- **Q**: Show energy usage above average
- **Expected**: `SELECT furnace_no, SUM(energy_used) as total_energy FROM kpi_energy_used_data GROUP BY furnace_no HAVING SUM(energy_used) > (SELECT AVG(energy_used) FROM kpi_energy_used_data)`
- **Actual**: `SELECT furnace_no, machine_id, AVG(energy_used) as avg_energy_used 
FROM kpi_energy_used_data 
GROUP BY furnace_no, machine_id 
HAVING AVG(energy_used) > (SELECT AVG(energy_used) FROM kpi_energy_used_data) 
ORDER BY avg_energy_used DESC`

### [FAIL - Mismatch] Test #68
- **Q**: Show top 5 furnaces by production
- **Expected**: `SELECT furnace_no, SUM(cast_weight) as total_production FROM core_process_tap_production GROUP BY furnace_no ORDER BY total_production DESC LIMIT 5`
- **Actual**: `SELECT furnace_no, SUM(quantity_produced) as total_qty 
FROM kpi_quantity_produced_data 
GROUP BY furnace_no 
ORDER BY total_qty DESC 
LIMIT 5`

### [FAIL - Mismatch] Test #73
- **Q**: What is the best shift by efficiency
- **Expected**: `SELECT shift_id, AVG(production_efficiency_percentage) as avg_efficiency FROM kpi_production_efficiency_data GROUP BY shift_id ORDER BY avg_efficiency DESC LIMIT 1`
- **Actual**: `SELECT shift_id, AVG(oee_percentage) as avg_oee FROM kpi_overall_equipment_efficiency_data GROUP BY shift_id ORDER BY avg_oee DESC`

### [FAIL - Mismatch] Test #74
- **Q**: What is the most reliable furnace
- **Expected**: `SELECT furnace_no, AVG(mtbf_hours) as avg_mtbf FROM kpi_mean_time_between_failures_data GROUP BY furnace_no ORDER BY avg_mtbf DESC LIMIT 1`
- **Actual**: `SELECT furnace_no, COUNT(*) as reliability_count FROM furnace_furnaceconfig GROUP BY furnace_no ORDER BY reliability_count DESC LIMIT 1`

### [FAIL - Mismatch] Test #75
- **Q**: Show oee statistics
- **Expected**: `SELECT MIN(oee_percentage) as min_oee, MAX(oee_percentage) as max_oee, AVG(oee_percentage) as avg_oee, STDDEV(oee_percentage) as stddev_oee FROM kpi_overall_equipment_efficiency_data`
- **Actual**: `SELECT record_id, date, shift_id, oee_percentage, furnace_no, machine_id, plant_id, product_type_id 
FROM kpi_overall_equipment_efficiency_data 
WHERE furnace_no = 1 
ORDER BY date DESC 
LIMIT 100`

### [FAIL - Mismatch] Test #76
- **Q**: Show downtime statistics by furnace
- **Expected**: `SELECT furnace_no, MIN(downtime_hours) as min, MAX(downtime_hours) as max, AVG(downtime_hours) as avg, SUM(downtime_hours) as total, COUNT(*) as count FROM kpi_downtime_data GROUP BY furnace_no`
- **Actual**: `SELECT 
    furnace_no, 
    SUM(downtime_hours) as total_downtime, 
    AVG(downtime_hours) as avg_downtime, 
    COUNT(record_id) as num_records
FROM 
    kpi_downtime_data
GROUP BY 
    furnace_no
ORDER BY 
    total_downtime DESC`

### [FAIL - Mismatch] Test #77
- **Q**: Show energy efficiency range
- **Expected**: `SELECT MIN(energy_efficiency) as min_eff, MAX(energy_efficiency) as max_eff, AVG(energy_efficiency) as avg_eff FROM kpi_energy_efficiency_data`
- **Actual**: `SELECT MIN(energy_efficiency) AS min_energy_efficiency, 
       MAX(energy_efficiency) AS max_energy_efficiency 
FROM kpi_energy_efficiency_data`

### [FAIL - Mismatch] Test #78
- **Q**: Show yield statistics by furnace
- **Expected**: `SELECT furnace_no, AVG(yield_percentage) as avg_yield, STDDEV(yield_percentage) as stddev_yield, MIN(yield_percentage) as min_yield, MAX(yield_percentage) as max_yield FROM kpi_yield_data GROUP BY furnace_no`
- **Actual**: `SELECT 
  furnace_no, 
  AVG(yield_percentage) as avg_yield, 
  SUM(yield_percentage) as total_yield, 
  COUNT(*) as num_records
FROM 
  kpi_yield_data
GROUP BY 
  furnace_no
ORDER BY 
  avg_yield DESC`

### [FAIL - Mismatch] Test #79
- **Q**: Show production quantity statistics
- **Expected**: `SELECT AVG(quantity_produced) as avg_qty, MAX(quantity_produced) as max_qty, MIN(quantity_produced) as min_qty, SUM(quantity_produced) as total_qty FROM kpi_quantity_produced_data`
- **Actual**: `SELECT 
  furnace_no, 
  SUM(cast_weight) as total_production, 
  AVG(cast_weight) as avg_production, 
  MIN(cast_weight) as min_production, 
  MAX(cast_weight) as max_production
FROM 
  core_process_tap_production
GROUP BY 
  furnace_no
ORDER BY 
  total_production DESC`

### [FAIL - Mismatch] Test #80
- **Q**: What is the average oee per day
- **Expected**: `SELECT DATE_TRUNC('day', date)::DATE as day, AVG(oee_percentage) as daily_avg FROM kpi_overall_equipment_efficiency_data GROUP BY DATE_TRUNC('day', date) ORDER BY day DESC`
- **Actual**: `SELECT date, AVG(oee_percentage) as avg_oee FROM kpi_overall_equipment_efficiency_data GROUP BY date ORDER BY date DESC`

### [FAIL - Mismatch] Test #81
- **Q**: What is the total production per week
- **Expected**: `SELECT DATE_TRUNC('week', tap_production_datetime)::DATE as week, SUM(cast_weight) as weekly_total FROM core_process_tap_production GROUP BY DATE_TRUNC('week', tap_production_datetime) ORDER BY week DESC`
- **Actual**: `SELECT 
    EXTRACT(WEEK FROM tap_production_datetime) AS week_number,
    SUM(cast_weight) AS total_production
FROM 
    core_process_tap_production
GROUP BY 
    EXTRACT(WEEK FROM tap_production_datetime)
ORDER BY 
    week_number DESC`

### [FAIL - Mismatch] Test #82
- **Q**: Show monthly energy by furnace
- **Expected**: `SELECT DATE_TRUNC('month', date)::DATE as month, furnace_no, SUM(energy_used) as monthly_total FROM kpi_energy_used_data GROUP BY DATE_TRUNC('month', date), furnace_no ORDER BY month DESC, furnace_no`
- **Actual**: `SELECT 
    EXTRACT(MONTH FROM date) AS month,
    furnace_no,
    SUM(energy_used) AS total_energy
FROM 
    kpi_energy_used_data
GROUP BY 
    EXTRACT(MONTH FROM date),
    furnace_no
ORDER BY 
    total_energy DESC`

### [FAIL - Mismatch] Test #83
- **Q**: Show daily downtime summary
- **Expected**: `SELECT DATE_TRUNC('day', date)::DATE as day, SUM(downtime_hours) as daily_downtime, COUNT(*) as event_count FROM kpi_downtime_data GROUP BY DATE_TRUNC('day', date) ORDER BY day DESC`
- **Actual**: `SELECT date, furnace_no, shift_id, downtime_hours 
FROM kpi_downtime_data 
WHERE furnace_no = 1 
ORDER BY date DESC 
LIMIT 100`
- **Diagnosis**: Missing GROUP BY

### [FAIL - Mismatch] Test #84
- **Q**: Show weekly yield trend
- **Expected**: `SELECT DATE_TRUNC('week', date)::DATE as week, AVG(yield_percentage) as weekly_avg_yield FROM kpi_yield_data GROUP BY DATE_TRUNC('week', date) ORDER BY week DESC`
- **Actual**: `SELECT date, yield_percentage 
FROM kpi_yield_data 
WHERE furnace_no = 1 
ORDER BY date DESC 
LIMIT 100`
- **Diagnosis**: Missing GROUP BY

### [FAIL - Mismatch] Test #85
- **Q**: Show daily tap production
- **Expected**: `SELECT DATE_TRUNC('day', tap_production_datetime)::DATE as production_date, COUNT(DISTINCT tap_id) as tap_count, SUM(cast_weight) as daily_weight FROM core_process_tap_production GROUP BY DATE_TRUNC('day', tap_production_datetime) ORDER BY production_date DESC`
- **Actual**: `SELECT tap_production_datetime, cast_weight, liquid_weight, energy, energy_efficiency, graded_cast_weight, downgrade_quantity, ladle_number_code 
FROM core_process_tap_production 
WHERE tap_production_datetime >= CURRENT_DATE - INTERVAL '7 days' 
ORDER BY tap_production_datetime DESC 
LIMIT 100`
- **Diagnosis**: Missing GROUP BY

### [FAIL - Mismatch] Test #86
- **Q**: Show unusually high downtime
- **Expected**: `SELECT obs_start_dt, furnace_no, downtime_hours FROM log_book_furnace_down_time_event WHERE downtime_hours > (SELECT AVG(downtime_hours) + 2 * STDDEV(downtime_hours) FROM log_book_furnace_down_time_event) ORDER BY downtime_hours DESC`
- **Actual**: `SELECT record_id, date, shift_id, downtime_hours, furnace_no, machine_id, plant_id, product_type_id 
FROM kpi_downtime_data 
WHERE downtime_hours > (SELECT AVG(downtime_hours) * 2 FROM kpi_downtime_data) 
ORDER BY date DESC 
LIMIT 100`

### [FAIL - Mismatch] Test #87
- **Q**: Show oee outliers below normal
- **Expected**: `SELECT date, furnace_no, oee_percentage FROM kpi_overall_equipment_efficiency_data WHERE oee_percentage < (SELECT AVG(oee_percentage) - 2 * STDDEV(oee_percentage) FROM kpi_overall_equipment_efficiency_data) ORDER BY oee_percentage`
- **Actual**: `SELECT record_id, date, shift_id, oee_percentage, furnace_no, machine_id, plant_id, product_type_id 
FROM kpi_overall_equipment_efficiency_data 
WHERE oee_percentage < (SELECT AVG(oee_percentage) - 2 * STDDEV(oee_percentage) FROM kpi_overall_equipment_efficiency_data) 
ORDER BY date DESC 
LIMIT 100`

### [FAIL - Mismatch] Test #88
- **Q**: Show unusually low yield
- **Expected**: `SELECT date, furnace_no, yield_percentage FROM kpi_yield_data WHERE yield_percentage < (SELECT AVG(yield_percentage) - 1.5 * STDDEV(yield_percentage) FROM kpi_yield_data) ORDER BY yield_percentage`
- **Actual**: `SELECT record_id, date, shift_id, yield_percentage, furnace_no, machine_id, plant_id, product_type_id 
FROM kpi_yield_data 
WHERE yield_percentage < (SELECT AVG(yield_percentage) * 0.8 FROM kpi_yield_data) 
ORDER BY date DESC 
LIMIT 100`

### [FAIL - Mismatch] Test #89
- **Q**: Show energy spikes above normal
- **Expected**: `SELECT date, furnace_no, energy_used FROM kpi_energy_used_data WHERE energy_used > (SELECT AVG(energy_used) + 2 * STDDEV(energy_used) FROM kpi_energy_used_data) ORDER BY energy_used DESC`
- **Actual**: `SELECT date, energy_used 
FROM kpi_energy_used_data 
WHERE energy_used > (SELECT AVG(energy_used) FROM kpi_energy_used_data) 
ORDER BY date DESC 
LIMIT 100`

### [FAIL - Mismatch] Test #90
- **Q**: Show high defect rate anomalies
- **Expected**: `SELECT date, furnace_no, defect_rate FROM kpi_defect_rate_data WHERE defect_rate > (SELECT AVG(defect_rate) + 1.5 * STDDEV(defect_rate) FROM kpi_defect_rate_data) ORDER BY defect_rate DESC`
- **Actual**: `SELECT record_id, date, shift_id, defect_rate, furnace_no, machine_id, plant_id, product_type_id 
FROM kpi_defect_rate_data 
WHERE defect_rate > (SELECT AVG(defect_rate) * 1.5 FROM kpi_defect_rate_data) 
ORDER BY date DESC 
LIMIT 100`

### [FAIL - Mismatch] Test #91
- **Q**: Show oee for shift 4
- **Expected**: `SELECT date, oee_percentage FROM kpi_overall_equipment_efficiency_data WHERE shift_id = '4' ORDER BY date DESC LIMIT 100`
- **Actual**: `SELECT record_id, date, shift_id, oee_percentage, furnace_no, machine_id, plant_id, product_type_id 
FROM kpi_overall_equipment_efficiency_data 
WHERE shift_id = '4' 
ORDER BY date DESC 
LIMIT 100`

### [FAIL - Mismatch] Test #93
- **Q**: Show oee for machine furnace
- **Expected**: `SELECT date, oee_percentage FROM kpi_overall_equipment_efficiency_data WHERE machine_id = 'FURNACE' ORDER BY date DESC LIMIT 100`
- **Actual**: `SELECT oee_percentage, date, furnace_no, machine_id 
FROM kpi_overall_equipment_efficiency_data 
WHERE machine_id = 'FURNACE' 
ORDER BY date DESC 
LIMIT 100`

### [FAIL - Mismatch] Test #94
- **Q**: Show production for product m004
- **Expected**: `SELECT date, quantity_produced FROM kpi_quantity_produced_data WHERE product_type_id = 'M004' ORDER BY date DESC LIMIT 100`
- **Actual**: `SELECT tap_id, tap_production_datetime, cast_weight, liquid_weight, energy, energy_efficiency, graded_cast_weight, downgrade_quantity, ladle_number_code 
FROM core_process_tap_production 
WHERE product_type_id = 'M004' 
ORDER BY tap_production_datetime DESC 
LIMIT 100`

### [FAIL - Mismatch] Test #96
- **Q**: What is the cycle time for FURNACE on 2024-01-07?
- **Expected**: `SELECT date, shift_id, cycle_time, furnace_no FROM kpi_cycle_time_data WHERE machine_id = 'FURNACE' AND date = '2024-01-07' ORDER BY shift_id`
- **Actual**: `SELECT cycle_time FROM kpi_cycle_time_data WHERE machine_id = 'FURNACE' AND date = '2024-01-07' LIMIT 100 ORDER BY date DESC`

### [FAIL - Mismatch] Test #97
- **Q**: Show all cycle time records for 2024-01-08
- **Expected**: `SELECT date, shift_id, cycle_time, furnace_no, machine_id FROM kpi_cycle_time_data WHERE date = '2024-01-08' ORDER BY shift_id`
- **Actual**: `SELECT record_id, date, shift_id, cycle_time, furnace_no, machine_id, plant_id, product_type_id 
FROM kpi_cycle_time_data 
WHERE date = '2024-01-08' 
ORDER BY date DESC 
LIMIT 100`

### [FAIL - Mismatch] Test #98
- **Q**: What was the cycle time for shift 12 on 2024-01-09?
- **Expected**: `SELECT date, shift_id, cycle_time, furnace_no, machine_id FROM kpi_cycle_time_data WHERE shift_id = '12' AND date = '2024-01-09'`
- **Actual**: `SELECT cycle_time FROM kpi_cycle_time_data WHERE shift_id = '12' AND date = '2024-01-09' ORDER BY date DESC LIMIT 100`

### [FAIL - Mismatch] Test #99
- **Q**: List cycle times for machine CAST_BAY
- **Expected**: `SELECT date, shift_id, cycle_time, furnace_no FROM kpi_cycle_time_data WHERE machine_id = 'CAST_BAY' ORDER BY date DESC LIMIT 100`
- **Actual**: `SELECT date, shift_id, cycle_time, furnace_no, machine_id, plant_id, product_type_id 
FROM kpi_cycle_time_data 
WHERE machine_id = 'CAST_BAY' 
ORDER BY date DESC 
LIMIT 100`

### [FAIL - Mismatch] Test #100
- **Q**: Show cycle time for furnace 888 on 2024-01-07
- **Expected**: `SELECT date, shift_id, cycle_time, machine_id FROM kpi_cycle_time_data WHERE furnace_no = 888 AND date = '2024-01-07' ORDER BY shift_id`
- **Actual**: `SELECT record_id, date, shift_id, cycle_time, furnace_no, machine_id, plant_id, product_type_id 
FROM kpi_cycle_time_data 
WHERE furnace_no = 888 AND date = '2024-01-07' 
ORDER BY date DESC 
LIMIT 100`

### [FAIL - Mismatch] Test #108
- **Q**: Compare cycle time between shifts 4, 12, and 20
- **Expected**: `SELECT shift_id, AVG(cycle_time) as avg_cycle_time, MIN(cycle_time) as min_cycle_time, MAX(cycle_time) as max_cycle_time FROM kpi_cycle_time_data WHERE shift_id IN ('4', '12', '20') GROUP BY shift_id ORDER BY avg_cycle_time DESC`
- **Actual**: `SELECT 
    shift_id, 
    AVG(cycle_time) as avg_cycle_time
FROM 
    kpi_cycle_time_data
WHERE 
    shift_id IN ('4', '12', '20')
GROUP BY 
    shift_id
ORDER BY 
    avg_cycle_time ASC`

### [FAIL - Mismatch] Test #109
- **Q**: Show cycle time trend by shift over time
- **Expected**: `SELECT date, shift_id, AVG(cycle_time) as avg_cycle_time FROM kpi_cycle_time_data GROUP BY date, shift_id ORDER BY date DESC, shift_id`
- **Actual**: `SELECT 
    DATE_TRUNC('month', date) AS month,
    shift_id,
    AVG(cycle_time) AS average_cycle_time
FROM 
    kpi_cycle_time_data
WHERE 
    furnace_no = 1
GROUP BY 
    DATE_TRUNC('month', date),
    shift_id
ORDER BY 
    month DESC`

### [FAIL - Mismatch] Test #110
- **Q**: Show on 2024-01-08, which shift was slowest?
- **Expected**: `SELECT shift_id, AVG(cycle_time) as avg_cycle_time FROM kpi_cycle_time_data WHERE date = '2024-01-08' GROUP BY shift_id ORDER BY avg_cycle_time DESC LIMIT 1`
- **Actual**: `SELECT shift_id, AVG(oee_percentage) as avg_oee 
FROM kpi_overall_equipment_efficiency_data 
WHERE date = '2024-01-08' 
GROUP BY shift_id 
ORDER BY avg_oee ASC 
LIMIT 1`

### [FAIL - Mismatch] Test #111
- **Q**: Show What's the average cycle time for shift 20 across all days?
- **Expected**: `SELECT AVG(cycle_time) as avg_cycle_time FROM kpi_cycle_time_data WHERE shift_id = '20'`
- **Actual**: `SELECT AVG(cycle_time) FROM kpi_cycle_time_data WHERE shift_id = '20'`

### [FAIL - Mismatch] Test #114
- **Q**: Which machine had cycle time above 90?
- **Expected**: `SELECT DISTINCT machine_id, date, shift_id, cycle_time FROM kpi_cycle_time_data WHERE cycle_time > 90 ORDER BY cycle_time DESC`
- **Actual**: `SELECT machine_id FROM kpi_cycle_time_data WHERE cycle_time > 90 ORDER BY date DESC LIMIT 100`

### [FAIL - Mismatch] Test #115
- **Q**: Compare cycle time for FURNACE vs ELECTROD
- **Expected**: `SELECT machine_id, AVG(cycle_time) as avg_cycle_time, MIN(cycle_time) as min_cycle_time, MAX(cycle_time) as max_cycle_time FROM kpi_cycle_time_data WHERE machine_id IN ('FURNACE', 'ELECTROD') GROUP BY machine_id ORDER BY avg_cycle_time DESC`
- **Actual**: `SELECT machine_id, AVG(cycle_time) as avg_cycle_time 
FROM kpi_cycle_time_data 
WHERE machine_id IN ('FURNACE', 'ELECTROD') 
GROUP BY machine_id 
ORDER BY avg_cycle_time DESC`

### [FAIL - Mismatch] Test #116
- **Q**: Show for unkwn_eq, what's the average cycle time by shift?
- **Expected**: `SELECT shift_id, AVG(cycle_time) as avg_cycle_time FROM kpi_cycle_time_data WHERE machine_id = 'UNKWN_EQ' GROUP BY shift_id ORDER BY avg_cycle_time DESC`
- **Actual**: `SELECT shift_id, AVG(cycle_time) as avg_cycle_time FROM kpi_cycle_time_data WHERE product_type_id = 'unkwn_eq' GROUP BY shift_id ORDER BY avg_cycle_time DESC`

### [FAIL - Mismatch] Test #118
- **Q**: Which furnace has more cycle time spikes?
- **Expected**: `SELECT furnace_no, COUNT(*) as spike_count FROM kpi_cycle_time_data WHERE cycle_time > (SELECT AVG(cycle_time) + STDDEV(cycle_time) FROM kpi_cycle_time_data) GROUP BY furnace_no ORDER BY spike_count DESC`
- **Actual**: `SELECT furnace_no, COUNT(cycle_time) as cycle_time_spikes 
FROM kpi_cycle_time_data 
WHERE cycle_time > (SELECT AVG(cycle_time) FROM kpi_cycle_time_data) 
GROUP BY furnace_no 
ORDER BY cycle_time_spikes DESC 
LIMIT 1`

### [FAIL - Mismatch] Test #119
- **Q**: Show cycle time distribution for furnace 888
- **Expected**: `SELECT MIN(cycle_time) as min_cycle_time, MAX(cycle_time) as max_cycle_time, AVG(cycle_time) as avg_cycle_time, STDDEV(cycle_time) as stddev_cycle_time, COUNT(*) as total_records FROM kpi_cycle_time_data WHERE furnace_no = 888`
- **Actual**: `SELECT record_id, date, shift_id, cycle_time, furnace_no, machine_id, plant_id, product_type_id 
FROM kpi_cycle_time_data 
WHERE furnace_no = 888 
ORDER BY date DESC 
LIMIT 100`

### [FAIL - Mismatch] Test #120
- **Q**: What is the max cycle time for furnace 1?
- **Expected**: `SELECT MAX(cycle_time) as max_cycle_time FROM kpi_cycle_time_data WHERE furnace_no = 1`
- **Actual**: `SELECT MAX(cycle_time) FROM kpi_cycle_time_data WHERE furnace_no = 1`

### [FAIL - Mismatch] Test #121
- **Q**: Show cycle time statistics by furnace
- **Expected**: `SELECT furnace_no, AVG(cycle_time) as avg_cycle_time, MIN(cycle_time) as min_cycle_time, MAX(cycle_time) as max_cycle_time, STDDEV(cycle_time) as stddev_cycle_time FROM kpi_cycle_time_data GROUP BY furnace_no ORDER BY avg_cycle_time DESC`
- **Actual**: `SELECT 
    furnace_no,
    AVG(cycle_time) AS average_cycle_time,
    MIN(cycle_time) AS min_cycle_time,
    MAX(cycle_time) AS max_cycle_time,
    PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY cycle_time) AS median_cycle_time,
    STDEV(cycle_time) AS std_dev_cycle_time
FROM 
    kpi_cycle_time_data
WHERE 
    furnace_no IN (1, 2, 3)
GROUP BY 
    furnace_no
ORDER BY 
    average_cycle_time DESC`

### [FAIL - Mismatch] Test #122
- **Q**: What is the average cycle time for product M004?
- **Expected**: `SELECT AVG(cycle_time) as avg_cycle_time FROM kpi_cycle_time_data WHERE product_type_id = 'M004'`
- **Actual**: `SELECT AVG(cycle_time) FROM kpi_cycle_time_data WHERE product_type_id = 'M004'`

### [FAIL - Mismatch] Test #124
- **Q**: Compare cycle time for MET30 vs MET32
- **Expected**: `SELECT product_type_id, AVG(cycle_time) as avg_cycle_time, MIN(cycle_time) as min_cycle_time, MAX(cycle_time) as max_cycle_time FROM kpi_cycle_time_data WHERE product_type_id IN ('MET30', 'MET32') GROUP BY product_type_id ORDER BY avg_cycle_time DESC`
- **Actual**: `SELECT product_type_id, AVG(cycle_time) as avg_cycle_time 
FROM kpi_cycle_time_data 
WHERE product_type_id IN ('MET30', 'MET32') 
GROUP BY product_type_id 
ORDER BY avg_cycle_time DESC`

### [FAIL - Mismatch] Test #125
- **Q**: Show cycle time by product_type_id for each day
- **Expected**: `SELECT date, product_type_id, AVG(cycle_time) as avg_cycle_time FROM kpi_cycle_time_data GROUP BY date, product_type_id ORDER BY date DESC, product_type_id`
- **Actual**: `SELECT 
    date, 
    product_type_id, 
    AVG(cycle_time) AS average_cycle_time
FROM 
    kpi_cycle_time_data
GROUP BY 
    date, 
    product_type_id
ORDER BY 
    date DESC`

### [FAIL - Mismatch] Test #126
- **Q**: Which products have cycle time above 80 on 2024-01-07?
- **Expected**: `SELECT DISTINCT product_type_id, cycle_time FROM kpi_cycle_time_data WHERE cycle_time > 80 AND date = '2024-01-07' ORDER BY cycle_time DESC`
- **Actual**: `SELECT product_type_id FROM kpi_cycle_time_data WHERE date = '2024-01-07' AND cycle_time > 80`

### [FAIL - Mismatch] Test #127
- **Q**: Show is cycle time increasing from jan 7 to jan 9?
- **Expected**: `SELECT date, AVG(cycle_time) as avg_cycle_time FROM kpi_cycle_time_data WHERE date BETWEEN '2024-01-07' AND '2024-01-09' GROUP BY date ORDER BY date`
- **Actual**: `SELECT date, cycle_time 
FROM kpi_cycle_time_data 
WHERE date BETWEEN '2024-01-07' AND '2024-01-09' 
ORDER BY date DESC 
LIMIT 100`
- **Diagnosis**: Missing GROUP BY

### [FAIL - Mismatch] Test #128
- **Q**: Show the cycle time trend per machine across days
- **Expected**: `SELECT date, machine_id, AVG(cycle_time) as avg_cycle_time FROM kpi_cycle_time_data GROUP BY date, machine_id ORDER BY date DESC, machine_id`
- **Actual**: `SELECT 
    date, 
    machine_id, 
    AVG(cycle_time) AS average_cycle_time
FROM 
    kpi_cycle_time_data 
WHERE 
    furnace_no = 1 
GROUP BY 
    date, 
    machine_id 
ORDER BY 
    date DESC`

### [FAIL - Mismatch] Test #129
- **Q**: Which machine improved the most between Jan 7 and Jan 9?
- **Expected**: `SELECT machine_id, AVG(CASE WHEN date = '2024-01-07' THEN cycle_time END) as jan7_avg, AVG(CASE WHEN date = '2024-01-09' THEN cycle_time END) as jan9_avg, AVG(CASE WHEN date = '2024-01-07' THEN cycle_time END) - AVG(CASE WHEN date = '2024-01-09' THEN cycle_time END) as improvement FROM kpi_cycle_time_data WHERE date IN ('2024-01-07', '2024-01-09') GROUP BY machine_id ORDER BY improvement DESC LIMIT 1`
- **Actual**: `SELECT machine_id, SUM(CASE WHEN date = '2024-01-07' THEN oee_percentage ELSE 0 END) AS oee_before, 
       SUM(CASE WHEN date = '2024-01-09' THEN oee_percentage ELSE 0 END) AS oee_after, 
       SUM(CASE WHEN date = '2024-01-09' THEN oee_percentage ELSE 0 END) - 
       SUM(CASE WHEN date = '2024-01-07' THEN oee_percentage ELSE 0 END) AS improvement
FROM kpi_overall_equipment_efficiency_data
WHERE date IN ('2024-01-07', '2024-01-09')
GROUP BY machine_id
ORDER BY improvement DESC
LIMIT 1`

### [FAIL - Mismatch] Test #130
- **Q**: Which shift shows the biggest cycle time variation?
- **Expected**: `SELECT shift_id, STDDEV(cycle_time) as cycle_time_variation, AVG(cycle_time) as avg_cycle_time FROM kpi_cycle_time_data GROUP BY shift_id ORDER BY cycle_time_variation DESC LIMIT 1`
- **Actual**: `SELECT shift_id, MAX(cycle_time) - MIN(cycle_time) as cycle_time_variation 
FROM kpi_cycle_time_data 
GROUP BY shift_id 
ORDER BY cycle_time_variation DESC 
LIMIT 1`

### [FAIL - Mismatch] Test #131
- **Q**: Show daily cycle time trend
- **Expected**: `SELECT date, AVG(cycle_time) as avg_cycle_time, MIN(cycle_time) as min_cycle_time, MAX(cycle_time) as max_cycle_time FROM kpi_cycle_time_data GROUP BY date ORDER BY date DESC`
- **Actual**: `SELECT date, cycle_time FROM kpi_cycle_time_data WHERE furnace_no = 1 ORDER BY date DESC LIMIT 100`
- **Diagnosis**: Missing GROUP BY

### [FAIL - Mismatch] Test #132
- **Q**: Show records where cycle time is greater than 90
- **Expected**: `SELECT date, shift_id, cycle_time, furnace_no, machine_id FROM kpi_cycle_time_data WHERE cycle_time > 90 ORDER BY cycle_time DESC LIMIT 100`
- **Actual**: `SELECT record_id, date, shift_id, cycle_time, furnace_no, machine_id, plant_id, product_type_id 
FROM kpi_cycle_time_data 
WHERE cycle_time > 90 
ORDER BY date DESC 
LIMIT 100`

### [FAIL - Mismatch] Test #133
- **Q**: Which machines crossed the cycle time threshold on Jan 8?
- **Expected**: `SELECT DISTINCT machine_id, cycle_time, shift_id FROM kpi_cycle_time_data WHERE date = '2024-01-08' AND cycle_time > 90 ORDER BY cycle_time DESC`
- **Actual**: `SELECT machine_id FROM kpi_cycle_time_data WHERE date = '2024-01-08' AND cycle_time > (SELECT AVG(cycle_time) FROM kpi_cycle_time_data)`

### [FAIL - Mismatch] Test #134
- **Q**: List the top 10 highest cycle time incidents
- **Expected**: `SELECT date, shift_id, cycle_time, furnace_no, machine_id FROM kpi_cycle_time_data ORDER BY cycle_time DESC LIMIT 10`
- **Actual**: `SELECT date, shift_id, cycle_time, furnace_no, machine_id, plant_id, product_type_id 
FROM kpi_cycle_time_data 
WHERE cycle_time IS NOT NULL 
ORDER BY cycle_time DESC 
LIMIT 10`

### [FAIL - Mismatch] Test #135
- **Q**: Which machine had the lowest cycle time and when?
- **Expected**: `SELECT machine_id, date, shift_id, cycle_time FROM kpi_cycle_time_data ORDER BY cycle_time ASC LIMIT 1`
- **Actual**: `SELECT machine_id, date, MIN(cycle_time) as min_cycle_time 
FROM kpi_cycle_time_data 
ORDER BY cycle_time ASC 
LIMIT 1`

### [FAIL - Mismatch] Test #136
- **Q**: Show cycle time anomalies above normal
- **Expected**: `SELECT date, shift_id, cycle_time, furnace_no, machine_id FROM kpi_cycle_time_data WHERE cycle_time > (SELECT AVG(cycle_time) + 2 * STDDEV(cycle_time) FROM kpi_cycle_time_data) ORDER BY cycle_time DESC`
- **Actual**: `SELECT record_id, date, shift_id, cycle_time, furnace_no, machine_id, plant_id, product_type_id 
FROM kpi_cycle_time_data 
WHERE cycle_time > (SELECT AVG(cycle_time) FROM kpi_cycle_time_data) 
ORDER BY date DESC 
LIMIT 100`

### [FAIL - Mismatch] Test #137
- **Q**: What are the slowest machines today?
- **Expected**: `SELECT machine_id, AVG(cycle_time) as avg_cycle_time FROM kpi_cycle_time_data WHERE date = CURRENT_DATE GROUP BY machine_id ORDER BY avg_cycle_time DESC LIMIT 5`
- **Actual**: `SELECT 
    machine_id, 
    AVG(downtime_hours) as avg_downtime_hours
FROM 
    kpi_downtime_data
WHERE 
    date = CURRENT_DATE
GROUP BY 
    machine_id
ORDER BY 
    avg_downtime_hours DESC
LIMIT 100`

### [FAIL - Mismatch] Test #138
- **Q**: Show where are we spending the most time in the process?
- **Expected**: `SELECT machine_id, SUM(cycle_time) as total_cycle_time, AVG(cycle_time) as avg_cycle_time FROM kpi_cycle_time_data GROUP BY machine_id ORDER BY total_cycle_time DESC LIMIT 5`
- **Actual**: `SELECT furnace_no, AVG(cycle_time) as avg_cycle_time FROM kpi_cycle_time_data GROUP BY furnace_no ORDER BY avg_cycle_time DESC`

### [FAIL - Mismatch] Test #139
- **Q**: Which area should I investigate first for long cycle times?
- **Expected**: `SELECT machine_id, furnace_no, AVG(cycle_time) as avg_cycle_time, COUNT(*) as record_count FROM kpi_cycle_time_data WHERE cycle_time > (SELECT AVG(cycle_time) FROM kpi_cycle_time_data) GROUP BY machine_id, furnace_no ORDER BY avg_cycle_time DESC LIMIT 5`
- **Actual**: `SELECT furnace_no, AVG(cycle_time) as avg_cycle_time 
FROM kpi_cycle_time_data 
WHERE date >= CURRENT_DATE - INTERVAL '30 days' 
GROUP BY furnace_no 
ORDER BY avg_cycle_time DESC 
LIMIT 1`

### [FAIL - Mismatch] Test #140
- **Q**: What changed on Jan 8 that caused higher cycle time?
- **Expected**: `SELECT machine_id, shift_id, AVG(cycle_time) as avg_cycle_time, COUNT(*) as record_count FROM kpi_cycle_time_data WHERE date = '2024-01-08' GROUP BY machine_id, shift_id ORDER BY avg_cycle_time DESC`
- **Actual**: `SELECT date, shift_id, machine_id, product_type_id, AVG(cycle_time) as avg_cycle_time 
FROM kpi_cycle_time_data 
WHERE date = '2024-01-08' 
GROUP BY date, shift_id, machine_id, product_type_id 
ORDER BY avg_cycle_time DESC`

### [FAIL - Mismatch] Test #141
- **Q**: Show me cycle time bottlenecks
- **Expected**: `SELECT machine_id, furnace_no, AVG(cycle_time) as avg_cycle_time, MAX(cycle_time) as max_cycle_time FROM kpi_cycle_time_data GROUP BY machine_id, furnace_no HAVING AVG(cycle_time) > (SELECT AVG(cycle_time) FROM kpi_cycle_time_data) ORDER BY avg_cycle_time DESC`
- **Actual**: `SELECT 
    kcd.record_id, 
    kcd.date, 
    kcd.shift_id, 
    kcd.cycle_time, 
    kcd.furnace_no, 
    kcd.machine_id, 
    kcd.plant_id, 
    kcd.product_type_id
FROM 
    kpi_cycle_time_data kcd
WHERE 
    kcd.cycle_time > (SELECT AVG(cycle_time) FROM kpi_cycle_time_data)
    AND kcd.furnace_no IN (
        SELECT 
            furnace_no 
        FROM 
            kpi_downtime_data 
        WHERE 
            downtime_hours > (SELECT AVG(downtime_hours) FROM kpi_downtime_data)
    )
ORDER BY 
    kcd.date DESC 
LIMIT 100`
- **Diagnosis**: Missing GROUP BY

### [FAIL - Mismatch] Test #142
- **Q**: What is the OEE for FURNACE on 2024-01-07?
- **Expected**: `SELECT date, shift_id, oee_percentage, furnace_no FROM kpi_overall_equipment_efficiency_data WHERE machine_id = 'FURNACE' AND date = '2024-01-07' ORDER BY shift_id`
- **Actual**: `SELECT oee_percentage FROM kpi_overall_equipment_efficiency_data WHERE machine_id = 'FURNACE' AND date = '2024-01-07'`

### [FAIL - Mismatch] Test #143
- **Q**: Show all OEE records for 2024-01-08
- **Expected**: `SELECT date, shift_id, oee_percentage, furnace_no, machine_id FROM kpi_overall_equipment_efficiency_data WHERE date = '2024-01-08' ORDER BY shift_id`
- **Actual**: `SELECT record_id, date, shift_id, oee_percentage, furnace_no, machine_id, plant_id, product_type_id 
FROM kpi_overall_equipment_efficiency_data 
WHERE date = '2024-01-08' 
ORDER BY date DESC 
LIMIT 100`

### [FAIL - Mismatch] Test #144
- **Q**: What was the OEE for shift 12 on 2024-01-09?
- **Expected**: `SELECT date, shift_id, oee_percentage, furnace_no, machine_id FROM kpi_overall_equipment_efficiency_data WHERE shift_id = '12' AND date = '2024-01-09'`
- **Actual**: `SELECT oee_percentage FROM kpi_overall_equipment_efficiency_data WHERE shift_id = '12' AND date = '2024-01-09' ORDER BY date DESC LIMIT 100`

### [FAIL - Mismatch] Test #145
- **Q**: List OEE for machine CAST_BAY
- **Expected**: `SELECT date, shift_id, oee_percentage, furnace_no FROM kpi_overall_equipment_efficiency_data WHERE machine_id = 'CAST_BAY' ORDER BY date DESC LIMIT 100`
- **Actual**: `SELECT oee_percentage, date 
FROM kpi_overall_equipment_efficiency_data 
WHERE machine_id = 'CAST_BAY' 
ORDER BY date DESC 
LIMIT 100`

### [FAIL - Mismatch] Test #146
- **Q**: Show OEE for furnace 888 on 2024-01-07
- **Expected**: `SELECT date, shift_id, oee_percentage, machine_id FROM kpi_overall_equipment_efficiency_data WHERE furnace_no = 888 AND date = '2024-01-07' ORDER BY shift_id`
- **Actual**: `SELECT oee_percentage 
FROM kpi_overall_equipment_efficiency_data 
WHERE furnace_no = 888 AND date = '2024-01-07' 
ORDER BY date DESC 
LIMIT 100`

### [FAIL - Mismatch] Test #154
- **Q**: Compare OEE between shifts 4, 12, and 20
- **Expected**: `SELECT shift_id, AVG(oee_percentage) as avg_oee, MIN(oee_percentage) as min_oee, MAX(oee_percentage) as max_oee FROM kpi_overall_equipment_efficiency_data WHERE shift_id IN ('4', '12', '20') GROUP BY shift_id ORDER BY avg_oee DESC`
- **Actual**: `SELECT 
    shift_id, 
    AVG(oee_percentage) as avg_oee
FROM 
    kpi_overall_equipment_efficiency_data
WHERE 
    shift_id IN ('4', '12', '20')
GROUP BY 
    shift_id
ORDER BY 
    avg_oee DESC`

### [FAIL - Mismatch] Test #155
- **Q**: Show OEE trend by shift over time
- **Expected**: `SELECT date, shift_id, AVG(oee_percentage) as avg_oee FROM kpi_overall_equipment_efficiency_data GROUP BY date, shift_id ORDER BY date DESC, shift_id`
- **Actual**: `SELECT 
    date, 
    shift_id, 
    AVG(oee_percentage) AS average_oee
FROM 
    kpi_overall_equipment_efficiency_data 
WHERE 
    furnace_no = 1 
GROUP BY 
    date, 
    shift_id 
ORDER BY 
    date DESC`

### [FAIL - Mismatch] Test #157
- **Q**: Show What's the average OEE for shift 20 across all days?
- **Expected**: `SELECT AVG(oee_percentage) as avg_oee FROM kpi_overall_equipment_efficiency_data WHERE shift_id = '20'`
- **Actual**: `SELECT AVG(oee_percentage) AS average_oee FROM kpi_overall_equipment_efficiency_data WHERE shift_id = '20'`

### [FAIL - Mismatch] Test #160
- **Q**: Which machines have OEE below 80?
- **Expected**: `SELECT DISTINCT machine_id, date, shift_id, oee_percentage FROM kpi_overall_equipment_efficiency_data WHERE oee_percentage < 80 ORDER BY oee_percentage ASC`
- **Actual**: `SELECT machine_id FROM kpi_overall_equipment_efficiency_data WHERE oee_percentage < '80' GROUP BY machine_id HAVING AVG(oee_percentage) < '80' ORDER BY AVG(oee_percentage) DESC`

### [FAIL - Mismatch] Test #161
- **Q**: Compare OEE for FURNACE vs ELECTROD
- **Expected**: `SELECT machine_id, AVG(oee_percentage) as avg_oee, MIN(oee_percentage) as min_oee, MAX(oee_percentage) as max_oee FROM kpi_overall_equipment_efficiency_data WHERE machine_id IN ('FURNACE', 'ELECTROD') GROUP BY machine_id ORDER BY avg_oee DESC`
- **Actual**: `SELECT machine_id, AVG(oee_percentage) as avg_oee 
FROM kpi_overall_equipment_efficiency_data 
WHERE machine_id IN ('FURNACE', 'ELECTROD') 
GROUP BY machine_id 
ORDER BY avg_oee DESC`

### [FAIL - Mismatch] Test #164
- **Q**: Which furnace has the most OEE drops below 70?
- **Expected**: `SELECT furnace_no, COUNT(*) as drop_count FROM kpi_overall_equipment_efficiency_data WHERE oee_percentage < 70 GROUP BY furnace_no ORDER BY drop_count DESC`
- **Actual**: `SELECT furnace_no, COUNT(*) as oee_drops
FROM kpi_overall_equipment_efficiency_data
WHERE oee_percentage < 70
GROUP BY furnace_no
ORDER BY oee_drops DESC
LIMIT 1`

### [FAIL - Mismatch] Test #165
- **Q**: Show OEE distribution for furnace 888
- **Expected**: `SELECT MIN(oee_percentage) as min_oee, MAX(oee_percentage) as max_oee, AVG(oee_percentage) as avg_oee, STDDEV(oee_percentage) as stddev_oee, COUNT(*) as total_records FROM kpi_overall_equipment_efficiency_data WHERE furnace_no = 888`
- **Actual**: `SELECT date, oee_percentage 
FROM kpi_overall_equipment_efficiency_data 
WHERE furnace_no = 888 
ORDER BY date DESC 
LIMIT 100`

### [FAIL - Mismatch] Test #166
- **Q**: What is the max OEE for furnace 1?
- **Expected**: `SELECT MAX(oee_percentage) as max_oee FROM kpi_overall_equipment_efficiency_data WHERE furnace_no = 1`
- **Actual**: `SELECT MAX(oee_percentage) FROM kpi_overall_equipment_efficiency_data WHERE furnace_no = 1`

### [FAIL - Mismatch] Test #167
- **Q**: Show oee statistics by furnace
- **Expected**: `SELECT furnace_no, AVG(oee_percentage) as avg_oee, MIN(oee_percentage) as min_oee, MAX(oee_percentage) as max_oee, STDDEV(oee_percentage) as stddev_oee FROM kpi_overall_equipment_efficiency_data GROUP BY furnace_no ORDER BY avg_oee DESC`
- **Actual**: `SELECT 
    furnace_no, 
    AVG(oee_percentage) as avg_oee, 
    SUM(cast_weight) as total_cast_weight, 
    COUNT(record_id) as num_records
FROM 
    kpi_overall_equipment_efficiency_data
GROUP BY 
    furnace_no
ORDER BY 
    avg_oee DESC`

### [FAIL - Mismatch] Test #168
- **Q**: What is the average OEE for product M004?
- **Expected**: `SELECT AVG(oee_percentage) as avg_oee FROM kpi_overall_equipment_efficiency_data WHERE product_type_id = 'M004'`
- **Actual**: `SELECT AVG(oee_percentage) FROM kpi_overall_equipment_efficiency_data WHERE product_type_id = 'M004'`

### [FAIL - Mismatch] Test #170
- **Q**: Compare OEE for MET30 vs MET32
- **Expected**: `SELECT product_type_id, AVG(oee_percentage) as avg_oee, MIN(oee_percentage) as min_oee, MAX(oee_percentage) as max_oee FROM kpi_overall_equipment_efficiency_data WHERE product_type_id IN ('MET30', 'MET32') GROUP BY product_type_id ORDER BY avg_oee DESC`
- **Actual**: `SELECT product_type_id, AVG(oee_percentage) as avg_oee 
FROM kpi_overall_equipment_efficiency_data 
WHERE product_type_id IN ('MET30', 'MET32') 
GROUP BY product_type_id 
ORDER BY avg_oee DESC`

### [FAIL - Mismatch] Test #171
- **Q**: Show OEE by product_type_id for each day
- **Expected**: `SELECT date, product_type_id, AVG(oee_percentage) as avg_oee FROM kpi_overall_equipment_efficiency_data GROUP BY date, product_type_id ORDER BY date DESC, product_type_id`
- **Actual**: `SELECT date, product_type_id, AVG(oee_percentage) as avg_oee 
FROM kpi_overall_equipment_efficiency_data 
WHERE date >= CURRENT_DATE - INTERVAL '30 days' 
GROUP BY date, product_type_id 
ORDER BY date DESC, avg_oee DESC`

### [FAIL - Mismatch] Test #172
- **Q**: Which products have OEE below 75 on 2024-01-07?
- **Expected**: `SELECT DISTINCT product_type_id, oee_percentage FROM kpi_overall_equipment_efficiency_data WHERE oee_percentage < 75 AND date = '2024-01-07' ORDER BY oee_percentage ASC`
- **Actual**: `SELECT product_type_id FROM kpi_overall_equipment_efficiency_data WHERE date = '2024-01-07' AND oee_percentage < '75'`

### [FAIL - Mismatch] Test #176
- **Q**: Compare OEE across plants
- **Expected**: `SELECT plant_id, AVG(oee_percentage) as avg_oee, COUNT(*) as record_count FROM kpi_overall_equipment_efficiency_data GROUP BY plant_id ORDER BY avg_oee DESC`
- **Actual**: `SELECT p.plant_name, AVG(k.oee_percentage) as avg_oee 
FROM kpi_overall_equipment_efficiency_data k
JOIN plant_plant p ON k.plant_id = p.id
GROUP BY p.plant_name
ORDER BY avg_oee DESC`

### [FAIL - Mismatch] Test #177
- **Q**: Show is oee increasing from jan 7 to jan 9?
- **Expected**: `SELECT date, AVG(oee_percentage) as avg_oee FROM kpi_overall_equipment_efficiency_data WHERE date BETWEEN '2024-01-07' AND '2024-01-09' GROUP BY date ORDER BY date`
- **Actual**: `SELECT date, oee_percentage 
FROM kpi_overall_equipment_efficiency_data 
WHERE date BETWEEN '2024-01-07' AND '2024-01-09' 
ORDER BY date DESC 
LIMIT 100`
- **Diagnosis**: Missing GROUP BY

### [FAIL - Mismatch] Test #178
- **Q**: Show the OEE trend per machine across days
- **Expected**: `SELECT date, machine_id, AVG(oee_percentage) as avg_oee FROM kpi_overall_equipment_efficiency_data GROUP BY date, machine_id ORDER BY date DESC, machine_id`
- **Actual**: `SELECT date, machine_id, oee_percentage 
FROM kpi_overall_equipment_efficiency_data 
WHERE date >= CURRENT_DATE - INTERVAL '30 days' 
ORDER BY date DESC 
LIMIT 100`
- **Diagnosis**: Missing GROUP BY

### [FAIL - Mismatch] Test #179
- **Q**: Which machine improved the most between Jan 7 and Jan 9?
- **Expected**: `SELECT machine_id, AVG(CASE WHEN date = '2024-01-07' THEN oee_percentage END) as jan7_avg, AVG(CASE WHEN date = '2024-01-09' THEN oee_percentage END) as jan9_avg, AVG(CASE WHEN date = '2024-01-09' THEN oee_percentage END) - AVG(CASE WHEN date = '2024-01-07' THEN oee_percentage END) as improvement FROM kpi_overall_equipment_efficiency_data WHERE date IN ('2024-01-07', '2024-01-09') GROUP BY machine_id ORDER BY improvement DESC LIMIT 1`
- **Actual**: `SELECT machine_id, SUM(CASE WHEN date = '2024-01-09' THEN oee_percentage ELSE 0 END) - SUM(CASE WHEN date = '2024-01-07' THEN oee_percentage ELSE 0 END) AS improvement 
FROM kpi_overall_equipment_efficiency_data 
WHERE date IN ('2024-01-07', '2024-01-09') 
GROUP BY machine_id 
ORDER BY improvement DESC 
LIMIT 1`

### [FAIL - Mismatch] Test #180
- **Q**: Which shift shows the biggest OEE variation?
- **Expected**: `SELECT shift_id, STDDEV(oee_percentage) as oee_variation, AVG(oee_percentage) as avg_oee FROM kpi_overall_equipment_efficiency_data GROUP BY shift_id ORDER BY oee_variation DESC LIMIT 1`
- **Actual**: `SELECT shift_id, AVG(oee_percentage) as avg_oee, MAX(oee_percentage) - MIN(oee_percentage) as oee_variation 
FROM kpi_overall_equipment_efficiency_data 
GROUP BY shift_id 
ORDER BY oee_variation DESC 
LIMIT 1`

### [FAIL - Mismatch] Test #181
- **Q**: Show daily oee trend
- **Expected**: `SELECT date, AVG(oee_percentage) as avg_oee, MIN(oee_percentage) as min_oee, MAX(oee_percentage) as max_oee FROM kpi_overall_equipment_efficiency_data GROUP BY date ORDER BY date DESC`
- **Actual**: `SELECT date, oee_percentage 
FROM kpi_overall_equipment_efficiency_data 
WHERE furnace_no = 1 
ORDER BY date DESC 
LIMIT 100`
- **Diagnosis**: Missing GROUP BY

### [FAIL - Mismatch] Test #182
- **Q**: Show records where OEE is below 70
- **Expected**: `SELECT date, shift_id, oee_percentage, furnace_no, machine_id FROM kpi_overall_equipment_efficiency_data WHERE oee_percentage < 70 ORDER BY oee_percentage ASC LIMIT 100`
- **Actual**: `SELECT record_id, date, shift_id, oee_percentage, furnace_no, machine_id, plant_id, product_type_id 
FROM kpi_overall_equipment_efficiency_data 
WHERE oee_percentage < '70' 
ORDER BY date DESC 
LIMIT 100`

### [FAIL - Mismatch] Test #183
- **Q**: Which machines had OEE below threshold on Jan 8?
- **Expected**: `SELECT DISTINCT machine_id, oee_percentage, shift_id FROM kpi_overall_equipment_efficiency_data WHERE date = '2024-01-08' AND oee_percentage < 75 ORDER BY oee_percentage ASC`
- **Actual**: `SELECT machine_id FROM kpi_overall_equipment_efficiency_data WHERE date = '2024-01-08' AND oee_percentage < 0.85`

### [FAIL - Mismatch] Test #184
- **Q**: List the top 10 lowest OEE incidents
- **Expected**: `SELECT date, shift_id, oee_percentage, furnace_no, machine_id FROM kpi_overall_equipment_efficiency_data ORDER BY oee_percentage ASC LIMIT 10`
- **Actual**: `SELECT record_id, date, shift_id, incidents_percentage, furnace_no, machine_id, plant_id, product_type_id 
FROM kpi_safety_incidents_reported_data 
ORDER BY incidents_percentage ASC 
LIMIT 10`

### [FAIL - Mismatch] Test #185
- **Q**: Which machine had the highest OEE and when?
- **Expected**: `SELECT machine_id, date, shift_id, oee_percentage FROM kpi_overall_equipment_efficiency_data ORDER BY oee_percentage DESC LIMIT 1`
- **Actual**: `SELECT machine_id, date, oee_percentage 
FROM kpi_overall_equipment_efficiency_data 
WHERE oee_percentage = (SELECT MAX(oee_percentage) FROM kpi_overall_equipment_efficiency_data) 
ORDER BY date DESC 
LIMIT 1`

### [FAIL - Mismatch] Test #186
- **Q**: Show oee anomalies below normal
- **Expected**: `SELECT date, shift_id, oee_percentage, furnace_no, machine_id FROM kpi_overall_equipment_efficiency_data WHERE oee_percentage < (SELECT AVG(oee_percentage) - 2 * STDDEV(oee_percentage) FROM kpi_overall_equipment_efficiency_data) ORDER BY oee_percentage ASC`
- **Actual**: `SELECT record_id, date, shift_id, oee_percentage, furnace_no, machine_id, plant_id, product_type_id 
FROM kpi_overall_equipment_efficiency_data 
WHERE oee_percentage < (SELECT AVG(oee_percentage) FROM kpi_overall_equipment_efficiency_data) 
ORDER BY date DESC 
LIMIT 100`

### [FAIL - Mismatch] Test #187
- **Q**: What is the furnace health today?
- **Expected**: `SELECT furnace_no, AVG(oee_percentage) as health_score FROM kpi_overall_equipment_efficiency_data WHERE date = CURRENT_DATE GROUP BY furnace_no ORDER BY health_score DESC`
- **Actual**: `SELECT AVG(oee_percentage) as avg_oee FROM kpi_overall_equipment_efficiency_data WHERE date = CURRENT_DATE`
- **Diagnosis**: Missing GROUP BY

### [FAIL - Mismatch] Test #188
- **Q**: Which furnaces need attention?
- **Expected**: `SELECT furnace_no, AVG(oee_percentage) as avg_oee FROM kpi_overall_equipment_efficiency_data WHERE oee_percentage < (SELECT AVG(oee_percentage) FROM kpi_overall_equipment_efficiency_data) GROUP BY furnace_no ORDER BY avg_oee ASC LIMIT 5`
- **Actual**: `SELECT 
    f.furnace_no,
    COALESCE(SUM(CASE WHEN kpi_downtime_data.downtime_hours > 0 THEN 1 ELSE 0 END), 0) AS downtime_count,
    COALESCE(SUM(CASE WHEN kpi_defect_rate_data.defect_rate > 0.05 THEN 1 ELSE 0 END), 0) AS defect_count,
    COALESCE(SUM(CASE WHEN kpi_energy_efficiency_data.energy_efficiency < 0.8 THEN 1 ELSE 0 END), 0) AS energy_efficiency_count
FROM 
    furnace_furnaceconfig f
LEFT JOIN 
    kpi_downtime_data ON f.furnace_no = kpi_downtime_data.furnace_no
LEFT JOIN 
    kpi_defect_rate_data ON f.furnace_no = kpi_defect_rate_data.furnace_no
LEFT JOIN 
    kpi_energy_efficiency_data ON f.furnace_no = kpi_energy_efficiency_data.furnace_no
WHERE 
    f.is_active = TRUE
GROUP BY 
    f.furnace_no
ORDER BY 
    downtime_count DESC, defect_count DESC, energy_efficiency_count DESC`

### [FAIL - Mismatch] Test #189
- **Q**: How is equipment performing overall?
- **Expected**: `SELECT AVG(oee_percentage) as overall_oee, MIN(oee_percentage) as min_oee, MAX(oee_percentage) as max_oee, COUNT(*) as total_records FROM kpi_overall_equipment_efficiency_data WHERE date >= CURRENT_DATE - INTERVAL '7 days'`
- **Actual**: `SELECT AVG(oee_percentage) as average_oee, AVG(downtime_hours) as average_downtime, AVG(yield_percentage) as average_yield FROM kpi_overall_equipment_efficiency_data`
- **Diagnosis**: Missing WHERE clause

### [FAIL - Mismatch] Test #190
- **Q**: Which areas have efficiency problems?
- **Expected**: `SELECT machine_id, furnace_no, AVG(oee_percentage) as avg_oee, COUNT(*) as record_count FROM kpi_overall_equipment_efficiency_data WHERE oee_percentage < 80 GROUP BY machine_id, furnace_no ORDER BY avg_oee ASC LIMIT 5`
- **Actual**: `SELECT furnace_no, AVG(oee_percentage) as avg_oee FROM kpi_overall_equipment_efficiency_data GROUP BY furnace_no HAVING AVG(oee_percentage) < 0.8 ORDER BY avg_oee ASC`
- **Diagnosis**: Missing WHERE clause

### [FAIL - Mismatch] Test #192
- **Q**: What caused low OEE on Jan 8?
- **Expected**: `SELECT machine_id, shift_id, furnace_no, AVG(oee_percentage) as avg_oee, COUNT(*) as record_count FROM kpi_overall_equipment_efficiency_data WHERE date = '2024-01-08' GROUP BY machine_id, shift_id, furnace_no ORDER BY avg_oee ASC LIMIT 10`
- **Actual**: `SELECT shift_id, machine_id, product_type_id, AVG(oee_percentage) as avg_oee 
FROM kpi_overall_equipment_efficiency_data 
WHERE date = '2024-01-08' 
GROUP BY shift_id, machine_id, product_type_id 
ORDER BY avg_oee ASC 
LIMIT 100`

### [FAIL - Mismatch] Test #193
- **Q**: What is the average defect rate?
- **Expected**: `SELECT AVG(defect_rate) as avg_defect_rate FROM kpi_defect_rate_data`
- **Actual**: `SELECT AVG(defect_rate) as average_defect_rate FROM kpi_defect_rate_data`

### [FAIL - Mismatch] Test #194
- **Q**: Show defect rate for furnace 1
- **Expected**: `SELECT date, shift_id, defect_rate FROM kpi_defect_rate_data WHERE furnace_no = 1 ORDER BY date DESC LIMIT 100`
- **Actual**: `SELECT defect_rate FROM kpi_defect_rate_data WHERE furnace_no = '1' ORDER BY date DESC LIMIT 100`

### [FAIL - Mismatch] Test #196
- **Q**: Show defect rate by shift
- **Expected**: `SELECT shift_id, AVG(defect_rate) as avg_defect_rate FROM kpi_defect_rate_data GROUP BY shift_id ORDER BY avg_defect_rate DESC`
- **Actual**: `SELECT 
    shift_id, 
    AVG(defect_rate) AS average_defect_rate
FROM 
    kpi_defect_rate_data
GROUP BY 
    shift_id
ORDER BY 
    average_defect_rate DESC`

### [FAIL - Mismatch] Test #197
- **Q**: Show defect rate trend last 30 days
- **Expected**: `SELECT date, AVG(defect_rate) as avg_defect_rate FROM kpi_defect_rate_data WHERE date >= CURRENT_DATE - INTERVAL '30 days' GROUP BY date ORDER BY date DESC`
- **Actual**: `SELECT date, defect_rate 
FROM kpi_defect_rate_data 
WHERE date >= CURRENT_DATE - INTERVAL '30 days' 
ORDER BY date DESC 
LIMIT 100`
- **Diagnosis**: Missing GROUP BY

### [FAIL - Mismatch] Test #199
- **Q**: Show defect rate above 5 percent
- **Expected**: `SELECT date, shift_id, furnace_no, defect_rate FROM kpi_defect_rate_data WHERE defect_rate > 5 ORDER BY defect_rate DESC LIMIT 100`
- **Actual**: `SELECT record_id, date, shift_id, defect_rate, furnace_no, machine_id, plant_id, product_type_id 
FROM kpi_defect_rate_data 
WHERE defect_rate > '5' 
ORDER BY date DESC 
LIMIT 100`

### [FAIL - Mismatch] Test #201
- **Q**: Show quality issues by machine
- **Expected**: `SELECT machine_id, AVG(defect_rate) as avg_defect_rate FROM kpi_defect_rate_data GROUP BY machine_id ORDER BY avg_defect_rate DESC`
- **Actual**: `SELECT 
    machine_id, 
    defect_rate 
FROM 
    kpi_defect_rate_data 
ORDER BY 
    machine_id`
- **Diagnosis**: Missing GROUP BY

### [FAIL - Mismatch] Test #202
- **Q**: Show defect rate statistics
- **Expected**: `SELECT MIN(defect_rate) as min_defect, MAX(defect_rate) as max_defect, AVG(defect_rate) as avg_defect, STDDEV(defect_rate) as stddev_defect FROM kpi_defect_rate_data`
- **Actual**: `SELECT record_id, date, shift_id, defect_rate, furnace_no, machine_id, plant_id, product_type_id 
FROM kpi_defect_rate_data 
WHERE date >= CURRENT_DATE - INTERVAL '30 days' 
ORDER BY date DESC 
LIMIT 100`

### [FAIL - Mismatch] Test #203
- **Q**: What is the average energy efficiency?
- **Expected**: `SELECT AVG(energy_efficiency) as avg_energy_efficiency FROM kpi_energy_efficiency_data`
- **Actual**: `SELECT AVG(energy_efficiency) as average_energy_efficiency FROM kpi_energy_efficiency_data`

### [FAIL - Mismatch] Test #204
- **Q**: Show energy efficiency for furnace 1
- **Expected**: `SELECT date, shift_id, energy_efficiency FROM kpi_energy_efficiency_data WHERE furnace_no = 1 ORDER BY date DESC LIMIT 100`
- **Actual**: `SELECT record_id, date, shift_id, energy_efficiency, furnace_no, machine_id, plant_id, product_type_id 
FROM kpi_energy_efficiency_data 
WHERE furnace_no = 1 
ORDER BY date DESC 
LIMIT 100`

### [FAIL - Mismatch] Test #205
- **Q**: Which furnace is most energy efficient?
- **Expected**: `SELECT furnace_no, AVG(energy_efficiency) as avg_efficiency FROM kpi_energy_efficiency_data GROUP BY furnace_no ORDER BY avg_efficiency ASC LIMIT 1`
- **Actual**: `SELECT furnace_no, AVG(energy_efficiency) as avg_energy_efficiency 
FROM kpi_energy_efficiency_data 
GROUP BY furnace_no 
ORDER BY avg_energy_efficiency DESC 
LIMIT 1`

### [FAIL - Mismatch] Test #206
- **Q**: Show energy efficiency by shift
- **Expected**: `SELECT shift_id, AVG(energy_efficiency) as avg_efficiency FROM kpi_energy_efficiency_data GROUP BY shift_id ORDER BY avg_efficiency`
- **Actual**: `SELECT 
    shift_id, 
    AVG(energy_efficiency) AS average_energy_efficiency
FROM 
    kpi_energy_efficiency_data
WHERE 
    date >= CURRENT_DATE - INTERVAL '1 month'
GROUP BY 
    shift_id
ORDER BY 
    average_energy_efficiency DESC`

### [FAIL - Mismatch] Test #207
- **Q**: Show energy efficiency trend
- **Expected**: `SELECT date, AVG(energy_efficiency) as avg_efficiency FROM kpi_energy_efficiency_data GROUP BY date ORDER BY date DESC LIMIT 30`
- **Actual**: `SELECT date, energy_efficiency 
FROM kpi_energy_efficiency_data 
WHERE furnace_no = 1 
ORDER BY date DESC 
LIMIT 100`
- **Diagnosis**: Missing GROUP BY

### [FAIL - Mismatch] Test #208
- **Q**: Compare energy efficiency between furnaces
- **Expected**: `SELECT furnace_no, AVG(energy_efficiency) as avg_efficiency, MIN(energy_efficiency) as min_eff, MAX(energy_efficiency) as max_eff FROM kpi_energy_efficiency_data GROUP BY furnace_no ORDER BY avg_efficiency`
- **Actual**: `SELECT 
  furnace_no, 
  AVG(energy_efficiency) as avg_energy_efficiency
FROM 
  kpi_energy_efficiency_data
GROUP BY 
  furnace_no
ORDER BY 
  avg_energy_efficiency DESC`

### [FAIL - Mismatch] Test #209
- **Q**: Which machines have poor energy efficiency?
- **Expected**: `SELECT machine_id, AVG(energy_efficiency) as avg_efficiency FROM kpi_energy_efficiency_data GROUP BY machine_id ORDER BY avg_efficiency DESC LIMIT 5`
- **Actual**: `SELECT machine_id, AVG(energy_efficiency) as avg_energy_efficiency 
FROM kpi_energy_efficiency_data 
GROUP BY machine_id 
ORDER BY avg_energy_efficiency ASC 
LIMIT 100`

### [FAIL - Mismatch] Test #210
- **Q**: Show energy efficiency by product type
- **Expected**: `SELECT product_type_id, AVG(energy_efficiency) as avg_efficiency FROM kpi_energy_efficiency_data GROUP BY product_type_id ORDER BY avg_efficiency`
- **Actual**: `SELECT 
    product_type_id, 
    AVG(energy_efficiency) AS average_energy_efficiency
FROM 
    kpi_energy_efficiency_data
GROUP BY 
    product_type_id
ORDER BY 
    average_energy_efficiency DESC`

### [FAIL - Mismatch] Test #211
- **Q**: Show energy efficiency above threshold
- **Expected**: `SELECT date, furnace_no, energy_efficiency FROM kpi_energy_efficiency_data WHERE energy_efficiency > 500 ORDER BY energy_efficiency DESC LIMIT 100`
- **Actual**: `SELECT record_id, date, shift_id, energy_efficiency, furnace_no, machine_id, plant_id, product_type_id 
FROM kpi_energy_efficiency_data 
WHERE energy_efficiency > (SELECT AVG(energy_efficiency) FROM kpi_energy_efficiency_data) 
ORDER BY date DESC 
LIMIT 100`

### [FAIL - Mismatch] Test #212
- **Q**: Show kwh per ton statistics
- **Expected**: `SELECT MIN(energy_efficiency) as min_kwh, MAX(energy_efficiency) as max_kwh, AVG(energy_efficiency) as avg_kwh FROM kpi_energy_efficiency_data`
- **Actual**: `SELECT 
    kpi_energy_efficiency_data.furnace_no, 
    kpi_quantity_produced_data.quantity_produced, 
    kpi_energy_used_data.energy_used, 
    (kpi_energy_used_data.energy_used / kpi_quantity_produced_data.quantity_produced) AS kwh_per_ton
FROM 
    kpi_energy_efficiency_data
JOIN 
    kpi_quantity_produced_data ON kpi_energy_efficiency_data.furnace_no = kpi_quantity_produced_data.furnace_no
JOIN 
    kpi_energy_used_data ON kpi_energy_efficiency_data.furnace_no = kpi_energy_used_data.furnace_no
WHERE 
    kpi_energy_efficiency_data.furnace_no = 1
ORDER BY 
    kpi_energy_efficiency_data.date DESC
LIMIT 100`

### [FAIL - Mismatch] Test #213
- **Q**: What is the total energy used?
- **Expected**: `SELECT SUM(energy_used) as total_energy_used FROM kpi_energy_used_data`
- **Actual**: `SELECT SUM(energy_used) as total_energy FROM kpi_energy_used_data`

### [FAIL - Mismatch] Test #215
- **Q**: Show energy used today
- **Expected**: `SELECT furnace_no, SUM(energy_used) as total_energy FROM kpi_energy_used_data WHERE date = CURRENT_DATE GROUP BY furnace_no`
- **Actual**: `SELECT record_id, date, shift_id, energy_used, furnace_no, machine_id, plant_id, product_type_id 
FROM kpi_energy_used_data 
WHERE date = CURRENT_DATE 
ORDER BY date DESC 
LIMIT 100`
- **Diagnosis**: Missing GROUP BY

### [FAIL - Mismatch] Test #218
- **Q**: Show monthly energy consumption
- **Expected**: `SELECT DATE_TRUNC('month', date)::DATE as month, SUM(energy_used) as monthly_energy FROM kpi_energy_used_data GROUP BY DATE_TRUNC('month', date) ORDER BY month DESC`
- **Actual**: `SELECT 
    EXTRACT(MONTH FROM date) AS month,
    SUM(energy_used) AS total_energy
FROM 
    kpi_energy_used_data
GROUP BY 
    EXTRACT(MONTH FROM date)
ORDER BY 
    total_energy DESC`

### [FAIL - Mismatch] Test #220
- **Q**: Show energy consumption last 7 days
- **Expected**: `SELECT date, SUM(energy_used) as daily_total FROM kpi_energy_used_data WHERE date >= CURRENT_DATE - INTERVAL '7 days' GROUP BY date ORDER BY date`
- **Actual**: `SELECT date, shift_id, energy_used, furnace_no, machine_id, plant_id, product_type_id 
FROM kpi_energy_used_data 
WHERE date >= CURRENT_DATE - INTERVAL '7 days' 
ORDER BY date DESC 
LIMIT 100`
- **Diagnosis**: Missing GROUP BY

### [FAIL - Mismatch] Test #221
- **Q**: Compare energy used between furnaces
- **Expected**: `SELECT furnace_no, SUM(energy_used) as total, AVG(energy_used) as avg_per_record FROM kpi_energy_used_data GROUP BY furnace_no ORDER BY total DESC`
- **Actual**: `SELECT furnace_no, SUM(energy_used) as total_energy FROM kpi_energy_used_data GROUP BY furnace_no ORDER BY total_energy DESC`

### [FAIL - Mismatch] Test #222
- **Q**: Show high energy consumption events
- **Expected**: `SELECT date, shift_id, furnace_no, energy_used FROM kpi_energy_used_data WHERE energy_used > (SELECT AVG(energy_used) + STDDEV(energy_used) FROM kpi_energy_used_data) ORDER BY energy_used DESC LIMIT 50`
- **Actual**: `SELECT record_id, date, shift_id, energy_used, furnace_no, machine_id, plant_id, product_type_id 
FROM kpi_energy_used_data 
WHERE energy_used > (SELECT AVG(energy_used) FROM kpi_energy_used_data) 
ORDER BY date DESC 
LIMIT 100`

### [FAIL - Mismatch] Test #225
- **Q**: Show downtime today
- **Expected**: `SELECT furnace_no, SUM(downtime_hours) as downtime FROM kpi_downtime_data WHERE date = CURRENT_DATE GROUP BY furnace_no`
- **Actual**: `SELECT record_id, date, shift_id, downtime_hours, furnace_no, machine_id, plant_id, product_type_id 
FROM kpi_downtime_data 
WHERE date = CURRENT_DATE 
ORDER BY date DESC 
LIMIT 100`
- **Diagnosis**: Missing GROUP BY

### [FAIL - Mismatch] Test #226
- **Q**: Show daily downtime trend
- **Expected**: `SELECT date, SUM(downtime_hours) as daily_downtime FROM kpi_downtime_data GROUP BY date ORDER BY date DESC LIMIT 30`
- **Actual**: `SELECT date, downtime_hours 
FROM kpi_downtime_data 
WHERE furnace_no = 1 
ORDER BY date DESC 
LIMIT 100`
- **Diagnosis**: Missing GROUP BY

### [FAIL - Mismatch] Test #229
- **Q**: Show downtime last week
- **Expected**: `SELECT date, furnace_no, SUM(downtime_hours) as downtime FROM kpi_downtime_data WHERE date >= CURRENT_DATE - INTERVAL '7 days' GROUP BY date, furnace_no ORDER BY date DESC`
- **Actual**: `SELECT record_id, date, shift_id, downtime_hours, furnace_no, machine_id, plant_id, product_type_id 
FROM kpi_downtime_data 
WHERE date >= CURRENT_DATE - INTERVAL '7 days' 
ORDER BY date DESC 
LIMIT 100`
- **Diagnosis**: Missing GROUP BY

### [FAIL - Mismatch] Test #230
- **Q**: What is the average downtime per day
- **Expected**: `SELECT date, AVG(downtime_hours) as avg_downtime FROM kpi_downtime_data GROUP BY date ORDER BY date DESC`
- **Actual**: `SELECT AVG(downtime_hours) as avg_downtime FROM kpi_downtime_data`
- **Diagnosis**: Missing GROUP BY

### [FAIL - Mismatch] Test #231
- **Q**: Show furnaces with high downtime
- **Expected**: `SELECT furnace_no, SUM(downtime_hours) as total_downtime FROM kpi_downtime_data GROUP BY furnace_no HAVING SUM(downtime_hours) > 10 ORDER BY total_downtime DESC`
- **Actual**: `SELECT furnace_no, SUM(downtime_hours) as total_downtime 
FROM kpi_downtime_data 
GROUP BY furnace_no 
ORDER BY total_downtime DESC`

### [FAIL - Mismatch] Test #233
- **Q**: What is the average MTBF?
- **Expected**: `SELECT AVG(mtbf_hours) as avg_mtbf FROM kpi_mean_time_between_failures_data`
- **Actual**: `SELECT AVG(mtbf_hours) as average_mtbf FROM kpi_mean_time_between_failures_data`

### [FAIL - Mismatch] Test #235
- **Q**: Which furnace is most reliable?
- **Expected**: `SELECT furnace_no, AVG(mtbf_hours) as avg_mtbf FROM kpi_mean_time_between_failures_data GROUP BY furnace_no ORDER BY avg_mtbf DESC LIMIT 1`
- **Actual**: `SELECT furnace_no, COUNT(*) as reliability_count FROM furnace_furnaceconfig GROUP BY furnace_no ORDER BY reliability_count DESC LIMIT 1`

### [FAIL - Mismatch] Test #236
- **Q**: Show mtbf trend last 30 days
- **Expected**: `SELECT date, AVG(mtbf_hours) as avg_mtbf FROM kpi_mean_time_between_failures_data WHERE date >= CURRENT_DATE - INTERVAL '30 days' GROUP BY date ORDER BY date DESC`
- **Actual**: `SELECT date, mtbf_hours FROM kpi_mean_time_between_failures_data WHERE date >= CURRENT_DATE - INTERVAL '30 days' ORDER BY date DESC LIMIT 100`
- **Diagnosis**: Missing GROUP BY

### [FAIL - Mismatch] Test #237
- **Q**: Show mtbf by machine
- **Expected**: `SELECT machine_id, AVG(mtbf_hours) as avg_mtbf FROM kpi_mean_time_between_failures_data GROUP BY machine_id ORDER BY avg_mtbf DESC`
- **Actual**: `SELECT machine_id, mtbf_hours FROM kpi_mean_time_between_failures_data ORDER BY date DESC LIMIT 100`
- **Diagnosis**: Missing GROUP BY

### [FAIL - Mismatch] Test #238
- **Q**: Show low reliability furnaces
- **Expected**: `SELECT furnace_no, AVG(mtbf_hours) as avg_mtbf FROM kpi_mean_time_between_failures_data GROUP BY furnace_no HAVING AVG(mtbf_hours) < 50 ORDER BY avg_mtbf`
- **Actual**: `SELECT furnace_no, AVG(mtbf_hours) as avg_mtbf 
FROM kpi_mean_time_between_failures_data 
WHERE mtbf_hours < (SELECT AVG(mtbf_hours) FROM kpi_mean_time_between_failures_data) 
GROUP BY furnace_no 
ORDER BY avg_mtbf ASC`

### [FAIL - Mismatch] Test #239
- **Q**: Show mtbf by shift
- **Expected**: `SELECT shift_id, AVG(mtbf_hours) as avg_mtbf FROM kpi_mean_time_between_failures_data GROUP BY shift_id ORDER BY avg_mtbf DESC`
- **Actual**: `SELECT shift_id, mtbf_hours FROM kpi_mean_time_between_failures_data ORDER BY date DESC LIMIT 100`
- **Diagnosis**: Missing GROUP BY

### [FAIL - Mismatch] Test #240
- **Q**: Show reliability statistics
- **Expected**: `SELECT MIN(mtbf_hours) as min_mtbf, MAX(mtbf_hours) as max_mtbf, AVG(mtbf_hours) as avg_mtbf FROM kpi_mean_time_between_failures_data`
- **Actual**: `SELECT record_id, date, shift_id, mtbf_hours, furnace_no, machine_id, plant_id, product_type_id 
FROM kpi_mean_time_between_failures_data 
WHERE furnace_no = 1 
ORDER BY date DESC 
LIMIT 100`

### [FAIL - Mismatch] Test #241
- **Q**: What is the average MTTR?
- **Expected**: `SELECT AVG(mttr_hours) as avg_mttr FROM kpi_mean_time_to_repair_data`
- **Actual**: `SELECT AVG(mttr_hours) as average_mttr FROM kpi_mean_time_to_repair_data`

### [FAIL - Mismatch] Test #244
- **Q**: Show mttr trend
- **Expected**: `SELECT date, AVG(mttr_hours) as avg_mttr FROM kpi_mean_time_to_repair_data GROUP BY date ORDER BY date DESC LIMIT 30`
- **Actual**: `SELECT date, mttr_hours FROM kpi_mean_time_to_repair_data WHERE furnace_no = 1 ORDER BY date DESC LIMIT 100`
- **Diagnosis**: Missing GROUP BY

### [FAIL - Mismatch] Test #245
- **Q**: Show repair time by machine
- **Expected**: `SELECT machine_id, AVG(mttr_hours) as avg_mttr FROM kpi_mean_time_to_repair_data GROUP BY machine_id ORDER BY avg_mttr DESC`
- **Actual**: `SELECT machine_id, mttr_hours, date FROM kpi_mean_time_to_repair_data ORDER BY date DESC LIMIT 100`
- **Diagnosis**: Missing GROUP BY

### [FAIL - Mismatch] Test #246
- **Q**: Show high repair time incidents
- **Expected**: `SELECT date, furnace_no, mttr_hours FROM kpi_mean_time_to_repair_data WHERE mttr_hours > 4 ORDER BY mttr_hours DESC LIMIT 50`
- **Actual**: `SELECT record_id, date, shift_id, mttr_hours, furnace_no, machine_id, plant_id, product_type_id 
FROM kpi_mean_time_to_repair_data 
WHERE mttr_hours > (SELECT AVG(mttr_hours) FROM kpi_mean_time_to_repair_data) 
ORDER BY date DESC 
LIMIT 100`

### [FAIL - Mismatch] Test #247
- **Q**: Show mttr by shift
- **Expected**: `SELECT shift_id, AVG(mttr_hours) as avg_mttr FROM kpi_mean_time_to_repair_data GROUP BY shift_id ORDER BY avg_mttr`
- **Actual**: `SELECT shift_id, AVG(mttr_hours) AS average_mttr 
FROM kpi_mean_time_to_repair_data 
GROUP BY shift_id`

### [FAIL - Mismatch] Test #248
- **Q**: Show repair time statistics
- **Expected**: `SELECT MIN(mttr_hours) as min_mttr, MAX(mttr_hours) as max_mttr, AVG(mttr_hours) as avg_mttr FROM kpi_mean_time_to_repair_data`
- **Actual**: `SELECT record_id, date, shift_id, mttr_hours, furnace_no, machine_id, plant_id, product_type_id 
FROM kpi_mean_time_to_repair_data 
WHERE furnace_no = 1 
ORDER BY date DESC 
LIMIT 100`

### [FAIL - Mismatch] Test #249
- **Q**: What is the average MTBS?
- **Expected**: `SELECT AVG(mtbs_hours) as avg_mtbs FROM kpi_mean_time_between_stoppages_data`
- **Actual**: `SELECT AVG(mtbs_hours) as average_mtbs FROM kpi_mean_time_between_stoppages_data`

### [FAIL - Mismatch] Test #251
- **Q**: Which furnace has least stoppages?
- **Expected**: `SELECT furnace_no, AVG(mtbs_hours) as avg_mtbs FROM kpi_mean_time_between_stoppages_data GROUP BY furnace_no ORDER BY avg_mtbs DESC LIMIT 1`
- **Actual**: `SELECT furnace_no, SUM(downtime_hours) as total_downtime FROM log_book_furnace_down_time_event GROUP BY furnace_no ORDER BY total_downtime ASC LIMIT 1`

### [FAIL - Mismatch] Test #252
- **Q**: Show mtbs trend
- **Expected**: `SELECT date, AVG(mtbs_hours) as avg_mtbs FROM kpi_mean_time_between_stoppages_data GROUP BY date ORDER BY date DESC LIMIT 30`
- **Actual**: `SELECT date, mtbs_hours FROM kpi_mean_time_between_stoppages_data ORDER BY date DESC LIMIT 100`
- **Diagnosis**: Missing GROUP BY

### [FAIL - Mismatch] Test #253
- **Q**: Show mtbs by machine
- **Expected**: `SELECT machine_id, AVG(mtbs_hours) as avg_mtbs FROM kpi_mean_time_between_stoppages_data GROUP BY machine_id ORDER BY avg_mtbs DESC`
- **Actual**: `SELECT machine_id, mtbs_hours, date FROM kpi_mean_time_between_stoppages_data ORDER BY date DESC LIMIT 100`
- **Diagnosis**: Missing GROUP BY

### [FAIL - Mismatch] Test #254
- **Q**: Show stoppage frequency statistics
- **Expected**: `SELECT MIN(mtbs_hours) as min_mtbs, MAX(mtbs_hours) as max_mtbs, AVG(mtbs_hours) as avg_mtbs FROM kpi_mean_time_between_stoppages_data`
- **Actual**: `SELECT 
  furnace_no, 
  COUNT(*) as stoppage_count, 
  AVG(downtime_hours) as avg_downtime, 
  MAX(downtime_hours) as max_downtime, 
  MIN(downtime_hours) as min_downtime
FROM 
  log_book_furnace_down_time_event
WHERE 
  downtime_type_id IN ('stoppage')
GROUP BY 
  furnace_no
ORDER BY 
  stoppage_count DESC`

### [FAIL - Mismatch] Test #255
- **Q**: What is the average yield?
- **Expected**: `SELECT AVG(yield_percentage) as avg_yield FROM kpi_yield_data`
- **Actual**: `SELECT AVG(yield_percentage) as average_yield FROM kpi_yield_data`

### [FAIL - Mismatch] Test #258
- **Q**: Show yield trend last 30 days
- **Expected**: `SELECT date, AVG(yield_percentage) as avg_yield FROM kpi_yield_data WHERE date >= CURRENT_DATE - INTERVAL '30 days' GROUP BY date ORDER BY date DESC`
- **Actual**: `SELECT date, yield_percentage 
FROM kpi_yield_data 
WHERE date >= CURRENT_DATE - INTERVAL '30 days' 
ORDER BY date DESC 
LIMIT 100`
- **Diagnosis**: Missing GROUP BY

### [FAIL - Mismatch] Test #260
- **Q**: Show low yield records
- **Expected**: `SELECT date, shift_id, furnace_no, yield_percentage FROM kpi_yield_data WHERE yield_percentage < 85 ORDER BY yield_percentage ASC LIMIT 100`
- **Actual**: `SELECT record_id, date, shift_id, yield_percentage, furnace_no, machine_id, plant_id, product_type_id 
FROM kpi_yield_data 
WHERE yield_percentage < 50 
ORDER BY date DESC 
LIMIT 100`

### [FAIL - Mismatch] Test #262
- **Q**: Compare yield between furnaces
- **Expected**: `SELECT furnace_no, AVG(yield_percentage) as avg_yield, MIN(yield_percentage) as min_yield, MAX(yield_percentage) as max_yield FROM kpi_yield_data GROUP BY furnace_no ORDER BY avg_yield DESC`
- **Actual**: `SELECT furnace_no, AVG(yield_percentage) as avg_yield 
FROM kpi_yield_data 
GROUP BY furnace_no 
ORDER BY avg_yield DESC`

### [FAIL - Mismatch] Test #263
- **Q**: Show daily yield summary
- **Expected**: `SELECT date, AVG(yield_percentage) as avg_yield, COUNT(*) as records FROM kpi_yield_data GROUP BY date ORDER BY date DESC LIMIT 30`
- **Actual**: `SELECT date, furnace_no, yield_percentage 
FROM kpi_yield_data 
WHERE furnace_no = 1 
ORDER BY date DESC 
LIMIT 100`
- **Diagnosis**: Missing GROUP BY

### [FAIL - Mismatch] Test #264
- **Q**: Show yield statistics by furnace
- **Expected**: `SELECT furnace_no, AVG(yield_percentage) as avg_yield, STDDEV(yield_percentage) as stddev_yield FROM kpi_yield_data GROUP BY furnace_no ORDER BY avg_yield DESC`
- **Actual**: `SELECT furnace_no, AVG(yield_percentage) as avg_yield, SUM(yield_percentage) as total_yield, COUNT(*) as num_records 
FROM kpi_yield_data 
GROUP BY furnace_no 
ORDER BY avg_yield DESC`

### [FAIL - Mismatch] Test #265
- **Q**: What is the average first pass yield?
- **Expected**: `SELECT AVG(first_pass_yield) as avg_fpy FROM kpi_first_pass_yield_data`
- **Actual**: `SELECT AVG(first_pass_yield) AS average_first_pass_yield FROM kpi_first_pass_yield_data`

### [FAIL - Mismatch] Test #266
- **Q**: Show first pass yield by furnace
- **Expected**: `SELECT furnace_no, AVG(first_pass_yield) as avg_fpy FROM kpi_first_pass_yield_data GROUP BY furnace_no ORDER BY avg_fpy DESC`
- **Actual**: `SELECT 
    furnace_no, 
    AVG(first_pass_yield) AS average_first_pass_yield
FROM 
    kpi_first_pass_yield_data
GROUP BY 
    furnace_no
ORDER BY 
    average_first_pass_yield DESC`

### [FAIL - Mismatch] Test #267
- **Q**: Show fpy trend
- **Expected**: `SELECT date, AVG(first_pass_yield) as avg_fpy FROM kpi_first_pass_yield_data GROUP BY date ORDER BY date DESC LIMIT 30`
- **Actual**: `SELECT date, first_pass_yield 
FROM kpi_first_pass_yield_data 
WHERE furnace_no = 1 
ORDER BY date DESC 
LIMIT 100`
- **Diagnosis**: Missing GROUP BY

### [FAIL - Mismatch] Test #268
- **Q**: Show low fpy records
- **Expected**: `SELECT date, furnace_no, first_pass_yield FROM kpi_first_pass_yield_data WHERE first_pass_yield < 90 ORDER BY first_pass_yield ASC LIMIT 50`
- **Actual**: `SELECT record_id, date, shift_id, first_pass_yield, furnace_no, machine_id, plant_id, product_type_id 
FROM kpi_first_pass_yield_data 
WHERE first_pass_yield < 0.5 
ORDER BY date DESC 
LIMIT 100`

### [FAIL - Mismatch] Test #269
- **Q**: Show first pass yield by shift
- **Expected**: `SELECT shift_id, AVG(first_pass_yield) as avg_fpy FROM kpi_first_pass_yield_data GROUP BY shift_id ORDER BY avg_fpy DESC`
- **Actual**: `SELECT shift_id, first_pass_yield FROM kpi_first_pass_yield_data ORDER BY date DESC LIMIT 100`
- **Diagnosis**: Missing GROUP BY

### [FAIL - Mismatch] Test #271
- **Q**: What is the average rework rate?
- **Expected**: `SELECT AVG(rework_rate_percentage) as avg_rework FROM kpi_rework_rate_data`
- **Actual**: `SELECT AVG(rework_rate_percentage) as average_rework_rate FROM kpi_rework_rate_data`

### [FAIL - Mismatch] Test #272
- **Q**: Show rework rate by furnace
- **Expected**: `SELECT furnace_no, AVG(rework_rate_percentage) as avg_rework FROM kpi_rework_rate_data GROUP BY furnace_no ORDER BY avg_rework DESC`
- **Actual**: `SELECT furnace_no, AVG(rework_rate_percentage) as avg_rework_rate 
FROM kpi_rework_rate_data 
GROUP BY furnace_no 
ORDER BY avg_rework_rate DESC`

### [FAIL - Mismatch] Test #273
- **Q**: Show high rework rate records
- **Expected**: `SELECT date, furnace_no, rework_rate_percentage FROM kpi_rework_rate_data WHERE rework_rate_percentage > 5 ORDER BY rework_rate_percentage DESC LIMIT 50`
- **Actual**: `SELECT record_id, date, shift_id, rework_rate_percentage, furnace_no, machine_id, plant_id, product_type_id 
FROM kpi_rework_rate_data 
WHERE rework_rate_percentage > (SELECT AVG(rework_rate_percentage) FROM kpi_rework_rate_data) 
ORDER BY date DESC 
LIMIT 100`

### [FAIL - Mismatch] Test #274
- **Q**: Show rework rate trend
- **Expected**: `SELECT date, AVG(rework_rate_percentage) as avg_rework FROM kpi_rework_rate_data GROUP BY date ORDER BY date DESC LIMIT 30`
- **Actual**: `SELECT date, rework_rate_percentage 
FROM kpi_rework_rate_data 
WHERE furnace_no = 1 
ORDER BY date DESC 
LIMIT 100`
- **Diagnosis**: Missing GROUP BY

### [FAIL - Mismatch] Test #275
- **Q**: Show rework by shift
- **Expected**: `SELECT shift_id, AVG(rework_rate_percentage) as avg_rework FROM kpi_rework_rate_data GROUP BY shift_id ORDER BY avg_rework DESC`
- **Actual**: `SELECT shift_id, rework_rate_percentage FROM kpi_rework_rate_data ORDER BY date DESC LIMIT 100`
- **Diagnosis**: Missing GROUP BY

### [FAIL - Mismatch] Test #277
- **Q**: What is the average capacity utilization?
- **Expected**: `SELECT AVG(utilization_percentage) as avg_utilization FROM kpi_resource_capacity_utilization_data`
- **Actual**: `SELECT AVG(utilization_percentage) as average_capacity_utilization FROM kpi_resource_capacity_utilization_data`

### [FAIL - Mismatch] Test #278
- **Q**: Show capacity utilization by furnace
- **Expected**: `SELECT furnace_no, AVG(utilization_percentage) as avg_utilization FROM kpi_resource_capacity_utilization_data GROUP BY furnace_no ORDER BY avg_utilization DESC`
- **Actual**: `SELECT 
    furnace_no, 
    AVG(utilization_percentage) AS average_utilization_percentage
FROM 
    kpi_resource_capacity_utilization_data
GROUP BY 
    furnace_no
ORDER BY 
    average_utilization_percentage DESC`

### [FAIL - Mismatch] Test #279
- **Q**: Show low utilization furnaces
- **Expected**: `SELECT furnace_no, AVG(utilization_percentage) as avg_utilization FROM kpi_resource_capacity_utilization_data GROUP BY furnace_no HAVING AVG(utilization_percentage) < 70 ORDER BY avg_utilization`
- **Actual**: `SELECT furnace_no, utilization_percentage 
FROM kpi_resource_capacity_utilization_data 
WHERE utilization_percentage < 50 
ORDER BY utilization_percentage ASC 
LIMIT 100`
- **Diagnosis**: Missing GROUP BY

### [FAIL - Mismatch] Test #280
- **Q**: Show utilization trend
- **Expected**: `SELECT date, AVG(utilization_percentage) as avg_utilization FROM kpi_resource_capacity_utilization_data GROUP BY date ORDER BY date DESC LIMIT 30`
- **Actual**: `SELECT date, utilization_percentage 
FROM kpi_resource_capacity_utilization_data 
WHERE furnace_no = 1 
ORDER BY date DESC 
LIMIT 100`
- **Diagnosis**: Missing GROUP BY

### [FAIL - Mismatch] Test #281
- **Q**: Show utilization by shift
- **Expected**: `SELECT shift_id, AVG(utilization_percentage) as avg_utilization FROM kpi_resource_capacity_utilization_data GROUP BY shift_id ORDER BY avg_utilization DESC`
- **Actual**: `SELECT shift_id, utilization_percentage, date FROM kpi_resource_capacity_utilization_data ORDER BY date DESC LIMIT 100`
- **Diagnosis**: Missing GROUP BY

### [FAIL - Mismatch] Test #282
- **Q**: Show machine utilization
- **Expected**: `SELECT machine_id, AVG(utilization_percentage) as avg_utilization FROM kpi_resource_capacity_utilization_data GROUP BY machine_id ORDER BY avg_utilization DESC`
- **Actual**: `SELECT record_id, date, shift_id, utilization_percentage, furnace_no, machine_id, plant_id, product_type_id 
FROM kpi_resource_capacity_utilization_data 
WHERE furnace_no = 1 
ORDER BY date DESC 
LIMIT 100`
- **Diagnosis**: Missing GROUP BY

### [FAIL - Mismatch] Test #284
- **Q**: Show production by furnace
- **Expected**: `SELECT furnace_no, SUM(quantity_produced) as total_production FROM kpi_quantity_produced_data GROUP BY furnace_no ORDER BY total_production DESC`
- **Actual**: `SELECT 
  f.furnace_no, 
  SUM(cp.cast_weight) as total_production
FROM 
  core_process_tap_production cp
  JOIN furnace_furnaceconfig f ON cp.furnace_no = f.furnace_no
GROUP BY 
  f.furnace_no
ORDER BY 
  total_production DESC`

### [FAIL - Mismatch] Test #285
- **Q**: Show daily production
- **Expected**: `SELECT date, SUM(quantity_produced) as daily_production FROM kpi_quantity_produced_data GROUP BY date ORDER BY date DESC LIMIT 30`
- **Actual**: `SELECT tap_production_datetime, cast_weight 
FROM core_process_tap_production 
WHERE furnace_no = 1 
ORDER BY tap_production_datetime DESC 
LIMIT 100`
- **Diagnosis**: Missing GROUP BY

### [FAIL - Mismatch] Test #286
- **Q**: Show production by shift
- **Expected**: `SELECT shift_id, SUM(quantity_produced) as total_production FROM kpi_quantity_produced_data GROUP BY shift_id ORDER BY total_production DESC`
- **Actual**: `SELECT shift_id, SUM(cast_weight) as total_production FROM core_process_tap_production GROUP BY shift_id ORDER BY total_production DESC`

### [FAIL - Mismatch] Test #287
- **Q**: Show production by product type
- **Expected**: `SELECT product_type_id, SUM(quantity_produced) as total_production FROM kpi_quantity_produced_data GROUP BY product_type_id ORDER BY total_production DESC`
- **Actual**: `SELECT product_type_id, SUM(cast_weight) as total_production 
FROM core_process_tap_production 
GROUP BY product_type_id 
ORDER BY total_production DESC`

### [FAIL - Mismatch] Test #288
- **Q**: Show top producing furnaces
- **Expected**: `SELECT furnace_no, SUM(quantity_produced) as total_production FROM kpi_quantity_produced_data GROUP BY furnace_no ORDER BY total_production DESC LIMIT 5`
- **Actual**: `SELECT furnace_no, SUM(quantity_produced) as total_qty 
FROM kpi_quantity_produced_data 
GROUP BY furnace_no 
ORDER BY total_qty DESC`

### [FAIL - Mismatch] Test #289
- **Q**: Show monthly production
- **Expected**: `SELECT DATE_TRUNC('month', date)::DATE as month, SUM(quantity_produced) as monthly_production FROM kpi_quantity_produced_data GROUP BY DATE_TRUNC('month', date) ORDER BY month DESC`
- **Actual**: `SELECT EXTRACT(MONTH FROM tap_production_datetime) AS month, SUM(cast_weight) AS total_production 
FROM core_process_tap_production 
GROUP BY EXTRACT(MONTH FROM tap_production_datetime) 
ORDER BY month DESC`

### [FAIL - Mismatch] Test #290
- **Q**: Show production trend last week
- **Expected**: `SELECT date, SUM(quantity_produced) as daily_production FROM kpi_quantity_produced_data WHERE date >= CURRENT_DATE - INTERVAL '7 days' GROUP BY date ORDER BY date`
- **Actual**: `SELECT tap_production_datetime, cast_weight 
FROM core_process_tap_production 
WHERE tap_production_datetime >= CURRENT_DATE - INTERVAL '7 days' 
ORDER BY tap_production_datetime DESC 
LIMIT 100`
- **Diagnosis**: Missing GROUP BY

### [FAIL - Mismatch] Test #291
- **Q**: What is the average output rate?
- **Expected**: `SELECT AVG(output_rate_percentage) as avg_output_rate FROM kpi_output_rate_data`
- **Actual**: `SELECT AVG(output_rate_percentage) AS average_output_rate FROM kpi_output_rate_data`

### [FAIL - Mismatch] Test #292
- **Q**: Show output rate by furnace
- **Expected**: `SELECT furnace_no, AVG(output_rate_percentage) as avg_output_rate FROM kpi_output_rate_data GROUP BY furnace_no ORDER BY avg_output_rate DESC`
- **Actual**: `SELECT furnace_no, output_rate_percentage FROM kpi_output_rate_data ORDER BY date DESC LIMIT 100`
- **Diagnosis**: Missing GROUP BY

### [FAIL - Mismatch] Test #293
- **Q**: Show output rate trend
- **Expected**: `SELECT date, AVG(output_rate_percentage) as avg_output_rate FROM kpi_output_rate_data GROUP BY date ORDER BY date DESC LIMIT 30`
- **Actual**: `SELECT record_id, date, shift_id, output_rate_percentage, furnace_no, machine_id, plant_id, product_type_id 
FROM kpi_output_rate_data 
WHERE furnace_no = 1 
ORDER BY date DESC 
LIMIT 100`
- **Diagnosis**: Missing GROUP BY

### [FAIL - Mismatch] Test #294
- **Q**: Show low output rate records
- **Expected**: `SELECT date, furnace_no, output_rate_percentage FROM kpi_output_rate_data WHERE output_rate_percentage < 80 ORDER BY output_rate_percentage ASC LIMIT 50`
- **Actual**: `SELECT record_id, date, shift_id, output_rate_percentage, furnace_no, machine_id, plant_id, product_type_id 
FROM kpi_output_rate_data 
WHERE output_rate_percentage < (SELECT AVG(output_rate_percentage) FROM kpi_output_rate_data) 
ORDER BY date DESC 
LIMIT 100`

### [FAIL - Mismatch] Test #295
- **Q**: Show output rate by shift
- **Expected**: `SELECT shift_id, AVG(output_rate_percentage) as avg_output_rate FROM kpi_output_rate_data GROUP BY shift_id ORDER BY avg_output_rate DESC`
- **Actual**: `SELECT 
    shift_id, 
    AVG(output_rate_percentage) AS average_output_rate
FROM 
    kpi_output_rate_data
GROUP BY 
    shift_id
ORDER BY 
    average_output_rate DESC`

### [FAIL - Mismatch] Test #297
- **Q**: What is the average production efficiency?
- **Expected**: `SELECT AVG(production_efficiency_percentage) as avg_efficiency FROM kpi_production_efficiency_data`
- **Actual**: `SELECT AVG(production_efficiency_percentage) as average_production_efficiency FROM kpi_production_efficiency_data`

### [FAIL - Mismatch] Test #298
- **Q**: Show production efficiency by furnace
- **Expected**: `SELECT furnace_no, AVG(production_efficiency_percentage) as avg_efficiency FROM kpi_production_efficiency_data GROUP BY furnace_no ORDER BY avg_efficiency DESC`
- **Actual**: `SELECT furnace_no, production_efficiency_percentage 
FROM kpi_production_efficiency_data 
ORDER BY date DESC 
LIMIT 100`
- **Diagnosis**: Missing GROUP BY

### [FAIL - Mismatch] Test #299
- **Q**: Show efficiency trend
- **Expected**: `SELECT date, AVG(production_efficiency_percentage) as avg_efficiency FROM kpi_production_efficiency_data GROUP BY date ORDER BY date DESC LIMIT 30`
- **Actual**: `SELECT date, oee_percentage 
FROM kpi_overall_equipment_efficiency_data 
WHERE furnace_no = 1 
ORDER BY date DESC 
LIMIT 100`
- **Diagnosis**: Missing GROUP BY

### [FAIL - Mismatch] Test #300
- **Q**: Show low efficiency records
- **Expected**: `SELECT date, furnace_no, production_efficiency_percentage FROM kpi_production_efficiency_data WHERE production_efficiency_percentage < 75 ORDER BY production_efficiency_percentage ASC LIMIT 50`
- **Actual**: `SELECT record_id, date, shift_id, oee_percentage, furnace_no, machine_id, plant_id, product_type_id 
FROM kpi_overall_equipment_efficiency_data 
WHERE oee_percentage < (SELECT AVG(oee_percentage) FROM kpi_overall_equipment_efficiency_data) 
ORDER BY date DESC 
LIMIT 100`

### [FAIL - Mismatch] Test #301
- **Q**: Show efficiency by shift
- **Expected**: `SELECT shift_id, AVG(production_efficiency_percentage) as avg_efficiency FROM kpi_production_efficiency_data GROUP BY shift_id ORDER BY avg_efficiency DESC`
- **Actual**: `SELECT shift_id, AVG(oee_percentage) as avg_efficiency 
FROM kpi_overall_equipment_efficiency_data 
GROUP BY shift_id 
ORDER BY avg_efficiency DESC`

### [FAIL - Mismatch] Test #302
- **Q**: Which furnace is most efficient?
- **Expected**: `SELECT furnace_no, AVG(production_efficiency_percentage) as avg_efficiency FROM kpi_production_efficiency_data GROUP BY furnace_no ORDER BY avg_efficiency DESC LIMIT 1`
- **Actual**: `SELECT furnace_no, AVG(oee_percentage) as avg_oee FROM kpi_overall_equipment_efficiency_data GROUP BY furnace_no ORDER BY avg_oee DESC LIMIT 1`

### [FAIL - Mismatch] Test #303
- **Q**: What is the production efficiency percentage in July?
- **Expected**: `SELECT AVG(production_efficiency_percentage) as avg_efficiency FROM kpi_production_efficiency_data WHERE EXTRACT(MONTH FROM date) = 7`
- **Actual**: `SELECT AVG(production_efficiency_percentage) 
FROM kpi_production_efficiency_data 
WHERE EXTRACT(MONTH FROM date) = 7`

### [FAIL - Mismatch] Test #304
- **Q**: Show production efficiency in the month of july
- **Expected**: `SELECT AVG(production_efficiency_percentage) as avg_efficiency FROM kpi_production_efficiency_data WHERE EXTRACT(MONTH FROM date) = 7`
- **Actual**: `SELECT date, shift_id, production_efficiency_percentage, furnace_no, machine_id, plant_id, product_type_id 
FROM kpi_production_efficiency_data 
WHERE EXTRACT(MONTH FROM date) = 7 
ORDER BY date DESC 
LIMIT 100`

### [FAIL - Mismatch] Test #305
- **Q**: Show production efficiency for January
- **Expected**: `SELECT AVG(production_efficiency_percentage) as avg_efficiency FROM kpi_production_efficiency_data WHERE EXTRACT(MONTH FROM date) = 1`
- **Actual**: `SELECT record_id, date, shift_id, production_efficiency_percentage, furnace_no, machine_id, plant_id, product_type_id 
FROM kpi_production_efficiency_data 
WHERE EXTRACT(MONTH FROM date) = 1 
ORDER BY date DESC 
LIMIT 100`

### [FAIL - Mismatch] Test #306
- **Q**: Show production efficiency percentage by month
- **Expected**: `SELECT EXTRACT(MONTH FROM date) as month, AVG(production_efficiency_percentage) as avg_efficiency FROM kpi_production_efficiency_data GROUP BY EXTRACT(MONTH FROM date) ORDER BY month`
- **Actual**: `SELECT 
    EXTRACT(MONTH FROM date) AS month,
    AVG(production_efficiency_percentage) AS avg_production_efficiency
FROM 
    kpi_production_efficiency_data
GROUP BY 
    EXTRACT(MONTH FROM date)
ORDER BY 
    avg_production_efficiency DESC`

### [FAIL - Mismatch] Test #307
- **Q**: What is the average on-time delivery?
- **Expected**: `SELECT AVG(on_time_delivery_percentage) as avg_otd FROM kpi_on_time_delivery_data`
- **Actual**: `SELECT AVG(on_time_delivery_percentage) as average_on_time_delivery FROM kpi_on_time_delivery_data`

### [FAIL - Mismatch] Test #308
- **Q**: Show on-time delivery by furnace
- **Expected**: `SELECT furnace_no, AVG(on_time_delivery_percentage) as avg_otd FROM kpi_on_time_delivery_data GROUP BY furnace_no ORDER BY avg_otd DESC`
- **Actual**: `SELECT furnace_no, on_time_delivery_percentage 
FROM kpi_on_time_delivery_data 
WHERE furnace_no IN (1, 2, 3) 
ORDER BY date DESC 
LIMIT 100`
- **Diagnosis**: Missing GROUP BY

### [FAIL - Mismatch] Test #309
- **Q**: Show otd trend
- **Expected**: `SELECT date, AVG(on_time_delivery_percentage) as avg_otd FROM kpi_on_time_delivery_data GROUP BY date ORDER BY date DESC LIMIT 30`
- **Actual**: `SELECT date, on_time_delivery_percentage 
FROM kpi_on_time_delivery_data 
WHERE furnace_no = 1 
ORDER BY date DESC 
LIMIT 100`
- **Diagnosis**: Missing GROUP BY

### [FAIL - Mismatch] Test #310
- **Q**: Show low otd records
- **Expected**: `SELECT date, furnace_no, on_time_delivery_percentage FROM kpi_on_time_delivery_data WHERE on_time_delivery_percentage < 90 ORDER BY on_time_delivery_percentage ASC LIMIT 50`
- **Actual**: `SELECT record_id, date, shift_id, on_time_delivery_percentage, furnace_no, machine_id, plant_id, product_type_id 
FROM kpi_on_time_delivery_data 
WHERE on_time_delivery_percentage < 0.5 
ORDER BY date DESC 
LIMIT 100`

### [FAIL - Mismatch] Test #311
- **Q**: Show delivery performance by shift
- **Expected**: `SELECT shift_id, AVG(on_time_delivery_percentage) as avg_otd FROM kpi_on_time_delivery_data GROUP BY shift_id ORDER BY avg_otd DESC`
- **Actual**: `SELECT shift_id, AVG(on_time_delivery_percentage) as avg_on_time_delivery FROM kpi_on_time_delivery_data GROUP BY shift_id ORDER BY avg_on_time_delivery DESC`

### [FAIL - Mismatch] Test #312
- **Q**: What is the best delivery performance
- **Expected**: `SELECT furnace_no, AVG(on_time_delivery_percentage) as avg_otd FROM kpi_on_time_delivery_data GROUP BY furnace_no ORDER BY avg_otd DESC LIMIT 1`
- **Actual**: `SELECT AVG(on_time_delivery_percentage) as avg_on_time_delivery FROM kpi_on_time_delivery_data`
- **Diagnosis**: Missing GROUP BY

### [FAIL - Mismatch] Test #313
- **Q**: What is the average maintenance compliance?
- **Expected**: `SELECT AVG(compliance_percentage) as avg_compliance FROM kpi_maintenance_compliance_data`
- **Actual**: `SELECT AVG(compliance_percentage) as average_compliance FROM kpi_maintenance_compliance_data`

### [FAIL - Mismatch] Test #314
- **Q**: Show maintenance compliance by furnace
- **Expected**: `SELECT furnace_no, AVG(compliance_percentage) as avg_compliance FROM kpi_maintenance_compliance_data GROUP BY furnace_no ORDER BY avg_compliance DESC`
- **Actual**: `SELECT furnace_no, compliance_percentage 
FROM kpi_maintenance_compliance_data 
WHERE furnace_no IN (1, 2, 3) 
ORDER BY date DESC 
LIMIT 100`
- **Diagnosis**: Missing GROUP BY

### [FAIL - Mismatch] Test #315
- **Q**: Show compliance trend
- **Expected**: `SELECT date, AVG(compliance_percentage) as avg_compliance FROM kpi_maintenance_compliance_data GROUP BY date ORDER BY date DESC LIMIT 30`
- **Actual**: `SELECT date, compliance_percentage 
FROM kpi_maintenance_compliance_data 
WHERE furnace_no = 1 
ORDER BY date DESC 
LIMIT 100`
- **Diagnosis**: Missing GROUP BY

### [FAIL - Mismatch] Test #316
- **Q**: Show low compliance records
- **Expected**: `SELECT date, furnace_no, compliance_percentage FROM kpi_maintenance_compliance_data WHERE compliance_percentage < 90 ORDER BY compliance_percentage ASC LIMIT 50`
- **Actual**: `SELECT record_id, date, shift_id, compliance_percentage, furnace_no, machine_id, plant_id, product_type_id 
FROM kpi_maintenance_compliance_data 
WHERE compliance_percentage < 0.5 
ORDER BY date DESC 
LIMIT 100`

### [FAIL - Mismatch] Test #317
- **Q**: Show compliance by shift
- **Expected**: `SELECT shift_id, AVG(compliance_percentage) as avg_compliance FROM kpi_maintenance_compliance_data GROUP BY shift_id ORDER BY avg_compliance DESC`
- **Actual**: `SELECT 
    shift_id, 
    AVG(compliance_percentage) AS average_compliance_percentage
FROM 
    kpi_maintenance_compliance_data
WHERE 
    date >= CURRENT_DATE - INTERVAL '7 day'
GROUP BY 
    shift_id
ORDER BY 
    average_compliance_percentage DESC`

### [FAIL - Mismatch] Test #319
- **Q**: What is the average planned maintenance?
- **Expected**: `SELECT AVG(planned_maintenance_percentage) as avg_planned FROM kpi_planned_maintenance_data`
- **Actual**: `SELECT AVG(planned_maintenance_percentage) as average_planned_maintenance FROM kpi_planned_maintenance_data`

### [FAIL - Mismatch] Test #320
- **Q**: Show planned maintenance by furnace
- **Expected**: `SELECT furnace_no, AVG(planned_maintenance_percentage) as avg_planned FROM kpi_planned_maintenance_data GROUP BY furnace_no ORDER BY avg_planned DESC`
- **Actual**: `SELECT 
    furnace_no, 
    planned_maintenance_percentage, 
    date
FROM 
    kpi_planned_maintenance_data
ORDER BY 
    date DESC`
- **Diagnosis**: Missing GROUP BY

### [FAIL - Mismatch] Test #321
- **Q**: Show planned maintenance trend
- **Expected**: `SELECT date, AVG(planned_maintenance_percentage) as avg_planned FROM kpi_planned_maintenance_data GROUP BY date ORDER BY date DESC LIMIT 30`
- **Actual**: `SELECT date, planned_maintenance_percentage 
FROM kpi_planned_maintenance_data 
ORDER BY date DESC 
LIMIT 100`
- **Diagnosis**: Missing GROUP BY

### [FAIL - Mismatch] Test #322
- **Q**: Show low planned maintenance
- **Expected**: `SELECT date, furnace_no, planned_maintenance_percentage FROM kpi_planned_maintenance_data WHERE planned_maintenance_percentage < 80 ORDER BY planned_maintenance_percentage ASC LIMIT 50`
- **Actual**: `SELECT record_id, date, shift_id, planned_maintenance_percentage, furnace_no, machine_id, plant_id, product_type_id 
FROM kpi_planned_maintenance_data 
WHERE planned_maintenance_percentage < 50 
ORDER BY date DESC 
LIMIT 100`

### [FAIL - Mismatch] Test #323
- **Q**: Show scheduled maintenance by shift
- **Expected**: `SELECT shift_id, AVG(planned_maintenance_percentage) as avg_planned FROM kpi_planned_maintenance_data GROUP BY shift_id ORDER BY avg_planned DESC`
- **Actual**: `SELECT 
    kpm.shift_id, 
    kpm.date, 
    kpm.planned_maintenance_percentage
FROM 
    kpi_planned_maintenance_data kpm
ORDER BY 
    kpm.date DESC`
- **Diagnosis**: Missing GROUP BY

### [FAIL - Mismatch] Test #324
- **Q**: Show maintenance schedule statistics
- **Expected**: `SELECT MIN(planned_maintenance_percentage) as min_planned, MAX(planned_maintenance_percentage) as max_planned, AVG(planned_maintenance_percentage) as avg_planned FROM kpi_planned_maintenance_data`
- **Actual**: `SELECT 
  p.plant_name, 
  f.furnace_no, 
  AVG(k.maintenance_compliance) as avg_maintenance_compliance,
  SUM(k.planned_maintenance) as total_planned_maintenance
FROM 
  kpi_maintenance_compliance_data k
JOIN 
  furnace_furnaceconfig f ON k.furnace_no = f.furnace_no
JOIN 
  plant_plant p ON k.plant_id = p.plant_id
GROUP BY 
  p.plant_name, 
  f.furnace_no
ORDER BY 
  avg_maintenance_compliance DESC`

### [FAIL - Mismatch] Test #325
- **Q**: What is the average safety incidents percentage?
- **Expected**: `SELECT AVG(incidents_percentage) as avg_incidents FROM kpi_safety_incidents_reported_data`
- **Actual**: `SELECT AVG(incidents_percentage) as average_safety_incidents FROM kpi_safety_incidents_reported_data`

### [FAIL - Mismatch] Test #326
- **Q**: Show safety incidents by furnace
- **Expected**: `SELECT furnace_no, AVG(incidents_percentage) as avg_incidents FROM kpi_safety_incidents_reported_data GROUP BY furnace_no ORDER BY avg_incidents DESC`
- **Actual**: `SELECT 
    furnace_no, 
    COUNT(record_id) AS total_safety_incidents
FROM 
    kpi_safety_incidents_reported_data
GROUP BY 
    furnace_no
ORDER BY 
    furnace_no`

### [FAIL - Mismatch] Test #327
- **Q**: Show safety incidents trend
- **Expected**: `SELECT date, AVG(incidents_percentage) as avg_incidents FROM kpi_safety_incidents_reported_data GROUP BY date ORDER BY date DESC LIMIT 30`
- **Actual**: `SELECT date, incidents_percentage 
FROM kpi_safety_incidents_reported_data 
WHERE furnace_no = 1 
ORDER BY date DESC 
LIMIT 100`
- **Diagnosis**: Missing GROUP BY

### [FAIL - Mismatch] Test #328
- **Q**: Show high incident records
- **Expected**: `SELECT date, furnace_no, incidents_percentage FROM kpi_safety_incidents_reported_data WHERE incidents_percentage > 5 ORDER BY incidents_percentage DESC LIMIT 50`
- **Actual**: `SELECT record_id, date, shift_id, furnace_no, machine_id, plant_id, product_type_id 
FROM kpi_safety_incidents_reported_data 
ORDER BY incidents_percentage DESC 
LIMIT 100`
- **Diagnosis**: Missing WHERE clause

### [FAIL - Mismatch] Test #329
- **Q**: Show safety by shift
- **Expected**: `SELECT shift_id, AVG(incidents_percentage) as avg_incidents FROM kpi_safety_incidents_reported_data GROUP BY shift_id ORDER BY avg_incidents DESC`
- **Actual**: `SELECT shift_id, incidents_percentage 
FROM kpi_safety_incidents_reported_data 
ORDER BY shift_id`
- **Diagnosis**: Missing GROUP BY

### [FAIL - Mismatch] Test #330
- **Q**: Which area has most incidents?
- **Expected**: `SELECT machine_id, AVG(incidents_percentage) as avg_incidents FROM kpi_safety_incidents_reported_data GROUP BY machine_id ORDER BY avg_incidents DESC LIMIT 5`
- **Actual**: `SELECT workshop_id, AVG(incidents_percentage) as avg_incidents FROM kpi_safety_incidents_reported_data GROUP BY workshop_id ORDER BY avg_incidents DESC LIMIT 1`

### [FAIL - Mismatch] Test #332
- **Q**: Show cast weight by plant
- **Expected**: `SELECT plant_id, SUM(cast_weight) as total_cast_weight FROM core_process_tap_production GROUP BY plant_id ORDER BY total_cast_weight DESC`
- **Actual**: `SELECT p.plant_name, tp.cast_weight 
FROM core_process_tap_production tp 
JOIN plant_plant p ON tp.plant_id = p.id 
ORDER BY tp.tap_production_datetime DESC 
LIMIT 100`
- **Diagnosis**: Missing GROUP BY

### [FAIL - Mismatch] Test #333
- **Q**: Show daily tap production
- **Expected**: `SELECT DATE_TRUNC('day', tap_production_datetime)::DATE as production_date, COUNT(DISTINCT tap_id) as tap_count, SUM(cast_weight) as total_weight FROM core_process_tap_production GROUP BY DATE_TRUNC('day', tap_production_datetime) ORDER BY production_date DESC LIMIT 30`
- **Actual**: `SELECT tap_production_datetime, cast_weight, liquid_weight, energy, energy_efficiency, graded_cast_weight, downgrade_quantity, ladle_number_code 
FROM core_process_tap_production 
WHERE tap_production_datetime >= CURRENT_DATE - INTERVAL '7 days' 
ORDER BY tap_production_datetime DESC 
LIMIT 100`
- **Diagnosis**: Missing GROUP BY

### [FAIL - Mismatch] Test #334
- **Q**: Show recent tap production
- **Expected**: `SELECT tap_id, cast_weight, liquid_weight, energy, tap_production_datetime FROM core_process_tap_production ORDER BY tap_production_datetime DESC LIMIT 20`
- **Actual**: `SELECT tap_id, tap_production_datetime, cast_weight, liquid_weight, energy, energy_efficiency, graded_cast_weight, downgrade_quantity, ladle_number_code 
FROM core_process_tap_production 
ORDER BY tap_production_datetime DESC 
LIMIT 100`

### [FAIL - Mismatch] Test #335
- **Q**: What is the average energy per tap
- **Expected**: `SELECT AVG(energy) as avg_energy FROM core_process_tap_production`
- **Actual**: `SELECT AVG(energy) as average_energy FROM core_process_tap_production`

### [FAIL - Mismatch] Test #336
- **Q**: Show tap production energy efficiency
- **Expected**: `SELECT AVG(energy_efficiency) as avg_energy_efficiency FROM core_process_tap_production`
- **Actual**: `SELECT date, shift_id, energy_efficiency, furnace_no, machine_id, plant_id, product_type_id 
FROM kpi_energy_efficiency_data 
WHERE furnace_no = 1 
ORDER BY date DESC 
LIMIT 100`

### [FAIL - Mismatch] Test #338
- **Q**: Show slag weight by plant
- **Expected**: `SELECT plant_id, SUM(casting_slag_weight) as total_slag FROM core_process_tap_production GROUP BY plant_id ORDER BY total_slag DESC`
- **Actual**: `SELECT p.plant_name, SUM(cp.cast_weight) as total_slag_weight 
FROM core_process_tap_production cp 
JOIN plant_plant p ON cp.plant_id = p.id 
GROUP BY p.plant_name 
ORDER BY total_slag_weight DESC`

### [FAIL - Mismatch] Test #339
- **Q**: Show recycling metal statistics
- **Expected**: `SELECT SUM(recycling_metal_weight) as total_recycled FROM core_process_tap_production`
- **Actual**: `SELECT furnace_no, SUM(cast_weight) as total_recycling FROM core_process_tap_production WHERE product_type_id = 'RECYCLING' GROUP BY furnace_no ORDER BY total_recycling DESC`

### [FAIL - Mismatch] Test #340
- **Q**: Show ladle weight analysis
- **Expected**: `SELECT AVG(ladle_weight_before_tapping) as avg_before, AVG(ladle_weight_after_tapping) as avg_after FROM core_process_tap_production`
- **Actual**: `SELECT tap_id, tap_production_datetime, cast_weight, liquid_weight, energy, energy_efficiency, graded_cast_weight, downgrade_quantity, ladle_number_code 
FROM core_process_tap_production 
WHERE furnace_no = 1 
ORDER BY tap_production_datetime DESC 
LIMIT 100`

### [FAIL - Mismatch] Test #341
- **Q**: How many taps today?
- **Expected**: `SELECT COUNT(DISTINCT tap_id) as tap_count FROM core_process_tap_process WHERE DATE(tap_datetime) = CURRENT_DATE`
- **Actual**: `SELECT COUNT(tap_id) FROM core_process_tap_production WHERE tap_production_datetime >= CURRENT_DATE ORDER BY tap_production_datetime DESC LIMIT 100`

### [FAIL - Mismatch] Test #342
- **Q**: Show taps by furnace
- **Expected**: `SELECT furnace_no, COUNT(DISTINCT tap_id) as tap_count FROM core_process_tap_process GROUP BY furnace_no ORDER BY tap_count DESC`
- **Actual**: `SELECT furnace_no, tap_id FROM core_process_tap_production ORDER BY created_at DESC LIMIT 100`
- **Diagnosis**: Missing GROUP BY

### [FAIL - Mismatch] Test #343
- **Q**: Show tap status summary
- **Expected**: `SELECT tap_status, COUNT(*) as count FROM core_process_tap_process GROUP BY tap_status ORDER BY count DESC`
- **Actual**: `SELECT tap_id, tap_status, tap_progress, tap_hole_id, target_material, plant_id 
FROM core_process_tap_process 
WHERE furnace_no = 1 
ORDER BY tap_datetime DESC 
LIMIT 100`
- **Diagnosis**: Missing GROUP BY

### [FAIL - Mismatch] Test #344
- **Q**: Show recent tap processes
- **Expected**: `SELECT tap_id, furnace_no, tap_datetime, tap_status, tap_progress FROM core_process_tap_process ORDER BY tap_datetime DESC LIMIT 20`
- **Actual**: `SELECT id, tap_id, furnace_no, tap_datetime, tap_progress, tap_status, tap_hole_id, target_material, plant_id 
FROM core_process_tap_process 
WHERE tap_datetime >= CURRENT_DATE - INTERVAL '30 days' 
ORDER BY tap_datetime DESC 
LIMIT 100`

### [FAIL - Mismatch] Test #346
- **Q**: Show taps by tap hole
- **Expected**: `SELECT tap_hole_id, COUNT(*) as tap_count FROM core_process_tap_process GROUP BY tap_hole_id ORDER BY tap_count DESC`
- **Actual**: `SELECT 
    cpt.tap_hole_id, 
    COUNT(*) as num_taps 
FROM 
    core_process_tap_process cpt 
GROUP BY 
    cpt.tap_hole_id 
ORDER BY 
    num_taps DESC 
LIMIT 100`

### [FAIL - Mismatch] Test #347
- **Q**: Show target materials used
- **Expected**: `SELECT target_material, COUNT(*) as count FROM core_process_tap_process GROUP BY target_material ORDER BY count DESC`
- **Actual**: `SELECT 
    target_material_id, 
    COUNT(*) as total_taps, 
    SUM(cast_weight) as total_cast_weight
FROM 
    core_process_tap_process
JOIN 
    core_process_tap_production ON core_process_tap_process.id = core_process_tap_production.tap_id
GROUP BY 
    target_material_id
ORDER BY 
    total_cast_weight DESC`

### [FAIL - Mismatch] Test #348
- **Q**: Show daily tap count trend
- **Expected**: `SELECT DATE_TRUNC('day', tap_datetime)::DATE as tap_date, COUNT(DISTINCT tap_id) as tap_count FROM core_process_tap_process GROUP BY DATE_TRUNC('day', tap_datetime) ORDER BY tap_date DESC LIMIT 30`
- **Actual**: `SELECT tap_production_datetime, COUNT(tap_id) as daily_tap_count 
FROM core_process_tap_production 
WHERE furnace_no = 1 
GROUP BY tap_production_datetime 
ORDER BY tap_production_datetime DESC 
LIMIT 100`

### [FAIL - Mismatch] Test #349
- **Q**: Show all allocated grades
- **Expected**: `SELECT allocated_grade, COUNT(*) as count FROM core_process_tap_grading GROUP BY allocated_grade ORDER BY count DESC`
- **Actual**: `SELECT allocated_grade, allocated_grade_quality, allocated_grade_priority, allocated_grade_bulk_pile, cast_process_code, plant_id 
FROM core_process_tap_grading 
ORDER BY created_at DESC 
LIMIT 100`
- **Diagnosis**: Missing GROUP BY

### [FAIL - Mismatch] Test #350
- **Q**: Show grade quality distribution
- **Expected**: `SELECT allocated_grade_quality, COUNT(*) as count FROM core_process_tap_grading GROUP BY allocated_grade_quality ORDER BY count DESC`
- **Actual**: `SELECT allocated_grade_quality, COUNT(*) as count 
FROM core_process_tap_grading 
WHERE furnace_no = 1 
GROUP BY allocated_grade_quality 
ORDER BY count DESC 
LIMIT 100`

### [FAIL - Mismatch] Test #351
- **Q**: Show grade priority breakdown
- **Expected**: `SELECT allocated_grade_priority, COUNT(*) as count FROM core_process_tap_grading GROUP BY allocated_grade_priority ORDER BY count DESC`
- **Actual**: `SELECT allocated_grade_priority, allocated_grade, COUNT(*) as count 
FROM core_process_tap_grading 
WHERE furnace_no = 1 
GROUP BY allocated_grade_priority, allocated_grade 
ORDER BY created_at DESC 
LIMIT 100`

### [FAIL - Mismatch] Test #352
- **Q**: Show grading by cast process
- **Expected**: `SELECT cast_process_code, COUNT(*) as count FROM core_process_tap_grading GROUP BY cast_process_code ORDER BY count DESC`
- **Actual**: `SELECT cast_process_code, allocated_grade, allocated_grade_quality, allocated_grade_priority, allocated_grade_bulk_pile 
FROM core_process_tap_grading 
ORDER BY created_at DESC 
LIMIT 100`
- **Diagnosis**: Missing GROUP BY

### [FAIL - Mismatch] Test #353
- **Q**: Show bulk pile allocations
- **Expected**: `SELECT allocated_grade_bulk_pile, COUNT(*) as count FROM core_process_tap_grading GROUP BY allocated_grade_bulk_pile ORDER BY count DESC`
- **Actual**: `SELECT allocated_grade_bulk_pile, created_at 
FROM core_process_tap_grading 
ORDER BY created_at DESC 
LIMIT 100`
- **Diagnosis**: Missing GROUP BY

### [FAIL - Mismatch] Test #354
- **Q**: Show recent grading records
- **Expected**: `SELECT tap_id, allocated_grade, allocated_grade_quality, allocated_grade_priority FROM core_process_tap_grading ORDER BY id DESC LIMIT 50`
- **Actual**: `SELECT id, tap_id, allocated_grade, allocated_grade_quality, allocated_grade_priority, allocated_grade_bulk_pile, cast_process_code, plant_id, created_at 
FROM core_process_tap_grading 
WHERE furnace_no = 1 
ORDER BY created_at DESC 
LIMIT 100`

### [FAIL - Mismatch] Test #356
- **Q**: Show downtime events by furnace
- **Expected**: `SELECT furnace_no, SUM(downtime_hours) as total_downtime, COUNT(*) as event_count FROM log_book_furnace_down_time_event GROUP BY furnace_no ORDER BY total_downtime DESC`
- **Actual**: `SELECT furnace_no, obs_start_dt, obs_end_dt, downtime_hours, equipment_id, reason_id, downtime_type_id 
FROM log_book_furnace_down_time_event 
WHERE furnace_no = 1 
ORDER BY obs_start_dt DESC 
LIMIT 100`
- **Diagnosis**: Missing GROUP BY

### [FAIL - Mismatch] Test #357
- **Q**: Show recent downtime events
- **Expected**: `SELECT furnace_no, obs_start_dt, obs_end_dt, downtime_hours FROM log_book_furnace_down_time_event ORDER BY obs_start_dt DESC LIMIT 20`
- **Actual**: `SELECT * FROM log_book_furnace_down_time_event ORDER BY obs_start_dt DESC LIMIT 100`

### [FAIL - No SQL] Test #358
- **Q**: Show downtime by reason
- **Error**: NLP Service returned 403

### [FAIL - Mismatch] Test #359
- **Q**: Show downtime by type
- **Expected**: `SELECT downtime_type_id, SUM(downtime_hours) as total_downtime, COUNT(*) as event_count FROM log_book_furnace_down_time_event GROUP BY downtime_type_id ORDER BY total_downtime DESC`
- **Actual**: `SELECT 
  lbdte.name, 
  SUM(kdd.downtime_hours) as total_downtime
FROM 
  kpi_downtime_data kdd
  JOIN log_book_furnace_down_time_event lbfdte ON kdd.record_id = lbfdte.record_id
  JOIN log_book_downtime_type_master lbdte ON lbfdte.downtime_type_id = lbdte.id
GROUP BY 
  lbdte.name
ORDER BY 
  total_downtime DESC`

### [FAIL - Mismatch] Test #360
- **Q**: Show long downtime events
- **Expected**: `SELECT furnace_no, obs_start_dt, obs_end_dt, downtime_hours FROM log_book_furnace_down_time_event WHERE downtime_hours > 4 ORDER BY downtime_hours DESC LIMIT 50`
- **Actual**: `SELECT id, furnace_no, obs_start_dt, obs_end_dt, downtime_hours, equipment_id, reason_id, downtime_type_id 
FROM log_book_furnace_down_time_event 
WHERE downtime_hours > 2 
ORDER BY obs_start_dt DESC 
LIMIT 100`

### [FAIL - Mismatch] Test #361
- **Q**: Show downtime events last 7 days
- **Expected**: `SELECT furnace_no, obs_start_dt, downtime_hours FROM log_book_furnace_down_time_event WHERE obs_start_dt >= CURRENT_DATE - INTERVAL '7 days' ORDER BY obs_start_dt DESC`
- **Actual**: `SELECT * 
FROM log_book_furnace_down_time_event 
WHERE obs_start_dt >= CURRENT_DATE - INTERVAL '7 days' 
ORDER BY obs_start_dt DESC 
LIMIT 100`

### [FAIL - Mismatch] Test #362
- **Q**: Show daily downtime event summary
- **Expected**: `SELECT DATE_TRUNC('day', obs_start_dt)::DATE as event_date, SUM(downtime_hours) as total_downtime, COUNT(*) as event_count FROM log_book_furnace_down_time_event GROUP BY DATE_TRUNC('day', obs_start_dt) ORDER BY event_date DESC LIMIT 30`
- **Actual**: `SELECT obs_start_dt, furnace_no, downtime_hours 
FROM log_book_furnace_down_time_event 
WHERE obs_start_dt >= CURRENT_DATE - INTERVAL '30 days' 
ORDER BY obs_start_dt DESC 
LIMIT 100`
- **Diagnosis**: Missing GROUP BY

### [FAIL - Mismatch] Test #363
- **Q**: Show downtime by equipment
- **Expected**: `SELECT equipment_id, SUM(downtime_hours) as total_downtime, COUNT(*) as event_count FROM log_book_furnace_down_time_event GROUP BY equipment_id ORDER BY total_downtime DESC`
- **Actual**: `SELECT machine_id, SUM(downtime_hours) as total_downtime FROM kpi_downtime_data GROUP BY machine_id ORDER BY total_downtime DESC`

### [FAIL - Mismatch] Test #364
- **Q**: Show downtime events by plant
- **Expected**: `SELECT plant_id, SUM(downtime_hours) as total_downtime, COUNT(*) as event_count FROM log_book_furnace_down_time_event GROUP BY plant_id ORDER BY total_downtime DESC`
- **Actual**: `SELECT p.plant_name, l.obs_start_dt, l.obs_end_dt, l.downtime_hours 
FROM log_book_furnace_down_time_event l 
JOIN plant_plant p ON l.plant_id = p.id 
ORDER BY l.obs_start_dt DESC 
LIMIT 100`
- **Diagnosis**: Missing GROUP BY

### [FAIL - Mismatch] Test #365
- **Q**: List all furnaces
- **Expected**: `SELECT furnace_no, furnace_description, is_active FROM furnace_furnaceconfig ORDER BY furnace_no`
- **Actual**: `SELECT furnace_no, furnace_description FROM furnace_furnaceconfig ORDER BY created_at DESC LIMIT 100`

### [FAIL - Mismatch] Test #366
- **Q**: Show active furnaces
- **Expected**: `SELECT furnace_no, furnace_description FROM furnace_furnaceconfig WHERE is_active = true ORDER BY furnace_no`
- **Actual**: `SELECT furnace_no, furnace_description, is_active FROM furnace_furnaceconfig WHERE is_active = 'true' ORDER BY created_at DESC LIMIT 100`

### [FAIL - Mismatch] Test #367
- **Q**: Show furnaces by workshop
- **Expected**: `SELECT workshop_id, COUNT(*) as furnace_count FROM furnace_furnaceconfig GROUP BY workshop_id ORDER BY furnace_count DESC`
- **Actual**: `SELECT 
    pcw.workshop_name, 
    ff.furnace_no, 
    ff.furnace_description
FROM 
    furnace_furnaceconfig ff
JOIN 
    plant_config_workshop pcw ON ff.workshop_id = pcw.id
ORDER BY 
    pcw.workshop_name, 
    ff.furnace_no`
- **Diagnosis**: Missing GROUP BY

### [FAIL - Mismatch] Test #368
- **Q**: Show furnace configuration parameters
- **Expected**: `SELECT furnace_config_id, crucible_diameter, crucible_depth, target_energy_efficiency FROM furnace_config_parameters ORDER BY furnace_config_id`
- **Actual**: `SELECT id, furnace_config_id, effective_date, crucible_diameter, crucible_depth, energy_losses, joule_losses_coefficient, default_epi_index, corrected_reactance_coefficient 
FROM furnace_config_parameters 
ORDER BY effective_date DESC 
LIMIT 100`

### [FAIL - Mismatch] Test #369
- **Q**: Show all plants
- **Expected**: `SELECT id, plant_code, plant_name FROM plant_plant ORDER BY id`
- **Actual**: `SELECT * FROM plant_plant ORDER BY created_at DESC LIMIT 100`

### [FAIL - No SQL] Test #370
- **Q**: Show downtime reasons list
- **Error**: NLP Service returned 403

### [FAIL - Mismatch] Test #371
- **Q**: Show downtime types list
- **Expected**: `SELECT id, name, down_time_type_code FROM log_book_downtime_type_master ORDER BY id`
- **Actual**: `SELECT down_time_type_code, name 
FROM log_book_downtime_type_master 
ORDER BY created_at DESC 
LIMIT 100`

### [FAIL - Mismatch] Test #372
- **Q**: Show furnace energy targets
- **Expected**: `SELECT furnace_config_id, target_energy_efficiency, target_availability, target_furnace_load FROM furnace_config_parameters ORDER BY furnace_config_id`
- **Actual**: `SELECT 
    f.furnace_no, 
    f.furnace_description, 
    fc.target_energy_efficiency
FROM 
    furnace_furnaceconfig f
JOIN 
    furnace_config_parameters fc ON f.id = fc.furnace_config_id
ORDER BY 
    f.created_at DESC`
