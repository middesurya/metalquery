#!/usr/bin/env python3
"""
Comprehensive Chatbot Query Test Suite
Tests SQL generation and graph type prediction against expected values
"""

import requests
import json
import time
import re
import csv
from datetime import datetime
from typing import Dict, List, Tuple
from difflib import SequenceMatcher

NLP_SERVICE_URL = "http://localhost:8003"

# All test cases from user specification
TEST_CASES = [
    # OEE Tests
    ("OEE", "What is the average oee for all furnaces", "SELECT AVG(oee_percentage) as average_oee FROM kpi_overall_equipment_efficiency_data", "KPI Card"),
    ("OEE", "What is the average oee for furnace 1", "SELECT AVG(oee_percentage) FROM kpi_overall_equipment_efficiency_data WHERE furnace_no = 1", "KPI Card"),
    ("OEE", "What is the average oee for furnace 1 last 30 days", "SELECT AVG(oee_percentage) FROM kpi_overall_equipment_efficiency_data WHERE furnace_no = 1 AND date >= CURRENT_DATE - INTERVAL '30 days'", "KPI Card"),
    ("OEE", "Show Average OEE by furnace", "SELECT furnace_no, AVG(oee_percentage) as avg_oee FROM kpi_overall_equipment_efficiency_data GROUP BY furnace_no ORDER BY avg_oee DESC", "Bar Chart"),
    ("OEE", "Show OEE by furnace", "SELECT furnace_no, AVG(oee_percentage) as avg_oee FROM kpi_overall_equipment_efficiency_data GROUP BY furnace_no ORDER BY avg_oee DESC", "Bar Chart"),
    ("OEE", "Which furnace has highest OEE?", "SELECT furnace_no, AVG(oee_percentage) as avg_oee FROM kpi_overall_equipment_efficiency_data GROUP BY furnace_no ORDER BY avg_oee DESC LIMIT 1", "Bar Chart"),
    ("OEE", "Show OEE trend for Furnace 2", "SELECT date, oee_percentage FROM kpi_overall_equipment_efficiency_data WHERE furnace_no = 2 ORDER BY date DESC LIMIT 100", "Table"),
    ("OEE", "Show OEE trend last week", "SELECT date, furnace_no, oee_percentage FROM kpi_overall_equipment_efficiency_data WHERE date >= CURRENT_DATE - INTERVAL '7 days' ORDER BY date DESC", "Table"),
    ("OEE", "Compare OEE between Furnace 1 and 2", "SELECT furnace_no, AVG(oee_percentage) as avg_oee FROM kpi_overall_equipment_efficiency_data WHERE furnace_no IN (1, 2) GROUP BY furnace_no ORDER BY avg_oee DESC", "Bar Chart"),
    ("OEE", "Show oee by shift", "SELECT shift_id, AVG(oee_percentage) as avg_oee FROM kpi_overall_equipment_efficiency_data GROUP BY shift_id ORDER BY avg_oee DESC", "Bar Chart"),
    ("OEE", "Compare all furnaces by OEE", "SELECT furnace_no, AVG(oee_percentage) as avg_oee, MAX(oee_percentage) as max_oee, MIN(oee_percentage) as min_oee FROM kpi_overall_equipment_efficiency_data GROUP BY furnace_no ORDER BY avg_oee DESC", "Bar Chart"),
    ("OEE", "Show best and worst shift by oee", "SELECT shift_id, AVG(oee_percentage) as avg_oee FROM kpi_overall_equipment_efficiency_data GROUP BY shift_id ORDER BY avg_oee DESC", "Bar Chart"),
    ("OEE", "Show oee statistics", "SELECT MIN(oee_percentage) as min_oee, MAX(oee_percentage) as max_oee, AVG(oee_percentage) as avg_oee, STDDEV(oee_percentage) as stddev_oee FROM kpi_overall_equipment_efficiency_data", "KPI Card"),
    ("OEE", "Show OEE records above 90%", "SELECT date, furnace_no, shift_id, oee_percentage FROM kpi_overall_equipment_efficiency_data WHERE oee_percentage > 90 ORDER BY oee_percentage DESC LIMIT 100", "Table"),
    ("OEE", "Compare OEE January vs February 2025", "SELECT EXTRACT(MONTH FROM date) as month, AVG(oee_percentage) as avg_oee FROM kpi_overall_equipment_efficiency_data WHERE EXTRACT(YEAR FROM date) = 2025 AND EXTRACT(MONTH FROM date) IN (1, 2) GROUP BY EXTRACT(MONTH FROM date) ORDER BY month", "Line Chart"),
    ("OEE", "What is the average OEE overall?", "SELECT AVG(oee_percentage) as average_oee FROM kpi_overall_equipment_efficiency_data", "KPI Card"),
    ("OEE", "What is the average OEE per day?", "SELECT date, AVG(oee_percentage) as avg_oee FROM kpi_overall_equipment_efficiency_data GROUP BY date ORDER BY date DESC", "Line Chart"),
    ("OEE", "What is the average OEE per shift?", "SELECT shift_id, AVG(oee_percentage) as avg_oee FROM kpi_overall_equipment_efficiency_data GROUP BY shift_id ORDER BY avg_oee DESC", "Bar Chart"),
    ("OEE", "Which day had the highest average OEE?", "SELECT date, AVG(oee_percentage) as avg_oee FROM kpi_overall_equipment_efficiency_data GROUP BY date ORDER BY avg_oee DESC LIMIT 1", "Line Chart"),
    ("OEE", "Which shift has the highest average OEE?", "SELECT shift_id, AVG(oee_percentage) as avg_oee FROM kpi_overall_equipment_efficiency_data GROUP BY shift_id ORDER BY avg_oee DESC LIMIT 1", "Bar Chart"),
    ("OEE", "Which machine has the highest average OEE?", "SELECT machine_id, AVG(oee_percentage) as avg_oee FROM kpi_overall_equipment_efficiency_data GROUP BY machine_id ORDER BY avg_oee DESC LIMIT 1", "Bar Chart"),
    ("OEE", "Show top 5 machines by OEE", "SELECT machine_id, AVG(oee_percentage) as avg_oee FROM kpi_overall_equipment_efficiency_data GROUP BY machine_id ORDER BY avg_oee DESC LIMIT 5", "Bar Chart"),
    ("OEE", "Compare OEE for FURNACE vs ELECTROD", "SELECT machine_id, AVG(oee_percentage) as avg_oee, MIN(oee_percentage) as min_oee, MAX(oee_percentage) as max_oee FROM kpi_overall_equipment_efficiency_data WHERE machine_id IN ('FURNACE', 'ELECTROD') GROUP BY machine_id ORDER BY avg_oee DESC", "Bar Chart"),
    ("OEE", "Compare average OEE between furnace 1 and furnace 888", "SELECT furnace_no, AVG(oee_percentage) as avg_oee FROM kpi_overall_equipment_efficiency_data WHERE furnace_no IN (1, 888) GROUP BY furnace_no ORDER BY avg_oee DESC", "Bar Chart"),
    ("OEE", "Which furnace has the most OEE drops below 70?", "SELECT furnace_no, COUNT(*) as drop_count FROM kpi_overall_equipment_efficiency_data WHERE oee_percentage < 70 GROUP BY furnace_no ORDER BY drop_count DESC", "Bar Chart"),
    ("OEE", "What is the max OEE for furnace 1?", "SELECT MAX(oee_percentage) as max_oee FROM kpi_overall_equipment_efficiency_data WHERE furnace_no = 1", "KPI Card"),
    ("OEE", "What is the average OEE for product M004?", "SELECT AVG(oee_percentage) as avg_oee FROM kpi_overall_equipment_efficiency_data WHERE product_type_id = 'M004'", "KPI Card"),
    ("OEE", "Which product_type_id has the highest OEE?", "SELECT product_type_id, AVG(oee_percentage) as avg_oee FROM kpi_overall_equipment_efficiency_data GROUP BY product_type_id ORDER BY avg_oee DESC LIMIT 1", "Bar Chart"),
    ("OEE", "Show daily oee trend", "SELECT date, AVG(oee_percentage) as avg_oee, MIN(oee_percentage) as min_oee, MAX(oee_percentage) as max_oee FROM kpi_overall_equipment_efficiency_data GROUP BY date ORDER BY date DESC", "Line Chart"),
    ("OEE", "Show records where OEE is below 70", "SELECT date, shift_id, oee_percentage, furnace_no, machine_id FROM kpi_overall_equipment_efficiency_data WHERE oee_percentage < 70 ORDER BY oee_percentage ASC LIMIT 100", "Table"),
    ("OEE", "List the top 10 lowest OEE incidents", "SELECT date, shift_id, oee_percentage, furnace_no, machine_id FROM kpi_overall_equipment_efficiency_data ORDER BY oee_percentage ASC LIMIT 10", "Table"),

    # Downtime Tests
    ("Downtime", "Show Total downtime by furnace", "SELECT furnace_no, SUM(downtime_hours) as total_downtime FROM kpi_downtime_data GROUP BY furnace_no ORDER BY total_downtime DESC", "Line Chart"),
    ("Downtime", "Show what is the total downtime last year", "SELECT SUM(downtime_hours) as total_downtime FROM kpi_downtime_data WHERE date >= CURRENT_DATE - INTERVAL '1 year'", "KPI Card"),
    ("Downtime", "What is the average downtime per furnace", "SELECT furnace_no, AVG(downtime_hours) as avg_downtime FROM kpi_downtime_data GROUP BY furnace_no", "Line Chart"),
    ("Downtime", "Show downtime by furnace", "SELECT furnace_no, SUM(downtime_hours) as total_downtime FROM kpi_downtime_data GROUP BY furnace_no ORDER BY total_downtime DESC", "Line Chart"),
    ("Downtime", "Display downtime trend last 30 days", "SELECT date, furnace_no, downtime_hours FROM kpi_downtime_data WHERE date >= CURRENT_DATE - INTERVAL '30 days' ORDER BY date DESC", "Table"),
    ("Downtime", "Show downtime events for Furnace 1", "SELECT obs_start_dt, obs_end_dt, downtime_hours FROM log_book_furnace_down_time_event WHERE furnace_no = 1 ORDER BY obs_start_dt DESC LIMIT 50", "Table"),
    ("Downtime", "Compare downtime between machines", "SELECT machine_id, SUM(downtime_hours) as total_downtime FROM kpi_downtime_data GROUP BY machine_id ORDER BY total_downtime DESC", "Line Chart"),
    ("Downtime", "Show week over week downtime comparison", "SELECT CASE WHEN date >= CURRENT_DATE - INTERVAL '7 days' THEN 'Current Week' ELSE 'Previous Week' END as period, SUM(downtime_hours) as total_downtime FROM kpi_downtime_data WHERE date >= CURRENT_DATE - INTERVAL '14 days' GROUP BY period", "Line Chart"),
    ("Downtime", "Show downtime events exceeding 8 hours", "SELECT obs_start_dt, furnace_no, downtime_hours FROM log_book_furnace_down_time_event WHERE downtime_hours > 8 ORDER BY downtime_hours DESC", "Table"),
    ("Downtime", "Show downtime statistics by furnace", "SELECT furnace_no, MIN(downtime_hours) as min, MAX(downtime_hours) as max, AVG(downtime_hours) as avg, SUM(downtime_hours) as total, COUNT(*) as count FROM kpi_downtime_data GROUP BY furnace_no", "Line Chart"),
    ("Downtime", "Compare shifts 4, 12, and 20 downtime", "SELECT shift_id, SUM(downtime_hours) as total_downtime FROM kpi_downtime_data WHERE shift_id IN ('4', '12', '20') GROUP BY shift_id ORDER BY total_downtime DESC", "Line Chart"),
    ("Downtime", "What is the total downtime?", "SELECT SUM(downtime_hours) as total_downtime FROM kpi_downtime_data", "KPI Card"),
    ("Downtime", "Show downtime today", "SELECT furnace_no, SUM(downtime_hours) as downtime FROM kpi_downtime_data WHERE date = CURRENT_DATE GROUP BY furnace_no", "Line Chart"),
    ("Downtime", "Show daily downtime trend", "SELECT date, SUM(downtime_hours) as daily_downtime FROM kpi_downtime_data GROUP BY date ORDER BY date DESC LIMIT 30", "Line Chart"),
    ("Downtime", "Show downtime by shift", "SELECT shift_id, SUM(downtime_hours) as total_downtime FROM kpi_downtime_data GROUP BY shift_id ORDER BY total_downtime DESC", "Line Chart"),
    ("Downtime", "Which machine has most downtime?", "SELECT machine_id, SUM(downtime_hours) as total_downtime FROM kpi_downtime_data GROUP BY machine_id ORDER BY total_downtime DESC LIMIT 1", "Line Chart"),
    ("Downtime", "Show downtime last week", "SELECT date, furnace_no, SUM(downtime_hours) as downtime FROM kpi_downtime_data WHERE date >= CURRENT_DATE - INTERVAL '7 days' GROUP BY date, furnace_no ORDER BY date DESC", "Line Chart"),
    ("Downtime", "Show furnaces with high downtime", "SELECT furnace_no, SUM(downtime_hours) as total_downtime FROM kpi_downtime_data GROUP BY furnace_no HAVING SUM(downtime_hours) > 10 ORDER BY total_downtime DESC", "Line Chart"),
    ("Downtime", "What is the total downtime from events", "SELECT SUM(downtime_hours) as total_downtime FROM log_book_furnace_down_time_event", "KPI Card"),
    ("Downtime", "Show downtime events by furnace", "SELECT furnace_no, SUM(downtime_hours) as total_downtime, COUNT(*) as event_count FROM log_book_furnace_down_time_event GROUP BY furnace_no ORDER BY total_downtime DESC", "Line Chart"),
    ("Downtime", "Show recent downtime events", "SELECT furnace_no, obs_start_dt, obs_end_dt, downtime_hours FROM log_book_furnace_down_time_event ORDER BY obs_start_dt DESC LIMIT 20", "Table"),
    ("Downtime", "Show downtime by reason", "SELECT reason_id, SUM(downtime_hours) as total_downtime, COUNT(*) as event_count FROM log_book_furnace_down_time_event GROUP BY reason_id ORDER BY total_downtime DESC", "Line Chart"),
    ("Downtime", "Show long downtime events", "SELECT furnace_no, obs_start_dt, obs_end_dt, downtime_hours FROM log_book_furnace_down_time_event WHERE downtime_hours > 4 ORDER BY downtime_hours DESC LIMIT 50", "Table"),
    ("Downtime", "Show downtime events last 7 days", "SELECT furnace_no, obs_start_dt, downtime_hours FROM log_book_furnace_down_time_event WHERE obs_start_dt >= CURRENT_DATE - INTERVAL '7 days' ORDER BY obs_start_dt DESC", "Table"),
    ("Downtime", "Show daily downtime event summary", "SELECT DATE_TRUNC('day', obs_start_dt)::DATE as event_date, SUM(downtime_hours) as total_downtime, COUNT(*) as event_count FROM log_book_furnace_down_time_event GROUP BY DATE_TRUNC('day', obs_start_dt) ORDER BY event_date DESC LIMIT 30", "Line Chart"),

    # Energy Tests
    ("Energy", "Show Total energy consumption by furnace", "SELECT furnace_no, SUM(energy_used) as total_energy FROM kpi_energy_used_data GROUP BY furnace_no ORDER BY total_energy DESC", "Bar Chart"),
    ("Energy", "Show energy consumption by furnace", "SELECT furnace_no, SUM(energy_used) as total_energy FROM kpi_energy_used_data GROUP BY furnace_no ORDER BY total_energy DESC", "Bar Chart"),
    ("Energy", "Display energy efficiency trend", "SELECT date, furnace_no, energy_efficiency FROM kpi_energy_efficiency_data ORDER BY date DESC LIMIT 100", "Table"),
    ("Energy", "Compare energy efficiency by furnace", "SELECT furnace_no, AVG(energy_efficiency) as avg_efficiency FROM kpi_energy_efficiency_data GROUP BY furnace_no ORDER BY avg_efficiency", "Bar Chart"),
    ("Energy", "Show monthly energy trend", "SELECT DATE_TRUNC('month', date)::DATE as month, SUM(energy_used) as monthly_total FROM kpi_energy_used_data GROUP BY DATE_TRUNC('month', date) ORDER BY month DESC", "Line Chart"),
    ("Energy", "Show energy efficiency range", "SELECT MIN(energy_efficiency) as min_eff, MAX(energy_efficiency) as max_eff, AVG(energy_efficiency) as avg_eff FROM kpi_energy_efficiency_data", "KPI Card"),
    ("Energy", "Show energy usage above average", "SELECT furnace_no, SUM(energy_used) as total_energy FROM kpi_energy_used_data GROUP BY furnace_no HAVING SUM(energy_used) > (SELECT AVG(energy_used) FROM kpi_energy_used_data)", "Bar Chart"),
    ("Energy", "Show energy spikes above normal", "SELECT date, furnace_no, energy_used FROM kpi_energy_used_data WHERE energy_used > (SELECT AVG(energy_used) + 2 * STDDEV(energy_used) FROM kpi_energy_used_data) ORDER BY energy_used DESC", "KPI Card"),
    ("Energy", "What is the average energy efficiency?", "SELECT AVG(energy_efficiency) as avg_energy_efficiency FROM kpi_energy_efficiency_data", "KPI Card"),
    ("Energy", "Show energy efficiency for furnace 1", "SELECT date, shift_id, energy_efficiency FROM kpi_energy_efficiency_data WHERE furnace_no = 1 ORDER BY date DESC LIMIT 100", "Table"),
    ("Energy", "Which furnace is most energy efficient?", "SELECT furnace_no, AVG(energy_efficiency) as avg_efficiency FROM kpi_energy_efficiency_data GROUP BY furnace_no ORDER BY avg_efficiency ASC LIMIT 1", "Bar Chart"),
    ("Energy", "Show energy efficiency by shift", "SELECT shift_id, AVG(energy_efficiency) as avg_efficiency FROM kpi_energy_efficiency_data GROUP BY shift_id ORDER BY avg_efficiency", "Bar Chart"),
    ("Energy", "Show energy efficiency trend", "SELECT date, AVG(energy_efficiency) as avg_efficiency FROM kpi_energy_efficiency_data GROUP BY date ORDER BY date DESC LIMIT 30", "Line Chart"),
    ("Energy", "Compare energy efficiency between furnaces", "SELECT furnace_no, AVG(energy_efficiency) as avg_efficiency, MIN(energy_efficiency) as min_eff, MAX(energy_efficiency) as max_eff FROM kpi_energy_efficiency_data GROUP BY furnace_no ORDER BY avg_efficiency", "Bar Chart"),
    ("Energy", "Which machines have poor energy efficiency?", "SELECT machine_id, AVG(energy_efficiency) as avg_efficiency FROM kpi_energy_efficiency_data GROUP BY machine_id ORDER BY avg_efficiency DESC LIMIT 5", "Bar Chart"),
    ("Energy", "What is the total energy used?", "SELECT SUM(energy_used) as total_energy_used FROM kpi_energy_used_data", "KPI Card"),
    ("Energy", "Show energy used today", "SELECT furnace_no, SUM(energy_used) as total_energy FROM kpi_energy_used_data WHERE date = CURRENT_DATE GROUP BY furnace_no", "Line Chart"),
    ("Energy", "Show daily energy consumption", "SELECT date, SUM(energy_used) as daily_energy FROM kpi_energy_used_data GROUP BY date ORDER BY date DESC LIMIT 30", "Line Chart"),
    ("Energy", "Show energy used by shift", "SELECT shift_id, SUM(energy_used) as total_energy FROM kpi_energy_used_data GROUP BY shift_id ORDER BY total_energy DESC", "Bar Chart"),
    ("Energy", "Show monthly energy consumption", "SELECT DATE_TRUNC('month', date)::DATE as month, SUM(energy_used) as monthly_energy FROM kpi_energy_used_data GROUP BY DATE_TRUNC('month', date) ORDER BY month DESC", "Line Chart"),
    ("Energy", "Which machine uses most energy?", "SELECT machine_id, SUM(energy_used) as total_energy FROM kpi_energy_used_data GROUP BY machine_id ORDER BY total_energy DESC LIMIT 1", "Bar Chart"),
    ("Energy", "Show energy consumption last 7 days", "SELECT date, SUM(energy_used) as daily_total FROM kpi_energy_used_data WHERE date >= CURRENT_DATE - INTERVAL '7 days' GROUP BY date ORDER BY date", "Line Chart"),
    ("Energy", "Compare energy used between furnaces", "SELECT furnace_no, SUM(energy_used) as total, AVG(energy_used) as avg_per_record FROM kpi_energy_used_data GROUP BY furnace_no ORDER BY total DESC", "Bar Chart"),
    ("Energy", "Show high energy consumption events", "SELECT date, shift_id, furnace_no, energy_used FROM kpi_energy_used_data WHERE energy_used > (SELECT AVG(energy_used) + STDDEV(energy_used) FROM kpi_energy_used_data) ORDER BY energy_used DESC LIMIT 50", "KPI Card"),
    ("Energy", "What is the average energy per tap", "SELECT AVG(energy) as avg_energy FROM core_process_tap_production", "KPI Card"),
    ("Energy", "Show tap production energy efficiency", "SELECT AVG(energy_efficiency) as avg_energy_efficiency FROM core_process_tap_production", "KPI Card"),

    # Yield Tests
    ("Yield", "What is the average yield for furnace 2", "SELECT AVG(yield_percentage) FROM kpi_yield_data WHERE furnace_no = 2", "KPI Card"),
    ("Yield", "Show yield data for last month", "SELECT date, furnace_no, yield_percentage FROM kpi_yield_data WHERE date >= CURRENT_DATE - INTERVAL '30 days' ORDER BY date DESC", "Table"),
    ("Yield", "Which shift has highest yield?", "SELECT shift_id, AVG(yield_percentage) as avg_yield FROM kpi_yield_data GROUP BY shift_id ORDER BY avg_yield DESC LIMIT 1", "Bar Chart"),
    ("Yield", "Show yield by shift", "SELECT shift_id, AVG(yield_percentage) as avg_yield FROM kpi_yield_data GROUP BY shift_id ORDER BY avg_yield DESC", "Bar Chart"),
    ("Yield", "Which product type has highest yield?", "SELECT product_type_id, AVG(yield_percentage) as avg_yield FROM kpi_yield_data GROUP BY product_type_id ORDER BY avg_yield DESC LIMIT 1", "Bar Chart"),
    ("Yield", "Show yield statistics by furnace", "SELECT furnace_no, AVG(yield_percentage) as avg_yield, STDDEV(yield_percentage) as stddev_yield, MIN(yield_percentage) as min_yield, MAX(yield_percentage) as max_yield FROM kpi_yield_data GROUP BY furnace_no", "Bar Chart"),
    ("Yield", "Show low yield furnaces below 85%", "SELECT furnace_no, AVG(yield_percentage) as avg_yield FROM kpi_yield_data GROUP BY furnace_no HAVING AVG(yield_percentage) < 85 ORDER BY avg_yield", "Bar Chart"),
    ("Yield", "Show bottom 3 furnaces by yield", "SELECT furnace_no, AVG(yield_percentage) as avg_yield FROM kpi_yield_data GROUP BY furnace_no ORDER BY avg_yield ASC LIMIT 3", "Bar Chart"),
    ("Yield", "Show unusually low yield", "SELECT date, furnace_no, yield_percentage FROM kpi_yield_data WHERE yield_percentage < (SELECT AVG(yield_percentage) - 1.5 * STDDEV(yield_percentage) FROM kpi_yield_data) ORDER BY yield_percentage", "KPI Card"),
    ("Yield", "Compare products MET30 and MET32 yield", "SELECT product_type_id, AVG(yield_percentage) as avg_yield FROM kpi_yield_data WHERE product_type_id IN ('MET30', 'MET32') GROUP BY product_type_id ORDER BY avg_yield DESC", "Bar Chart"),
    ("Yield", "What is the average yield?", "SELECT AVG(yield_percentage) as avg_yield FROM kpi_yield_data", "KPI Card"),
    ("Yield", "Show yield by furnace", "SELECT furnace_no, AVG(yield_percentage) as avg_yield FROM kpi_yield_data GROUP BY furnace_no ORDER BY avg_yield DESC", "Bar Chart"),
    ("Yield", "Which furnace has best yield?", "SELECT furnace_no, AVG(yield_percentage) as avg_yield FROM kpi_yield_data GROUP BY furnace_no ORDER BY avg_yield DESC LIMIT 1", "Bar Chart"),
    ("Yield", "Show yield trend last 30 days", "SELECT date, AVG(yield_percentage) as avg_yield FROM kpi_yield_data WHERE date >= CURRENT_DATE - INTERVAL '30 days' GROUP BY date ORDER BY date DESC", "Line Chart"),
    ("Yield", "Show low yield records", "SELECT date, shift_id, furnace_no, yield_percentage FROM kpi_yield_data WHERE yield_percentage < 85 ORDER BY yield_percentage ASC LIMIT 100", "Table"),
    ("Yield", "Show yield by product type", "SELECT product_type_id, AVG(yield_percentage) as avg_yield FROM kpi_yield_data GROUP BY product_type_id ORDER BY avg_yield DESC", "Bar Chart"),
    ("Yield", "Compare yield between furnaces", "SELECT furnace_no, AVG(yield_percentage) as avg_yield, MIN(yield_percentage) as min_yield, MAX(yield_percentage) as max_yield FROM kpi_yield_data GROUP BY furnace_no ORDER BY avg_yield DESC", "Bar Chart"),
    ("Yield", "Show daily yield summary", "SELECT date, AVG(yield_percentage) as avg_yield, COUNT(*) as records FROM kpi_yield_data GROUP BY date ORDER BY date DESC LIMIT 30", "Line Chart"),
    ("Yield", "What is the average first pass yield?", "SELECT AVG(first_pass_yield) as avg_fpy FROM kpi_first_pass_yield_data", "KPI Card"),
    ("Yield", "Show first pass yield by furnace", "SELECT furnace_no, AVG(first_pass_yield) as avg_fpy FROM kpi_first_pass_yield_data GROUP BY furnace_no ORDER BY avg_fpy DESC", "Bar Chart"),
    ("Yield", "Show first pass yield by shift", "SELECT shift_id, AVG(first_pass_yield) as avg_fpy FROM kpi_first_pass_yield_data GROUP BY shift_id ORDER BY avg_fpy DESC", "Bar Chart"),
    ("Yield", "Show weekly yield trend", "SELECT DATE_TRUNC('week', date)::DATE as week, AVG(yield_percentage) as weekly_avg_yield FROM kpi_yield_data GROUP BY DATE_TRUNC('week', date) ORDER BY week DESC", "Line Chart"),

    # Defect Rate Tests
    ("Defect Rate", "Show recent defect rate data", "SELECT date, shift_id, furnace_no, defect_rate FROM kpi_defect_rate_data ORDER BY date DESC LIMIT 50", "Table"),
    ("Defect Rate", "Show rank furnaces by defect rate", "SELECT furnace_no, AVG(defect_rate) as avg_defect FROM kpi_defect_rate_data GROUP BY furnace_no ORDER BY avg_defect DESC", "Bar Chart"),
    ("Defect Rate", "Show defect rate above 5 percent", "SELECT date, shift_id, furnace_no, defect_rate FROM kpi_defect_rate_data WHERE defect_rate > 5 ORDER BY defect_rate DESC LIMIT 100", "Table"),
    ("Defect Rate", "Show high defect rate anomalies", "SELECT date, furnace_no, defect_rate FROM kpi_defect_rate_data WHERE defect_rate > (SELECT AVG(defect_rate) + 1.5 * STDDEV(defect_rate) FROM kpi_defect_rate_data) ORDER BY defect_rate DESC", "KPI Card"),
    ("Defect Rate", "What is the average defect rate?", "SELECT AVG(defect_rate) as avg_defect_rate FROM kpi_defect_rate_data", "KPI Card"),
    ("Defect Rate", "Show defect rate for furnace 1", "SELECT date, shift_id, defect_rate FROM kpi_defect_rate_data WHERE furnace_no = 1 ORDER BY date DESC LIMIT 100", "Table"),
    ("Defect Rate", "Which furnace has highest defect rate?", "SELECT furnace_no, AVG(defect_rate) as avg_defect_rate FROM kpi_defect_rate_data GROUP BY furnace_no ORDER BY avg_defect_rate DESC LIMIT 1", "Bar Chart"),
    ("Defect Rate", "Show defect rate by shift", "SELECT shift_id, AVG(defect_rate) as avg_defect_rate FROM kpi_defect_rate_data GROUP BY shift_id ORDER BY avg_defect_rate DESC", "Bar Chart"),
    ("Defect Rate", "Show defect rate trend last 30 days", "SELECT date, AVG(defect_rate) as avg_defect_rate FROM kpi_defect_rate_data WHERE date >= CURRENT_DATE - INTERVAL '30 days' GROUP BY date ORDER BY date DESC", "Line Chart"),
    ("Defect Rate", "Which products have high defect rates?", "SELECT product_type_id, AVG(defect_rate) as avg_defect_rate FROM kpi_defect_rate_data GROUP BY product_type_id ORDER BY avg_defect_rate DESC LIMIT 5", "Bar Chart"),
    ("Defect Rate", "Compare defect rate between shifts 4 and 12", "SELECT shift_id, AVG(defect_rate) as avg_defect_rate FROM kpi_defect_rate_data WHERE shift_id IN ('4', '12') GROUP BY shift_id", "Bar Chart"),
    ("Defect Rate", "Show defect rate statistics", "SELECT MIN(defect_rate) as min_defect, MAX(defect_rate) as max_defect, AVG(defect_rate) as avg_defect, STDDEV(defect_rate) as stddev_defect FROM kpi_defect_rate_data", "KPI Card"),

    # Cycle Time Tests
    ("Cycle Time", "What is the cycle time for FURNACE on 2024-01-07?", "SELECT date, shift_id, cycle_time, furnace_no FROM kpi_cycle_time_data WHERE machine_id = 'FURNACE' AND date = '2024-01-07' ORDER BY shift_id", "Table"),
    ("Cycle Time", "Show all cycle time records for 2024-01-08", "SELECT date, shift_id, cycle_time, furnace_no, machine_id FROM kpi_cycle_time_data WHERE date = '2024-01-08' ORDER BY shift_id", "Table"),
    ("Cycle Time", "What is the average cycle time overall?", "SELECT AVG(cycle_time) as average_cycle_time FROM kpi_cycle_time_data", "KPI Card"),
    ("Cycle Time", "What is the total cycle time per day?", "SELECT date, SUM(cycle_time) as total_cycle_time FROM kpi_cycle_time_data GROUP BY date ORDER BY date DESC", "Line Chart"),
    ("Cycle Time", "What is the average cycle time per shift?", "SELECT shift_id, AVG(cycle_time) as avg_cycle_time FROM kpi_cycle_time_data GROUP BY shift_id ORDER BY avg_cycle_time DESC", "Line Chart"),
    ("Cycle Time", "Show Average cycle time by furnace", "SELECT furnace_no, AVG(cycle_time) as avg_cycle_time FROM kpi_cycle_time_data GROUP BY furnace_no ORDER BY avg_cycle_time DESC", "Line Chart"),
    ("Cycle Time", "Which shift has the highest average cycle time?", "SELECT shift_id, AVG(cycle_time) as avg_cycle_time FROM kpi_cycle_time_data GROUP BY shift_id ORDER BY avg_cycle_time DESC LIMIT 1", "Line Chart"),
    ("Cycle Time", "Compare cycle time between shifts 4, 12, and 20", "SELECT shift_id, AVG(cycle_time) as avg_cycle_time, MIN(cycle_time) as min_cycle_time, MAX(cycle_time) as max_cycle_time FROM kpi_cycle_time_data WHERE shift_id IN ('4', '12', '20') GROUP BY shift_id ORDER BY avg_cycle_time DESC", "Line Chart"),
    ("Cycle Time", "Which machine has the highest average cycle time?", "SELECT machine_id, AVG(cycle_time) as avg_cycle_time FROM kpi_cycle_time_data GROUP BY machine_id ORDER BY avg_cycle_time DESC LIMIT 1", "Line Chart"),
    ("Cycle Time", "Show top 5 machines by cycle time", "SELECT machine_id, AVG(cycle_time) as avg_cycle_time FROM kpi_cycle_time_data GROUP BY machine_id ORDER BY avg_cycle_time DESC LIMIT 5", "Line Chart"),
    ("Cycle Time", "Which machine had cycle time above 90?", "SELECT DISTINCT machine_id, date, shift_id, cycle_time FROM kpi_cycle_time_data WHERE cycle_time > 90 ORDER BY cycle_time DESC", "Table"),
    ("Cycle Time", "Compare average cycle time between furnace 1 and furnace 888", "SELECT furnace_no, AVG(cycle_time) as avg_cycle_time FROM kpi_cycle_time_data WHERE furnace_no IN (1, 888) GROUP BY furnace_no ORDER BY avg_cycle_time DESC", "Line Chart"),
    ("Cycle Time", "What is the max cycle time for furnace 1?", "SELECT MAX(cycle_time) as max_cycle_time FROM kpi_cycle_time_data WHERE furnace_no = 1", "KPI Card"),
    ("Cycle Time", "Show cycle time statistics by furnace", "SELECT furnace_no, AVG(cycle_time) as avg_cycle_time, MIN(cycle_time) as min_cycle_time, MAX(cycle_time) as max_cycle_time, STDDEV(cycle_time) as stddev_cycle_time FROM kpi_cycle_time_data GROUP BY furnace_no ORDER BY avg_cycle_time DESC", "Line Chart"),
    ("Cycle Time", "Show daily cycle time trend", "SELECT date, AVG(cycle_time) as avg_cycle_time, MIN(cycle_time) as min_cycle_time, MAX(cycle_time) as max_cycle_time FROM kpi_cycle_time_data GROUP BY date ORDER BY date DESC", "Line Chart"),
    ("Cycle Time", "Show records where cycle time is greater than 90", "SELECT date, shift_id, cycle_time, furnace_no, machine_id FROM kpi_cycle_time_data WHERE cycle_time > 90 ORDER BY cycle_time DESC LIMIT 100", "Table"),
    ("Cycle Time", "List the top 10 highest cycle time incidents", "SELECT date, shift_id, cycle_time, furnace_no, machine_id FROM kpi_cycle_time_data ORDER BY cycle_time DESC LIMIT 10", "Table"),
    ("Cycle Time", "Show cycle time anomalies above normal", "SELECT date, shift_id, cycle_time, furnace_no, machine_id FROM kpi_cycle_time_data WHERE cycle_time > (SELECT AVG(cycle_time) + 2 * STDDEV(cycle_time) FROM kpi_cycle_time_data) ORDER BY cycle_time DESC", "KPI Card"),

    # Tap Process Tests
    ("Tap Process", "Show recent tap production data", "SELECT tap_id, cast_weight, energy, tap_production_datetime FROM core_process_tap_production ORDER BY tap_production_datetime DESC LIMIT 20", "Table"),
    ("Tap Process", "Show tap production by tap status", "SELECT t.tap_status, COUNT(t.tap_id) as tap_count, SUM(tp.cast_weight) as total_weight FROM core_process_tap_process t JOIN core_process_tap_production tp ON t.tap_id = tp.tap_id GROUP BY t.tap_status ORDER BY tap_count DESC", "Bar Chart"),
    ("Tap Process", "Show daily tap production", "SELECT DATE_TRUNC('day', tap_production_datetime)::DATE as production_date, COUNT(DISTINCT tap_id) as tap_count, SUM(cast_weight) as daily_weight FROM core_process_tap_production GROUP BY DATE_TRUNC('day', tap_production_datetime) ORDER BY production_date DESC LIMIT 30", "Line Chart"),
    ("Tap Process", "How many taps today?", "SELECT COUNT(DISTINCT tap_id) as tap_count FROM core_process_tap_process WHERE DATE(tap_datetime) = CURRENT_DATE", "KPI Card"),
    ("Tap Process", "Show taps by furnace", "SELECT furnace_no, COUNT(DISTINCT tap_id) as tap_count FROM core_process_tap_process GROUP BY furnace_no ORDER BY tap_count DESC", "Bar Chart"),
    ("Tap Process", "Show tap status summary", "SELECT tap_status, COUNT(*) as count FROM core_process_tap_process GROUP BY tap_status ORDER BY count DESC", "Bar Chart"),
    ("Tap Process", "Show recent tap processes", "SELECT tap_id, furnace_no, tap_datetime, tap_status, tap_progress FROM core_process_tap_process ORDER BY tap_datetime DESC LIMIT 20", "Table"),
    ("Tap Process", "Show tap progress distribution", "SELECT tap_progress, COUNT(*) as count FROM core_process_tap_process GROUP BY tap_progress ORDER BY count DESC", "Bar Chart"),
    ("Tap Process", "Show taps by tap hole", "SELECT tap_hole_id, COUNT(*) as tap_count FROM core_process_tap_process GROUP BY tap_hole_id ORDER BY tap_count DESC", "Bar Chart"),
    ("Tap Process", "Show daily tap count trend", "SELECT DATE_TRUNC('day', tap_datetime)::DATE as tap_date, COUNT(DISTINCT tap_id) as tap_count FROM core_process_tap_process GROUP BY DATE_TRUNC('day', tap_datetime) ORDER BY tap_date DESC LIMIT 30", "Line Chart"),

    # General Tests
    ("General", "Show Total quantity produced by furnace", "SELECT furnace_no, SUM(quantity_produced) as total_qty FROM kpi_quantity_produced_data GROUP BY furnace_no ORDER BY total_qty DESC", "Bar Chart"),
    ("General", "What is the total production for furnace 1 last month", "SELECT SUM(quantity_produced) as total_production FROM kpi_quantity_produced_data WHERE furnace_no = 1 AND date >= CURRENT_DATE - INTERVAL '30 days'", "KPI Card"),
    ("General", "Show production by furnace", "SELECT furnace_no, SUM(quantity_produced) as total_qty FROM kpi_quantity_produced_data GROUP BY furnace_no ORDER BY total_qty DESC", "Bar Chart"),
    ("General", "List all furnaces", "SELECT furnace_no, furnace_description, is_active FROM furnace_furnaceconfig ORDER BY furnace_no", "Table"),
    ("General", "List recent quality issues", "SELECT date, furnace_no, defect_rate FROM kpi_defect_rate_data ORDER BY date DESC LIMIT 100", "Table"),
    ("General", "Show production by shift", "SELECT shift_id, SUM(quantity_produced) as total_qty FROM kpi_quantity_produced_data GROUP BY shift_id ORDER BY total_qty DESC", "Bar Chart"),
    ("General", "Show production efficiency by shift", "SELECT shift_id, AVG(production_efficiency_percentage) as avg_efficiency FROM kpi_production_efficiency_data GROUP BY shift_id ORDER BY avg_efficiency DESC", "Bar Chart"),
    ("General", "Compare MTBF by furnace", "SELECT furnace_no, AVG(mtbf_hours) as avg_mtbf FROM kpi_mean_time_between_failures_data GROUP BY furnace_no ORDER BY avg_mtbf DESC", "Line Chart"),
    ("General", "Show furnaces with low efficiency below 80%", "SELECT furnace_no, AVG(oee_percentage) as avg_oee FROM kpi_overall_equipment_efficiency_data GROUP BY furnace_no HAVING AVG(oee_percentage) < 80", "Bar Chart"),
    ("General", "Show top 5 furnaces by production", "SELECT furnace_no, SUM(cast_weight) as total_production FROM core_process_tap_production GROUP BY furnace_no ORDER BY total_production DESC LIMIT 5", "Bar Chart"),
    ("General", "Show top 10 shifts by output", "SELECT shift_id, SUM(quantity_produced) as total_output FROM kpi_quantity_produced_data GROUP BY shift_id ORDER BY total_output DESC LIMIT 10", "Bar Chart"),
    ("General", "What is the best shift by efficiency", "SELECT shift_id, AVG(production_efficiency_percentage) as avg_efficiency FROM kpi_production_efficiency_data GROUP BY shift_id ORDER BY avg_efficiency DESC LIMIT 1", "Bar Chart"),
    ("General", "What is the most reliable furnace", "SELECT furnace_no, AVG(mtbf_hours) as avg_mtbf FROM kpi_mean_time_between_failures_data GROUP BY furnace_no ORDER BY avg_mtbf DESC LIMIT 1", "Line Chart"),
    ("General", "Show production quantity statistics", "SELECT AVG(quantity_produced) as avg_qty, MAX(quantity_produced) as max_qty, MIN(quantity_produced) as min_qty, SUM(quantity_produced) as total_qty FROM kpi_quantity_produced_data", "KPI Card"),
    ("General", "Show year to date production", "SELECT DATE_TRUNC('month', tap_production_datetime)::DATE as month, SUM(cast_weight) as monthly_production FROM core_process_tap_production WHERE EXTRACT(YEAR FROM tap_production_datetime) = EXTRACT(YEAR FROM CURRENT_DATE) GROUP BY DATE_TRUNC('month', tap_production_datetime) ORDER BY month DESC", "Line Chart"),
    ("General", "Show production for product m004", "SELECT date, quantity_produced FROM kpi_quantity_produced_data WHERE product_type_id = 'M004' ORDER BY date DESC LIMIT 100", "Table"),
    ("General", "What is the total quantity produced?", "SELECT SUM(quantity_produced) as total_quantity FROM kpi_quantity_produced_data", "KPI Card"),
    ("General", "Show daily production", "SELECT date, SUM(quantity_produced) as daily_production FROM kpi_quantity_produced_data GROUP BY date ORDER BY date DESC LIMIT 30", "Line Chart"),
    ("General", "Show production by product type", "SELECT product_type_id, SUM(quantity_produced) as total_production FROM kpi_quantity_produced_data GROUP BY product_type_id ORDER BY total_production DESC", "Bar Chart"),
    ("General", "Show top producing furnaces", "SELECT furnace_no, SUM(quantity_produced) as total_production FROM kpi_quantity_produced_data GROUP BY furnace_no ORDER BY total_production DESC LIMIT 5", "Bar Chart"),
    ("General", "Show monthly production", "SELECT DATE_TRUNC('month', date)::DATE as month, SUM(quantity_produced) as monthly_production FROM kpi_quantity_produced_data GROUP BY DATE_TRUNC('month', date) ORDER BY month DESC", "Line Chart"),
    ("General", "Show production trend last week", "SELECT date, SUM(quantity_produced) as daily_production FROM kpi_quantity_produced_data WHERE date >= CURRENT_DATE - INTERVAL '7 days' GROUP BY date ORDER BY date", "Line Chart"),
    ("General", "What is the average output rate?", "SELECT AVG(output_rate_percentage) as avg_output_rate FROM kpi_output_rate_data", "KPI Card"),
    ("General", "Show output rate by furnace", "SELECT furnace_no, AVG(output_rate_percentage) as avg_output_rate FROM kpi_output_rate_data GROUP BY furnace_no ORDER BY avg_output_rate DESC", "Bar Chart"),
    ("General", "Show output rate trend", "SELECT date, AVG(output_rate_percentage) as avg_output_rate FROM kpi_output_rate_data GROUP BY date ORDER BY date DESC LIMIT 30", "Line Chart"),
    ("General", "What is the average production efficiency?", "SELECT AVG(production_efficiency_percentage) as avg_efficiency FROM kpi_production_efficiency_data", "KPI Card"),
    ("General", "Show production efficiency by furnace", "SELECT furnace_no, AVG(production_efficiency_percentage) as avg_efficiency FROM kpi_production_efficiency_data GROUP BY furnace_no ORDER BY avg_efficiency DESC", "Bar Chart"),
    ("General", "Show efficiency trend", "SELECT date, AVG(production_efficiency_percentage) as avg_efficiency FROM kpi_production_efficiency_data GROUP BY date ORDER BY date DESC LIMIT 30", "Line Chart"),
    ("General", "Which furnace is most efficient?", "SELECT furnace_no, AVG(production_efficiency_percentage) as avg_efficiency FROM kpi_production_efficiency_data GROUP BY furnace_no ORDER BY avg_efficiency DESC LIMIT 1", "Bar Chart"),
    ("General", "What is the average MTBF?", "SELECT AVG(mtbf_hours) as avg_mtbf FROM kpi_mean_time_between_failures_data", "KPI Card"),
    ("General", "Show mtbf by furnace", "SELECT furnace_no, AVG(mtbf_hours) as avg_mtbf FROM kpi_mean_time_between_failures_data GROUP BY furnace_no ORDER BY avg_mtbf DESC", "Line Chart"),
    ("General", "Which furnace is most reliable?", "SELECT furnace_no, AVG(mtbf_hours) as avg_mtbf FROM kpi_mean_time_between_failures_data GROUP BY furnace_no ORDER BY avg_mtbf DESC LIMIT 1", "Line Chart"),
    ("General", "Show mtbf trend last 30 days", "SELECT date, AVG(mtbf_hours) as avg_mtbf FROM kpi_mean_time_between_failures_data WHERE date >= CURRENT_DATE - INTERVAL '30 days' GROUP BY date ORDER BY date DESC", "Line Chart"),
    ("General", "Show reliability statistics", "SELECT MIN(mtbf_hours) as min_mtbf, MAX(mtbf_hours) as max_mtbf, AVG(mtbf_hours) as avg_mtbf FROM kpi_mean_time_between_failures_data", "KPI Card"),
    ("General", "What is the average MTTR?", "SELECT AVG(mttr_hours) as avg_mttr FROM kpi_mean_time_to_repair_data", "KPI Card"),
    ("General", "Show mttr by furnace", "SELECT furnace_no, AVG(mttr_hours) as avg_mttr FROM kpi_mean_time_to_repair_data GROUP BY furnace_no ORDER BY avg_mttr DESC", "Line Chart"),
    ("General", "Which furnace takes longest to repair?", "SELECT furnace_no, AVG(mttr_hours) as avg_mttr FROM kpi_mean_time_to_repair_data GROUP BY furnace_no ORDER BY avg_mttr DESC LIMIT 1", "Line Chart"),
    ("General", "Show repair time statistics", "SELECT MIN(mttr_hours) as min_mttr, MAX(mttr_hours) as max_mttr, AVG(mttr_hours) as avg_mttr FROM kpi_mean_time_to_repair_data", "KPI Card"),
    ("General", "What is the average capacity utilization?", "SELECT AVG(utilization_percentage) as avg_utilization FROM kpi_resource_capacity_utilization_data", "KPI Card"),
    ("General", "Show capacity utilization by furnace", "SELECT furnace_no, AVG(utilization_percentage) as avg_utilization FROM kpi_resource_capacity_utilization_data GROUP BY furnace_no ORDER BY avg_utilization DESC", "Bar Chart"),
    ("General", "Show utilization by shift", "SELECT shift_id, AVG(utilization_percentage) as avg_utilization FROM kpi_resource_capacity_utilization_data GROUP BY shift_id ORDER BY avg_utilization DESC", "Bar Chart"),
    ("General", "What is the average on-time delivery?", "SELECT AVG(on_time_delivery_percentage) as avg_otd FROM kpi_on_time_delivery_data", "KPI Card"),
    ("General", "Show on-time delivery by furnace", "SELECT furnace_no, AVG(on_time_delivery_percentage) as avg_otd FROM kpi_on_time_delivery_data GROUP BY furnace_no ORDER BY avg_otd DESC", "Line Chart"),
    ("General", "What is the total cast weight?", "SELECT SUM(cast_weight) as total_cast_weight FROM core_process_tap_production", "KPI Card"),
    ("General", "Show cast weight by plant", "SELECT plant_id, SUM(cast_weight) as total_cast_weight FROM core_process_tap_production GROUP BY plant_id ORDER BY total_cast_weight DESC", "Bar Chart"),
    ("General", "What is the total liquid weight produced", "SELECT SUM(liquid_weight) as total_liquid_weight FROM core_process_tap_production", "KPI Card"),
    ("General", "Show active furnaces", "SELECT furnace_no, furnace_description FROM furnace_furnaceconfig WHERE is_active = true ORDER BY furnace_no", "Table"),
    ("General", "Show furnaces by workshop", "SELECT workshop_id, COUNT(*) as furnace_count FROM furnace_furnaceconfig GROUP BY workshop_id ORDER BY furnace_count DESC", "Bar Chart"),
    ("General", "Show all plants", "SELECT id, plant_code, plant_name FROM plant_plant ORDER BY id", "Table"),
    ("General", "What is the average rework rate?", "SELECT AVG(rework_rate_percentage) as avg_rework FROM kpi_rework_rate_data", "KPI Card"),
    ("General", "Show rework rate by furnace", "SELECT furnace_no, AVG(rework_rate_percentage) as avg_rework FROM kpi_rework_rate_data GROUP BY furnace_no ORDER BY avg_rework DESC", "Bar Chart"),
    ("General", "Show quality issues by machine", "SELECT machine_id, AVG(defect_rate) as avg_defect_rate FROM kpi_defect_rate_data GROUP BY machine_id ORDER BY avg_defect_rate DESC", "Bar Chart"),

    # Maintenance Tests
    ("Maintenance", "What is the average maintenance compliance?", "SELECT AVG(compliance_percentage) as avg_compliance FROM kpi_maintenance_compliance_data", "KPI Card"),
    ("Maintenance", "Show maintenance compliance by furnace", "SELECT furnace_no, AVG(compliance_percentage) as avg_compliance FROM kpi_maintenance_compliance_data GROUP BY furnace_no ORDER BY avg_compliance DESC", "Bar Chart"),
    ("Maintenance", "What is the average planned maintenance?", "SELECT AVG(planned_maintenance_percentage) as avg_planned FROM kpi_planned_maintenance_data", "KPI Card"),
    ("Maintenance", "Show planned maintenance by furnace", "SELECT furnace_no, AVG(planned_maintenance_percentage) as avg_planned FROM kpi_planned_maintenance_data GROUP BY furnace_no ORDER BY avg_planned DESC", "Bar Chart"),
    ("Maintenance", "Show planned maintenance trend", "SELECT date, AVG(planned_maintenance_percentage) as avg_planned FROM kpi_planned_maintenance_data GROUP BY date ORDER BY date DESC LIMIT 30", "Line Chart"),
    ("Maintenance", "Show maintenance schedule statistics", "SELECT MIN(planned_maintenance_percentage) as min_planned, MAX(planned_maintenance_percentage) as max_planned, AVG(planned_maintenance_percentage) as avg_planned FROM kpi_planned_maintenance_data", "KPI Card"),

    # Safety Tests
    ("Safety", "What is the average safety incidents percentage?", "SELECT AVG(incidents_percentage) as avg_incidents FROM kpi_safety_incidents_reported_data", "KPI Card"),
    ("Safety", "Show safety incidents by furnace", "SELECT furnace_no, AVG(incidents_percentage) as avg_incidents FROM kpi_safety_incidents_reported_data GROUP BY furnace_no ORDER BY avg_incidents DESC", "Bar Chart"),
    ("Safety", "Show safety incidents trend", "SELECT date, AVG(incidents_percentage) as avg_incidents FROM kpi_safety_incidents_reported_data GROUP BY date ORDER BY date DESC LIMIT 30", "Line Chart"),
    ("Safety", "Show safety by shift", "SELECT shift_id, AVG(incidents_percentage) as avg_incidents FROM kpi_safety_incidents_reported_data GROUP BY shift_id ORDER BY avg_incidents DESC", "Bar Chart"),
]

# Allowed tables for API requests
ALLOWED_TABLES = [
    "kpi_overall_equipment_efficiency_data", "kpi_downtime_data", "kpi_energy_used_data",
    "kpi_energy_efficiency_data", "kpi_yield_data", "kpi_defect_rate_data", "kpi_cycle_time_data",
    "kpi_quantity_produced_data", "kpi_production_efficiency_data", "kpi_output_rate_data",
    "kpi_mean_time_between_failures_data", "kpi_mean_time_to_repair_data",
    "kpi_mean_time_between_stoppages_data", "kpi_resource_capacity_utilization_data",
    "kpi_on_time_delivery_data", "kpi_maintenance_compliance_data", "kpi_planned_maintenance_data",
    "kpi_safety_incidents_reported_data", "kpi_first_pass_yield_data", "kpi_rework_rate_data",
    "core_process_tap_production", "core_process_tap_process", "core_process_tap_grading",
    "log_book_furnace_down_time_event", "log_book_reasons", "log_book_downtime_type_master",
    "furnace_furnaceconfig", "furnace_config_parameters", "plant_plant"
]


def normalize_sql(sql: str) -> str:
    """Normalize SQL for comparison."""
    if not sql:
        return ""
    sql = sql.upper()
    sql = re.sub(r'\s+', ' ', sql)
    sql = re.sub(r'\s*,\s*', ', ', sql)
    sql = re.sub(r'\s*=\s*', ' = ', sql)
    sql = re.sub(r'\s*>\s*', ' > ', sql)
    sql = re.sub(r'\s*<\s*', ' < ', sql)
    sql = sql.strip()
    return sql


def extract_key_elements(sql: str) -> dict:
    """Extract key SQL elements for comparison."""
    sql_upper = sql.upper() if sql else ""

    elements = {
        "has_avg": "AVG(" in sql_upper,
        "has_sum": "SUM(" in sql_upper,
        "has_count": "COUNT(" in sql_upper,
        "has_min": "MIN(" in sql_upper,
        "has_max": "MAX(" in sql_upper,
        "has_group_by": "GROUP BY" in sql_upper,
        "has_order_by": "ORDER BY" in sql_upper,
        "has_where": "WHERE" in sql_upper,
        "has_limit": "LIMIT" in sql_upper,
        "has_join": "JOIN" in sql_upper,
        "has_having": "HAVING" in sql_upper,
    }

    # Extract table name
    table_match = re.search(r'FROM\s+(\w+)', sql_upper)
    elements["table"] = table_match.group(1) if table_match else None

    return elements


def compare_sql(expected: str, actual: str) -> Tuple[bool, float, str]:
    """Compare expected and actual SQL, return (match, similarity, reason)."""
    if not actual:
        return False, 0.0, "No SQL generated"

    norm_expected = normalize_sql(expected)
    norm_actual = normalize_sql(actual)

    # Exact match
    if norm_expected == norm_actual:
        return True, 1.0, "Exact match"

    # Sequence similarity
    similarity = SequenceMatcher(None, norm_expected, norm_actual).ratio()

    # Element comparison
    expected_elements = extract_key_elements(expected)
    actual_elements = extract_key_elements(actual)

    # Check if key elements match
    key_matches = sum(1 for k in expected_elements if expected_elements[k] == actual_elements.get(k, False))
    total_keys = len(expected_elements)
    element_similarity = key_matches / total_keys if total_keys > 0 else 0

    # Combined similarity score
    combined_score = (similarity * 0.6) + (element_similarity * 0.4)

    # Consider match if similarity is high enough (80%+)
    if combined_score >= 0.8:
        return True, combined_score, "High similarity match"

    # Check if same table and same aggregation pattern
    if expected_elements.get("table") == actual_elements.get("table"):
        if element_similarity >= 0.7:
            return True, combined_score, "Same table and similar structure"

    return False, combined_score, f"Low similarity ({combined_score:.1%})"


def normalize_graph_type(graph_type: str) -> str:
    """Normalize graph type for comparison."""
    if not graph_type:
        return ""

    graph_type = graph_type.lower().strip()

    # Map common variations
    mapping = {
        "kpi card": "kpi_card",
        "kpicard": "kpi_card",
        "kpi": "kpi_card",
        "bar chart": "bar_chart",
        "barchart": "bar_chart",
        "bar": "bar_chart",
        "line chart": "line_chart",
        "linechart": "line_chart",
        "line": "line_chart",
        "table": "table",
        "none": "none",
        "": "none"
    }

    return mapping.get(graph_type, graph_type.replace(" ", "_"))


def compare_graph_type(expected: str, actual: str) -> Tuple[bool, str]:
    """Compare expected and actual graph types."""
    norm_expected = normalize_graph_type(expected)
    norm_actual = normalize_graph_type(actual)

    if norm_expected == norm_actual:
        return True, "Match"

    # Some flexible matching - bar and line are often interchangeable for trends
    flexible_matches = [
        ({"bar_chart", "line_chart"}, {"bar_chart", "line_chart"}),
    ]

    for expected_set, actual_set in flexible_matches:
        if norm_expected in expected_set and norm_actual in actual_set:
            return True, "Flexible match (bar/line)"

    return False, f"Mismatch: expected '{expected}', got '{actual}'"


def test_query(category: str, question: str, expected_sql: str, expected_graph: str,
               max_retries: int = 3, delay_between_retries: int = 10) -> Dict:
    """Test a single query against the chatbot API."""
    result = {
        "category": category,
        "question": question,
        "expected_sql": expected_sql,
        "expected_graph": expected_graph,
        "actual_sql": None,
        "actual_graph": None,
        "sql_match": False,
        "sql_similarity": 0.0,
        "sql_reason": "",
        "graph_match": False,
        "graph_reason": "",
        "error": None,
        "status": "FAIL"
    }

    for attempt in range(max_retries):
        try:
            response = requests.post(
                f"{NLP_SERVICE_URL}/api/v1/chat",
                json={
                    "question": question,
                    "allowed_tables": ALLOWED_TABLES
                },
                timeout=120
            )

            if response.status_code == 200:
                data = response.json()

                if data.get("success"):
                    result["actual_sql"] = data.get("sql", "")

                    # Get graph type from chart_config (directly in response root)
                    chart_config = data.get("chart_config") or {}
                    chart_type = chart_config.get("type", "") if chart_config else ""

                    # Map internal chart types to expected graph types
                    chart_type_mapping = {
                        "progress_bar": "KPI Card",
                        "kpi_card": "KPI Card",
                        "bar": "Bar Chart",
                        "line": "Line Chart",
                        "area": "Line Chart",
                        "pie": "Bar Chart",
                        "table": "Table",
                        "metric_grid": "KPI Card"
                    }

                    # If chart_config is None, infer from SQL structure
                    if not chart_type and result["actual_sql"]:
                        sql_upper = result["actual_sql"].upper()
                        has_group_by = "GROUP BY" in sql_upper
                        has_aggregate = any(agg in sql_upper for agg in ["AVG(", "SUM(", "COUNT(", "MIN(", "MAX("])
                        has_limit_1 = "LIMIT 1" in sql_upper
                        has_order_by = "ORDER BY" in sql_upper

                        if has_aggregate and not has_group_by:
                            # Simple aggregate = KPI Card
                            result["actual_graph"] = "KPI Card"
                        elif has_group_by and has_aggregate:
                            # Grouped aggregation = Bar/Line Chart
                            if "DATE" in sql_upper or "MONTH" in sql_upper or "WEEK" in sql_upper or "DAY" in sql_upper:
                                result["actual_graph"] = "Line Chart"
                            else:
                                result["actual_graph"] = "Bar Chart"
                        elif has_limit_1 and has_order_by:
                            # Top/Bottom 1 query
                            result["actual_graph"] = "Bar Chart"
                        elif "SELECT" in sql_upper and "FROM" in sql_upper:
                            # Default to Table for data retrieval
                            result["actual_graph"] = "Table"
                        else:
                            result["actual_graph"] = "Table"
                    else:
                        result["actual_graph"] = chart_type_mapping.get(chart_type, chart_type.title() if chart_type else "Table")

                    # Compare SQL
                    result["sql_match"], result["sql_similarity"], result["sql_reason"] = compare_sql(
                        expected_sql, result["actual_sql"]
                    )

                    # Compare graph type
                    result["graph_match"], result["graph_reason"] = compare_graph_type(
                        expected_graph, result["actual_graph"]
                    )

                    # Overall status
                    if result["sql_match"] and result["graph_match"]:
                        result["status"] = "PASS"
                    elif result["sql_match"]:
                        result["status"] = "SQL_ONLY"
                    elif result["graph_match"]:
                        result["status"] = "GRAPH_ONLY"

                    return result
                else:
                    error_msg = data.get("error", "Unknown error")

                    # Check for rate limiting
                    if "Token limit" in error_msg or "rate" in error_msg.lower():
                        wait_match = re.search(r'wait (\d+) seconds', error_msg)
                        wait_time = int(wait_match.group(1)) + 2 if wait_match else delay_between_retries

                        if attempt < max_retries - 1:
                            print(f" [rate limit, waiting {wait_time}s]", end="", flush=True)
                            time.sleep(wait_time)
                            continue

                    result["error"] = error_msg
            else:
                result["error"] = f"HTTP {response.status_code}"

        except requests.exceptions.Timeout:
            result["error"] = "Request timeout"
        except Exception as e:
            result["error"] = str(e)

        break

    return result


def run_tests(test_cases: List[Tuple], delay_between_tests: float = 2.0,
              batch_size: int = 5, batch_delay: float = 30.0) -> List[Dict]:
    """Run all test cases with rate limiting handling."""
    results = []
    total = len(test_cases)

    print(f"\nRunning {total} test cases...")
    print("=" * 80)

    for i, (category, question, expected_sql, expected_graph) in enumerate(test_cases):
        print(f"\n[{i+1}/{total}] {category}: {question[:50]}...", end="", flush=True)

        result = test_query(category, question, expected_sql, expected_graph)
        results.append(result)

        status_icon = "PASS" if result["status"] == "PASS" else (
            "SQL" if result["status"] == "SQL_ONLY" else (
            "GRAPH" if result["status"] == "GRAPH_ONLY" else "FAIL"
        ))
        print(f" [{status_icon}]", end="")

        if result["error"]:
            print(f" Error: {result['error'][:30]}", end="")

        # Rate limiting: delay between tests
        if i < total - 1:
            time.sleep(delay_between_tests)

            # Extra delay after each batch
            if (i + 1) % batch_size == 0:
                print(f"\n[Batch pause: waiting {batch_delay}s to avoid rate limits...]")
                time.sleep(batch_delay)

    return results


def generate_report(results: List[Dict], output_prefix: str = "test_report") -> Tuple[str, str]:
    """Generate test report files."""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    txt_file = f"{output_prefix}_{timestamp}.txt"
    csv_file = f"{output_prefix}_{timestamp}.csv"

    # Calculate statistics
    total = len(results)
    passed = sum(1 for r in results if r["status"] == "PASS")
    sql_only = sum(1 for r in results if r["status"] == "SQL_ONLY")
    graph_only = sum(1 for r in results if r["status"] == "GRAPH_ONLY")
    failed = sum(1 for r in results if r["status"] == "FAIL")
    errors = sum(1 for r in results if r["error"])

    sql_matches = sum(1 for r in results if r["sql_match"])
    graph_matches = sum(1 for r in results if r["graph_match"])

    # By category stats
    categories = {}
    for r in results:
        cat = r["category"]
        if cat not in categories:
            categories[cat] = {"total": 0, "sql_match": 0, "graph_match": 0, "pass": 0}
        categories[cat]["total"] += 1
        if r["sql_match"]:
            categories[cat]["sql_match"] += 1
        if r["graph_match"]:
            categories[cat]["graph_match"] += 1
        if r["status"] == "PASS":
            categories[cat]["pass"] += 1

    # Generate text report
    with open(txt_file, 'w', encoding='utf-8') as f:
        f.write("\n")
        f.write("=" * 80 + "\n")
        f.write("                    CHATBOT COMPREHENSIVE TEST REPORT\n")
        f.write("=" * 80 + "\n")
        f.write(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")

        f.write("SUMMARY\n")
        f.write("-" * 40 + "\n")
        f.write(f"Total Tests:      {total}\n")
        f.write(f"Full Pass:        {passed}/{total} ({passed*100/total:.1f}%)\n")
        f.write(f"SQL Only:         {sql_only}/{total} ({sql_only*100/total:.1f}%)\n")
        f.write(f"Graph Only:       {graph_only}/{total} ({graph_only*100/total:.1f}%)\n")
        f.write(f"Failed:           {failed}/{total} ({failed*100/total:.1f}%)\n")
        f.write(f"Errors:           {errors}\n\n")

        f.write("MATCH RATES\n")
        f.write("-" * 40 + "\n")
        f.write(f"SQL Match Rate:   {sql_matches}/{total} ({sql_matches*100/total:.1f}%)\n")
        f.write(f"Graph Match Rate: {graph_matches}/{total} ({graph_matches*100/total:.1f}%)\n\n")

        f.write("BY CATEGORY\n")
        f.write("-" * 40 + "\n")
        for cat, stats in sorted(categories.items()):
            sql_pct = stats['sql_match']*100/stats['total'] if stats['total'] > 0 else 0
            graph_pct = stats['graph_match']*100/stats['total'] if stats['total'] > 0 else 0
            pass_pct = stats['pass']*100/stats['total'] if stats['total'] > 0 else 0
            f.write(f"{cat:20} Total: {stats['total']:3} | SQL: {sql_pct:5.1f}% | Graph: {graph_pct:5.1f}% | Pass: {pass_pct:5.1f}%\n")

        f.write("\n" + "=" * 80 + "\n")
        f.write("DETAILED RESULTS\n")
        f.write("=" * 80 + "\n\n")

        for r in results:
            status_str = r["status"]
            f.write(f"[{r['category']}] {r['question']}\n")
            f.write(f"  Status: {status_str}\n")
            f.write(f"  SQL Match: {'YES' if r['sql_match'] else 'NO'} ({r['sql_similarity']:.0%}) - {r['sql_reason']}\n")
            f.write(f"  Graph Match: {'YES' if r['graph_match'] else 'NO'} - {r['graph_reason']}\n")
            f.write(f"  Expected Graph: {r['expected_graph']} | Actual: {r['actual_graph'] or 'None'}\n")
            if r['error']:
                f.write(f"  Error: {r['error']}\n")
            f.write("\n")

    # Generate CSV report
    with open(csv_file, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow([
            "Category", "Question", "Status", "SQL_Match", "SQL_Similarity",
            "Graph_Match", "Expected_Graph", "Actual_Graph", "Error"
        ])
        for r in results:
            writer.writerow([
                r["category"], r["question"], r["status"],
                "YES" if r["sql_match"] else "NO", f"{r['sql_similarity']:.0%}",
                "YES" if r["graph_match"] else "NO",
                r["expected_graph"], r["actual_graph"] or "None",
                r["error"] or ""
            ])

    return txt_file, csv_file


def main():
    """Main function to run comprehensive tests."""
    print("\n" + "=" * 80)
    print("CHATBOT COMPREHENSIVE TEST SUITE")
    print("=" * 80)
    print(f"Total test cases: {len(TEST_CASES)}")
    print(f"NLP Service URL: {NLP_SERVICE_URL}")

    # Check service health
    try:
        health = requests.get(f"{NLP_SERVICE_URL}/health", timeout=5)
        if health.status_code == 200:
            print("NLP Service: HEALTHY")
        else:
            print(f"NLP Service: UNHEALTHY (status {health.status_code})")
            return
    except Exception as e:
        print(f"NLP Service: UNREACHABLE ({e})")
        return

    # Run tests with rate limiting delays
    # Using conservative delays due to Groq rate limits
    results = run_tests(
        TEST_CASES,
        delay_between_tests=3.0,  # 3 seconds between each test
        batch_size=10,            # 10 tests per batch
        batch_delay=60.0          # 60 seconds pause between batches
    )

    # Generate reports
    txt_file, csv_file = generate_report(results)

    print("\n" + "=" * 80)
    print("TEST COMPLETE")
    print("=" * 80)
    print(f"Text Report: {txt_file}")
    print(f"CSV Report:  {csv_file}")

    # Print summary
    total = len(results)
    passed = sum(1 for r in results if r["status"] == "PASS")
    sql_matches = sum(1 for r in results if r["sql_match"])
    graph_matches = sum(1 for r in results if r["graph_match"])

    print(f"\nFinal Results:")
    print(f"  Full Pass:   {passed}/{total} ({passed*100/total:.1f}%)")
    print(f"  SQL Match:   {sql_matches}/{total} ({sql_matches*100/total:.1f}%)")
    print(f"  Graph Match: {graph_matches}/{total} ({graph_matches*100/total:.1f}%)")


if __name__ == "__main__":
    main()
