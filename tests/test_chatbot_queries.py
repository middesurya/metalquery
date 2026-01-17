"""
Comprehensive Chatbot Query Test Suite
Tests NL-to-SQL generation and graph type prediction
"""

import requests
import json
import time
import re
from datetime import datetime
from typing import List, Dict, Tuple
import csv

# Test configuration
NLP_SERVICE_URL = "http://localhost:8003"
DJANGO_URL = "http://localhost:8000"

# All test cases from the provided data
TEST_CASES = [
    {"category": "OEE", "question": "What is the average oee for all furnaces", "expected_sql": "SELECT AVG(oee_percentage) as average_oee FROM kpi_overall_equipment_efficiency_data", "expected_graph": "KPI Card"},
    {"category": "OEE", "question": "What is the average oee for furnace 1", "expected_sql": "SELECT AVG(oee_percentage) FROM kpi_overall_equipment_efficiency_data WHERE furnace_no = 1", "expected_graph": "KPI Card"},
    {"category": "OEE", "question": "What is the average oee for furnace 1 last 30 days", "expected_sql": "SELECT AVG(oee_percentage) FROM kpi_overall_equipment_efficiency_data WHERE furnace_no = 1 AND date >= CURRENT_DATE - INTERVAL '30 days'", "expected_graph": "KPI Card"},
    {"category": "OEE", "question": "Show Average OEE by furnace", "expected_sql": "SELECT furnace_no, AVG(oee_percentage) as avg_oee FROM kpi_overall_equipment_efficiency_data GROUP BY furnace_no ORDER BY avg_oee DESC", "expected_graph": "Bar Chart"},
    {"category": "OEE", "question": "Show OEE by furnace", "expected_sql": "SELECT furnace_no, AVG(oee_percentage) as avg_oee FROM kpi_overall_equipment_efficiency_data GROUP BY furnace_no ORDER BY avg_oee DESC", "expected_graph": "Bar Chart"},
    {"category": "Downtime", "question": "Show Total downtime by furnace", "expected_sql": "SELECT furnace_no, SUM(downtime_hours) as total_downtime FROM kpi_downtime_data GROUP BY furnace_no ORDER BY total_downtime DESC", "expected_graph": "Line Chart"},
    {"category": "Energy", "question": "Show Total energy consumption by furnace", "expected_sql": "SELECT furnace_no, SUM(energy_used) as total_energy FROM kpi_energy_used_data GROUP BY furnace_no ORDER BY total_energy DESC", "expected_graph": "Bar Chart"},
    {"category": "OEE", "question": "Which furnace has highest OEE?", "expected_sql": "SELECT furnace_no, AVG(oee_percentage) as avg_oee FROM kpi_overall_equipment_efficiency_data GROUP BY furnace_no ORDER BY avg_oee DESC LIMIT 1", "expected_graph": "Bar Chart"},
    {"category": "General", "question": "Show Total quantity produced by furnace", "expected_sql": "SELECT furnace_no, SUM(quantity_produced) as total_qty FROM kpi_quantity_produced_data GROUP BY furnace_no ORDER BY total_qty DESC", "expected_graph": "Bar Chart"},
    {"category": "Yield", "question": "What is the average yield for furnace 2", "expected_sql": "SELECT AVG(yield_percentage) FROM kpi_yield_data WHERE furnace_no = 2", "expected_graph": "KPI Card"},
    {"category": "Downtime", "question": "Show what is the total downtime last year", "expected_sql": "SELECT SUM(downtime_hours) as total_downtime FROM kpi_downtime_data WHERE date >= CURRENT_DATE - INTERVAL '1 year'", "expected_graph": "KPI Card"},
    {"category": "Downtime", "question": "What is the average downtime per furnace", "expected_sql": "SELECT furnace_no, AVG(downtime_hours) as avg_downtime FROM kpi_downtime_data GROUP BY furnace_no", "expected_graph": "Line Chart"},
    {"category": "General", "question": "What is the total production for furnace 1 last month", "expected_sql": "SELECT SUM(quantity_produced) as total_production FROM kpi_quantity_produced_data WHERE furnace_no = 1 AND date >= CURRENT_DATE - INTERVAL '30 days'", "expected_graph": "KPI Card"},
    {"category": "General", "question": "Show production by furnace", "expected_sql": "SELECT furnace_no, SUM(quantity_produced) as total_qty FROM kpi_quantity_produced_data GROUP BY furnace_no ORDER BY total_qty DESC", "expected_graph": "Bar Chart"},
    {"category": "Downtime", "question": "Show downtime by furnace", "expected_sql": "SELECT furnace_no, SUM(downtime_hours) as total_downtime FROM kpi_downtime_data GROUP BY furnace_no ORDER BY total_downtime DESC", "expected_graph": "Line Chart"},
    {"category": "Energy", "question": "Show energy consumption by furnace", "expected_sql": "SELECT furnace_no, SUM(energy_used) as total_energy FROM kpi_energy_used_data GROUP BY furnace_no ORDER BY total_energy DESC", "expected_graph": "Bar Chart"},
    {"category": "OEE", "question": "Show OEE trend for Furnace 2", "expected_sql": "SELECT date, oee_percentage FROM kpi_overall_equipment_efficiency_data WHERE furnace_no = 2 ORDER BY date DESC LIMIT 100", "expected_graph": "Table"},
    {"category": "Downtime", "question": "Display downtime trend last 30 days", "expected_sql": "SELECT date, furnace_no, downtime_hours FROM kpi_downtime_data WHERE date >= CURRENT_DATE - INTERVAL '30 days' ORDER BY date DESC", "expected_graph": "Table"},
    {"category": "Defect Rate", "question": "Show recent defect rate data", "expected_sql": "SELECT date, shift_id, furnace_no, defect_rate FROM kpi_defect_rate_data ORDER BY date DESC LIMIT 50", "expected_graph": "Table"},
    {"category": "OEE", "question": "Show OEE trend last week", "expected_sql": "SELECT date, furnace_no, oee_percentage FROM kpi_overall_equipment_efficiency_data WHERE date >= CURRENT_DATE - INTERVAL '7 days' ORDER BY date DESC", "expected_graph": "Table"},
    {"category": "General", "question": "List all furnaces", "expected_sql": "SELECT furnace_no, furnace_description, is_active FROM furnace_furnaceconfig ORDER BY furnace_no", "expected_graph": "Table"},
    {"category": "Downtime", "question": "Show downtime events for Furnace 1", "expected_sql": "SELECT obs_start_dt, obs_end_dt, downtime_hours FROM log_book_furnace_down_time_event WHERE furnace_no = 1 ORDER BY obs_start_dt DESC LIMIT 50", "expected_graph": "Table"},
    {"category": "Tap Process", "question": "Show recent tap production data", "expected_sql": "SELECT tap_id, cast_weight, energy, tap_production_datetime FROM core_process_tap_production ORDER BY tap_production_datetime DESC LIMIT 20", "expected_graph": "Table"},
    {"category": "Yield", "question": "Show yield data for last month", "expected_sql": "SELECT date, furnace_no, yield_percentage FROM kpi_yield_data WHERE date >= CURRENT_DATE - INTERVAL '30 days' ORDER BY date DESC", "expected_graph": "Table"},
    {"category": "Energy", "question": "Display energy efficiency trend", "expected_sql": "SELECT date, furnace_no, energy_efficiency FROM kpi_energy_efficiency_data ORDER BY date DESC LIMIT 100", "expected_graph": "Table"},
    {"category": "General", "question": "Show MTTR data for Furnace 2", "expected_sql": "SELECT date, mttr_hours FROM kpi_mean_time_to_repair_data WHERE furnace_no = 2 ORDER BY date DESC LIMIT 100", "expected_graph": "Table"},
    {"category": "General", "question": "List recent quality issues", "expected_sql": "SELECT date, furnace_no, defect_rate FROM kpi_defect_rate_data ORDER BY date DESC LIMIT 100", "expected_graph": "Table"},
    {"category": "OEE", "question": "Compare OEE between Furnace 1 and 2", "expected_sql": "SELECT furnace_no, AVG(oee_percentage) as avg_oee FROM kpi_overall_equipment_efficiency_data WHERE furnace_no IN (1, 2) GROUP BY furnace_no ORDER BY avg_oee DESC", "expected_graph": "Bar Chart"},
    {"category": "Yield", "question": "Which shift has highest yield?", "expected_sql": "SELECT shift_id, AVG(yield_percentage) as avg_yield FROM kpi_yield_data GROUP BY shift_id ORDER BY avg_yield DESC LIMIT 1", "expected_graph": "Bar Chart"},
    {"category": "Yield", "question": "Show yield by shift", "expected_sql": "SELECT shift_id, AVG(yield_percentage) as avg_yield FROM kpi_yield_data GROUP BY shift_id ORDER BY avg_yield DESC", "expected_graph": "Bar Chart"},
    {"category": "General", "question": "Show production by shift", "expected_sql": "SELECT shift_id, SUM(quantity_produced) as total_qty FROM kpi_quantity_produced_data GROUP BY shift_id ORDER BY total_qty DESC", "expected_graph": "Bar Chart"},
    {"category": "OEE", "question": "Show oee by shift", "expected_sql": "SELECT shift_id, AVG(oee_percentage) as avg_oee FROM kpi_overall_equipment_efficiency_data GROUP BY shift_id ORDER BY avg_oee DESC", "expected_graph": "Bar Chart"},
    {"category": "OEE", "question": "Compare all furnaces by OEE", "expected_sql": "SELECT furnace_no, AVG(oee_percentage) as avg_oee, MAX(oee_percentage) as max_oee, MIN(oee_percentage) as min_oee FROM kpi_overall_equipment_efficiency_data GROUP BY furnace_no ORDER BY avg_oee DESC", "expected_graph": "Bar Chart"},
    {"category": "Defect Rate", "question": "Show rank furnaces by defect rate", "expected_sql": "SELECT furnace_no, AVG(defect_rate) as avg_defect FROM kpi_defect_rate_data GROUP BY furnace_no ORDER BY avg_defect DESC", "expected_graph": "Bar Chart"},
    {"category": "Downtime", "question": "Compare downtime between machines", "expected_sql": "SELECT machine_id, SUM(downtime_hours) as total_downtime FROM kpi_downtime_data GROUP BY machine_id ORDER BY total_downtime DESC", "expected_graph": "Line Chart"},
    {"category": "Yield", "question": "Which product type has highest yield?", "expected_sql": "SELECT product_type_id, AVG(yield_percentage) as avg_yield FROM kpi_yield_data GROUP BY product_type_id ORDER BY avg_yield DESC LIMIT 1", "expected_graph": "Bar Chart"},
    {"category": "Energy", "question": "Compare energy efficiency by furnace", "expected_sql": "SELECT furnace_no, AVG(energy_efficiency) as avg_efficiency FROM kpi_energy_efficiency_data GROUP BY furnace_no ORDER BY avg_efficiency", "expected_graph": "Bar Chart"},
    {"category": "General", "question": "Show production efficiency by shift", "expected_sql": "SELECT shift_id, AVG(production_efficiency_percentage) as avg_efficiency FROM kpi_production_efficiency_data GROUP BY shift_id ORDER BY avg_efficiency DESC", "expected_graph": "Bar Chart"},
    {"category": "General", "question": "Compare MTBF by furnace", "expected_sql": "SELECT furnace_no, AVG(mtbf_hours) as avg_mtbf FROM kpi_mean_time_between_failures_data GROUP BY furnace_no ORDER BY avg_mtbf DESC", "expected_graph": "Line Chart"},
    {"category": "OEE", "question": "Show best and worst shift by oee", "expected_sql": "SELECT shift_id, AVG(oee_percentage) as avg_oee FROM kpi_overall_equipment_efficiency_data GROUP BY shift_id ORDER BY avg_oee DESC", "expected_graph": "Bar Chart"},
    {"category": "OEE", "question": "Show oee statistics", "expected_sql": "SELECT MIN(oee_percentage) as min_oee, MAX(oee_percentage) as max_oee, AVG(oee_percentage) as avg_oee, STDDEV(oee_percentage) as stddev_oee FROM kpi_overall_equipment_efficiency_data", "expected_graph": "KPI Card"},
    {"category": "Downtime", "question": "Show downtime statistics by furnace", "expected_sql": "SELECT furnace_no, MIN(downtime_hours) as min, MAX(downtime_hours) as max, AVG(downtime_hours) as avg, SUM(downtime_hours) as total, COUNT(*) as count FROM kpi_downtime_data GROUP BY furnace_no", "expected_graph": "Line Chart"},
    {"category": "Energy", "question": "Show energy efficiency range", "expected_sql": "SELECT MIN(energy_efficiency) as min_eff, MAX(energy_efficiency) as max_eff, AVG(energy_efficiency) as avg_eff FROM kpi_energy_efficiency_data", "expected_graph": "KPI Card"},
    {"category": "Yield", "question": "Show yield statistics by furnace", "expected_sql": "SELECT furnace_no, AVG(yield_percentage) as avg_yield, STDDEV(yield_percentage) as stddev_yield, MIN(yield_percentage) as min_yield, MAX(yield_percentage) as max_yield FROM kpi_yield_data GROUP BY furnace_no", "expected_graph": "Bar Chart"},
    {"category": "General", "question": "Show production quantity statistics", "expected_sql": "SELECT AVG(quantity_produced) as avg_qty, MAX(quantity_produced) as max_qty, MIN(quantity_produced) as min_qty, SUM(quantity_produced) as total_qty FROM kpi_quantity_produced_data", "expected_graph": "KPI Card"},
    {"category": "OEE", "question": "Show OEE records above 90%", "expected_sql": "SELECT date, furnace_no, shift_id, oee_percentage FROM kpi_overall_equipment_efficiency_data WHERE oee_percentage > 90 ORDER BY oee_percentage DESC LIMIT 100", "expected_graph": "Table"},
    {"category": "Downtime", "question": "Show downtime events exceeding 8 hours", "expected_sql": "SELECT obs_start_dt, furnace_no, downtime_hours FROM log_book_furnace_down_time_event WHERE downtime_hours > 8 ORDER BY downtime_hours DESC", "expected_graph": "Table"},
    {"category": "General", "question": "Show furnaces with low efficiency below 80%", "expected_sql": "SELECT furnace_no, AVG(oee_percentage) as avg_oee FROM kpi_overall_equipment_efficiency_data GROUP BY furnace_no HAVING AVG(oee_percentage) < 80", "expected_graph": "Bar Chart"},
    {"category": "Defect Rate", "question": "Show defect rate above 5 percent", "expected_sql": "SELECT date, shift_id, furnace_no, defect_rate FROM kpi_defect_rate_data WHERE defect_rate > 5 ORDER BY defect_rate DESC LIMIT 100", "expected_graph": "Table"},
    {"category": "Energy", "question": "Show energy usage above average", "expected_sql": "SELECT furnace_no, SUM(energy_used) as total_energy FROM kpi_energy_used_data GROUP BY furnace_no HAVING SUM(energy_used) > (SELECT AVG(energy_used) FROM kpi_energy_used_data)", "expected_graph": "Bar Chart"},
    {"category": "Yield", "question": "Show low yield furnaces below 85%", "expected_sql": "SELECT furnace_no, AVG(yield_percentage) as avg_yield FROM kpi_yield_data GROUP BY furnace_no HAVING AVG(yield_percentage) < 85 ORDER BY avg_yield", "expected_graph": "Bar Chart"},
    {"category": "General", "question": "Show top 5 furnaces by production", "expected_sql": "SELECT furnace_no, SUM(cast_weight) as total_production FROM core_process_tap_production GROUP BY furnace_no ORDER BY total_production DESC LIMIT 5", "expected_graph": "Bar Chart"},
    {"category": "Yield", "question": "Show bottom 3 furnaces by yield", "expected_sql": "SELECT furnace_no, AVG(yield_percentage) as avg_yield FROM kpi_yield_data GROUP BY furnace_no ORDER BY avg_yield ASC LIMIT 3", "expected_graph": "Bar Chart"},
    {"category": "General", "question": "Show top 10 shifts by output", "expected_sql": "SELECT shift_id, SUM(quantity_produced) as total_output FROM kpi_quantity_produced_data GROUP BY shift_id ORDER BY total_output DESC LIMIT 10", "expected_graph": "Bar Chart"},
    {"category": "OEE", "question": "What is the worst furnace by OEE", "expected_sql": "SELECT furnace_no, AVG(oee_percentage) as avg_oee FROM kpi_overall_equipment_efficiency_data GROUP BY furnace_no ORDER BY avg_oee ASC LIMIT 1", "expected_graph": "Bar Chart"},
    {"category": "Energy", "question": "Show top 3 machines by energy", "expected_sql": "SELECT machine_id, SUM(energy_used) as total_energy FROM kpi_energy_used_data GROUP BY machine_id ORDER BY total_energy DESC LIMIT 3", "expected_graph": "Bar Chart"},
    {"category": "General", "question": "What is the best shift by efficiency", "expected_sql": "SELECT shift_id, AVG(production_efficiency_percentage) as avg_efficiency FROM kpi_production_efficiency_data GROUP BY shift_id ORDER BY avg_efficiency DESC LIMIT 1", "expected_graph": "Bar Chart"},
    {"category": "General", "question": "What is the most reliable furnace", "expected_sql": "SELECT furnace_no, AVG(mtbf_hours) as avg_mtbf FROM kpi_mean_time_between_failures_data GROUP BY furnace_no ORDER BY avg_mtbf DESC LIMIT 1", "expected_graph": "Line Chart"},
    {"category": "Cycle Time", "question": "What is the average cycle time overall?", "expected_sql": "SELECT AVG(cycle_time) as average_cycle_time FROM kpi_cycle_time_data", "expected_graph": "KPI Card"},
    {"category": "Cycle Time", "question": "What is the total cycle time per day?", "expected_sql": "SELECT date, SUM(cycle_time) as total_cycle_time FROM kpi_cycle_time_data GROUP BY date ORDER BY date DESC", "expected_graph": "Line Chart"},
    {"category": "Cycle Time", "question": "What is the average cycle time per shift?", "expected_sql": "SELECT shift_id, AVG(cycle_time) as avg_cycle_time FROM kpi_cycle_time_data GROUP BY shift_id ORDER BY avg_cycle_time DESC", "expected_graph": "Line Chart"},
    {"category": "Cycle Time", "question": "Show Average cycle time by furnace", "expected_sql": "SELECT furnace_no, AVG(cycle_time) as avg_cycle_time FROM kpi_cycle_time_data GROUP BY furnace_no ORDER BY avg_cycle_time DESC", "expected_graph": "Line Chart"},
    {"category": "Cycle Time", "question": "Which shift has the highest average cycle time?", "expected_sql": "SELECT shift_id, AVG(cycle_time) as avg_cycle_time FROM kpi_cycle_time_data GROUP BY shift_id ORDER BY avg_cycle_time DESC LIMIT 1", "expected_graph": "Line Chart"},
    {"category": "Cycle Time", "question": "Show daily cycle time trend", "expected_sql": "SELECT date, AVG(cycle_time) as avg_cycle_time, MIN(cycle_time) as min_cycle_time, MAX(cycle_time) as max_cycle_time FROM kpi_cycle_time_data GROUP BY date ORDER BY date DESC", "expected_graph": "Line Chart"},
    {"category": "Defect Rate", "question": "What is the average defect rate?", "expected_sql": "SELECT AVG(defect_rate) as avg_defect_rate FROM kpi_defect_rate_data", "expected_graph": "KPI Card"},
    {"category": "Defect Rate", "question": "Show defect rate for furnace 1", "expected_sql": "SELECT date, shift_id, defect_rate FROM kpi_defect_rate_data WHERE furnace_no = 1 ORDER BY date DESC LIMIT 100", "expected_graph": "Table"},
    {"category": "Defect Rate", "question": "Which furnace has highest defect rate?", "expected_sql": "SELECT furnace_no, AVG(defect_rate) as avg_defect_rate FROM kpi_defect_rate_data GROUP BY furnace_no ORDER BY avg_defect_rate DESC LIMIT 1", "expected_graph": "Bar Chart"},
    {"category": "Defect Rate", "question": "Show defect rate by shift", "expected_sql": "SELECT shift_id, AVG(defect_rate) as avg_defect_rate FROM kpi_defect_rate_data GROUP BY shift_id ORDER BY avg_defect_rate DESC", "expected_graph": "Bar Chart"},
    {"category": "Defect Rate", "question": "Show defect rate trend last 30 days", "expected_sql": "SELECT date, AVG(defect_rate) as avg_defect_rate FROM kpi_defect_rate_data WHERE date >= CURRENT_DATE - INTERVAL '30 days' GROUP BY date ORDER BY date DESC", "expected_graph": "Line Chart"},
    {"category": "Energy", "question": "What is the average energy efficiency?", "expected_sql": "SELECT AVG(energy_efficiency) as avg_energy_efficiency FROM kpi_energy_efficiency_data", "expected_graph": "KPI Card"},
    {"category": "Energy", "question": "Show energy efficiency for furnace 1", "expected_sql": "SELECT date, shift_id, energy_efficiency FROM kpi_energy_efficiency_data WHERE furnace_no = 1 ORDER BY date DESC LIMIT 100", "expected_graph": "Table"},
    {"category": "Energy", "question": "Which furnace is most energy efficient?", "expected_sql": "SELECT furnace_no, AVG(energy_efficiency) as avg_efficiency FROM kpi_energy_efficiency_data GROUP BY furnace_no ORDER BY avg_efficiency ASC LIMIT 1", "expected_graph": "Bar Chart"},
    {"category": "Energy", "question": "Show energy efficiency by shift", "expected_sql": "SELECT shift_id, AVG(energy_efficiency) as avg_efficiency FROM kpi_energy_efficiency_data GROUP BY shift_id ORDER BY avg_efficiency", "expected_graph": "Bar Chart"},
    {"category": "Energy", "question": "Show energy efficiency trend", "expected_sql": "SELECT date, AVG(energy_efficiency) as avg_efficiency FROM kpi_energy_efficiency_data GROUP BY date ORDER BY date DESC LIMIT 30", "expected_graph": "Line Chart"},
    {"category": "Energy", "question": "What is the total energy used?", "expected_sql": "SELECT SUM(energy_used) as total_energy_used FROM kpi_energy_used_data", "expected_graph": "KPI Card"},
    {"category": "Energy", "question": "Show daily energy consumption", "expected_sql": "SELECT date, SUM(energy_used) as daily_energy FROM kpi_energy_used_data GROUP BY date ORDER BY date DESC LIMIT 30", "expected_graph": "Line Chart"},
    {"category": "Energy", "question": "Show energy used by shift", "expected_sql": "SELECT shift_id, SUM(energy_used) as total_energy FROM kpi_energy_used_data GROUP BY shift_id ORDER BY total_energy DESC", "expected_graph": "Bar Chart"},
    {"category": "Energy", "question": "Show monthly energy consumption", "expected_sql": "SELECT DATE_TRUNC('month', date)::DATE as month, SUM(energy_used) as monthly_energy FROM kpi_energy_used_data GROUP BY DATE_TRUNC('month', date) ORDER BY month DESC", "expected_graph": "Line Chart"},
    {"category": "Energy", "question": "Which machine uses most energy?", "expected_sql": "SELECT machine_id, SUM(energy_used) as total_energy FROM kpi_energy_used_data GROUP BY machine_id ORDER BY total_energy DESC LIMIT 1", "expected_graph": "Bar Chart"},
    {"category": "Downtime", "question": "What is the total downtime?", "expected_sql": "SELECT SUM(downtime_hours) as total_downtime FROM kpi_downtime_data", "expected_graph": "KPI Card"},
    {"category": "Downtime", "question": "Show daily downtime trend", "expected_sql": "SELECT date, SUM(downtime_hours) as daily_downtime FROM kpi_downtime_data GROUP BY date ORDER BY date DESC LIMIT 30", "expected_graph": "Line Chart"},
    {"category": "Downtime", "question": "Show downtime by shift", "expected_sql": "SELECT shift_id, SUM(downtime_hours) as total_downtime FROM kpi_downtime_data GROUP BY shift_id ORDER BY total_downtime DESC", "expected_graph": "Line Chart"},
    {"category": "Downtime", "question": "Which machine has most downtime?", "expected_sql": "SELECT machine_id, SUM(downtime_hours) as total_downtime FROM kpi_downtime_data GROUP BY machine_id ORDER BY total_downtime DESC LIMIT 1", "expected_graph": "Line Chart"},
    {"category": "Downtime", "question": "Show downtime last week", "expected_sql": "SELECT date, furnace_no, SUM(downtime_hours) as downtime FROM kpi_downtime_data WHERE date >= CURRENT_DATE - INTERVAL '7 days' GROUP BY date, furnace_no ORDER BY date DESC", "expected_graph": "Line Chart"},
    {"category": "General", "question": "What is the average MTBF?", "expected_sql": "SELECT AVG(mtbf_hours) as avg_mtbf FROM kpi_mean_time_between_failures_data", "expected_graph": "KPI Card"},
    {"category": "General", "question": "Show mtbf by furnace", "expected_sql": "SELECT furnace_no, AVG(mtbf_hours) as avg_mtbf FROM kpi_mean_time_between_failures_data GROUP BY furnace_no ORDER BY avg_mtbf DESC", "expected_graph": "Line Chart"},
    {"category": "General", "question": "Which furnace is most reliable?", "expected_sql": "SELECT furnace_no, AVG(mtbf_hours) as avg_mtbf FROM kpi_mean_time_between_failures_data GROUP BY furnace_no ORDER BY avg_mtbf DESC LIMIT 1", "expected_graph": "Line Chart"},
    {"category": "General", "question": "What is the average MTTR?", "expected_sql": "SELECT AVG(mttr_hours) as avg_mttr FROM kpi_mean_time_to_repair_data", "expected_graph": "KPI Card"},
    {"category": "General", "question": "Show mttr by furnace", "expected_sql": "SELECT furnace_no, AVG(mttr_hours) as avg_mttr FROM kpi_mean_time_to_repair_data GROUP BY furnace_no ORDER BY avg_mttr DESC", "expected_graph": "Line Chart"},
    {"category": "General", "question": "Which furnace takes longest to repair?", "expected_sql": "SELECT furnace_no, AVG(mttr_hours) as avg_mttr FROM kpi_mean_time_to_repair_data GROUP BY furnace_no ORDER BY avg_mttr DESC LIMIT 1", "expected_graph": "Line Chart"},
    {"category": "Yield", "question": "What is the average yield?", "expected_sql": "SELECT AVG(yield_percentage) as avg_yield FROM kpi_yield_data", "expected_graph": "KPI Card"},
    {"category": "Yield", "question": "Show yield by furnace", "expected_sql": "SELECT furnace_no, AVG(yield_percentage) as avg_yield FROM kpi_yield_data GROUP BY furnace_no ORDER BY avg_yield DESC", "expected_graph": "Bar Chart"},
    {"category": "Yield", "question": "Which furnace has best yield?", "expected_sql": "SELECT furnace_no, AVG(yield_percentage) as avg_yield FROM kpi_yield_data GROUP BY furnace_no ORDER BY avg_yield DESC LIMIT 1", "expected_graph": "Bar Chart"},
    {"category": "Yield", "question": "Show yield trend last 30 days", "expected_sql": "SELECT date, AVG(yield_percentage) as avg_yield FROM kpi_yield_data WHERE date >= CURRENT_DATE - INTERVAL '30 days' GROUP BY date ORDER BY date DESC", "expected_graph": "Line Chart"},
    {"category": "Yield", "question": "Show low yield records", "expected_sql": "SELECT date, shift_id, furnace_no, yield_percentage FROM kpi_yield_data WHERE yield_percentage < 85 ORDER BY yield_percentage ASC LIMIT 100", "expected_graph": "Table"},
    {"category": "Yield", "question": "Show yield by product type", "expected_sql": "SELECT product_type_id, AVG(yield_percentage) as avg_yield FROM kpi_yield_data GROUP BY product_type_id ORDER BY avg_yield DESC", "expected_graph": "Bar Chart"},
    {"category": "General", "question": "What is the total quantity produced?", "expected_sql": "SELECT SUM(quantity_produced) as total_quantity FROM kpi_quantity_produced_data", "expected_graph": "KPI Card"},
    {"category": "General", "question": "Show daily production", "expected_sql": "SELECT date, SUM(quantity_produced) as daily_production FROM kpi_quantity_produced_data GROUP BY date ORDER BY date DESC LIMIT 30", "expected_graph": "Line Chart"},
    {"category": "General", "question": "Show production by product type", "expected_sql": "SELECT product_type_id, SUM(quantity_produced) as total_production FROM kpi_quantity_produced_data GROUP BY product_type_id ORDER BY total_production DESC", "expected_graph": "Bar Chart"},
    {"category": "General", "question": "Show monthly production", "expected_sql": "SELECT DATE_TRUNC('month', date)::DATE as month, SUM(quantity_produced) as monthly_production FROM kpi_quantity_produced_data GROUP BY DATE_TRUNC('month', date) ORDER BY month DESC", "expected_graph": "Line Chart"},
    {"category": "General", "question": "What is the average production efficiency?", "expected_sql": "SELECT AVG(production_efficiency_percentage) as avg_efficiency FROM kpi_production_efficiency_data", "expected_graph": "KPI Card"},
    {"category": "General", "question": "Show production efficiency by furnace", "expected_sql": "SELECT furnace_no, AVG(production_efficiency_percentage) as avg_efficiency FROM kpi_production_efficiency_data GROUP BY furnace_no ORDER BY avg_efficiency DESC", "expected_graph": "Bar Chart"},
    {"category": "General", "question": "Show efficiency trend", "expected_sql": "SELECT date, AVG(production_efficiency_percentage) as avg_efficiency FROM kpi_production_efficiency_data GROUP BY date ORDER BY date DESC LIMIT 30", "expected_graph": "Line Chart"},
    {"category": "General", "question": "Show efficiency by shift", "expected_sql": "SELECT shift_id, AVG(production_efficiency_percentage) as avg_efficiency FROM kpi_production_efficiency_data GROUP BY shift_id ORDER BY avg_efficiency DESC", "expected_graph": "Bar Chart"},
    {"category": "Tap Process", "question": "How many taps today?", "expected_sql": "SELECT COUNT(DISTINCT tap_id) as tap_count FROM core_process_tap_process WHERE DATE(tap_datetime) = CURRENT_DATE", "expected_graph": "KPI Card"},
    {"category": "Tap Process", "question": "Show taps by furnace", "expected_sql": "SELECT furnace_no, COUNT(DISTINCT tap_id) as tap_count FROM core_process_tap_process GROUP BY furnace_no ORDER BY tap_count DESC", "expected_graph": "Bar Chart"},
    {"category": "Tap Process", "question": "Show tap status summary", "expected_sql": "SELECT tap_status, COUNT(*) as count FROM core_process_tap_process GROUP BY tap_status ORDER BY count DESC", "expected_graph": "Bar Chart"},
    {"category": "Tap Process", "question": "Show recent tap processes", "expected_sql": "SELECT tap_id, furnace_no, tap_datetime, tap_status, tap_progress FROM core_process_tap_process ORDER BY tap_datetime DESC LIMIT 20", "expected_graph": "Table"},
    {"category": "Tap Process", "question": "Show daily tap count trend", "expected_sql": "SELECT DATE_TRUNC('day', tap_datetime)::DATE as tap_date, COUNT(DISTINCT tap_id) as tap_count FROM core_process_tap_process GROUP BY DATE_TRUNC('day', tap_datetime) ORDER BY tap_date DESC LIMIT 30", "expected_graph": "Line Chart"},
    {"category": "General", "question": "What is the total cast weight?", "expected_sql": "SELECT SUM(cast_weight) as total_cast_weight FROM core_process_tap_production", "expected_graph": "KPI Card"},
    {"category": "Downtime", "question": "What is the total downtime from events", "expected_sql": "SELECT SUM(downtime_hours) as total_downtime FROM log_book_furnace_down_time_event", "expected_graph": "KPI Card"},
    {"category": "Downtime", "question": "Show downtime events by furnace", "expected_sql": "SELECT furnace_no, SUM(downtime_hours) as total_downtime, COUNT(*) as event_count FROM log_book_furnace_down_time_event GROUP BY furnace_no ORDER BY total_downtime DESC", "expected_graph": "Line Chart"},
    {"category": "Downtime", "question": "Show recent downtime events", "expected_sql": "SELECT furnace_no, obs_start_dt, obs_end_dt, downtime_hours FROM log_book_furnace_down_time_event ORDER BY obs_start_dt DESC LIMIT 20", "expected_graph": "Table"},
    {"category": "Downtime", "question": "Show long downtime events", "expected_sql": "SELECT furnace_no, obs_start_dt, obs_end_dt, downtime_hours FROM log_book_furnace_down_time_event WHERE downtime_hours > 4 ORDER BY downtime_hours DESC LIMIT 50", "expected_graph": "Table"},
    {"category": "General", "question": "Show active furnaces", "expected_sql": "SELECT furnace_no, furnace_description FROM furnace_furnaceconfig WHERE is_active = true ORDER BY furnace_no", "expected_graph": "Table"},
    {"category": "General", "question": "Show all plants", "expected_sql": "SELECT id, plant_code, plant_name FROM plant_plant ORDER BY id", "expected_graph": "Table"},
    {"category": "Maintenance", "question": "What is the average maintenance compliance?", "expected_sql": "SELECT AVG(compliance_percentage) as avg_compliance FROM kpi_maintenance_compliance_data", "expected_graph": "KPI Card"},
    {"category": "Maintenance", "question": "Show maintenance compliance by furnace", "expected_sql": "SELECT furnace_no, AVG(compliance_percentage) as avg_compliance FROM kpi_maintenance_compliance_data GROUP BY furnace_no ORDER BY avg_compliance DESC", "expected_graph": "Bar Chart"},
    {"category": "Safety", "question": "What is the average safety incidents percentage?", "expected_sql": "SELECT AVG(incidents_percentage) as avg_incidents FROM kpi_safety_incidents_reported_data", "expected_graph": "KPI Card"},
    {"category": "Safety", "question": "Show safety incidents by furnace", "expected_sql": "SELECT furnace_no, AVG(incidents_percentage) as avg_incidents FROM kpi_safety_incidents_reported_data GROUP BY furnace_no ORDER BY avg_incidents DESC", "expected_graph": "Bar Chart"},
]


def normalize_sql(sql: str) -> str:
    """Normalize SQL for comparison by removing extra whitespace and standardizing case."""
    if not sql:
        return ""
    # Remove extra whitespace
    sql = re.sub(r'\s+', ' ', sql.strip())
    # Lowercase for comparison (SQL is case-insensitive)
    sql = sql.lower()
    # Remove trailing semicolon if present
    sql = sql.rstrip(';')
    return sql


def compare_sql(expected: str, actual: str) -> Tuple[bool, float]:
    """
    Compare expected and actual SQL.
    Returns (is_match, similarity_score)
    """
    norm_expected = normalize_sql(expected)
    norm_actual = normalize_sql(actual)

    # Exact match
    if norm_expected == norm_actual:
        return True, 1.0

    # Check key components match
    expected_tables = set(re.findall(r'from\s+(\w+)', norm_expected))
    actual_tables = set(re.findall(r'from\s+(\w+)', norm_actual))

    expected_columns = set(re.findall(r'select\s+(.+?)\s+from', norm_expected))
    actual_columns = set(re.findall(r'select\s+(.+?)\s+from', norm_actual))

    # Table match is critical
    table_match = expected_tables == actual_tables

    # Calculate similarity
    if table_match:
        # If tables match, check for semantic similarity
        expected_words = set(norm_expected.split())
        actual_words = set(norm_actual.split())
        common = expected_words.intersection(actual_words)
        similarity = len(common) / max(len(expected_words), len(actual_words))

        # Consider a match if similarity is high enough
        if similarity >= 0.7:
            return True, similarity

    return False, 0.0


def test_query(question: str, expected_sql: str, expected_graph: str, max_retries: int = 3) -> Dict:
    """Test a single query against the chatbot API with retry logic for rate limits."""
    result = {
        "question": question,
        "expected_sql": expected_sql,
        "expected_graph": expected_graph,
        "actual_sql": None,
        "actual_graph": None,
        "sql_match": False,
        "graph_match": False,
        "error": None,
        "similarity": 0.0
    }

    for attempt in range(max_retries):
        try:
            # Call the NLP service directly
            response = requests.post(
                f"{NLP_SERVICE_URL}/api/v1/chat",
                json={
                    "question": question,
                    "allowed_tables": ["kpi_overall_equipment_efficiency_data", "kpi_downtime_data",
                                      "kpi_energy_used_data", "kpi_energy_efficiency_data",
                                      "kpi_yield_data", "kpi_defect_rate_data", "kpi_cycle_time_data",
                                      "kpi_quantity_produced_data", "kpi_production_efficiency_data",
                                      "kpi_mean_time_between_failures_data", "kpi_mean_time_to_repair_data",
                                      "kpi_mean_time_between_stoppages_data", "kpi_first_pass_yield_data",
                                      "kpi_rework_rate_data", "kpi_resource_capacity_utilization_data",
                                      "kpi_output_rate_data", "kpi_on_time_delivery_data",
                                      "kpi_maintenance_compliance_data", "kpi_planned_maintenance_data",
                                      "kpi_safety_incidents_reported_data", "core_process_tap_production",
                                      "core_process_tap_process", "core_process_tap_grading",
                                      "log_book_furnace_down_time_event", "log_book_reasons",
                                      "log_book_downtime_type_master", "furnace_furnaceconfig",
                                      "furnace_config_parameters", "plant_plant"]
                },
                timeout=60
            )

            if response.status_code == 200:
                data = response.json()

                # Check if success
                if data.get("success"):
                    result["actual_sql"] = data.get("sql", "")

                    # Extract graph type from chart_config
                    chart_config = data.get("chart_config", {})
                    if chart_config:
                        chart_type = chart_config.get("chartType", "") or chart_config.get("type", "")
                        if chart_type == "kpi" or chart_type == "progress":
                            result["actual_graph"] = "KPI Card"
                        elif chart_type == "bar":
                            result["actual_graph"] = "Bar Chart"
                        elif chart_type == "line":
                            result["actual_graph"] = "Line Chart"
                        elif chart_type == "table":
                            result["actual_graph"] = "Table"
                        else:
                            result["actual_graph"] = chart_type
                    else:
                        # Default to table if no chart config
                        result["actual_graph"] = "Table"

                    # Compare SQL
                    sql_match, similarity = compare_sql(expected_sql, result["actual_sql"])
                    result["sql_match"] = sql_match
                    result["similarity"] = similarity

                    # Compare graph type
                    if result["actual_graph"] and expected_graph:
                        result["graph_match"] = result["actual_graph"].lower() == expected_graph.lower()
                else:
                    # API returned success=false - check if rate limit
                    error_msg = data.get("error", "Unknown error")
                    if "Token limit" in error_msg or "rate" in error_msg.lower():
                        # Extract wait time
                        wait_match = re.search(r'wait (\d+) seconds', error_msg)
                        wait_time = int(wait_match.group(1)) + 2 if wait_match else 15
                        if attempt < max_retries - 1:
                            print(f" (rate limit, waiting {wait_time}s...)", end="", flush=True)
                            time.sleep(wait_time)
                            continue  # Retry
                    result["error"] = error_msg
            else:
                result["error"] = f"HTTP {response.status_code}: {response.text[:200]}"

        except requests.exceptions.Timeout:
            result["error"] = "Request timeout"
        except requests.exceptions.ConnectionError:
            result["error"] = "Connection error - service not available"
        except Exception as e:
            result["error"] = str(e)

        # If we got here without continuing, break out of retry loop
        break

    return result


def wait_for_services():
    """Wait for services to be healthy."""
    print("Waiting for services to be ready...")
    max_retries = 30

    for i in range(max_retries):
        try:
            django_health = requests.get(f"{DJANGO_URL}/api/chatbot/health/", timeout=5)
            nlp_health = requests.get(f"{NLP_SERVICE_URL}/health", timeout=5)

            if django_health.status_code == 200 and nlp_health.status_code == 200:
                nlp_data = nlp_health.json()
                if nlp_data.get("schema_loaded"):
                    print("Services are ready!")
                    return True
        except:
            pass

        print(f"  Waiting... ({i+1}/{max_retries})")
        time.sleep(2)

    return False


def run_tests(test_cases: List[Dict], delay: float = 1.0) -> List[Dict]:
    """Run all test cases."""
    results = []
    total = len(test_cases)

    for i, test_case in enumerate(test_cases):
        print(f"\nTesting [{i+1}/{total}]: {test_case['question'][:50]}...")
        result = test_query(
            test_case["question"],
            test_case["expected_sql"],
            test_case["expected_graph"]
        )
        result["category"] = test_case["category"]
        results.append(result)

        status = "PASS" if result["sql_match"] else "FAIL"
        graph_status = "PASS" if result["graph_match"] else "FAIL"
        print(f"  SQL: {status} (similarity: {result['similarity']:.2f}) | Graph: {graph_status}")

        if result["error"]:
            print(f"  Error: {result['error']}")

        time.sleep(delay)  # Rate limiting

    return results


def generate_report(results: List[Dict]) -> str:
    """Generate a summary report."""
    total = len(results)
    sql_pass = sum(1 for r in results if r["sql_match"])
    graph_pass = sum(1 for r in results if r["graph_match"])
    errors = sum(1 for r in results if r["error"])

    report = f"""
================================================================================
                        CHATBOT QUERY TEST REPORT
================================================================================
Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

SUMMARY
-------
Total Tests:     {total}
SQL Matches:     {sql_pass}/{total} ({100*sql_pass/total:.1f}%)
Graph Matches:   {graph_pass}/{total} ({100*graph_pass/total:.1f}%)
Errors:          {errors}

BY CATEGORY
-----------"""

    # Group by category
    categories = {}
    for r in results:
        cat = r["category"]
        if cat not in categories:
            categories[cat] = {"total": 0, "sql_pass": 0, "graph_pass": 0}
        categories[cat]["total"] += 1
        if r["sql_match"]:
            categories[cat]["sql_pass"] += 1
        if r["graph_match"]:
            categories[cat]["graph_pass"] += 1

    for cat, stats in sorted(categories.items()):
        sql_pct = 100 * stats["sql_pass"] / stats["total"]
        graph_pct = 100 * stats["graph_pass"] / stats["total"]
        report += f"\n{cat:20} SQL: {stats['sql_pass']}/{stats['total']} ({sql_pct:.0f}%) | Graph: {stats['graph_pass']}/{stats['total']} ({graph_pct:.0f}%)"

    report += "\n\nFAILED TESTS\n------------"

    failures = [r for r in results if not r["sql_match"] or not r["graph_match"]]
    for r in failures[:50]:  # Limit to first 50 failures
        sql_status = "PASS" if r["sql_match"] else "FAIL"
        graph_status = "PASS" if r["graph_match"] else "FAIL"
        report += f"\n\n[{r['category']}] {r['question']}"
        report += f"\n  SQL: {sql_status} | Graph: {graph_status}"
        if not r["sql_match"]:
            report += f"\n  Expected: {r['expected_sql'][:100]}..."
            report += f"\n  Actual:   {(r['actual_sql'] or 'N/A')[:100]}..."
        if not r["graph_match"]:
            report += f"\n  Expected Graph: {r['expected_graph']} | Actual: {r['actual_graph']}"
        if r["error"]:
            report += f"\n  Error: {r['error']}"

    if len(failures) > 50:
        report += f"\n\n... and {len(failures) - 50} more failures"

    return report


def save_results_csv(results: List[Dict], filename: str):
    """Save results to CSV file."""
    with open(filename, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow([
            "Category", "Question", "Expected SQL", "Actual SQL",
            "SQL Match", "Similarity", "Expected Graph", "Actual Graph",
            "Graph Match", "Error", "Status"
        ])

        for r in results:
            status = "PASS" if r["sql_match"] and r["graph_match"] else "FAIL"
            writer.writerow([
                r["category"],
                r["question"],
                r["expected_sql"],
                r["actual_sql"] or "",
                r["sql_match"],
                f"{r['similarity']:.2f}",
                r["expected_graph"],
                r["actual_graph"] or "",
                r["graph_match"],
                r["error"] or "",
                status
            ])


if __name__ == "__main__":
    print("=" * 60)
    print("CHATBOT QUERY TEST SUITE")
    print("=" * 60)

    # Wait for services
    if not wait_for_services():
        print("ERROR: Services not ready. Exiting.")
        exit(1)

    # Run tests
    print(f"\nRunning {len(TEST_CASES)} test cases...")
    results = run_tests(TEST_CASES, delay=2.0)  # Increased delay for rate limiting

    # Generate report
    report = generate_report(results)
    print(report)

    # Save results
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    csv_file = f"test_results_{timestamp}.csv"
    save_results_csv(results, csv_file)
    print(f"\nResults saved to: {csv_file}")

    # Save report
    report_file = f"test_report_{timestamp}.txt"
    with open(report_file, 'w', encoding='utf-8') as f:
        f.write(report)
    print(f"Report saved to: {report_file}")
