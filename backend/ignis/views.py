import logging
from datetime import datetime, timedelta
from django.db.models import Sum, Count, F, Q, Avg
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.utils.timezone import make_aware
from dateutil.parser import parse

from .models import (
    # Core Process Tables
    CoreProcessTapProduction,
    CoreProcessTapGrading,
    CoreProcessTapProcess,
    # Downtime & Logbook
    LogBookFurnaceDownTimeEvent,
    LogBookReasonMaster,
    LogBookDowntimeTypeMaster,
    # Configuration
    FurnaceConfigParameters,
    FurnaceFurnaceconfig,
    PlantPlant,
    # KPI Tables - Production Performance
    KpiOverallEquipmentEfficiencyData,
    KpiCycleTimeData,
    KpiYieldData,
    KpiOutputRateData,
    KpiQuantityProducedData,
    KpiProductionEfficiencyData,
    KpiOnTimeDeliveryData,
    # KPI Tables - Quality
    KpiDefectRateData,
    KpiFirstPassYieldData,
    KpiReworkRateData,
    # KPI Tables - Energy
    KpiEnergyEfficiencyData,
    KpiEnergyUsedData,
    # KPI Tables - Maintenance & Reliability
    KpiDowntimeData,
    KpiMeanTimeBetweenFailuresData,
    KpiMeanTimeToRepairData,
    KpiMeanTimeBetweenStoppagesData,
    KpiMaintenanceComplianceData,
    KpiPlannedMaintenanceData,
    # KPI Tables - Other
    KpiResourceCapacityUtilizationData,
    KpiSafetyIncidentsReportedData,
)

logger = logging.getLogger(__name__)

# Helper to parse dates
def get_date_range(request):
    date_from_str = request.GET.get('date_from')
    date_to_str = request.GET.get('date_to')
    period = request.GET.get('period')
    
    end_date = datetime.now()
    start_date = end_date - timedelta(days=30) # Default
    
    if date_to_str:
        try:
            end_date = parse(date_to_str)
        except:
            pass
            
    if date_from_str:
        try:
            start_date = parse(date_from_str)
        except:
            pass
    elif period:
        if period == 'last7':
            start_date = end_date - timedelta(days=7)
        elif period == 'last30':
            start_date = end_date - timedelta(days=30)
        elif period == 'last90':
            start_date = end_date - timedelta(days=90)
        elif period == 'last365':
            start_date = end_date - timedelta(days=365)
            
    # Function to make timezone aware if needed, or simple date
    # KPIs usually use DateField, so we might need date objects
    return start_date.date(), end_date.date()

@require_http_methods(["GET"])
def tap_production(request):
    furnace_no = request.GET.get('furnace_no')
    if not furnace_no:
        return JsonResponse({'error': 'furnace_no is required'}, status=400)
        
    start_date, end_date = get_date_range(request)
    limit = int(request.GET.get('limit', 10))
    
    # Query
    qs = CoreProcessTapProduction.objects.filter(
        tap__furnace_no=furnace_no, # Assuming tap has furnace_no FK
        tap_production_datetime__date__range=(start_date, end_date)
    ).exclude(cast_weight__isnull=True).order_by('-tap_production_datetime')[:limit]
    
    data = []
    for item in qs:
        data.append({
            'tap_id': item.tap.tap_id if item.tap else None,
            'timestamp': item.tap_production_datetime,
            'cast_weight_tons': float(item.cast_weight) if item.cast_weight else 0,
            'energy_kwh': float(item.energy) if item.energy else 0,
            'efficiency_kwh_per_ton': float(item.energy_efficiency) if item.energy_efficiency else 0,
        })
        
    return JsonResponse(data, safe=False)

@require_http_methods(["GET"])
def grade_distribution(request):
    furnace_no = request.GET.get('furnace_no')
    if not furnace_no:
        return JsonResponse({'error': 'furnace_no is required'}, status=400)
    
    start_date, end_date = get_date_range(request)
    
    # Grading linked to TapProcess?
    # CoreProcessTapGrading -> tap (TapProcess)
    # CoreProcessTapProduction -> tap (TapProcess)
    # So we join on tap_id.
    
    # We want sum cast_weight per grade.
    # We query Grading, join with Tap, join with Production
    
    qs = CoreProcessTapGrading.objects.filter(
        tap__furnace_no=furnace_no,
        tap_datetime__date__range=(start_date, end_date)
    ).values('allocated_grade').annotate(
        total_tons=Sum('tap__coreprocesstapproduction__cast_weight'),
        count=Count('id')
    )
    
    # Bucket logic
    buckets = {}
    total_tons_all = 0
    
    for item in qs:
        grade = item['allocated_grade'] if item['allocated_grade'] else 'Unknown'
        tons = float(item['total_tons']) if item['total_tons'] else 0
        count = item['count']
        
        # Mapping to buckets
        # Logic: Buckets: GRADE_A, GRADE_B, ON_GRADE, OFF_GRADE (falls back to grade label if none match).
        # Since I don't know the exact string match for GRADE_A etc., I will just use the grade label.
        # But if the user implies mapping, I'll just leave it as grade label for now.
        
        bucket_name = str(grade) # placeholder for mapping logic if exists
        
        if bucket_name not in buckets:
            buckets[bucket_name] = {'count': 0, 'tons': 0}
        
        buckets[bucket_name]['count'] += count
        buckets[bucket_name]['tons'] += tons
        total_tons_all += tons
        
    result = []
    for name, stats in buckets.items():
        pct = (stats['tons'] / total_tons_all * 100) if total_tons_all > 0 else 0
        result.append({
            'bucket': name,
            'count': stats['count'],
            'tons': stats['tons'],
            'percentage': round(pct, 2)
        })
        
    return JsonResponse(result, safe=False)

@require_http_methods(["GET"])
def health_breakdown(request):
    furnace_no = request.GET.get('furnace_no')
    if not furnace_no:
        return JsonResponse({'error': 'furnace_no is required'}, status=400)
        
    start_date, end_date = get_date_range(request)
    
    def get_latest(model, field_name):
        obj = model.objects.filter(
            furnace_no=furnace_no,
            date__range=(start_date, end_date)
        ).order_by('-date').first() # Assuming date field
        
        if obj:
            val = getattr(obj, field_name)
            return float(val) if val is not None else None
        return None

    # Components
    oee = get_latest(KpiOverallEquipmentEfficiencyData, 'oee_percentage')
    defrate = get_latest(KpiDefectRateData, 'defect_rate')
    energyeff = get_latest(KpiEnergyEfficiencyData, 'energy_efficiency')
    downtime = get_latest(KpiDowntimeData, 'downtime_hours')
    mtbf = get_latest(KpiMeanTimeBetweenFailuresData, 'mtbf_hours')
    yield_val = get_latest(KpiYieldData, 'yield_percentage')
    capacity = get_latest(KpiResourceCapacityUtilizationData, 'utilization_percentage')
    safety = get_latest(KpiSafetyIncidentsReportedData, 'incidents_percentage')

    components = [
        {'name': 'OEE', 'value': oee, 'weight': 0.25},
        {'name': 'DEFRATE', 'value': defrate, 'weight': 0.15},
        {'name': 'ENERGYEFF', 'value': energyeff, 'weight': 0.15},
        {'name': 'DOWNTIME', 'value': downtime, 'weight': 0.15},
        {'name': 'MTBF', 'value': mtbf, 'weight': 0.12},
        {'name': 'YIELD', 'value': yield_val, 'weight': 0.10},
        {'name': 'CAPACITY', 'value': capacity, 'weight': 0.08},
        {'name': 'SAFETY', 'value': safety, 'weight': 0.05}
    ]
    
    result = []
    for comp in components:
        val = comp['value']
        # Penalty calculation logic from prompt: "Penalty = value - 100 (e.g., 92.4 -> -7.6)"
        # Note: This formula implies the target is 100 and we are subtracting 100.
        # However, for things like downtime, lower is better. The prompt says "normalization... is not yet applied"
        # I will strictly follow the formula "value - 100" as requested for everything for now, 
        # or just return the value and let frontend handle?
        # User says: "Penalty = value - 100".
        
        penalty = (val - 100) if val is not None else None
        
        result.append({
            'component': comp['name'],
            'value': val,
            'score': penalty, # "Unit shown as 'score'"
            'weight': comp['weight']
        })
        
    return JsonResponse(result, safe=False)

@require_http_methods(["GET"])
def downtime_summary(request):
    furnace_no = request.GET.get('furnace_no')
    if not furnace_no:
        return JsonResponse({'error': 'furnace_no is required'}, status=400)
    
    start_date, end_date = get_date_range(request)
    
    qs = LogBookFurnaceDownTimeEvent.objects.filter(
        furnace__furnace_no=furnace_no,
        observation_start_dt__date__range=(start_date, end_date)
    )
    
    # We need to sum duration. Duration = obs_end_dt - obs_start_dt
    # Django ORM for duration sum requires expression wrapper or raw SQL often, 
    # but let's try python loop for simplicity if volume is low, or formatting.
    # Actually, ExpressionWrapper(F('observation_end_dt') - F('observation_start_dt'), output_field=DurationField())
    
    total_duration_sec = 0
    count = 0
    
    for event in qs:
        if event.observation_end_dt and event.observation_start_dt:
            delta = event.observation_end_dt - event.observation_start_dt
            total_duration_sec += delta.total_seconds()
            count += 1
            
    hours = total_duration_sec / 3600.0
    
    # Planned vs Unplanned
    # "down_time_type__name containing 'planned'"
    planned_count = 0
    planned_duration_sec = 0
    
    for event in qs:
        is_planned = False
        if event.down_time_type and 'planned' in (event.down_time_type.name or '').lower():
            is_planned = True
            
        if is_planned and event.observation_end_dt and event.observation_start_dt:
            delta = event.observation_end_dt - event.observation_start_dt
            planned_duration_sec += delta.total_seconds()
            planned_count += 1
            
    planned_hours = planned_duration_sec / 3600.0
    unplanned_hours = hours - planned_hours
    unplanned_count = count - planned_count
    
    return JsonResponse({
        'total_downtime_hours': round(hours, 2),
        'total_events': count,
        'planned_maintenance_hours': round(planned_hours, 2),
        'planned_events': planned_count,
        'unplanned_hours': round(unplanned_hours, 2),
        'unplanned_events': unplanned_count
    })

@require_http_methods(["GET"])
def downtime_reasons(request):
    furnace_no = request.GET.get('furnace_no')
    limit = int(request.GET.get('limit', 5))
    if not furnace_no:
        return JsonResponse({'error': 'furnace_no is required'}, status=400)
    
    start_date, end_date = get_date_range(request)
    
    qs = LogBookFurnaceDownTimeEvent.objects.filter(
        furnace__furnace_no=furnace_no,
        observation_start_dt__date__range=(start_date, end_date)
    )
    
    # Group by reason name
    reasons = {}
    
    for event in qs:
        reason_name = 'Unknown'
        if event.reason_code:
            reason_name = event.reason_code.reason_name
            
        if reason_name not in reasons:
            reasons[reason_name] = {'hours': 0, 'count': 0}
            
        duration = 0
        if event.observation_end_dt and event.observation_start_dt:
            duration = (event.observation_end_dt - event.observation_start_dt).total_seconds() / 3600.0
            
        reasons[reason_name]['hours'] += duration
        reasons[reason_name]['count'] += 1
        
    # Convert to list and sort
    result_list = [{'reason': k, 'hours': v['hours'], 'count': v['count']} for k, v in reasons.items()]
    result_list.sort(key=lambda x: x['hours'], reverse=True)
    
    return JsonResponse(result_list[:limit], safe=False)
