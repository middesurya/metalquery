# This is an auto-generated Django model module.
# You'll have to do the following manually to clean this up:
#   * Rearrange models' order
#   * Make sure each model has one field with primary_key=True
#   * Make sure each ForeignKey and OneToOneField has `on_delete` set to the desired behavior
#   * Remove `managed = False` lines if you wish to allow Django to create, modify, and delete the table
# Feel free to rename the models, but don't rename db_table values or field names.
from django.db import models


class AdditiveAdditionalinformation(models.Model):
    id = models.BigAutoField(primary_key=True)
    created_at = models.DateTimeField()
    modified_at = models.DateTimeField(blank=True, null=True)
    record_status = models.BooleanField()
    unit_weight = models.DecimalField(max_digits=10, decimal_places=2)
    actual_cost = models.DecimalField(max_digits=10, decimal_places=2)
    addition_group = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    density = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    standard_cost = models.DecimalField(max_digits=10, decimal_places=2)
    co_contributor = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    kwh_melting = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    effective_date = models.DateField()
    created_by = models.ForeignKey('UsersUser', models.DO_NOTHING, to_field='username', blank=True, null=True)
    material_master = models.ForeignKey('MaterialMasterMaterialmaster', models.DO_NOTHING, to_field='mes_mat_code')
    modified_by = models.ForeignKey('UsersUser', models.DO_NOTHING, to_field='username', related_name='additiveadditionalinformation_modified_by_set', blank=True, null=True)
    plant = models.ForeignKey('PlantPlant', models.DO_NOTHING, to_field='plant_id')
    plant_material_code = models.CharField(max_length=50, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'additive_additionalinformation'
        unique_together = (('material_master', 'effective_date'),)


class AuthGroup(models.Model):
    name = models.CharField(unique=True, max_length=150)

    class Meta:
        managed = False
        db_table = 'auth_group'


class AuthGroupPermissions(models.Model):
    id = models.BigAutoField(primary_key=True)
    group = models.ForeignKey(AuthGroup, models.DO_NOTHING)
    permission = models.ForeignKey('AuthPermission', models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'auth_group_permissions'
        unique_together = (('group', 'permission'),)


class AuthPermission(models.Model):
    name = models.CharField(max_length=255)
    content_type = models.ForeignKey('DjangoContentType', models.DO_NOTHING)
    codename = models.CharField(max_length=100)

    class Meta:
        managed = False
        db_table = 'auth_permission'
        unique_together = (('content_type', 'codename'),)


class ByProductsAdditionalinformation(models.Model):
    id = models.BigAutoField(primary_key=True)
    created_at = models.DateTimeField()
    modified_at = models.DateTimeField(blank=True, null=True)
    record_status = models.BooleanField()
    unit_weight = models.DecimalField(max_digits=10, decimal_places=2)
    density = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    effective_date = models.DateField()
    created_by = models.ForeignKey('UsersUser', models.DO_NOTHING, to_field='username', blank=True, null=True)
    material_master = models.ForeignKey('MaterialMasterMaterialmaster', models.DO_NOTHING, to_field='mes_mat_code')
    modified_by = models.ForeignKey('UsersUser', models.DO_NOTHING, to_field='username', related_name='byproductsadditionalinformation_modified_by_set', blank=True, null=True)
    plant = models.ForeignKey('PlantPlant', models.DO_NOTHING, to_field='plant_id')
    plant_material_code = models.CharField(max_length=50, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'by_products_additionalinformation'
        unique_together = (('material_master', 'effective_date'),)


class ChatbotAuditlog(models.Model):
    id = models.BigAutoField(primary_key=True)
    timestamp = models.DateTimeField()
    client_ip = models.GenericIPAddressField(blank=True, null=True)
    user_id = models.CharField(max_length=255, blank=True, null=True)
    question = models.TextField()
    sql = models.TextField(blank=True, null=True)
    success = models.BooleanField()
    row_count = models.IntegerField()
    error = models.TextField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'chatbot_auditlog'


class CoreProcessProductionchangelog(models.Model):
    id = models.BigAutoField(primary_key=True)
    created_at = models.DateTimeField()
    modified_at = models.DateTimeField(blank=True, null=True)
    record_status = models.BooleanField()
    change_log = models.JSONField()
    created_by = models.ForeignKey('UsersUser', models.DO_NOTHING, to_field='username', blank=True, null=True)
    modified_by = models.ForeignKey('UsersUser', models.DO_NOTHING, to_field='username', related_name='coreprocessproductionchangelog_modified_by_set', blank=True, null=True)
    tap_production = models.ForeignKey('CoreProcessTapProduction', models.DO_NOTHING)
    plant = models.ForeignKey('PlantPlant', models.DO_NOTHING, to_field='plant_id')

    class Meta:
        managed = False
        db_table = 'core_process_productionchangelog'


class CoreProcessRaafProduction(models.Model):
    id = models.BigAutoField(primary_key=True)
    created_at = models.DateTimeField()
    modified_at = models.DateTimeField(blank=True, null=True)
    record_status = models.BooleanField()
    raaf_id = models.BigIntegerField(unique=True)
    tap_number = models.SmallIntegerField()
    production_json = models.JSONField(blank=True, null=True)
    refining_steps_json = models.JSONField(blank=True, null=True)
    created_by = models.ForeignKey('UsersUser', models.DO_NOTHING, to_field='username', blank=True, null=True)
    furnace_no = models.ForeignKey('FurnaceFurnaceconfig', models.DO_NOTHING, db_column='furnace_no', to_field='furnace_no')
    modified_by = models.ForeignKey('UsersUser', models.DO_NOTHING, to_field='username', related_name='coreprocessraafproduction_modified_by_set', blank=True, null=True)
    tap = models.ForeignKey('CoreProcessTapProcess', models.DO_NOTHING, to_field='tap_id')
    plant = models.ForeignKey('PlantPlant', models.DO_NOTHING, to_field='plant_id')
    plant_furnace_code = models.CharField(max_length=10, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'core_process_raaf_production'
        unique_together = (('furnace_no', 'tap_number'),)


class CoreProcessTapGrading(models.Model):
    id = models.BigAutoField(primary_key=True)
    created_at = models.DateTimeField()
    modified_at = models.DateTimeField(blank=True, null=True)
    record_status = models.BooleanField()
    allocated_grade_quality = models.CharField(blank=True, null=True)
    allocated_grade_priority = models.SmallIntegerField(blank=True, null=True)
    tap_analysis_target_material_result = models.JSONField(blank=True, null=True)
    allocated_grade = models.ForeignKey('FurnaceFurnaceproduct', models.DO_NOTHING, db_column='allocated_grade', to_field='furnace_product_code', blank=True, null=True)
    allocated_grade_bulk_pile = models.ForeignKey('UtilsMaster', models.DO_NOTHING, db_column='allocated_grade_bulk_pile', to_field='master_code', blank=True, null=True)
    cast_process_code = models.ForeignKey('UtilsMaster', models.DO_NOTHING, db_column='cast_process_code', to_field='master_code', related_name='coreprocesstapgrading_cast_process_code_set', blank=True, null=True)
    created_by = models.ForeignKey('UsersUser', models.DO_NOTHING, to_field='username', blank=True, null=True)
    modified_by = models.ForeignKey('UsersUser', models.DO_NOTHING, to_field='username', related_name='coreprocesstapgrading_modified_by_set', blank=True, null=True)
    spout_analysis = models.ForeignKey('LabAnalysisSpoutanalysisbasicinfo', models.DO_NOTHING, to_field='spout_analysis_id', blank=True, null=True)
    tap_analysis = models.ForeignKey('LabAnalysisTapanalysisbasicinfo', models.DO_NOTHING, to_field='tap_analysis_id', blank=True, null=True)
    tap = models.ForeignKey('CoreProcessTapProcess', models.DO_NOTHING, to_field='tap_id')
    plant = models.ForeignKey('PlantPlant', models.DO_NOTHING, to_field='plant_id')

    class Meta:
        managed = False
        db_table = 'core_process_tap_grading'


class CoreProcessTapProcess(models.Model):
    id = models.BigAutoField(primary_key=True)
    created_at = models.DateTimeField()
    modified_at = models.DateTimeField(blank=True, null=True)
    record_status = models.BooleanField()
    tap_id = models.CharField(unique=True, max_length=50)
    tap_progress = models.CharField()
    tap_status = models.CharField()
    tap_datetime = models.DateTimeField()
    is_delete = models.BooleanField()
    created_by = models.ForeignKey('UsersUser', models.DO_NOTHING, to_field='username', blank=True, null=True)
    furnace_no = models.ForeignKey('FurnaceFurnaceconfig', models.DO_NOTHING, db_column='furnace_no', to_field='furnace_no')
    tap_hole = models.ForeignKey('FurnaceConfigTapHole', models.DO_NOTHING, to_field='tap_hole_id')
    modified_by = models.ForeignKey('UsersUser', models.DO_NOTHING, to_field='username', related_name='coreprocesstapprocess_modified_by_set', blank=True, null=True)
    target_material = models.ForeignKey('FurnaceFurnaceproduct', models.DO_NOTHING, db_column='target_material', to_field='furnace_product_code')
    plant = models.ForeignKey('PlantPlant', models.DO_NOTHING, to_field='plant_id')
    plant_furnace_code = models.CharField(max_length=10, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'core_process_tap_process'


class CoreProcessTapProduction(models.Model):
    id = models.BigAutoField(primary_key=True)
    created_at = models.DateTimeField()
    modified_at = models.DateTimeField(blank=True, null=True)
    record_status = models.BooleanField()
    tapping_metal_flow = models.DecimalField(max_digits=12, decimal_places=4, blank=True, null=True)
    liquid_weight = models.DecimalField(max_digits=12, decimal_places=2)
    casting_slag_weight = models.DecimalField(max_digits=12, decimal_places=2)
    recycling_metal_weight = models.DecimalField(max_digits=12, decimal_places=2)
    ladle_weight_before_tapping = models.DecimalField(max_digits=12, decimal_places=2)
    ladle_weight_after_tapping = models.DecimalField(max_digits=12, decimal_places=2)
    ladle_weight_after_casting = models.DecimalField(max_digits=12, decimal_places=2)
    ladle_weight_after_slag_removal = models.DecimalField(max_digits=12, decimal_places=2)
    tap_production_datetime = models.DateTimeField()
    external_source_raaf_id = models.BigIntegerField(blank=True, null=True)
    source = models.CharField()
    ferrous_pans = models.DecimalField(max_digits=12, decimal_places=2)
    created_by = models.ForeignKey('UsersUser', models.DO_NOTHING, to_field='username', blank=True, null=True)
    ladle_number_code = models.ForeignKey('UtilsMaster', models.DO_NOTHING, db_column='ladle_number_code', to_field='master_code')
    modified_by = models.ForeignKey('UsersUser', models.DO_NOTHING, to_field='username', related_name='coreprocesstapproduction_modified_by_set', blank=True, null=True)
    tap = models.ForeignKey(CoreProcessTapProcess, models.DO_NOTHING, to_field='tap_id')
    plant = models.ForeignKey('PlantPlant', models.DO_NOTHING, to_field='plant_id')
    cast_weight = models.DecimalField(max_digits=12, decimal_places=2)
    downgrade_material = models.ForeignKey('FurnaceFurnaceproduct', models.DO_NOTHING, db_column='downgrade_material', to_field='furnace_product_code', blank=True, null=True)
    downgrade_quantity = models.DecimalField(max_digits=12, decimal_places=2)
    energy = models.DecimalField(max_digits=12, decimal_places=2)
    energy_efficiency = models.DecimalField(max_digits=12, decimal_places=4)
    graded_cast_weight = models.DecimalField(max_digits=12, decimal_places=2)

    class Meta:
        managed = False
        db_table = 'core_process_tap_production'


class CoreProcessTapRefiningStepAdditive(models.Model):
    id = models.BigAutoField(primary_key=True)
    created_at = models.DateTimeField()
    modified_at = models.DateTimeField(blank=True, null=True)
    record_status = models.BooleanField()
    quantity = models.FloatField(blank=True, null=True)
    created_by = models.ForeignKey('UsersUser', models.DO_NOTHING, to_field='username', blank=True, null=True)
    tap_refining_additive_material = models.ForeignKey('UtilsMaster', models.DO_NOTHING, db_column='tap_refining_additive_material', to_field='master_code')
    modified_by = models.ForeignKey('UsersUser', models.DO_NOTHING, to_field='username', related_name='coreprocesstaprefiningstepadditive_modified_by_set', blank=True, null=True)
    tap_refining_step_code = models.ForeignKey('CoreProcessTapRefiningSteps', models.DO_NOTHING, db_column='tap_refining_step_code', to_field='tap_refining_step_code')
    plant = models.ForeignKey('PlantPlant', models.DO_NOTHING, to_field='plant_id')

    class Meta:
        managed = False
        db_table = 'core_process_tap_refining_step_additive'


class CoreProcessTapRefiningStepControlParam(models.Model):
    id = models.BigAutoField(primary_key=True)
    created_at = models.DateTimeField()
    modified_at = models.DateTimeField(blank=True, null=True)
    record_status = models.BooleanField()
    value = models.FloatField(blank=True, null=True)
    created_by = models.ForeignKey('UsersUser', models.DO_NOTHING, to_field='username', blank=True, null=True)
    modified_by = models.ForeignKey('UsersUser', models.DO_NOTHING, to_field='username', related_name='coreprocesstaprefiningstepcontrolparam_modified_by_set', blank=True, null=True)
    tap_refining_control_param = models.ForeignKey('UtilsMaster', models.DO_NOTHING, db_column='tap_refining_control_param', to_field='master_code')
    tap_refining_step_code = models.ForeignKey('CoreProcessTapRefiningSteps', models.DO_NOTHING, db_column='tap_refining_step_code', to_field='tap_refining_step_code')
    plant = models.ForeignKey('PlantPlant', models.DO_NOTHING, to_field='plant_id')

    class Meta:
        managed = False
        db_table = 'core_process_tap_refining_step_control_param'


class CoreProcessTapRefiningSteps(models.Model):
    id = models.BigAutoField(primary_key=True)
    created_at = models.DateTimeField()
    modified_at = models.DateTimeField(blank=True, null=True)
    record_status = models.BooleanField()
    tap_refining_step_code = models.CharField(unique=True)
    created_by = models.ForeignKey('UsersUser', models.DO_NOTHING, to_field='username', blank=True, null=True)
    modified_by = models.ForeignKey('UsersUser', models.DO_NOTHING, to_field='username', related_name='coreprocesstaprefiningsteps_modified_by_set', blank=True, null=True)
    tap_refining_step_master = models.ForeignKey('UtilsMaster', models.DO_NOTHING, db_column='tap_refining_step_master', to_field='master_code')
    tap = models.ForeignKey(CoreProcessTapProcess, models.DO_NOTHING, to_field='tap_id')
    plant = models.ForeignKey('PlantPlant', models.DO_NOTHING, to_field='plant_id')

    class Meta:
        managed = False
        db_table = 'core_process_tap_refining_steps'
        unique_together = (('tap', 'tap_refining_step_master'),)


class DashboardShareddashboards(models.Model):
    id = models.BigAutoField(primary_key=True)
    created_at = models.DateTimeField()
    modified_at = models.DateTimeField(blank=True, null=True)
    record_status = models.BooleanField()
    created_by = models.ForeignKey('UsersUser', models.DO_NOTHING, to_field='username', blank=True, null=True)
    dashboard = models.ForeignKey('Dashboards', models.DO_NOTHING)
    modified_by = models.ForeignKey('UsersUser', models.DO_NOTHING, to_field='username', related_name='dashboardshareddashboards_modified_by_set', blank=True, null=True)
    owner_user = models.ForeignKey('UsersUser', models.DO_NOTHING, related_name='dashboardshareddashboards_owner_user_set')
    plant = models.ForeignKey('PlantPlant', models.DO_NOTHING, blank=True, null=True)
    shared_user = models.ForeignKey('UsersUser', models.DO_NOTHING, related_name='dashboardshareddashboards_shared_user_set')

    class Meta:
        managed = False
        db_table = 'dashboard_shareddashboards'
        unique_together = (('dashboard', 'shared_user', 'plant'),)
        db_table_comment = 'Stores shared dashboard configurations'


class DashboardWidgets(models.Model):
    id = models.BigAutoField(primary_key=True)
    created_at = models.DateTimeField()
    modified_at = models.DateTimeField(blank=True, null=True)
    record_status = models.BooleanField()
    widget_grid_id = models.CharField(max_length=100)
    widget_type = models.CharField(max_length=100)
    metric_name = models.CharField(max_length=255)
    size = models.CharField(max_length=50)
    visualisation = models.CharField(max_length=100)
    position_x = models.IntegerField()
    position_y = models.IntegerField()
    width_in_grid_units = models.IntegerField()
    height_in_grid_units = models.IntegerField()
    created_by = models.ForeignKey('UsersUser', models.DO_NOTHING, to_field='username', blank=True, null=True)
    dashboard = models.ForeignKey('Dashboards', models.DO_NOTHING)
    modified_by = models.ForeignKey('UsersUser', models.DO_NOTHING, to_field='username', related_name='dashboardwidgets_modified_by_set', blank=True, null=True)
    plant = models.ForeignKey('PlantPlant', models.DO_NOTHING, blank=True, null=True)
    filters = models.JSONField()

    class Meta:
        managed = False
        db_table = 'dashboard_widgets'
        db_table_comment = 'Stores widget configurations for dashboards'


class Dashboards(models.Model):
    id = models.BigAutoField(primary_key=True)
    name = models.CharField(max_length=255)
    is_default = models.BooleanField()
    created_at = models.DateTimeField()
    modified_at = models.DateTimeField(blank=True, null=True)
    record_status = models.BooleanField()
    created_by = models.ForeignKey('UsersUser', models.DO_NOTHING, to_field='username', blank=True, null=True)
    modified_by = models.ForeignKey('UsersUser', models.DO_NOTHING, to_field='username', related_name='dashboards_modified_by_set', blank=True, null=True)
    plant = models.ForeignKey('PlantPlant', models.DO_NOTHING, to_field='plant_id')

    class Meta:
        managed = False
        db_table = 'dashboards'
        db_table_comment = 'Stores user dashboard configurations'


class DashboardsKpiMetricFiltersConfig(models.Model):
    id = models.BigAutoField(primary_key=True)
    created_at = models.DateTimeField()
    modified_at = models.DateTimeField(blank=True, null=True)
    record_status = models.BooleanField()
    filters = models.JSONField()
    created_by = models.ForeignKey('UsersUser', models.DO_NOTHING, to_field='username', blank=True, null=True)
    kpi_metric_code = models.ForeignKey('UsersKpiMetricMaster', models.DO_NOTHING, db_column='kpi_metric_code', to_field='kpi_metric_code')
    modified_by = models.ForeignKey('UsersUser', models.DO_NOTHING, to_field='username', related_name='dashboardskpimetricfiltersconfig_modified_by_set', blank=True, null=True)
    plant = models.ForeignKey('PlantPlant', models.DO_NOTHING, to_field='plant_id')

    class Meta:
        managed = False
        db_table = 'dashboards_kpi_metric_filters_config'
        db_table_comment = 'Stores filter configurations for KPI metrics'


class DashboardsKpiMetricVisualisationsConfig(models.Model):
    id = models.BigAutoField(primary_key=True)
    created_at = models.DateTimeField()
    modified_at = models.DateTimeField(blank=True, null=True)
    record_status = models.BooleanField()
    visualization_type = models.CharField(max_length=100)
    sizes = models.JSONField()
    created_by = models.ForeignKey('UsersUser', models.DO_NOTHING, to_field='username', blank=True, null=True)
    kpi_metric_code = models.ForeignKey('UsersKpiMetricMaster', models.DO_NOTHING, db_column='kpi_metric_code', to_field='kpi_metric_code')
    modified_by = models.ForeignKey('UsersUser', models.DO_NOTHING, to_field='username', related_name='dashboardskpimetricvisualisationsconfig_modified_by_set', blank=True, null=True)
    plant = models.ForeignKey('PlantPlant', models.DO_NOTHING, to_field='plant_id')

    class Meta:
        managed = False
        db_table = 'dashboards_kpi_metric_visualisations_config'
        db_table_comment = 'Stores visualization configurations for KPI metrics'


class DashboardsKpiVisualisationTypeColumnsConfig(models.Model):
    id = models.BigAutoField(primary_key=True)
    created_at = models.DateTimeField()
    modified_at = models.DateTimeField(blank=True, null=True)
    record_status = models.BooleanField()
    visualization_type = models.CharField(max_length=100)
    required_columns = models.JSONField()
    created_by = models.ForeignKey('UsersUser', models.DO_NOTHING, to_field='username', blank=True, null=True)
    kpi_metric_code = models.ForeignKey('UsersKpiMetricMaster', models.DO_NOTHING, db_column='kpi_metric_code', to_field='kpi_metric_code')
    modified_by = models.ForeignKey('UsersUser', models.DO_NOTHING, to_field='username', related_name='dashboardskpivisualisationtypecolumnsconfig_modified_by_set', blank=True, null=True)
    plant = models.ForeignKey('PlantPlant', models.DO_NOTHING, to_field='plant_id')

    class Meta:
        managed = False
        db_table = 'dashboards_kpi_visualisation_type_columns_config'
        db_table_comment = 'Stores required columns configuration for different visualisation types of KPI metrics'


class DataIntegrationDatavalidation(models.Model):
    id = models.BigAutoField(primary_key=True)
    validation_type = models.CharField(max_length=100)
    status = models.CharField(max_length=20)
    message = models.TextField()
    created_at = models.DateTimeField()
    etl_process = models.ForeignKey('DataIntegrationEtlprocess', models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'data_integration_datavalidation'


class DataIntegrationEtlprocess(models.Model):
    id = models.BigAutoField(primary_key=True)
    process_name = models.CharField(max_length=255)
    start_time = models.DateTimeField()
    end_time = models.DateTimeField(blank=True, null=True)
    status = models.CharField(max_length=20)
    error_message = models.TextField()
    records_processed = models.IntegerField()
    source_file = models.CharField(max_length=255)
    target_table = models.CharField(max_length=255)

    class Meta:
        managed = False
        db_table = 'data_integration_etlprocess'


class DataIntegrationTableschema(models.Model):
    id = models.BigAutoField(primary_key=True)
    table_name = models.CharField(unique=True, max_length=255)
    schema_definition = models.JSONField()
    created_at = models.DateTimeField()
    updated_at = models.DateTimeField()
    is_active = models.BooleanField()

    class Meta:
        managed = False
        db_table = 'data_integration_tableschema'


class DjangoAdminLog(models.Model):
    action_time = models.DateTimeField()
    object_id = models.TextField(blank=True, null=True)
    object_repr = models.CharField(max_length=200)
    action_flag = models.SmallIntegerField()
    change_message = models.TextField()
    content_type = models.ForeignKey('DjangoContentType', models.DO_NOTHING, blank=True, null=True)
    user = models.ForeignKey('UsersUser', models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'django_admin_log'


class DjangoContentType(models.Model):
    app_label = models.CharField(max_length=100)
    model = models.CharField(max_length=100)

    class Meta:
        managed = False
        db_table = 'django_content_type'
        unique_together = (('app_label', 'model'),)


class DjangoMigrations(models.Model):
    id = models.BigAutoField(primary_key=True)
    app = models.CharField(max_length=255)
    name = models.CharField(max_length=255)
    applied = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'django_migrations'


class DjangoSession(models.Model):
    session_key = models.CharField(primary_key=True, max_length=40)
    session_data = models.TextField()
    expire_date = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'django_session'


class EtlProductionrecord(models.Model):
    source = models.CharField(max_length=255, blank=True, null=True)
    tap_no = models.BigIntegerField(blank=True, null=True)
    ladle_no = models.BigIntegerField(blank=True, null=True)
    ladle_before_tap = models.FloatField(blank=True, null=True)
    ladle_after_tap = models.FloatField(blank=True, null=True)
    recycling_metal = models.FloatField(blank=True, null=True)
    ferrous_pans = models.FloatField(blank=True, null=True)
    ladle_after_casting = models.FloatField(blank=True, null=True)
    ladle_after_slag_removal = models.FloatField(blank=True, null=True)
    energy = models.FloatField(blank=True, null=True)
    downgrade_total = models.FloatField(blank=True, null=True)
    downgrade_material = models.CharField(max_length=255, blank=True, null=True)
    liquid_weight = models.FloatField(blank=True, null=True)
    total_cast_weight = models.FloatField(blank=True, null=True)
    refining_fill_duration = models.FloatField(blank=True, null=True)
    graded_cast_weight = models.FloatField(blank=True, null=True)
    energy_efficiency_kwh_t = models.FloatField(blank=True, null=True)
    tapping_metal_flow_t_h = models.FloatField(blank=True, null=True)
    slag_weight = models.FloatField(blank=True, null=True)
    metal_temperature_at_end_of_tapping_c = models.FloatField(blank=True, null=True)
    metal_temperature_before_casting_c = models.FloatField(blank=True, null=True)
    injected_o2_volume_phase_1_nm3 = models.FloatField(blank=True, null=True)
    injected_air_volume_phase_1_nm3 = models.FloatField(blank=True, null=True)
    duration_phase_1_min = models.FloatField(blank=True, null=True)
    injection_pressure_phase_1_bar = models.FloatField(blank=True, null=True)
    injected_o2_volume_phase_2_nm3 = models.FloatField(blank=True, null=True)
    injected_air_volume_phase_2_nm3 = models.FloatField(blank=True, null=True)
    duration_phase_2_min = models.FloatField(blank=True, null=True)
    injection_pressure_phase_2_bar = models.FloatField(blank=True, null=True)
    injected_o2_volume_phase_3_nm3 = models.FloatField(blank=True, null=True)
    injected_air_volume_phase_3_nm3 = models.FloatField(blank=True, null=True)
    duration_phase_3_min = models.FloatField(blank=True, null=True)
    injection_pressure_phase_3_bar = models.FloatField(blank=True, null=True)
    injected_o2_volume_phase_4_nm3 = models.FloatField(blank=True, null=True)
    injected_air_volume_phase_4_nm3 = models.FloatField(blank=True, null=True)
    duration_phase_4_min = models.FloatField(blank=True, null=True)
    injection_pressure_phase_4_bar = models.FloatField(blank=True, null=True)
    injected_o2_volume_phase_5_nm3 = models.FloatField(blank=True, null=True)
    injected_air_volume_phase_5_nm3 = models.FloatField(blank=True, null=True)
    duration_phase_5_min = models.FloatField(blank=True, null=True)
    injected_o2_volume_overall_nm3 = models.FloatField(blank=True, null=True)
    injected_air_volume_overall_nm3 = models.FloatField(blank=True, null=True)
    duration_overall_min = models.FloatField(blank=True, null=True)
    record_id = models.IntegerField(blank=True, null=True)
    furnace_id = models.IntegerField(blank=True, null=True)
    production_date_time = models.DateTimeField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'etl_productionrecord'


class FurnaceAdditive(models.Model):
    id = models.BigAutoField(primary_key=True)
    created_at = models.DateTimeField()
    modified_at = models.DateTimeField(blank=True, null=True)
    record_status = models.BooleanField()
    material = models.CharField(max_length=50)
    quantity = models.FloatField()
    created_by = models.ForeignKey('UsersUser', models.DO_NOTHING, to_field='username', blank=True, null=True)
    furnace_config_step = models.ForeignKey('FurnaceFurnaceconfigstep', models.DO_NOTHING)
    modified_by = models.ForeignKey('UsersUser', models.DO_NOTHING, to_field='username', related_name='furnaceadditive_modified_by_set', blank=True, null=True)
    plant = models.ForeignKey('PlantPlant', models.DO_NOTHING, to_field='plant_id')

    class Meta:
        managed = False
        db_table = 'furnace_additive'


class FurnaceConfigParameters(models.Model):
    id = models.BigAutoField(primary_key=True)
    created_at = models.DateTimeField()
    modified_at = models.DateTimeField(blank=True, null=True)
    record_status = models.BooleanField()
    effective_date = models.DateField()
    energy_losses = models.DecimalField(max_digits=10, decimal_places=2)
    joule_losses_coefficient = models.DecimalField(max_digits=13, decimal_places=5)
    default_epi_index = models.DecimalField(max_digits=10, decimal_places=2)
    corrected_reactance_coefficient = models.DecimalField(max_digits=13, decimal_places=5)
    design_mv = models.DecimalField(max_digits=10, decimal_places=2)
    fixed_cost = models.DecimalField(max_digits=10, decimal_places=2)
    target_energy_efficiency = models.DecimalField(max_digits=10, decimal_places=2)
    target_cost_budget = models.DecimalField(max_digits=10, decimal_places=2)
    target_availability = models.DecimalField(max_digits=10, decimal_places=2)
    target_furnace_load = models.DecimalField(max_digits=10, decimal_places=2)
    crucible_diameter = models.DecimalField(max_digits=10, decimal_places=2)
    crucible_depth = models.DecimalField(max_digits=10, decimal_places=2)
    pcd_theoretical = models.DecimalField(max_digits=10, decimal_places=2)
    pcd_actual = models.DecimalField(max_digits=10, decimal_places=2)
    default_moisture = models.BooleanField()
    created_by = models.ForeignKey('UsersUser', models.DO_NOTHING, to_field='username', blank=True, null=True)
    furnace_config = models.ForeignKey('FurnaceFurnaceconfig', models.DO_NOTHING, to_field='furnace_no')
    modified_by = models.ForeignKey('UsersUser', models.DO_NOTHING, to_field='username', related_name='furnaceconfigparameters_modified_by_set', blank=True, null=True)
    plant = models.ForeignKey('PlantPlant', models.DO_NOTHING, to_field='plant_id')
    plant_furnace_code = models.CharField(max_length=10, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'furnace_config_parameters'
        unique_together = (('furnace_config', 'effective_date'),)
        db_table_comment = 'It holds the furnace config  parameters'


class FurnaceConfigTapHole(models.Model):
    id = models.BigAutoField(primary_key=True)
    created_at = models.DateTimeField()
    modified_at = models.DateTimeField(blank=True, null=True)
    record_status = models.BooleanField()
    tap_hole_id = models.CharField(unique=True, max_length=100, blank=True, null=True)
    tap_hole_number = models.SmallIntegerField()
    tap_hole_status = models.CharField(max_length=20)
    activated_on = models.DateTimeField(blank=True, null=True)
    deactivated_on = models.DateTimeField(blank=True, null=True)
    status_effective_date = models.DateTimeField(blank=True, null=True)
    tap_hole_description = models.CharField(max_length=50, blank=True, null=True)
    is_deleted = models.BooleanField()
    activated_by = models.ForeignKey('UsersUser', models.DO_NOTHING, to_field='username', blank=True, null=True)
    created_by = models.ForeignKey('UsersUser', models.DO_NOTHING, to_field='username', related_name='furnaceconfigtaphole_created_by_set', blank=True, null=True)
    deactivated_by = models.ForeignKey('UsersUser', models.DO_NOTHING, to_field='username', related_name='furnaceconfigtaphole_deactivated_by_set', blank=True, null=True)
    furnace_no = models.ForeignKey('FurnaceFurnaceconfig', models.DO_NOTHING, db_column='furnace_no', to_field='furnace_no')
    modified_by = models.ForeignKey('UsersUser', models.DO_NOTHING, to_field='username', related_name='furnaceconfigtaphole_modified_by_set', blank=True, null=True)
    tap_hole_type_code = models.ForeignKey('UtilsMaster', models.DO_NOTHING, db_column='tap_hole_type_code', to_field='master_code')
    plant = models.ForeignKey('PlantPlant', models.DO_NOTHING, to_field='plant_id')
    plant_furnace_code = models.CharField(max_length=10, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'furnace_config_tap_hole'
        unique_together = (('furnace_no', 'tap_hole_number', 'tap_hole_id'),)


class FurnaceConfigTapHoleChangeLog(models.Model):
    id = models.BigAutoField(primary_key=True)
    created_at = models.DateTimeField()
    modified_at = models.DateTimeField(blank=True, null=True)
    record_status = models.BooleanField()
    change_log = models.JSONField()
    created_by = models.ForeignKey('UsersUser', models.DO_NOTHING, to_field='username', blank=True, null=True)
    tap_hole = models.ForeignKey(FurnaceConfigTapHole, models.DO_NOTHING, to_field='tap_hole_id')
    modified_by = models.ForeignKey('UsersUser', models.DO_NOTHING, to_field='username', related_name='furnaceconfigtapholechangelog_modified_by_set', blank=True, null=True)
    plant = models.ForeignKey('PlantPlant', models.DO_NOTHING, to_field='plant_id')

    class Meta:
        managed = False
        db_table = 'furnace_config_tap_hole_change_log'


class FurnaceControlparameter(models.Model):
    id = models.BigAutoField(primary_key=True)
    created_at = models.DateTimeField()
    modified_at = models.DateTimeField(blank=True, null=True)
    record_status = models.BooleanField()
    param = models.CharField(max_length=50)
    value = models.FloatField()
    is_mandatory = models.BooleanField()
    created_by = models.ForeignKey('UsersUser', models.DO_NOTHING, to_field='username', blank=True, null=True)
    furnace_config_step = models.ForeignKey('FurnaceFurnaceconfigstep', models.DO_NOTHING)
    modified_by = models.ForeignKey('UsersUser', models.DO_NOTHING, to_field='username', related_name='furnacecontrolparameter_modified_by_set', blank=True, null=True)
    plant = models.ForeignKey('PlantPlant', models.DO_NOTHING, to_field='plant_id')

    class Meta:
        managed = False
        db_table = 'furnace_controlparameter'


class FurnaceFurnacechangelog(models.Model):
    id = models.BigAutoField(primary_key=True)
    created_at = models.DateTimeField()
    modified_at = models.DateTimeField(blank=True, null=True)
    record_status = models.BooleanField()
    change_log = models.JSONField()
    created_by = models.ForeignKey('UsersUser', models.DO_NOTHING, to_field='username', blank=True, null=True)
    furnace = models.ForeignKey('FurnaceFurnaceconfig', models.DO_NOTHING)
    modified_by = models.ForeignKey('UsersUser', models.DO_NOTHING, to_field='username', related_name='furnacefurnacechangelog_modified_by_set', blank=True, null=True)
    plant = models.ForeignKey('PlantPlant', models.DO_NOTHING, to_field='plant_id')
    plant_furnace_code = models.CharField(max_length=10, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'furnace_furnacechangelog'


class FurnaceFurnaceconfig(models.Model):
    id = models.BigAutoField(primary_key=True)
    created_at = models.DateTimeField()
    modified_at = models.DateTimeField(blank=True, null=True)
    record_status = models.BooleanField()
    furnace_no = models.SmallIntegerField(unique=True)
    furnace_description = models.CharField(max_length=500)
    is_active = models.BooleanField()
    cost_center = models.ForeignKey('UtilsMaster', models.DO_NOTHING, to_field='master_code')
    created_by = models.ForeignKey('UsersUser', models.DO_NOTHING, to_field='username', blank=True, null=True)
    modified_by = models.ForeignKey('UsersUser', models.DO_NOTHING, to_field='username', related_name='furnacefurnaceconfig_modified_by_set', blank=True, null=True)
    power_delivery = models.ForeignKey('UtilsMaster', models.DO_NOTHING, to_field='master_code', related_name='furnacefurnaceconfig_power_delivery_set')
    silica_fume_default_material = models.ForeignKey('UtilsMaster', models.DO_NOTHING, to_field='master_code', related_name='furnacefurnaceconfig_silica_fume_default_material_set', blank=True, null=True)
    skull = models.ForeignKey('UtilsMaster', models.DO_NOTHING, to_field='master_code', related_name='furnacefurnaceconfig_skull_set', blank=True, null=True)
    slag = models.ForeignKey('UtilsMaster', models.DO_NOTHING, to_field='master_code', related_name='furnacefurnaceconfig_slag_set', blank=True, null=True)
    workshop = models.ForeignKey('PlantConfigWorkshop', models.DO_NOTHING)
    plant = models.ForeignKey('PlantPlant', models.DO_NOTHING, to_field='plant_id')
    plant_furnace_code = models.CharField(max_length=10, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'furnace_furnaceconfig'


class FurnaceFurnaceconfigstep(models.Model):
    id = models.BigAutoField(primary_key=True)
    created_at = models.DateTimeField()
    modified_at = models.DateTimeField(blank=True, null=True)
    record_status = models.BooleanField()
    step = models.CharField(max_length=10)
    order = models.SmallIntegerField()
    created_by = models.ForeignKey('UsersUser', models.DO_NOTHING, to_field='username', blank=True, null=True)
    furnace = models.ForeignKey(FurnaceFurnaceconfig, models.DO_NOTHING, to_field='furnace_no')
    modified_by = models.ForeignKey('UsersUser', models.DO_NOTHING, to_field='username', related_name='furnacefurnaceconfigstep_modified_by_set', blank=True, null=True)
    plant = models.ForeignKey('PlantPlant', models.DO_NOTHING, to_field='plant_id')
    plant_furnace_code = models.CharField(max_length=10, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'furnace_furnaceconfigstep'


class FurnaceFurnaceelectrode(models.Model):
    id = models.BigAutoField(primary_key=True)
    created_at = models.DateTimeField()
    modified_at = models.DateTimeField(blank=True, null=True)
    record_status = models.BooleanField()
    electrode_name = models.CharField(max_length=50)
    core_mass_length = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    paste_mass_length = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    casing_mass_length = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    diameter = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    effective_date = models.DateField()
    casing = models.ForeignKey('UtilsMaster', models.DO_NOTHING, to_field='master_code', blank=True, null=True)
    core = models.ForeignKey('UtilsMaster', models.DO_NOTHING, to_field='master_code', related_name='furnacefurnaceelectrode_core_set', blank=True, null=True)
    created_by = models.ForeignKey('UsersUser', models.DO_NOTHING, to_field='username', blank=True, null=True)
    electrode_type = models.ForeignKey('UtilsMaster', models.DO_NOTHING, to_field='master_code', related_name='furnacefurnaceelectrode_electrode_type_set')
    furnace_config = models.ForeignKey(FurnaceFurnaceconfig, models.DO_NOTHING, to_field='furnace_no')
    modified_by = models.ForeignKey('UsersUser', models.DO_NOTHING, to_field='username', related_name='furnacefurnaceelectrode_modified_by_set', blank=True, null=True)
    paste = models.ForeignKey('UtilsMaster', models.DO_NOTHING, to_field='master_code', related_name='furnacefurnaceelectrode_paste_set', blank=True, null=True)
    plant = models.ForeignKey('PlantPlant', models.DO_NOTHING, to_field='plant_id')
    plant_furnace_code = models.CharField(max_length=10, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'furnace_furnaceelectrode'
        unique_together = (('furnace_config', 'electrode_name', 'effective_date'),)


class FurnaceFurnaceproduct(models.Model):
    id = models.BigAutoField(primary_key=True)
    created_at = models.DateTimeField()
    modified_at = models.DateTimeField(blank=True, null=True)
    record_status = models.BooleanField()
    created_by = models.ForeignKey('UsersUser', models.DO_NOTHING, to_field='username', blank=True, null=True)
    furnace_config = models.ForeignKey(FurnaceFurnaceconfig, models.DO_NOTHING, to_field='furnace_no')
    material_master = models.ForeignKey('MaterialMasterMaterialmaster', models.DO_NOTHING)
    modified_by = models.ForeignKey('UsersUser', models.DO_NOTHING, to_field='username', related_name='furnacefurnaceproduct_modified_by_set', blank=True, null=True)
    product_type = models.ForeignKey('FurnaceProducttype', models.DO_NOTHING)
    furnace_product_code = models.CharField(unique=True, max_length=100, blank=True, null=True)
    plant = models.ForeignKey('PlantPlant', models.DO_NOTHING, to_field='plant_id')
    plant_furnace_code = models.CharField(max_length=10, blank=True, null=True)
    plant_material_code = models.CharField(max_length=50, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'furnace_furnaceproduct'


class FurnaceFurnacestepchangelog(models.Model):
    id = models.BigAutoField(primary_key=True)
    created_at = models.DateTimeField()
    modified_at = models.DateTimeField(blank=True, null=True)
    record_status = models.BooleanField()
    change_log = models.JSONField()
    created_by = models.ForeignKey('UsersUser', models.DO_NOTHING, to_field='username', blank=True, null=True)
    furnace = models.ForeignKey(FurnaceFurnaceconfig, models.DO_NOTHING, to_field='furnace_no')
    modified_by = models.ForeignKey('UsersUser', models.DO_NOTHING, to_field='username', related_name='furnacefurnacestepchangelog_modified_by_set', blank=True, null=True)
    plant = models.ForeignKey('PlantPlant', models.DO_NOTHING, to_field='plant_id')
    plant_furnace_code = models.CharField(max_length=10, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'furnace_furnacestepchangelog'


class FurnaceMaterialAdditionalinformation(models.Model):
    id = models.BigAutoField(primary_key=True)
    created_at = models.DateTimeField()
    modified_at = models.DateTimeField(blank=True, null=True)
    record_status = models.BooleanField()
    unit_weight = models.DecimalField(max_digits=10, decimal_places=2)
    actual_cost = models.DecimalField(max_digits=10, decimal_places=2)
    addition_group = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    density = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    standard_cost = models.DecimalField(max_digits=10, decimal_places=2)
    co_contributor = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    kwh_melting = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    effective_date = models.DateField()
    created_by = models.ForeignKey('UsersUser', models.DO_NOTHING, to_field='username', blank=True, null=True)
    material_master = models.ForeignKey('MaterialMasterMaterialmaster', models.DO_NOTHING, to_field='mes_mat_code')
    modified_by = models.ForeignKey('UsersUser', models.DO_NOTHING, to_field='username', related_name='furnacematerialadditionalinformation_modified_by_set', blank=True, null=True)
    plant = models.ForeignKey('PlantPlant', models.DO_NOTHING, to_field='plant_id')
    plant_material_code = models.CharField(max_length=50, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'furnace_material_additionalinformation'
        unique_together = (('material_master', 'effective_date'),)


class FurnaceProductcode(models.Model):
    id = models.BigAutoField(primary_key=True)
    created_at = models.DateTimeField()
    modified_at = models.DateTimeField(blank=True, null=True)
    record_status = models.BooleanField()
    name = models.CharField(max_length=50)
    created_by = models.ForeignKey('UsersUser', models.DO_NOTHING, to_field='username', blank=True, null=True)
    modified_by = models.ForeignKey('UsersUser', models.DO_NOTHING, to_field='username', related_name='furnaceproductcode_modified_by_set', blank=True, null=True)
    product_type = models.ForeignKey('FurnaceProducttype', models.DO_NOTHING)
    plant = models.ForeignKey('PlantPlant', models.DO_NOTHING, to_field='plant_id')

    class Meta:
        managed = False
        db_table = 'furnace_productcode'


class FurnaceProducttype(models.Model):
    id = models.BigAutoField(primary_key=True)
    created_at = models.DateTimeField()
    modified_at = models.DateTimeField(blank=True, null=True)
    record_status = models.BooleanField()
    name = models.CharField(max_length=50)
    created_by = models.ForeignKey('UsersUser', models.DO_NOTHING, to_field='username', blank=True, null=True)
    modified_by = models.ForeignKey('UsersUser', models.DO_NOTHING, to_field='username', related_name='furnaceproducttype_modified_by_set', blank=True, null=True)
    plant = models.ForeignKey('PlantPlant', models.DO_NOTHING, to_field='plant_id')

    class Meta:
        managed = False
        db_table = 'furnace_producttype'


class GradingPlanBasicInfo(models.Model):
    id = models.BigAutoField(primary_key=True)
    created_at = models.DateTimeField()
    modified_at = models.DateTimeField(blank=True, null=True)
    record_status = models.BooleanField()
    variant_id = models.CharField(unique=True, max_length=100)
    variant_name = models.CharField(max_length=50)
    activation_date = models.DateTimeField(blank=True, null=True)
    comments = models.TextField(blank=True, null=True)
    is_deleted = models.BooleanField()
    created_by = models.ForeignKey('UsersUser', models.DO_NOTHING, to_field='username', blank=True, null=True)
    furnace_no = models.ForeignKey(FurnaceFurnaceconfig, models.DO_NOTHING, db_column='furnace_no', to_field='furnace_no')
    modified_by = models.ForeignKey('UsersUser', models.DO_NOTHING, to_field='username', related_name='gradingplanbasicinfo_modified_by_set', blank=True, null=True)
    plant = models.ForeignKey('PlantPlant', models.DO_NOTHING, to_field='plant_id')
    plant_furnace_code = models.CharField(max_length=10, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'grading_plan_basic_info'
        unique_together = (('variant_id', 'variant_name'),)


class GradingPlanMaterials(models.Model):
    id = models.BigAutoField(primary_key=True)
    created_at = models.DateTimeField()
    modified_at = models.DateTimeField(blank=True, null=True)
    record_status = models.BooleanField()
    grading_plan_material_code = models.CharField(unique=True, max_length=100)
    priority = models.IntegerField()
    is_deleted = models.BooleanField()
    bulk_pile = models.ForeignKey('UtilsMaster', models.DO_NOTHING, db_column='bulk_pile', to_field='master_code')
    created_by = models.ForeignKey('UsersUser', models.DO_NOTHING, to_field='username', blank=True, null=True)
    furnace_product = models.ForeignKey(FurnaceFurnaceproduct, models.DO_NOTHING, db_column='furnace_product', to_field='furnace_product_code')
    grading_plan = models.ForeignKey(GradingPlanBasicInfo, models.DO_NOTHING, db_column='grading_plan', to_field='variant_id')
    modified_by = models.ForeignKey('UsersUser', models.DO_NOTHING, to_field='username', related_name='gradingplanmaterials_modified_by_set', blank=True, null=True)
    quality = models.ForeignKey('UtilsMaster', models.DO_NOTHING, db_column='quality', to_field='master_code', related_name='gradingplanmaterials_quality_set')
    plant = models.ForeignKey('PlantPlant', models.DO_NOTHING, to_field='plant_id')

    class Meta:
        managed = False
        db_table = 'grading_plan_materials'


class HealthCheckDbTestmodel(models.Model):
    title = models.CharField(max_length=128)

    class Meta:
        managed = False
        db_table = 'health_check_db_testmodel'


class HeatTreatments(models.Model):
    name = models.CharField(unique=True, max_length=100)
    description = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'heat_treatments'


class KpiCycleTimeData(models.Model):
    record_id = models.BigIntegerField(primary_key=True)
    date = models.DateField(blank=True, null=True)
    shift_id = models.CharField(max_length=255)
    cycle_time = models.DecimalField(max_digits=12, decimal_places=2, blank=True, null=True)
    furnace_no = models.ForeignKey(FurnaceFurnaceconfig, models.DO_NOTHING, db_column='furnace_no', to_field='furnace_no', blank=True, null=True)
    machine = models.ForeignKey('LogBookEquipments', models.DO_NOTHING, to_field='equipment_code', blank=True, null=True)
    plant = models.ForeignKey('PlantPlant', models.DO_NOTHING, blank=True, null=True)
    product_type = models.ForeignKey('MaterialMasterMaterialtypemaster', models.DO_NOTHING, to_field='type_code', blank=True, null=True)
    workshop = models.ForeignKey('PlantConfigWorkshop', models.DO_NOTHING, blank=True, null=True)
    material_id = models.ForeignKey('MaterialMasterMaterialmaster', models.DO_NOTHING, to_field='mes_mat_code', blank=True, null=True)
    supplier_id = models.CharField(max_length=100)

    class Meta:
        managed = False
        db_table = 'kpi_cycle_time_data'


class KpiDefectRateData(models.Model):
    record_id = models.BigIntegerField(primary_key=True)
    date = models.DateField(blank=True, null=True)
    shift_id = models.CharField(max_length=255)
    defect_rate = models.DecimalField(max_digits=5, decimal_places=2, blank=True, null=True)
    furnace_no = models.ForeignKey(FurnaceFurnaceconfig, models.DO_NOTHING, db_column='furnace_no', to_field='furnace_no', blank=True, null=True)
    machine = models.ForeignKey('LogBookEquipments', models.DO_NOTHING, to_field='equipment_code', blank=True, null=True)
    plant = models.ForeignKey('PlantPlant', models.DO_NOTHING, blank=True, null=True)
    product_type = models.ForeignKey('MaterialMasterMaterialtypemaster', models.DO_NOTHING, to_field='type_code', blank=True, null=True)
    workshop = models.ForeignKey('PlantConfigWorkshop', models.DO_NOTHING, blank=True, null=True)
    material_id = models.ForeignKey('MaterialMasterMaterialmaster', models.DO_NOTHING, to_field='mes_mat_code', blank=True, null=True)
    supplier_id = models.CharField(max_length=100)

    class Meta:
        managed = False
        db_table = 'kpi_defect_rate_data'


class KpiDowntimeData(models.Model):
    record_id = models.BigIntegerField(primary_key=True)
    date = models.DateField(blank=True, null=True)
    shift_id = models.CharField(max_length=255)
    downtime_hours = models.DecimalField(max_digits=8, decimal_places=2, blank=True, null=True)
    furnace_no = models.ForeignKey(FurnaceFurnaceconfig, models.DO_NOTHING, db_column='furnace_no', to_field='furnace_no', blank=True, null=True)
    machine = models.ForeignKey('LogBookEquipments', models.DO_NOTHING, to_field='equipment_code', blank=True, null=True)
    plant = models.ForeignKey('PlantPlant', models.DO_NOTHING, blank=True, null=True)
    product_type = models.ForeignKey('MaterialMasterMaterialtypemaster', models.DO_NOTHING, to_field='type_code', blank=True, null=True)
    workshop = models.ForeignKey('PlantConfigWorkshop', models.DO_NOTHING, blank=True, null=True)
    material_id = models.ForeignKey('MaterialMasterMaterialmaster', models.DO_NOTHING, to_field='mes_mat_code', blank=True, null=True)
    supplier_id = models.CharField(max_length=100)

    class Meta:
        managed = False
        db_table = 'kpi_downtime_data'


class KpiEnergyEfficiencyData(models.Model):
    record_id = models.BigIntegerField(primary_key=True)
    date = models.DateField(blank=True, null=True)
    shift_id = models.CharField(max_length=255)
    energy_efficiency = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    furnace_no = models.ForeignKey(FurnaceFurnaceconfig, models.DO_NOTHING, db_column='furnace_no', to_field='furnace_no', blank=True, null=True)
    machine = models.ForeignKey('LogBookEquipments', models.DO_NOTHING, to_field='equipment_code', blank=True, null=True)
    plant = models.ForeignKey('PlantPlant', models.DO_NOTHING, blank=True, null=True)
    product_type = models.ForeignKey('MaterialMasterMaterialtypemaster', models.DO_NOTHING, to_field='type_code', blank=True, null=True)
    workshop = models.ForeignKey('PlantConfigWorkshop', models.DO_NOTHING, blank=True, null=True)
    material_id = models.ForeignKey('MaterialMasterMaterialmaster', models.DO_NOTHING, to_field='mes_mat_code', blank=True, null=True)
    supplier_id = models.CharField(max_length=100)

    class Meta:
        managed = False
        db_table = 'kpi_energy_efficiency_data'


class KpiEnergyUsedData(models.Model):
    record_id = models.BigIntegerField(primary_key=True)
    date = models.DateField(blank=True, null=True)
    shift_id = models.CharField(max_length=255)
    energy_used = models.DecimalField(max_digits=12, decimal_places=2, blank=True, null=True)
    furnace_no = models.ForeignKey(FurnaceFurnaceconfig, models.DO_NOTHING, db_column='furnace_no', to_field='furnace_no', blank=True, null=True)
    machine = models.ForeignKey('LogBookEquipments', models.DO_NOTHING, to_field='equipment_code', blank=True, null=True)
    plant = models.ForeignKey('PlantPlant', models.DO_NOTHING, blank=True, null=True)
    product_type = models.ForeignKey('MaterialMasterMaterialtypemaster', models.DO_NOTHING, to_field='type_code', blank=True, null=True)
    workshop = models.ForeignKey('PlantConfigWorkshop', models.DO_NOTHING, blank=True, null=True)
    material_id = models.ForeignKey('MaterialMasterMaterialmaster', models.DO_NOTHING, to_field='mes_mat_code', blank=True, null=True)
    supplier_id = models.CharField(max_length=100)

    class Meta:
        managed = False
        db_table = 'kpi_energy_used_data'


class KpiFirstPassYieldData(models.Model):
    record_id = models.BigIntegerField(primary_key=True)
    date = models.DateField(blank=True, null=True)
    shift_id = models.CharField(max_length=255)
    first_pass_yield = models.DecimalField(max_digits=5, decimal_places=2, blank=True, null=True)
    furnace_no = models.ForeignKey(FurnaceFurnaceconfig, models.DO_NOTHING, db_column='furnace_no', to_field='furnace_no', blank=True, null=True)
    machine = models.ForeignKey('LogBookEquipments', models.DO_NOTHING, to_field='equipment_code', blank=True, null=True)
    plant = models.ForeignKey('PlantPlant', models.DO_NOTHING, blank=True, null=True)
    product_type = models.ForeignKey('MaterialMasterMaterialtypemaster', models.DO_NOTHING, to_field='type_code', blank=True, null=True)
    workshop = models.ForeignKey('PlantConfigWorkshop', models.DO_NOTHING, blank=True, null=True)
    material_id = models.ForeignKey('MaterialMasterMaterialmaster', models.DO_NOTHING, to_field='mes_mat_code', blank=True, null=True)
    supplier_id = models.CharField(max_length=100)

    class Meta:
        managed = False
        db_table = 'kpi_first_pass_yield_data'


class KpiGreenhouseGasEmissionsData(models.Model):
    record_id = models.BigIntegerField(primary_key=True)
    date = models.DateField(blank=True, null=True)
    shift_id = models.CharField(max_length=255)
    emissions_tons = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    furnace_no = models.ForeignKey(FurnaceFurnaceconfig, models.DO_NOTHING, db_column='furnace_no', to_field='furnace_no', blank=True, null=True)
    machine = models.ForeignKey('LogBookEquipments', models.DO_NOTHING, to_field='equipment_code', blank=True, null=True)
    plant = models.ForeignKey('PlantPlant', models.DO_NOTHING, blank=True, null=True)
    product_type = models.ForeignKey('MaterialMasterMaterialtypemaster', models.DO_NOTHING, to_field='type_code', blank=True, null=True)
    workshop = models.ForeignKey('PlantConfigWorkshop', models.DO_NOTHING, blank=True, null=True)
    material_id = models.ForeignKey('MaterialMasterMaterialmaster', models.DO_NOTHING, to_field='mes_mat_code', blank=True, null=True)
    supplier_id = models.CharField(max_length=100)

    class Meta:
        managed = False
        db_table = 'kpi_greenhouse_gas_emissions_data'


class KpiMaintenanceComplianceData(models.Model):
    record_id = models.BigIntegerField(primary_key=True)
    date = models.DateField(blank=True, null=True)
    shift_id = models.CharField(max_length=255)
    compliance_percentage = models.DecimalField(max_digits=5, decimal_places=2, blank=True, null=True)
    furnace_no = models.ForeignKey(FurnaceFurnaceconfig, models.DO_NOTHING, db_column='furnace_no', to_field='furnace_no', blank=True, null=True)
    machine = models.ForeignKey('LogBookEquipments', models.DO_NOTHING, to_field='equipment_code', blank=True, null=True)
    plant = models.ForeignKey('PlantPlant', models.DO_NOTHING, blank=True, null=True)
    product_type = models.ForeignKey('MaterialMasterMaterialtypemaster', models.DO_NOTHING, to_field='type_code', blank=True, null=True)
    workshop = models.ForeignKey('PlantConfigWorkshop', models.DO_NOTHING, blank=True, null=True)
    material_id = models.ForeignKey('MaterialMasterMaterialmaster', models.DO_NOTHING, to_field='mes_mat_code', blank=True, null=True)
    supplier_id = models.CharField(max_length=100)

    class Meta:
        managed = False
        db_table = 'kpi_maintenance_compliance_data'


class KpiMaterialConsumptionData(models.Model):
    record_id = models.BigIntegerField(primary_key=True)
    date = models.DateField(blank=True, null=True)
    shift_id = models.CharField(max_length=255)
    material_consumption_tons = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    furnace_no = models.ForeignKey(FurnaceFurnaceconfig, models.DO_NOTHING, db_column='furnace_no', to_field='furnace_no', blank=True, null=True)
    machine = models.ForeignKey('LogBookEquipments', models.DO_NOTHING, to_field='equipment_code', blank=True, null=True)
    plant = models.ForeignKey('PlantPlant', models.DO_NOTHING, blank=True, null=True)
    product_type = models.ForeignKey('MaterialMasterMaterialtypemaster', models.DO_NOTHING, to_field='type_code', blank=True, null=True)
    workshop = models.ForeignKey('PlantConfigWorkshop', models.DO_NOTHING, blank=True, null=True)
    material_id = models.ForeignKey('MaterialMasterMaterialmaster', models.DO_NOTHING, to_field='mes_mat_code', blank=True, null=True)
    supplier_id = models.CharField(max_length=100)

    class Meta:
        managed = False
        db_table = 'kpi_material_consumption_data'


class KpiMaterialVarianceCostData(models.Model):
    record_id = models.BigIntegerField(primary_key=True)
    date = models.DateField(blank=True, null=True)
    shift_id = models.CharField(max_length=255)
    variance_cost = models.DecimalField(max_digits=12, decimal_places=2, blank=True, null=True)
    furnace_no = models.ForeignKey(FurnaceFurnaceconfig, models.DO_NOTHING, db_column='furnace_no', to_field='furnace_no', blank=True, null=True)
    machine = models.ForeignKey('LogBookEquipments', models.DO_NOTHING, to_field='equipment_code', blank=True, null=True)
    plant = models.ForeignKey('PlantPlant', models.DO_NOTHING, blank=True, null=True)
    product_type = models.ForeignKey('MaterialMasterMaterialtypemaster', models.DO_NOTHING, to_field='type_code', blank=True, null=True)
    workshop = models.ForeignKey('PlantConfigWorkshop', models.DO_NOTHING, blank=True, null=True)
    material_id = models.ForeignKey('MaterialMasterMaterialmaster', models.DO_NOTHING, to_field='mes_mat_code', blank=True, null=True)
    supplier_id = models.CharField(max_length=100)

    class Meta:
        managed = False
        db_table = 'kpi_material_variance_cost_data'


class KpiMaterialVarianceQuantityData(models.Model):
    record_id = models.BigIntegerField(primary_key=True)
    date = models.DateField(blank=True, null=True)
    shift_id = models.CharField(max_length=255)
    variance_quantity = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    furnace_no = models.ForeignKey(FurnaceFurnaceconfig, models.DO_NOTHING, db_column='furnace_no', to_field='furnace_no', blank=True, null=True)
    machine = models.ForeignKey('LogBookEquipments', models.DO_NOTHING, to_field='equipment_code', blank=True, null=True)
    plant = models.ForeignKey('PlantPlant', models.DO_NOTHING, blank=True, null=True)
    product_type = models.ForeignKey('MaterialMasterMaterialtypemaster', models.DO_NOTHING, to_field='type_code', blank=True, null=True)
    workshop = models.ForeignKey('PlantConfigWorkshop', models.DO_NOTHING, blank=True, null=True)
    material_id = models.ForeignKey('MaterialMasterMaterialmaster', models.DO_NOTHING, to_field='mes_mat_code', blank=True, null=True)
    supplier_id = models.CharField(max_length=100)

    class Meta:
        managed = False
        db_table = 'kpi_material_variance_quantity_data'


class KpiMeanTimeBetweenFailuresData(models.Model):
    record_id = models.BigIntegerField(primary_key=True)
    date = models.DateField(blank=True, null=True)
    shift_id = models.CharField(max_length=255)
    mtbf_hours = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    furnace_no = models.ForeignKey(FurnaceFurnaceconfig, models.DO_NOTHING, db_column='furnace_no', to_field='furnace_no', blank=True, null=True)
    machine = models.ForeignKey('LogBookEquipments', models.DO_NOTHING, to_field='equipment_code', blank=True, null=True)
    plant = models.ForeignKey('PlantPlant', models.DO_NOTHING, blank=True, null=True)
    product_type = models.ForeignKey('MaterialMasterMaterialtypemaster', models.DO_NOTHING, to_field='type_code', blank=True, null=True)
    workshop = models.ForeignKey('PlantConfigWorkshop', models.DO_NOTHING, blank=True, null=True)
    material_id = models.ForeignKey('MaterialMasterMaterialmaster', models.DO_NOTHING, to_field='mes_mat_code', blank=True, null=True)
    supplier_id = models.CharField(max_length=100)

    class Meta:
        managed = False
        db_table = 'kpi_mean_time_between_failures_data'


class KpiMeanTimeBetweenStoppagesData(models.Model):
    record_id = models.BigIntegerField(primary_key=True)
    date = models.DateField(blank=True, null=True)
    shift_id = models.CharField(max_length=255)
    mtbs_hours = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    furnace_no = models.ForeignKey(FurnaceFurnaceconfig, models.DO_NOTHING, db_column='furnace_no', to_field='furnace_no', blank=True, null=True)
    machine = models.ForeignKey('LogBookEquipments', models.DO_NOTHING, to_field='equipment_code', blank=True, null=True)
    plant = models.ForeignKey('PlantPlant', models.DO_NOTHING, blank=True, null=True)
    product_type = models.ForeignKey('MaterialMasterMaterialtypemaster', models.DO_NOTHING, to_field='type_code', blank=True, null=True)
    workshop = models.ForeignKey('PlantConfigWorkshop', models.DO_NOTHING, blank=True, null=True)
    material_id = models.ForeignKey('MaterialMasterMaterialmaster', models.DO_NOTHING, to_field='mes_mat_code', blank=True, null=True)
    supplier_id = models.CharField(max_length=100)

    class Meta:
        managed = False
        db_table = 'kpi_mean_time_between_stoppages_data'


class KpiMeanTimeToRepairData(models.Model):
    record_id = models.BigIntegerField(primary_key=True)
    date = models.DateField(blank=True, null=True)
    shift_id = models.CharField(max_length=255)
    mttr_hours = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    furnace_no = models.ForeignKey(FurnaceFurnaceconfig, models.DO_NOTHING, db_column='furnace_no', to_field='furnace_no', blank=True, null=True)
    machine = models.ForeignKey('LogBookEquipments', models.DO_NOTHING, to_field='equipment_code', blank=True, null=True)
    plant = models.ForeignKey('PlantPlant', models.DO_NOTHING, blank=True, null=True)
    product_type = models.ForeignKey('MaterialMasterMaterialtypemaster', models.DO_NOTHING, to_field='type_code', blank=True, null=True)
    workshop = models.ForeignKey('PlantConfigWorkshop', models.DO_NOTHING, blank=True, null=True)
    material_id = models.ForeignKey('MaterialMasterMaterialmaster', models.DO_NOTHING, to_field='mes_mat_code', blank=True, null=True)
    supplier_id = models.CharField(max_length=100)

    class Meta:
        managed = False
        db_table = 'kpi_mean_time_to_repair_data'


class KpiOnTimeDeliveryData(models.Model):
    record_id = models.BigIntegerField(primary_key=True)
    date = models.DateField(blank=True, null=True)
    shift_id = models.CharField(max_length=255)
    on_time_delivery_percentage = models.DecimalField(max_digits=5, decimal_places=2, blank=True, null=True)
    furnace_no = models.ForeignKey(FurnaceFurnaceconfig, models.DO_NOTHING, db_column='furnace_no', to_field='furnace_no', blank=True, null=True)
    machine = models.ForeignKey('LogBookEquipments', models.DO_NOTHING, to_field='equipment_code', blank=True, null=True)
    plant = models.ForeignKey('PlantPlant', models.DO_NOTHING, blank=True, null=True)
    product_type = models.ForeignKey('MaterialMasterMaterialtypemaster', models.DO_NOTHING, to_field='type_code', blank=True, null=True)
    workshop = models.ForeignKey('PlantConfigWorkshop', models.DO_NOTHING, blank=True, null=True)
    material_id = models.ForeignKey('MaterialMasterMaterialmaster', models.DO_NOTHING, to_field='mes_mat_code', blank=True, null=True)
    supplier_id = models.CharField(max_length=100)

    class Meta:
        managed = False
        db_table = 'kpi_on_time_delivery_data'


class KpiOperatingCostsData(models.Model):
    record_id = models.BigIntegerField(primary_key=True)
    date = models.DateField(blank=True, null=True)
    shift_id = models.CharField(max_length=255)
    operating_costs = models.DecimalField(max_digits=12, decimal_places=2, blank=True, null=True)
    furnace_no = models.ForeignKey(FurnaceFurnaceconfig, models.DO_NOTHING, db_column='furnace_no', to_field='furnace_no', blank=True, null=True)
    machine = models.ForeignKey('LogBookEquipments', models.DO_NOTHING, to_field='equipment_code', blank=True, null=True)
    plant = models.ForeignKey('PlantPlant', models.DO_NOTHING, blank=True, null=True)
    product_type = models.ForeignKey('MaterialMasterMaterialtypemaster', models.DO_NOTHING, to_field='type_code', blank=True, null=True)
    workshop = models.ForeignKey('PlantConfigWorkshop', models.DO_NOTHING, blank=True, null=True)
    material_id = models.ForeignKey('MaterialMasterMaterialmaster', models.DO_NOTHING, to_field='mes_mat_code', blank=True, null=True)
    supplier_id = models.CharField(max_length=100)

    class Meta:
        managed = False
        db_table = 'kpi_operating_costs_data'


class KpiOutputRateData(models.Model):
    record_id = models.BigIntegerField(primary_key=True)
    date = models.DateField(blank=True, null=True)
    shift_id = models.CharField(max_length=255)
    output_rate_percentage = models.DecimalField(max_digits=5, decimal_places=2, blank=True, null=True)
    furnace_no = models.ForeignKey(FurnaceFurnaceconfig, models.DO_NOTHING, db_column='furnace_no', to_field='furnace_no', blank=True, null=True)
    machine = models.ForeignKey('LogBookEquipments', models.DO_NOTHING, to_field='equipment_code', blank=True, null=True)
    plant = models.ForeignKey('PlantPlant', models.DO_NOTHING, blank=True, null=True)
    product_type = models.ForeignKey('MaterialMasterMaterialtypemaster', models.DO_NOTHING, to_field='type_code', blank=True, null=True)
    workshop = models.ForeignKey('PlantConfigWorkshop', models.DO_NOTHING, blank=True, null=True)
    material_id = models.ForeignKey('MaterialMasterMaterialmaster', models.DO_NOTHING, to_field='mes_mat_code', blank=True, null=True)
    supplier_id = models.CharField(max_length=100)

    class Meta:
        managed = False
        db_table = 'kpi_output_rate_data'


class KpiOverallEquipmentEfficiencyData(models.Model):
    record_id = models.BigIntegerField(primary_key=True)
    date = models.DateField(blank=True, null=True)
    shift_id = models.CharField(max_length=255)
    oee_percentage = models.DecimalField(max_digits=5, decimal_places=2, blank=True, null=True)
    furnace_no = models.ForeignKey(FurnaceFurnaceconfig, models.DO_NOTHING, db_column='furnace_no', to_field='furnace_no', blank=True, null=True)
    machine = models.ForeignKey('LogBookEquipments', models.DO_NOTHING, to_field='equipment_code', blank=True, null=True)
    plant = models.ForeignKey('PlantPlant', models.DO_NOTHING, blank=True, null=True)
    product_type = models.ForeignKey('MaterialMasterMaterialtypemaster', models.DO_NOTHING, to_field='type_code', blank=True, null=True)
    workshop = models.ForeignKey('PlantConfigWorkshop', models.DO_NOTHING, blank=True, null=True)
    material_id = models.ForeignKey('MaterialMasterMaterialmaster', models.DO_NOTHING, to_field='mes_mat_code', blank=True, null=True)
    supplier_id = models.CharField(max_length=100)

    class Meta:
        managed = False
        db_table = 'kpi_overall_equipment_efficiency_data'


class KpiPlannedMaintenanceData(models.Model):
    record_id = models.BigIntegerField(primary_key=True)
    date = models.DateField(blank=True, null=True)
    shift_id = models.CharField(max_length=255)
    planned_maintenance_percentage = models.DecimalField(max_digits=5, decimal_places=2, blank=True, null=True)
    furnace_no = models.ForeignKey(FurnaceFurnaceconfig, models.DO_NOTHING, db_column='furnace_no', to_field='furnace_no', blank=True, null=True)
    machine = models.ForeignKey('LogBookEquipments', models.DO_NOTHING, to_field='equipment_code', blank=True, null=True)
    plant = models.ForeignKey('PlantPlant', models.DO_NOTHING, blank=True, null=True)
    product_type = models.ForeignKey('MaterialMasterMaterialtypemaster', models.DO_NOTHING, to_field='type_code', blank=True, null=True)
    workshop = models.ForeignKey('PlantConfigWorkshop', models.DO_NOTHING, blank=True, null=True)
    material_id = models.ForeignKey('MaterialMasterMaterialmaster', models.DO_NOTHING, to_field='mes_mat_code', blank=True, null=True)
    supplier_id = models.CharField(max_length=100)

    class Meta:
        managed = False
        db_table = 'kpi_planned_maintenance_data'


class KpiPpeUsageComplianceData(models.Model):
    record_id = models.BigIntegerField(primary_key=True)
    date = models.DateField(blank=True, null=True)
    shift_id = models.CharField(max_length=255)
    ppe_compliance_percentage = models.DecimalField(max_digits=5, decimal_places=2, blank=True, null=True)
    furnace_no = models.ForeignKey(FurnaceFurnaceconfig, models.DO_NOTHING, db_column='furnace_no', to_field='furnace_no', blank=True, null=True)
    machine = models.ForeignKey('LogBookEquipments', models.DO_NOTHING, to_field='equipment_code', blank=True, null=True)
    plant = models.ForeignKey('PlantPlant', models.DO_NOTHING, blank=True, null=True)
    product_type = models.ForeignKey('MaterialMasterMaterialtypemaster', models.DO_NOTHING, to_field='type_code', blank=True, null=True)
    workshop = models.ForeignKey('PlantConfigWorkshop', models.DO_NOTHING, blank=True, null=True)
    material_id = models.ForeignKey('MaterialMasterMaterialmaster', models.DO_NOTHING, to_field='mes_mat_code', blank=True, null=True)
    supplier_id = models.CharField(max_length=100)

    class Meta:
        managed = False
        db_table = 'kpi_ppe_usage_compliance_data'


class KpiProductionEfficiencyData(models.Model):
    record_id = models.BigIntegerField(primary_key=True)
    date = models.DateField(blank=True, null=True)
    shift_id = models.CharField(max_length=255)
    production_efficiency_percentage = models.DecimalField(max_digits=5, decimal_places=2, blank=True, null=True)
    furnace_no = models.ForeignKey(FurnaceFurnaceconfig, models.DO_NOTHING, db_column='furnace_no', to_field='furnace_no', blank=True, null=True)
    machine = models.ForeignKey('LogBookEquipments', models.DO_NOTHING, to_field='equipment_code', blank=True, null=True)
    plant = models.ForeignKey('PlantPlant', models.DO_NOTHING, blank=True, null=True)
    product_type = models.ForeignKey('MaterialMasterMaterialtypemaster', models.DO_NOTHING, to_field='type_code', blank=True, null=True)
    workshop = models.ForeignKey('PlantConfigWorkshop', models.DO_NOTHING, blank=True, null=True)
    material_id = models.ForeignKey('MaterialMasterMaterialmaster', models.DO_NOTHING, to_field='mes_mat_code', blank=True, null=True)
    supplier_id = models.CharField(max_length=100)

    class Meta:
        managed = False
        db_table = 'kpi_production_efficiency_data'


class KpiProfitMarginData(models.Model):
    record_id = models.BigIntegerField(primary_key=True)
    date = models.DateField(blank=True, null=True)
    shift_id = models.CharField(max_length=255)
    profit_margin_percentage = models.DecimalField(max_digits=5, decimal_places=2, blank=True, null=True)
    furnace_no = models.ForeignKey(FurnaceFurnaceconfig, models.DO_NOTHING, db_column='furnace_no', to_field='furnace_no', blank=True, null=True)
    machine = models.ForeignKey('LogBookEquipments', models.DO_NOTHING, to_field='equipment_code', blank=True, null=True)
    plant = models.ForeignKey('PlantPlant', models.DO_NOTHING, blank=True, null=True)
    product_type = models.ForeignKey('MaterialMasterMaterialtypemaster', models.DO_NOTHING, to_field='type_code', blank=True, null=True)
    workshop = models.ForeignKey('PlantConfigWorkshop', models.DO_NOTHING, blank=True, null=True)
    material_id = models.ForeignKey('MaterialMasterMaterialmaster', models.DO_NOTHING, to_field='mes_mat_code', blank=True, null=True)
    supplier_id = models.CharField(max_length=100)

    class Meta:
        managed = False
        db_table = 'kpi_profit_margin_data'


class KpiQuantityProducedData(models.Model):
    record_id = models.BigIntegerField(primary_key=True)
    date = models.DateField(blank=True, null=True)
    shift_id = models.CharField(max_length=255)
    quantity_produced = models.DecimalField(max_digits=12, decimal_places=2, blank=True, null=True)
    furnace_no = models.ForeignKey(FurnaceFurnaceconfig, models.DO_NOTHING, db_column='furnace_no', to_field='furnace_no', blank=True, null=True)
    machine = models.ForeignKey('LogBookEquipments', models.DO_NOTHING, to_field='equipment_code', blank=True, null=True)
    plant = models.ForeignKey('PlantPlant', models.DO_NOTHING, blank=True, null=True)
    product_type = models.ForeignKey('MaterialMasterMaterialtypemaster', models.DO_NOTHING, to_field='type_code', blank=True, null=True)
    workshop = models.ForeignKey('PlantConfigWorkshop', models.DO_NOTHING, blank=True, null=True)
    material_id = models.ForeignKey('MaterialMasterMaterialmaster', models.DO_NOTHING, to_field='mes_mat_code', blank=True, null=True)
    supplier_id = models.CharField(max_length=100)
    record_id_0 = models.IntegerField(db_column='Record ID', blank=True, null=True)  # Field name made lowercase. Field renamed to remove unsuitable characters. Field renamed because of name conflict.
    plant_id_legacy = models.CharField(db_column='Plant ID', max_length=50, blank=True, null=True)  # Field name made lowercase. Field renamed to remove unsuitable characters.
    furnace_id = models.IntegerField(db_column='Furnace ID', blank=True, null=True)  # Field name made lowercase. Field renamed to remove unsuitable characters.
    shift_id_0 = models.CharField(db_column='Shift ID', max_length=50, blank=True, null=True)  # Field name made lowercase. Field renamed to remove unsuitable characters. Field renamed because of name conflict.
    material_type = models.CharField(db_column='Material Type', max_length=50, blank=True, null=True)  # Field name made lowercase. Field renamed to remove unsuitable characters.
    material_id_0 = models.CharField(db_column='Material ID', max_length=50, blank=True, null=True)  # Field name made lowercase. Field renamed to remove unsuitable characters. Field renamed because of name conflict.
    supplier_id_0 = models.CharField(db_column='Supplier ID', max_length=50, blank=True, null=True)  # Field name made lowercase. Field renamed to remove unsuitable characters. Field renamed because of name conflict.
    equipment_id = models.CharField(db_column='Equipment ID', max_length=50, blank=True, null=True)  # Field name made lowercase. Field renamed to remove unsuitable characters.
    quantity_produced_units_field = models.FloatField(db_column='Quantity Produced (units)', blank=True, null=True)  # Field name made lowercase. Field renamed to remove unsuitable characters. Field renamed because it ended with '_'.

    class Meta:
        managed = False
        db_table = 'kpi_quantity_produced_data'


class KpiResourceCapacityUtilizationData(models.Model):
    record_id = models.BigIntegerField(primary_key=True)
    date = models.DateField(blank=True, null=True)
    shift_id = models.CharField(max_length=255)
    utilization_percentage = models.DecimalField(max_digits=5, decimal_places=2, blank=True, null=True)
    furnace_no = models.ForeignKey(FurnaceFurnaceconfig, models.DO_NOTHING, db_column='furnace_no', to_field='furnace_no', blank=True, null=True)
    machine = models.ForeignKey('LogBookEquipments', models.DO_NOTHING, to_field='equipment_code', blank=True, null=True)
    plant = models.ForeignKey('PlantPlant', models.DO_NOTHING, blank=True, null=True)
    product_type = models.ForeignKey('MaterialMasterMaterialtypemaster', models.DO_NOTHING, to_field='type_code', blank=True, null=True)
    workshop = models.ForeignKey('PlantConfigWorkshop', models.DO_NOTHING, blank=True, null=True)
    material_id = models.ForeignKey('MaterialMasterMaterialmaster', models.DO_NOTHING, to_field='mes_mat_code', blank=True, null=True)
    supplier_id = models.CharField(max_length=100)

    class Meta:
        managed = False
        db_table = 'kpi_resource_capacity_utilization_data'


class KpiReworkRateData(models.Model):
    record_id = models.BigIntegerField(primary_key=True)
    date = models.DateField(blank=True, null=True)
    shift_id = models.CharField(max_length=255)
    rework_rate_percentage = models.DecimalField(max_digits=5, decimal_places=2, blank=True, null=True)
    furnace_no = models.ForeignKey(FurnaceFurnaceconfig, models.DO_NOTHING, db_column='furnace_no', to_field='furnace_no', blank=True, null=True)
    machine = models.ForeignKey('LogBookEquipments', models.DO_NOTHING, to_field='equipment_code', blank=True, null=True)
    plant = models.ForeignKey('PlantPlant', models.DO_NOTHING, blank=True, null=True)
    product_type = models.ForeignKey('MaterialMasterMaterialtypemaster', models.DO_NOTHING, to_field='type_code', blank=True, null=True)
    workshop = models.ForeignKey('PlantConfigWorkshop', models.DO_NOTHING, blank=True, null=True)
    material_id = models.ForeignKey('MaterialMasterMaterialmaster', models.DO_NOTHING, to_field='mes_mat_code', blank=True, null=True)
    supplier_id = models.CharField(max_length=100)

    class Meta:
        managed = False
        db_table = 'kpi_rework_rate_data'


class KpiRoiOnInvestmentsData(models.Model):
    record_id = models.BigIntegerField(primary_key=True)
    date = models.DateField(blank=True, null=True)
    shift_id = models.CharField(max_length=255)
    roi_percentage = models.DecimalField(max_digits=5, decimal_places=2, blank=True, null=True)
    furnace_no = models.ForeignKey(FurnaceFurnaceconfig, models.DO_NOTHING, db_column='furnace_no', to_field='furnace_no', blank=True, null=True)
    machine = models.ForeignKey('LogBookEquipments', models.DO_NOTHING, to_field='equipment_code', blank=True, null=True)
    plant = models.ForeignKey('PlantPlant', models.DO_NOTHING, blank=True, null=True)
    product_type = models.ForeignKey('MaterialMasterMaterialtypemaster', models.DO_NOTHING, to_field='type_code', blank=True, null=True)
    workshop = models.ForeignKey('PlantConfigWorkshop', models.DO_NOTHING, blank=True, null=True)
    material_id = models.ForeignKey('MaterialMasterMaterialmaster', models.DO_NOTHING, to_field='mes_mat_code', blank=True, null=True)
    supplier_id = models.CharField(max_length=100)

    class Meta:
        managed = False
        db_table = 'kpi_roi_on_investments_data'


class KpiSafetyIncidentsReportedData(models.Model):
    record_id = models.BigIntegerField(primary_key=True)
    date = models.DateField(blank=True, null=True)
    shift_id = models.CharField(max_length=255)
    incidents_percentage = models.DecimalField(max_digits=5, decimal_places=2, blank=True, null=True)
    furnace_no = models.ForeignKey(FurnaceFurnaceconfig, models.DO_NOTHING, db_column='furnace_no', to_field='furnace_no', blank=True, null=True)
    machine = models.ForeignKey('LogBookEquipments', models.DO_NOTHING, to_field='equipment_code', blank=True, null=True)
    plant = models.ForeignKey('PlantPlant', models.DO_NOTHING, blank=True, null=True)
    product_type = models.ForeignKey('MaterialMasterMaterialtypemaster', models.DO_NOTHING, to_field='type_code', blank=True, null=True)
    workshop = models.ForeignKey('PlantConfigWorkshop', models.DO_NOTHING, blank=True, null=True)
    material_id = models.ForeignKey('MaterialMasterMaterialmaster', models.DO_NOTHING, to_field='mes_mat_code', blank=True, null=True)
    supplier_id = models.CharField(max_length=100)

    class Meta:
        managed = False
        db_table = 'kpi_safety_incidents_reported_data'


class KpiTotalRevenueData(models.Model):
    record_id = models.BigIntegerField(primary_key=True)
    date = models.DateField(blank=True, null=True)
    shift_id = models.CharField(max_length=255)
    total_revenue = models.DecimalField(max_digits=12, decimal_places=2, blank=True, null=True)
    furnace_no = models.ForeignKey(FurnaceFurnaceconfig, models.DO_NOTHING, db_column='furnace_no', to_field='furnace_no', blank=True, null=True)
    machine = models.ForeignKey('LogBookEquipments', models.DO_NOTHING, to_field='equipment_code', blank=True, null=True)
    plant = models.ForeignKey('PlantPlant', models.DO_NOTHING, blank=True, null=True)
    product_type = models.ForeignKey('MaterialMasterMaterialtypemaster', models.DO_NOTHING, to_field='type_code', blank=True, null=True)
    workshop = models.ForeignKey('PlantConfigWorkshop', models.DO_NOTHING, blank=True, null=True)
    material_id = models.ForeignKey('MaterialMasterMaterialmaster', models.DO_NOTHING, to_field='mes_mat_code', blank=True, null=True)
    supplier_id = models.CharField(max_length=100)

    class Meta:
        managed = False
        db_table = 'kpi_total_revenue_data'


class KpiTrainingComplianceData(models.Model):
    record_id = models.BigIntegerField(primary_key=True)
    date = models.DateField(blank=True, null=True)
    shift_id = models.CharField(max_length=255)
    training_compliance_percentage = models.DecimalField(max_digits=5, decimal_places=2, blank=True, null=True)
    furnace_no = models.ForeignKey(FurnaceFurnaceconfig, models.DO_NOTHING, db_column='furnace_no', to_field='furnace_no', blank=True, null=True)
    machine = models.ForeignKey('LogBookEquipments', models.DO_NOTHING, to_field='equipment_code', blank=True, null=True)
    plant = models.ForeignKey('PlantPlant', models.DO_NOTHING, blank=True, null=True)
    product_type = models.ForeignKey('MaterialMasterMaterialtypemaster', models.DO_NOTHING, to_field='type_code', blank=True, null=True)
    workshop = models.ForeignKey('PlantConfigWorkshop', models.DO_NOTHING, blank=True, null=True)
    material_id = models.ForeignKey('MaterialMasterMaterialmaster', models.DO_NOTHING, to_field='mes_mat_code', blank=True, null=True)
    supplier_id = models.CharField(max_length=100)

    class Meta:
        managed = False
        db_table = 'kpi_training_compliance_data'


class KpiWaterUsagePerUnitData(models.Model):
    record_id = models.BigIntegerField(primary_key=True)
    date = models.DateField(blank=True, null=True)
    shift_id = models.CharField(max_length=255)
    water_usage_percentage = models.DecimalField(max_digits=5, decimal_places=2, blank=True, null=True)
    furnace_no = models.ForeignKey(FurnaceFurnaceconfig, models.DO_NOTHING, db_column='furnace_no', to_field='furnace_no', blank=True, null=True)
    machine = models.ForeignKey('LogBookEquipments', models.DO_NOTHING, to_field='equipment_code', blank=True, null=True)
    plant = models.ForeignKey('PlantPlant', models.DO_NOTHING, blank=True, null=True)
    product_type = models.ForeignKey('MaterialMasterMaterialtypemaster', models.DO_NOTHING, to_field='type_code', blank=True, null=True)
    workshop = models.ForeignKey('PlantConfigWorkshop', models.DO_NOTHING, blank=True, null=True)
    material_id = models.ForeignKey('MaterialMasterMaterialmaster', models.DO_NOTHING, to_field='mes_mat_code', blank=True, null=True)
    supplier_id = models.CharField(max_length=100)

    class Meta:
        managed = False
        db_table = 'kpi_water_usage_per_unit_data'


class KpiYieldData(models.Model):
    record_id = models.BigIntegerField(primary_key=True)
    date = models.DateField(blank=True, null=True)
    shift_id = models.CharField(max_length=255)
    yield_percentage = models.DecimalField(max_digits=5, decimal_places=2, blank=True, null=True)
    furnace_no = models.ForeignKey(FurnaceFurnaceconfig, models.DO_NOTHING, db_column='furnace_no', to_field='furnace_no', blank=True, null=True)
    machine = models.ForeignKey('LogBookEquipments', models.DO_NOTHING, to_field='equipment_code', blank=True, null=True)
    plant = models.ForeignKey('PlantPlant', models.DO_NOTHING, blank=True, null=True)
    product_type = models.ForeignKey('MaterialMasterMaterialtypemaster', models.DO_NOTHING, to_field='type_code', blank=True, null=True)
    workshop = models.ForeignKey('PlantConfigWorkshop', models.DO_NOTHING, blank=True, null=True)
    material_id = models.ForeignKey('MaterialMasterMaterialmaster', models.DO_NOTHING, to_field='mes_mat_code', blank=True, null=True)
    supplier_id = models.CharField(max_length=100)

    class Meta:
        managed = False
        db_table = 'kpi_yield_data'


class LabAnalysisAnalysiselementmaster(models.Model):
    id = models.BigAutoField(primary_key=True)
    element_code = models.ForeignKey('MaterialMasterElement', models.DO_NOTHING, db_column='element_code', to_field='element_code')
    function_code = models.ForeignKey('UtilsFunction', models.DO_NOTHING, db_column='function_code', to_field='function_code')

    class Meta:
        managed = False
        db_table = 'lab_analysis_analysiselementmaster'
        unique_together = (('element_code', 'function_code'),)


class LabAnalysisRawmaterialanalysisbasicinfo(models.Model):
    id = models.BigAutoField(primary_key=True)
    created_at = models.DateTimeField()
    modified_at = models.DateTimeField(blank=True, null=True)
    record_status = models.BooleanField()
    batch_id = models.CharField(max_length=50, blank=True, null=True)
    raw_mat_analysis_dt = models.DateTimeField()
    sample_id = models.CharField(max_length=50)
    shipment_id = models.CharField(max_length=50, blank=True, null=True)
    comments = models.TextField(blank=True, null=True)
    raw_mat_analysis_status = models.CharField(max_length=20)
    raw_mat_analysis_id = models.CharField(unique=True, max_length=50)
    created_by = models.ForeignKey('UsersUser', models.DO_NOTHING, to_field='username', blank=True, null=True)
    mes_mat_code = models.ForeignKey('MaterialMasterMaterialmaster', models.DO_NOTHING, db_column='mes_mat_code', to_field='mes_mat_code')
    material_type_code = models.ForeignKey('MaterialMasterMaterialtypemaster', models.DO_NOTHING, db_column='material_type_code', to_field='type_code')
    modified_by = models.ForeignKey('UsersUser', models.DO_NOTHING, to_field='username', related_name='labanalysisrawmaterialanalysisbasicinfo_modified_by_set', blank=True, null=True)
    sample_source_code = models.ForeignKey('UtilsMaster', models.DO_NOTHING, db_column='sample_source_code', to_field='master_code', blank=True, null=True)
    sample_type_code = models.ForeignKey('UtilsMaster', models.DO_NOTHING, db_column='sample_type_code', to_field='master_code', related_name='labanalysisrawmaterialanalysisbasicinfo_sample_type_code_set', blank=True, null=True)
    plant = models.ForeignKey('PlantPlant', models.DO_NOTHING, to_field='plant_id')
    plant_material_code = models.CharField(max_length=50, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'lab_analysis_rawmaterialanalysisbasicinfo'
        unique_together = (('raw_mat_analysis_dt', 'sample_id', 'mes_mat_code'),)


class LabAnalysisRawmaterialanalysischangehistory(models.Model):
    id = models.BigAutoField(primary_key=True)
    created_at = models.DateTimeField()
    modified_at = models.DateTimeField(blank=True, null=True)
    record_status = models.BooleanField()
    analysis_value = models.DecimalField(max_digits=10, decimal_places=4)
    created_by = models.ForeignKey('UsersUser', models.DO_NOTHING, to_field='username', blank=True, null=True)
    element_code = models.ForeignKey('MaterialMasterElement', models.DO_NOTHING, db_column='element_code', to_field='element_code')
    modified_by = models.ForeignKey('UsersUser', models.DO_NOTHING, to_field='username', related_name='labanalysisrawmaterialanalysischangehistory_modified_by_set', blank=True, null=True)
    raw_mat_analysis = models.ForeignKey(LabAnalysisRawmaterialanalysisbasicinfo, models.DO_NOTHING, to_field='raw_mat_analysis_id')
    plant = models.ForeignKey('PlantPlant', models.DO_NOTHING, to_field='plant_id')

    class Meta:
        managed = False
        db_table = 'lab_analysis_rawmaterialanalysischangehistory'


class LabAnalysisRawmaterialanalysischangelog(models.Model):
    id = models.BigAutoField(primary_key=True)
    created_at = models.DateTimeField()
    modified_at = models.DateTimeField(blank=True, null=True)
    record_status = models.BooleanField()
    change_log = models.JSONField()
    created_by = models.ForeignKey('UsersUser', models.DO_NOTHING, to_field='username', blank=True, null=True)
    modified_by = models.ForeignKey('UsersUser', models.DO_NOTHING, to_field='username', related_name='labanalysisrawmaterialanalysischangelog_modified_by_set', blank=True, null=True)
    raw_mat_analysis = models.ForeignKey(LabAnalysisRawmaterialanalysisbasicinfo, models.DO_NOTHING, to_field='raw_mat_analysis_id')
    plant = models.ForeignKey('PlantPlant', models.DO_NOTHING, to_field='plant_id')

    class Meta:
        managed = False
        db_table = 'lab_analysis_rawmaterialanalysischangelog'


class LabAnalysisRawmaterialanalysisvalue(models.Model):
    id = models.BigAutoField(primary_key=True)
    created_at = models.DateTimeField()
    modified_at = models.DateTimeField(blank=True, null=True)
    record_status = models.BooleanField()
    analysis_value = models.DecimalField(max_digits=10, decimal_places=4, blank=True, null=True)
    created_by = models.ForeignKey('UsersUser', models.DO_NOTHING, to_field='username', blank=True, null=True)
    element_code = models.ForeignKey('MaterialMasterElement', models.DO_NOTHING, db_column='element_code', to_field='element_code')
    modified_by = models.ForeignKey('UsersUser', models.DO_NOTHING, to_field='username', related_name='labanalysisrawmaterialanalysisvalue_modified_by_set', blank=True, null=True)
    raw_mat_analysis = models.ForeignKey(LabAnalysisRawmaterialanalysisbasicinfo, models.DO_NOTHING, to_field='raw_mat_analysis_id')
    plant = models.ForeignKey('PlantPlant', models.DO_NOTHING, to_field='plant_id')

    class Meta:
        managed = False
        db_table = 'lab_analysis_rawmaterialanalysisvalue'


class LabAnalysisSpoutanalysisbasicinfo(models.Model):
    id = models.BigAutoField(primary_key=True)
    created_at = models.DateTimeField()
    modified_at = models.DateTimeField(blank=True, null=True)
    record_status = models.BooleanField()
    spout_analysis_dt = models.DateTimeField()
    reprise = models.CharField(max_length=2)
    source = models.CharField(max_length=20)
    comments = models.TextField(blank=True, null=True)
    spout_analysis_status = models.CharField(max_length=50)
    spout_analysis_id = models.CharField(unique=True, max_length=50)
    analytical_device_code = models.ForeignKey('UtilsMaster', models.DO_NOTHING, db_column='analytical_device_code', to_field='master_code', blank=True, null=True)
    created_by = models.ForeignKey('UsersUser', models.DO_NOTHING, to_field='username', blank=True, null=True)
    furnace_no = models.ForeignKey(FurnaceFurnaceconfig, models.DO_NOTHING, db_column='furnace_no', to_field='furnace_no')
    modified_by = models.ForeignKey('UsersUser', models.DO_NOTHING, to_field='username', related_name='labanalysisspoutanalysisbasicinfo_modified_by_set', blank=True, null=True)
    plant_shift_code = models.ForeignKey('UtilsMaster', models.DO_NOTHING, db_column='plant_shift_code', to_field='master_code', related_name='labanalysisspoutanalysisbasicinfo_plant_shift_code_set')
    plant = models.ForeignKey('PlantPlant', models.DO_NOTHING, to_field='plant_id')
    plant_furnace_code = models.CharField(max_length=10, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'lab_analysis_spoutanalysisbasicinfo'
        unique_together = (('furnace_no', 'spout_analysis_dt', 'reprise'),)


class LabAnalysisSpoutanalysischangehistory(models.Model):
    id = models.BigAutoField(primary_key=True)
    created_at = models.DateTimeField()
    modified_at = models.DateTimeField(blank=True, null=True)
    record_status = models.BooleanField()
    analysis_value = models.DecimalField(max_digits=10, decimal_places=4)
    created_by = models.ForeignKey('UsersUser', models.DO_NOTHING, to_field='username', blank=True, null=True)
    element_code = models.ForeignKey('MaterialMasterElement', models.DO_NOTHING, db_column='element_code', to_field='element_code')
    modified_by = models.ForeignKey('UsersUser', models.DO_NOTHING, to_field='username', related_name='labanalysisspoutanalysischangehistory_modified_by_set', blank=True, null=True)
    spout_analysis = models.ForeignKey(LabAnalysisSpoutanalysisbasicinfo, models.DO_NOTHING, to_field='spout_analysis_id')
    plant = models.ForeignKey('PlantPlant', models.DO_NOTHING, to_field='plant_id')

    class Meta:
        managed = False
        db_table = 'lab_analysis_spoutanalysischangehistory'


class LabAnalysisSpoutanalysischangelog(models.Model):
    id = models.BigAutoField(primary_key=True)
    created_at = models.DateTimeField()
    modified_at = models.DateTimeField(blank=True, null=True)
    record_status = models.BooleanField()
    change_log = models.JSONField()
    created_by = models.ForeignKey('UsersUser', models.DO_NOTHING, to_field='username', blank=True, null=True)
    modified_by = models.ForeignKey('UsersUser', models.DO_NOTHING, to_field='username', related_name='labanalysisspoutanalysischangelog_modified_by_set', blank=True, null=True)
    spout_analysis = models.ForeignKey(LabAnalysisSpoutanalysisbasicinfo, models.DO_NOTHING, to_field='spout_analysis_id')
    plant = models.ForeignKey('PlantPlant', models.DO_NOTHING, to_field='plant_id')

    class Meta:
        managed = False
        db_table = 'lab_analysis_spoutanalysischangelog'


class LabAnalysisSpoutanalysisvalue(models.Model):
    id = models.BigAutoField(primary_key=True)
    created_at = models.DateTimeField()
    modified_at = models.DateTimeField(blank=True, null=True)
    record_status = models.BooleanField()
    analysis_value = models.DecimalField(max_digits=10, decimal_places=4, blank=True, null=True)
    created_by = models.ForeignKey('UsersUser', models.DO_NOTHING, to_field='username', blank=True, null=True)
    element_code = models.ForeignKey('MaterialMasterElement', models.DO_NOTHING, db_column='element_code', to_field='element_code')
    modified_by = models.ForeignKey('UsersUser', models.DO_NOTHING, to_field='username', related_name='labanalysisspoutanalysisvalue_modified_by_set', blank=True, null=True)
    spout_analysis = models.ForeignKey(LabAnalysisSpoutanalysisbasicinfo, models.DO_NOTHING, to_field='spout_analysis_id')
    plant = models.ForeignKey('PlantPlant', models.DO_NOTHING, to_field='plant_id')

    class Meta:
        managed = False
        db_table = 'lab_analysis_spoutanalysisvalue'


class LabAnalysisTapanalysisbasicinfo(models.Model):
    id = models.BigAutoField(primary_key=True)
    created_at = models.DateTimeField()
    modified_at = models.DateTimeField(blank=True, null=True)
    record_status = models.BooleanField()
    tap_no = models.IntegerField()
    tap_analysis_dt = models.DateTimeField()
    reprise = models.CharField(max_length=50)
    source = models.CharField(max_length=20)
    comments = models.TextField(blank=True, null=True)
    tap_analysis_status = models.CharField(max_length=20)
    tap_analysis_id = models.CharField(unique=True, max_length=50)
    analytical_device_code = models.ForeignKey('UtilsMaster', models.DO_NOTHING, db_column='analytical_device_code', to_field='master_code', blank=True, null=True)
    created_by = models.ForeignKey('UsersUser', models.DO_NOTHING, to_field='username', blank=True, null=True)
    furnace_no = models.ForeignKey(FurnaceFurnaceconfig, models.DO_NOTHING, db_column='furnace_no', to_field='furnace_no')
    modified_by = models.ForeignKey('UsersUser', models.DO_NOTHING, to_field='username', related_name='labanalysistapanalysisbasicinfo_modified_by_set', blank=True, null=True)
    plant = models.ForeignKey('PlantPlant', models.DO_NOTHING, to_field='plant_id')
    plant_furnace_code = models.CharField(max_length=10, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'lab_analysis_tapanalysisbasicinfo'
        unique_together = (('furnace_no', 'tap_analysis_dt', 'tap_no', 'reprise'),)


class LabAnalysisTapanalysischangehistory(models.Model):
    id = models.BigAutoField(primary_key=True)
    created_at = models.DateTimeField()
    modified_at = models.DateTimeField(blank=True, null=True)
    record_status = models.BooleanField()
    analysis_value = models.DecimalField(max_digits=10, decimal_places=4)
    created_by = models.ForeignKey('UsersUser', models.DO_NOTHING, to_field='username', blank=True, null=True)
    element_code = models.ForeignKey('MaterialMasterElement', models.DO_NOTHING, db_column='element_code', to_field='element_code')
    modified_by = models.ForeignKey('UsersUser', models.DO_NOTHING, to_field='username', related_name='labanalysistapanalysischangehistory_modified_by_set', blank=True, null=True)
    tap_analysis = models.ForeignKey(LabAnalysisTapanalysisbasicinfo, models.DO_NOTHING, to_field='tap_analysis_id')
    plant = models.ForeignKey('PlantPlant', models.DO_NOTHING, to_field='plant_id')

    class Meta:
        managed = False
        db_table = 'lab_analysis_tapanalysischangehistory'


class LabAnalysisTapanalysischangelog(models.Model):
    id = models.BigAutoField(primary_key=True)
    created_at = models.DateTimeField()
    modified_at = models.DateTimeField(blank=True, null=True)
    record_status = models.BooleanField()
    change_log = models.JSONField()
    created_by = models.ForeignKey('UsersUser', models.DO_NOTHING, to_field='username', blank=True, null=True)
    modified_by = models.ForeignKey('UsersUser', models.DO_NOTHING, to_field='username', related_name='labanalysistapanalysischangelog_modified_by_set', blank=True, null=True)
    tap_analysis = models.ForeignKey(LabAnalysisTapanalysisbasicinfo, models.DO_NOTHING, to_field='tap_analysis_id')
    plant = models.ForeignKey('PlantPlant', models.DO_NOTHING, to_field='plant_id')

    class Meta:
        managed = False
        db_table = 'lab_analysis_tapanalysischangelog'


class LabAnalysisTapanalysisvalue(models.Model):
    id = models.BigAutoField(primary_key=True)
    created_at = models.DateTimeField()
    modified_at = models.DateTimeField(blank=True, null=True)
    record_status = models.BooleanField()
    analysis_value = models.DecimalField(max_digits=10, decimal_places=4, blank=True, null=True)
    created_by = models.ForeignKey('UsersUser', models.DO_NOTHING, to_field='username', blank=True, null=True)
    element_code = models.ForeignKey('MaterialMasterElement', models.DO_NOTHING, db_column='element_code', to_field='element_code')
    modified_by = models.ForeignKey('UsersUser', models.DO_NOTHING, to_field='username', related_name='labanalysistapanalysisvalue_modified_by_set', blank=True, null=True)
    tap_analysis = models.ForeignKey(LabAnalysisTapanalysisbasicinfo, models.DO_NOTHING, to_field='tap_analysis_id')
    plant = models.ForeignKey('PlantPlant', models.DO_NOTHING, to_field='plant_id')

    class Meta:
        managed = False
        db_table = 'lab_analysis_tapanalysisvalue'


class LogBookCategoryMaster(models.Model):
    id = models.BigAutoField(primary_key=True)
    category = models.CharField(max_length=100)
    log_name = models.CharField(max_length=100)
    category_code = models.CharField(unique=True, max_length=8)

    class Meta:
        managed = False
        db_table = 'log_book_category_master'


class LogBookDowntimeTypeMaster(models.Model):
    id = models.BigAutoField(primary_key=True)
    name = models.CharField(max_length=50)
    down_time_type_code = models.CharField(unique=True, max_length=8)

    class Meta:
        managed = False
        db_table = 'log_book_downtime_type_master'


class LogBookEquipmentMaster(models.Model):
    id = models.BigAutoField(primary_key=True)
    down_time_type = models.ForeignKey(LogBookDowntimeTypeMaster, models.DO_NOTHING, to_field='down_time_type_code')
    equipment = models.ForeignKey('LogBookEquipments', models.DO_NOTHING, to_field='equipment_code')

    class Meta:
        managed = False
        db_table = 'log_book_equipment_master'


class LogBookEquipments(models.Model):
    id = models.BigAutoField(primary_key=True)
    equipment_name = models.CharField(unique=True, max_length=50)
    equipment_code = models.CharField(unique=True, max_length=8)

    class Meta:
        managed = False
        db_table = 'log_book_equipments'
        unique_together = (('equipment_name', 'equipment_code'),)
        db_table_comment = 'This table holds the equipment  data'


class LogBookFurnaceBedLog(models.Model):
    id = models.BigAutoField(primary_key=True)
    created_at = models.DateTimeField()
    modified_at = models.DateTimeField(blank=True, null=True)
    record_status = models.BooleanField()
    observation_dt = models.DateTimeField()
    comments = models.TextField(blank=True, null=True)
    activity_homogeneity = models.ForeignKey('LogBookRadioMaster', models.DO_NOTHING, to_field='radio_code')
    auto_collapse = models.ForeignKey('LogBookRadioMaster', models.DO_NOTHING, to_field='radio_code', related_name='logbookfurnacebedlog_auto_collapse_set')
    bed_conditions = models.ForeignKey('LogBookRadioMaster', models.DO_NOTHING, to_field='radio_code', related_name='logbookfurnacebedlog_bed_conditions_set')
    created_by = models.ForeignKey('UsersUser', models.DO_NOTHING, to_field='username', blank=True, null=True)
    electrode_auto_lining_wideness = models.ForeignKey('LogBookRadioMaster', models.DO_NOTHING, to_field='radio_code', related_name='logbookfurnacebedlog_electrode_auto_lining_wideness_set')
    electrode_blows_direction = models.ForeignKey('LogBookRadioMaster', models.DO_NOTHING, to_field='radio_code', related_name='logbookfurnacebedlog_electrode_blows_direction_set')
    electrode_crust_formation = models.ForeignKey('LogBookRadioMaster', models.DO_NOTHING, to_field='radio_code', related_name='logbookfurnacebedlog_electrode_crust_formation_set')
    furnace = models.ForeignKey(FurnaceFurnaceconfig, models.DO_NOTHING, to_field='furnace_no')
    modified_by = models.ForeignKey('UsersUser', models.DO_NOTHING, to_field='username', related_name='logbookfurnacebedlog_modified_by_set', blank=True, null=True)
    noise_when_collapsing = models.ForeignKey('LogBookRadioMaster', models.DO_NOTHING, to_field='radio_code', related_name='logbookfurnacebedlog_noise_when_collapsing_set')
    plant = models.ForeignKey('PlantPlant', models.DO_NOTHING, to_field='plant_id')
    plant_furnace_code = models.CharField(max_length=10, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'log_book_furnace_bed_log'


class LogBookFurnaceDownTimeEvent(models.Model):
    id = models.BigAutoField(primary_key=True)
    created_at = models.DateTimeField()
    modified_at = models.DateTimeField(blank=True, null=True)
    record_status = models.BooleanField()
    observation_start_dt = models.DateTimeField()
    observation_end_dt = models.DateTimeField(blank=True, null=True)
    source = models.CharField(max_length=20)
    external_source_id = models.CharField(max_length=100, blank=True, null=True)
    event_status = models.BooleanField()
    comments = models.TextField(blank=True, null=True)
    created_by = models.ForeignKey('UsersUser', models.DO_NOTHING, to_field='username', blank=True, null=True)
    down_time_type = models.ForeignKey(LogBookDowntimeTypeMaster, models.DO_NOTHING, to_field='down_time_type_code')
    furnace = models.ForeignKey(FurnaceFurnaceconfig, models.DO_NOTHING, to_field='furnace_no')
    modified_by = models.ForeignKey('UsersUser', models.DO_NOTHING, to_field='username', related_name='logbookfurnacedowntimeevent_modified_by_set', blank=True, null=True)
    plant = models.ForeignKey('PlantPlant', models.DO_NOTHING, to_field='plant_id')
    plant_furnace_code = models.CharField(max_length=10, blank=True, null=True)
    equipment_code = models.ForeignKey(LogBookEquipments, models.DO_NOTHING, db_column='equipment_code', to_field='equipment_code')
    reason_code = models.ForeignKey('LogBookReasons', models.DO_NOTHING, db_column='reason_code', to_field='reason_code')

    class Meta:
        managed = False
        db_table = 'log_book_furnace_down_time_event'


class LogBookFurnaceDownTimeSplit(models.Model):
    id = models.BigAutoField(primary_key=True)
    created_at = models.DateTimeField()
    modified_at = models.DateTimeField(blank=True, null=True)
    record_status = models.BooleanField()
    observation_start_dt = models.DateTimeField()
    observation_end_dt = models.DateTimeField()
    comments = models.TextField(blank=True, null=True)
    created_by = models.ForeignKey('UsersUser', models.DO_NOTHING, to_field='username', blank=True, null=True)
    down_time_type = models.ForeignKey(LogBookDowntimeTypeMaster, models.DO_NOTHING, to_field='down_time_type_code')
    furnace_down_time_event = models.ForeignKey(LogBookFurnaceDownTimeEvent, models.DO_NOTHING)
    modified_by = models.ForeignKey('UsersUser', models.DO_NOTHING, to_field='username', related_name='logbookfurnacedowntimesplit_modified_by_set', blank=True, null=True)
    plant = models.ForeignKey('PlantPlant', models.DO_NOTHING, to_field='plant_id')
    equipment_code = models.ForeignKey(LogBookEquipments, models.DO_NOTHING, db_column='equipment_code', to_field='equipment_code')
    reason_code = models.ForeignKey('LogBookReasons', models.DO_NOTHING, db_column='reason_code', to_field='reason_code')

    class Meta:
        managed = False
        db_table = 'log_book_furnace_down_time_split'


class LogBookRadioMaster(models.Model):
    id = models.BigAutoField(primary_key=True)
    value = models.CharField(max_length=100)
    radio_code = models.CharField(unique=True, max_length=8)
    log_category_master = models.ForeignKey(LogBookCategoryMaster, models.DO_NOTHING, to_field='category_code')

    class Meta:
        managed = False
        db_table = 'log_book_radio_master'


class LogBookReasonMaster(models.Model):
    id = models.BigAutoField(primary_key=True)
    equipment = models.ForeignKey(LogBookEquipmentMaster, models.DO_NOTHING)
    reason = models.ForeignKey('LogBookReasons', models.DO_NOTHING, to_field='reason_code')

    class Meta:
        managed = False
        db_table = 'log_book_reason_master'


class LogBookReasons(models.Model):
    id = models.BigAutoField(primary_key=True)
    reason_name = models.CharField(unique=True, max_length=50)
    reason_code = models.CharField(unique=True, max_length=8)

    class Meta:
        managed = False
        db_table = 'log_book_reasons'
        unique_together = (('reason_name', 'reason_code'),)
        db_table_comment = 'This table holds the  reason data'


class LogBookTapHoleLog(models.Model):
    id = models.BigAutoField(primary_key=True)
    created_at = models.DateTimeField()
    modified_at = models.DateTimeField(blank=True, null=True)
    record_status = models.BooleanField()
    observation_dt = models.DateTimeField()
    comments = models.TextField(blank=True, null=True)
    created_by = models.ForeignKey('UsersUser', models.DO_NOTHING, to_field='username', blank=True, null=True)
    flame = models.ForeignKey(LogBookRadioMaster, models.DO_NOTHING, to_field='radio_code')
    flame_colour = models.ForeignKey(LogBookRadioMaster, models.DO_NOTHING, to_field='radio_code', related_name='logbooktapholelog_flame_colour_set')
    flame_intensity = models.ForeignKey(LogBookRadioMaster, models.DO_NOTHING, to_field='radio_code', related_name='logbooktapholelog_flame_intensity_set')
    furnace_tapping = models.ForeignKey(LogBookRadioMaster, models.DO_NOTHING, to_field='radio_code', related_name='logbooktapholelog_furnace_tapping_set')
    metal_output = models.ForeignKey(LogBookRadioMaster, models.DO_NOTHING, to_field='radio_code', related_name='logbooktapholelog_metal_output_set')
    modified_by = models.ForeignKey('UsersUser', models.DO_NOTHING, to_field='username', related_name='logbooktapholelog_modified_by_set', blank=True, null=True)
    slag = models.ForeignKey(LogBookRadioMaster, models.DO_NOTHING, to_field='radio_code', related_name='logbooktapholelog_slag_set')
    tap_hole_bottom = models.ForeignKey(LogBookRadioMaster, models.DO_NOTHING, to_field='radio_code', related_name='logbooktapholelog_tap_hole_bottom_set')
    tap_hole = models.ForeignKey(FurnaceConfigTapHole, models.DO_NOTHING, to_field='tap_hole_id')
    plant = models.ForeignKey('PlantPlant', models.DO_NOTHING, to_field='plant_id')

    class Meta:
        managed = False
        db_table = 'log_book_tap_hole_log'


class MaterialCategories(models.Model):
    name = models.CharField(unique=True, max_length=100)
    description = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'material_categories'


class MaterialMasterElement(models.Model):
    id = models.BigAutoField(primary_key=True)
    created_at = models.DateTimeField()
    modified_at = models.DateTimeField(blank=True, null=True)
    record_status = models.BooleanField()
    name = models.CharField(max_length=50)
    unit = models.CharField(max_length=8)
    element_code = models.CharField(unique=True, max_length=8)
    created_by = models.ForeignKey('UsersUser', models.DO_NOTHING, to_field='username', blank=True, null=True)
    modified_by = models.ForeignKey('UsersUser', models.DO_NOTHING, to_field='username', related_name='materialmasterelement_modified_by_set', blank=True, null=True)
    plant = models.ForeignKey('PlantPlant', models.DO_NOTHING, to_field='plant_id')

    class Meta:
        managed = False
        db_table = 'material_master_element'
        unique_together = (('name', 'unit'),)


class MaterialMasterElementgroup(models.Model):
    id = models.BigAutoField(primary_key=True)
    created_at = models.DateTimeField()
    modified_at = models.DateTimeField(blank=True, null=True)
    record_status = models.BooleanField()
    element_group = models.CharField(max_length=100)
    element_group_code = models.CharField(unique=True, max_length=8)
    created_by = models.ForeignKey('UsersUser', models.DO_NOTHING, to_field='username', blank=True, null=True)
    modified_by = models.ForeignKey('UsersUser', models.DO_NOTHING, to_field='username', related_name='materialmasterelementgroup_modified_by_set', blank=True, null=True)
    plant = models.ForeignKey('PlantPlant', models.DO_NOTHING, to_field='plant_id')

    class Meta:
        managed = False
        db_table = 'material_master_elementgroup'


class MaterialMasterElementspecification(models.Model):
    id = models.BigAutoField(primary_key=True)
    created_at = models.DateTimeField()
    modified_at = models.DateTimeField(blank=True, null=True)
    record_status = models.BooleanField()
    low = models.DecimalField(max_digits=10, decimal_places=4)
    aim = models.DecimalField(max_digits=10, decimal_places=4)
    high = models.DecimalField(max_digits=10, decimal_places=4)
    created_by = models.ForeignKey('UsersUser', models.DO_NOTHING, to_field='username', blank=True, null=True)
    element = models.ForeignKey(MaterialMasterElement, models.DO_NOTHING, to_field='element_code')
    material_master = models.ForeignKey('MaterialMasterMaterialmaster', models.DO_NOTHING, to_field='mes_mat_code')
    modified_by = models.ForeignKey('UsersUser', models.DO_NOTHING, to_field='username', related_name='materialmasterelementspecification_modified_by_set', blank=True, null=True)
    plant = models.ForeignKey('PlantPlant', models.DO_NOTHING, to_field='plant_id')
    plant_material_code = models.CharField(max_length=50, blank=True, null=True)
    control = models.BooleanField()
    warning_tolerance = models.DecimalField(max_digits=10, decimal_places=4, blank=True, null=True)
    is_wt_edited = models.BooleanField(blank=True, null=True, db_comment='Indicates if the warning tolerance has been edited')

    class Meta:
        managed = False
        db_table = 'material_master_elementspecification'


class MaterialMasterElementspecificationchangehistory(models.Model):
    id = models.BigAutoField(primary_key=True)
    created_at = models.DateTimeField()
    modified_at = models.DateTimeField(blank=True, null=True)
    record_status = models.BooleanField()
    low = models.DecimalField(max_digits=10, decimal_places=4)
    aim = models.DecimalField(max_digits=10, decimal_places=4)
    high = models.DecimalField(max_digits=10, decimal_places=4)
    created_by = models.ForeignKey('UsersUser', models.DO_NOTHING, to_field='username', blank=True, null=True)
    element = models.ForeignKey(MaterialMasterElement, models.DO_NOTHING, to_field='element_code')
    material_master = models.ForeignKey('MaterialMasterMaterialmaster', models.DO_NOTHING, to_field='mes_mat_code')
    modified_by = models.ForeignKey('UsersUser', models.DO_NOTHING, to_field='username', related_name='materialmasterelementspecificationchangehistory_modified_by_set', blank=True, null=True)
    plant = models.ForeignKey('PlantPlant', models.DO_NOTHING, to_field='plant_id')
    plant_material_code = models.CharField(max_length=50, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'material_master_elementspecificationchangehistory'
        db_table_comment = 'It holds the history of material master element specification modifications'


class MaterialMasterElementspecificationchangelog(models.Model):
    id = models.BigAutoField(primary_key=True)
    created_at = models.DateTimeField()
    modified_at = models.DateTimeField(blank=True, null=True)
    record_status = models.BooleanField()
    change_log = models.JSONField()
    created_by = models.ForeignKey('UsersUser', models.DO_NOTHING, to_field='username', blank=True, null=True)
    material_master = models.ForeignKey('MaterialMasterMaterialmaster', models.DO_NOTHING, to_field='mes_mat_code', blank=True, null=True)
    modified_by = models.ForeignKey('UsersUser', models.DO_NOTHING, to_field='username', related_name='materialmasterelementspecificationchangelog_modified_by_set', blank=True, null=True)
    plant = models.ForeignKey('PlantPlant', models.DO_NOTHING, to_field='plant_id')
    plant_material_code = models.CharField(max_length=50, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'material_master_elementspecificationchangelog'


class MaterialMasterGroupmaster(models.Model):
    id = models.BigAutoField(primary_key=True)
    created_at = models.DateTimeField()
    modified_at = models.DateTimeField(blank=True, null=True)
    record_status = models.BooleanField()
    group_id = models.CharField(unique=True, max_length=50)
    group_name = models.CharField(max_length=100)
    created_by = models.ForeignKey('UsersUser', models.DO_NOTHING, to_field='username', blank=True, null=True)
    modified_by = models.ForeignKey('UsersUser', models.DO_NOTHING, to_field='username', related_name='materialmastergroupmaster_modified_by_set', blank=True, null=True)
    plant = models.ForeignKey('PlantPlant', models.DO_NOTHING, to_field='plant_id')

    class Meta:
        managed = False
        db_table = 'material_master_groupmaster'


class MaterialMasterMaterialcategorymaster(models.Model):
    id = models.BigAutoField(primary_key=True)
    created_at = models.DateTimeField()
    modified_at = models.DateTimeField(blank=True, null=True)
    record_status = models.BooleanField()
    category_name = models.CharField(max_length=100)
    category_code = models.CharField(unique=True, max_length=8)
    created_by = models.ForeignKey('UsersUser', models.DO_NOTHING, to_field='username', blank=True, null=True)
    modified_by = models.ForeignKey('UsersUser', models.DO_NOTHING, to_field='username', related_name='materialmastermaterialcategorymaster_modified_by_set', blank=True, null=True)
    plant = models.ForeignKey('PlantPlant', models.DO_NOTHING, to_field='plant_id')

    class Meta:
        managed = False
        db_table = 'material_master_materialcategorymaster'


class MaterialMasterMaterialelementmaster(models.Model):
    id = models.BigAutoField(primary_key=True)
    created_at = models.DateTimeField()
    modified_at = models.DateTimeField(blank=True, null=True)
    record_status = models.BooleanField()
    created_by = models.ForeignKey('UsersUser', models.DO_NOTHING, to_field='username', blank=True, null=True)
    element = models.ForeignKey(MaterialMasterElement, models.DO_NOTHING, to_field='element_code')
    element_group = models.ForeignKey(MaterialMasterElementgroup, models.DO_NOTHING, to_field='element_group_code')
    modified_by = models.ForeignKey('UsersUser', models.DO_NOTHING, to_field='username', related_name='materialmastermaterialelementmaster_modified_by_set', blank=True, null=True)
    plant = models.ForeignKey('PlantPlant', models.DO_NOTHING, to_field='plant_id')

    class Meta:
        managed = False
        db_table = 'material_master_materialelementmaster'
        unique_together = (('element_group', 'element'),)


class MaterialMasterMaterialmaster(models.Model):
    id = models.BigAutoField(primary_key=True)
    created_at = models.DateTimeField()
    modified_at = models.DateTimeField(blank=True, null=True)
    record_status = models.BooleanField()
    mes_mat_code = models.CharField(unique=True, max_length=50)
    material_name = models.CharField(max_length=100)
    erp_commercial_mat_code = models.CharField(max_length=100)
    erp_commercial_mat_name = models.CharField(max_length=100)
    erp_acc_mat_code = models.CharField(max_length=100)
    erp_acc_mat_name = models.CharField(max_length=100)
    ops_tech_mat_code = models.CharField(max_length=100)
    consumption_flag = models.BooleanField()
    material_description = models.CharField(max_length=100, blank=True, null=True)
    created_by = models.ForeignKey('UsersUser', models.DO_NOTHING, to_field='username', blank=True, null=True)
    material_type = models.ForeignKey('MaterialMasterMaterialtypemaster', models.DO_NOTHING, to_field='type_code')
    modified_by = models.ForeignKey('UsersUser', models.DO_NOTHING, to_field='username', related_name='materialmastermaterialmaster_modified_by_set', blank=True, null=True)
    plant = models.ForeignKey('PlantPlant', models.DO_NOTHING, to_field='plant_id')
    plant_material_code = models.CharField(max_length=50, blank=True, null=True)
    ismaterialinfovalid = models.BooleanField(db_column='isMaterialInfoValid')  # Field name made lowercase.
    group = models.ForeignKey(MaterialMasterGroupmaster, models.DO_NOTHING, to_field='group_id', blank=True, null=True)
    client_id = models.CharField(max_length=50, blank=True, null=True)
    supplier_id = models.CharField(max_length=50, blank=True, null=True)
    group_id_legacy = models.CharField(db_column='Group ID', max_length=50, blank=True, null=True)  # Field name made lowercase. Field renamed to remove unsuitable characters.

    class Meta:
        managed = False
        db_table = 'material_master_materialmaster'


class MaterialMasterMaterialtypemaster(models.Model):
    id = models.BigAutoField(primary_key=True)
    created_at = models.DateTimeField()
    modified_at = models.DateTimeField(blank=True, null=True)
    record_status = models.BooleanField()
    type_name = models.CharField(max_length=100)
    type_code = models.CharField(unique=True, max_length=8)
    category = models.ForeignKey(MaterialMasterMaterialcategorymaster, models.DO_NOTHING, to_field='category_code')
    created_by = models.ForeignKey('UsersUser', models.DO_NOTHING, to_field='username', blank=True, null=True)
    modified_by = models.ForeignKey('UsersUser', models.DO_NOTHING, to_field='username', related_name='materialmastermaterialtypemaster_modified_by_set', blank=True, null=True)
    plant = models.ForeignKey('PlantPlant', models.DO_NOTHING, to_field='plant_id')

    class Meta:
        managed = False
        db_table = 'material_master_materialtypemaster'


class MaterialMasterSize(models.Model):
    id = models.BigAutoField(primary_key=True)
    created_at = models.DateTimeField()
    modified_at = models.DateTimeField(blank=True, null=True)
    record_status = models.BooleanField()
    below_tolerance = models.DecimalField(max_digits=7, decimal_places=4)
    above_tolerance = models.DecimalField(max_digits=7, decimal_places=4)
    created_by = models.ForeignKey('UsersUser', models.DO_NOTHING, to_field='username', blank=True, null=True)
    high_size = models.ForeignKey(MaterialMasterElement, models.DO_NOTHING, to_field='element_code', blank=True, null=True)
    low_size = models.ForeignKey(MaterialMasterElement, models.DO_NOTHING, to_field='element_code', related_name='materialmastersize_low_size_set', blank=True, null=True)
    material_master = models.ForeignKey(MaterialMasterMaterialmaster, models.DO_NOTHING, to_field='mes_mat_code', blank=True, null=True)
    modified_by = models.ForeignKey('UsersUser', models.DO_NOTHING, to_field='username', related_name='materialmastersize_modified_by_set', blank=True, null=True)
    plant = models.ForeignKey('PlantPlant', models.DO_NOTHING, to_field='plant_id')
    plant_material_code = models.CharField(max_length=50, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'material_master_size'


class MaterialMasterSizespecificationchangehistory(models.Model):
    id = models.BigAutoField(primary_key=True)
    created_at = models.DateTimeField()
    modified_at = models.DateTimeField(blank=True, null=True)
    record_status = models.BooleanField()
    below_tolerance = models.DecimalField(max_digits=5, decimal_places=2)
    above_tolerance = models.DecimalField(max_digits=5, decimal_places=2)
    created_by = models.ForeignKey('UsersUser', models.DO_NOTHING, to_field='username', blank=True, null=True)
    high_size = models.ForeignKey(MaterialMasterElement, models.DO_NOTHING, to_field='element_code', blank=True, null=True)
    low_size = models.ForeignKey(MaterialMasterElement, models.DO_NOTHING, to_field='element_code', related_name='materialmastersizespecificationchangehistory_low_size_set', blank=True, null=True)
    material_master = models.ForeignKey(MaterialMasterMaterialmaster, models.DO_NOTHING, to_field='mes_mat_code', blank=True, null=True)
    modified_by = models.ForeignKey('UsersUser', models.DO_NOTHING, to_field='username', related_name='materialmastersizespecificationchangehistory_modified_by_set', blank=True, null=True)
    plant = models.ForeignKey('PlantPlant', models.DO_NOTHING, to_field='plant_id')
    plant_material_code = models.CharField(max_length=50, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'material_master_sizespecificationchangehistory'
        db_table_comment = 'It holds the history of material master element size specification modifications'


class MaterialProperties(models.Model):
    material = models.OneToOneField('Materials', models.DO_NOTHING, blank=True, null=True)
    ultimate_tensile_strength = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    yield_strength = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    elastic_modulus = models.DecimalField(max_digits=12, decimal_places=2, blank=True, null=True)
    shear_modulus = models.DecimalField(max_digits=12, decimal_places=2, blank=True, null=True)
    poisson_ratio = models.DecimalField(max_digits=4, decimal_places=3, blank=True, null=True)
    density = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    brinell_hardness = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    vickers_hardness = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    surface_hardness = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    elongation = models.DecimalField(max_digits=6, decimal_places=2, blank=True, null=True)
    created_at = models.DateTimeField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'material_properties'


class MaterialStandards(models.Model):
    code = models.CharField(unique=True, max_length=10)
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'material_standards'


class Materials(models.Model):
    material_id = models.CharField(unique=True, max_length=50, blank=True, null=True)
    standard = models.ForeignKey(MaterialStandards, models.DO_NOTHING, blank=True, null=True)
    category = models.ForeignKey(MaterialCategories, models.DO_NOTHING, blank=True, null=True)
    name = models.CharField(max_length=200)
    grade = models.CharField(max_length=100, blank=True, null=True)
    heat_treatment = models.ForeignKey(HeatTreatments, models.DO_NOTHING, blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    is_stainless = models.BooleanField(blank=True, null=True)
    is_in_use = models.BooleanField(blank=True, null=True)
    created_at = models.DateTimeField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'materials'


class PlantConfigParameters(models.Model):
    id = models.BigAutoField(primary_key=True)
    created_at = models.DateTimeField()
    modified_at = models.DateTimeField(blank=True, null=True)
    record_status = models.BooleanField()
    effective_date = models.DateField()
    energy_price = models.DecimalField(max_digits=10, decimal_places=2)
    created_by = models.ForeignKey('UsersUser', models.DO_NOTHING, to_field='username', blank=True, null=True)
    modified_by = models.ForeignKey('UsersUser', models.DO_NOTHING, to_field='username', related_name='plantconfigparameters_modified_by_set', blank=True, null=True)
    plant_config = models.ForeignKey('PlantPlantconfig', models.DO_NOTHING)
    plant = models.ForeignKey('PlantPlant', models.DO_NOTHING, to_field='plant_id')

    class Meta:
        managed = False
        db_table = 'plant_config_parameters'
        unique_together = (('plant_config', 'effective_date'),)
        db_table_comment = 'It holds the Plant config  parameters'


class PlantConfigProduct(models.Model):
    id = models.BigAutoField(primary_key=True)
    created_at = models.DateTimeField()
    modified_at = models.DateTimeField(blank=True, null=True)
    record_status = models.BooleanField()
    created_by = models.ForeignKey('UsersUser', models.DO_NOTHING, to_field='username', blank=True, null=True)
    modified_by = models.ForeignKey('UsersUser', models.DO_NOTHING, to_field='username', related_name='plantconfigproduct_modified_by_set', blank=True, null=True)
    plant_config = models.ForeignKey('PlantPlantconfig', models.DO_NOTHING)
    product = models.ForeignKey('UtilsMaster', models.DO_NOTHING, to_field='master_code')
    plant = models.ForeignKey('PlantPlant', models.DO_NOTHING, to_field='plant_id')

    class Meta:
        managed = False
        db_table = 'plant_config_product'


class PlantConfigWorkshop(models.Model):
    id = models.BigAutoField(primary_key=True)
    created_at = models.DateTimeField()
    modified_at = models.DateTimeField(blank=True, null=True)
    record_status = models.BooleanField()
    workshop_name = models.CharField(max_length=500)
    created_by = models.ForeignKey('UsersUser', models.DO_NOTHING, to_field='username', blank=True, null=True)
    modified_by = models.ForeignKey('UsersUser', models.DO_NOTHING, to_field='username', related_name='plantconfigworkshop_modified_by_set', blank=True, null=True)
    plant_config = models.ForeignKey('PlantPlantconfig', models.DO_NOTHING)
    plant = models.ForeignKey('PlantPlant', models.DO_NOTHING, to_field='plant_id')

    class Meta:
        managed = False
        db_table = 'plant_config_workshop'


class PlantPlant(models.Model):
    id = models.BigAutoField(primary_key=True)
    created_at = models.DateTimeField()
    modified_at = models.DateTimeField()
    record_status = models.BooleanField()
    plant_name = models.CharField(max_length=100)
    plant_id = models.CharField(unique=True, max_length=20)
    area_code = models.CharField(max_length=20)
    created_by = models.ForeignKey('UsersUser', models.DO_NOTHING, to_field='username', blank=True, null=True)
    modified_by = models.ForeignKey('UsersUser', models.DO_NOTHING, to_field='username', related_name='plantplant_modified_by_set', blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'plant_plant'


class PlantPlantconfig(models.Model):
    id = models.BigAutoField(primary_key=True)
    created_at = models.DateTimeField()
    modified_at = models.DateTimeField(blank=True, null=True)
    record_status = models.BooleanField()
    plant_name = models.CharField(max_length=100)
    area_code = models.CharField(max_length=100)
    plant_address = models.CharField(max_length=100)
    shift1_from = models.CharField(max_length=100)
    shift1_to = models.CharField(max_length=100)
    shift2_from = models.CharField(max_length=100)
    shift2_to = models.CharField(max_length=100)
    shift3_from = models.CharField(max_length=100)
    shift3_to = models.CharField(max_length=100)
    created_by = models.ForeignKey('UsersUser', models.DO_NOTHING, to_field='username', blank=True, null=True)
    currency = models.ForeignKey('UtilsMaster', models.DO_NOTHING, to_field='master_code')
    language = models.ForeignKey('UtilsMaster', models.DO_NOTHING, to_field='master_code', related_name='plantplantconfig_language_set')
    modified_by = models.ForeignKey('UsersUser', models.DO_NOTHING, to_field='username', related_name='plantplantconfig_modified_by_set', blank=True, null=True)
    timezone = models.ForeignKey('UtilsMaster', models.DO_NOTHING, to_field='master_code', related_name='plantplantconfig_timezone_set')
    unit = models.ForeignKey('UtilsMaster', models.DO_NOTHING, to_field='master_code', related_name='plantplantconfig_unit_set')
    plant = models.ForeignKey(PlantPlant, models.DO_NOTHING, to_field='plant_id')

    class Meta:
        managed = False
        db_table = 'plant_plantconfig'


class PlantPlantconfigfunction(models.Model):
    id = models.BigAutoField(primary_key=True)
    created_at = models.DateTimeField()
    modified_at = models.DateTimeField(blank=True, null=True)
    record_status = models.BooleanField()
    created_by = models.ForeignKey('UsersUser', models.DO_NOTHING, to_field='username', blank=True, null=True)
    function = models.ForeignKey('UtilsFunction', models.DO_NOTHING, to_field='function_code')
    modified_by = models.ForeignKey('UsersUser', models.DO_NOTHING, to_field='username', related_name='plantplantconfigfunction_modified_by_set', blank=True, null=True)
    module = models.ForeignKey('UtilsModule', models.DO_NOTHING, to_field='module_code')
    plant_config = models.ForeignKey(PlantPlantconfig, models.DO_NOTHING)
    plant = models.ForeignKey(PlantPlant, models.DO_NOTHING, to_field='plant_id')

    class Meta:
        managed = False
        db_table = 'plant_plantconfigfunction'
        unique_together = (('module', 'function'),)


class ProductsAdditionalinformation(models.Model):
    id = models.BigAutoField(primary_key=True)
    created_at = models.DateTimeField()
    modified_at = models.DateTimeField(blank=True, null=True)
    record_status = models.BooleanField()
    unit_weight = models.DecimalField(max_digits=10, decimal_places=2)
    actual_cost = models.DecimalField(max_digits=10, decimal_places=2)
    density = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    standard_cost = models.DecimalField(max_digits=10, decimal_places=2)
    effective_date = models.DateField()
    plant_material_code = models.CharField(max_length=50, blank=True, null=True)
    created_by = models.ForeignKey('UsersUser', models.DO_NOTHING, to_field='username', blank=True, null=True)
    material_master = models.ForeignKey(MaterialMasterMaterialmaster, models.DO_NOTHING, to_field='mes_mat_code')
    modified_by = models.ForeignKey('UsersUser', models.DO_NOTHING, to_field='username', related_name='productsadditionalinformation_modified_by_set', blank=True, null=True)
    plant = models.ForeignKey(PlantPlant, models.DO_NOTHING, to_field='plant_id')

    class Meta:
        managed = False
        db_table = 'products_additionalinformation'
        unique_together = (('material_master', 'effective_date'),)


class ReportsBaseanalysisreport(models.Model):
    id = models.BigAutoField(primary_key=True)
    year = models.CharField(max_length=100, blank=True, null=True)
    date = models.DateField(blank=True, null=True)
    time = models.TimeField(blank=True, null=True)
    date_timestamp = models.DateTimeField(blank=True, null=True)
    element_value = models.DecimalField(max_digits=12, decimal_places=4, blank=True, null=True)
    element = models.ForeignKey(MaterialMasterElement, models.DO_NOTHING, to_field='element_code')
    mes_mat_code = models.ForeignKey(MaterialMasterMaterialmaster, models.DO_NOTHING, db_column='mes_mat_code', to_field='mes_mat_code')
    plant = models.ForeignKey(PlantPlant, models.DO_NOTHING, to_field='plant_id')
    plant_material_code = models.CharField(max_length=50, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'reports_baseanalysisreport'


class ReportsBaseconsumptionreport(models.Model):
    id = models.BigAutoField(primary_key=True)
    source_id = models.CharField(max_length=100, blank=True, null=True)
    bin_id = models.BigIntegerField(blank=True, null=True)
    date = models.DateField(blank=True, null=True)
    time = models.TimeField(blank=True, null=True)
    date_timestamp = models.DateTimeField(blank=True, null=True)
    cons_type = models.IntegerField(blank=True, null=True)
    cons_poste = models.IntegerField(blank=True, null=True)
    dry_quantity = models.DecimalField(max_digits=10, decimal_places=4, blank=True, null=True)
    humidity_quantity = models.DecimalField(max_digits=10, decimal_places=4, blank=True, null=True)
    furnace_master = models.ForeignKey(FurnaceFurnaceconfig, models.DO_NOTHING, to_field='furnace_no')
    material_type = models.ForeignKey(MaterialMasterMaterialtypemaster, models.DO_NOTHING, to_field='type_code')
    mes_mat_code = models.ForeignKey(MaterialMasterMaterialmaster, models.DO_NOTHING, db_column='mes_mat_code', to_field='mes_mat_code')
    cp_code = models.CharField(max_length=3, blank=True, null=True)
    status_code = models.CharField(max_length=1, blank=True, null=True)
    plant = models.ForeignKey(PlantPlant, models.DO_NOTHING, to_field='plant_id')
    plant_furnace_code = models.CharField(max_length=10, blank=True, null=True)
    plant_material_code = models.CharField(max_length=50, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'reports_baseconsumptionreport'


class ReportsFiltersMaster(models.Model):
    id = models.BigAutoField(primary_key=True)
    created_at = models.DateTimeField()
    modified_at = models.DateTimeField(blank=True, null=True)
    record_status = models.BooleanField()
    filter_name = models.CharField(max_length=100)
    filter_type = models.CharField(max_length=10)
    is_active = models.BooleanField()
    created_by = models.ForeignKey('UsersUser', models.DO_NOTHING, to_field='username', blank=True, null=True)
    group_code = models.ForeignKey('ReportsGroupsMaster', models.DO_NOTHING, db_column='group_code', to_field='group_code')
    modified_by = models.ForeignKey('UsersUser', models.DO_NOTHING, to_field='username', related_name='reportsfiltersmaster_modified_by_set', blank=True, null=True)
    plant = models.ForeignKey(PlantPlant, models.DO_NOTHING, to_field='plant_id')
    report_code = models.ForeignKey('ReportsMaster', models.DO_NOTHING, db_column='report_code', to_field='report_code')
    is_required = models.BooleanField()

    class Meta:
        managed = False
        db_table = 'reports_filters_master'
        unique_together = (('filter_name', 'report_code', 'group_code'),)
        db_table_comment = 'It holds the Report Filters'


class ReportsGroupsMaster(models.Model):
    id = models.BigAutoField(primary_key=True)
    created_at = models.DateTimeField()
    modified_at = models.DateTimeField(blank=True, null=True)
    record_status = models.BooleanField()
    group_name = models.CharField(unique=True, max_length=100)
    group_code = models.CharField(unique=True, max_length=8)
    created_by = models.ForeignKey('UsersUser', models.DO_NOTHING, to_field='username', blank=True, null=True)
    modified_by = models.ForeignKey('UsersUser', models.DO_NOTHING, to_field='username', related_name='reportsgroupsmaster_modified_by_set', blank=True, null=True)
    plant = models.ForeignKey(PlantPlant, models.DO_NOTHING, to_field='plant_id')

    class Meta:
        managed = False
        db_table = 'reports_groups_master'
        db_table_comment = 'It holds the Report Groups'


class ReportsMaster(models.Model):
    id = models.BigAutoField(primary_key=True)
    created_at = models.DateTimeField()
    modified_at = models.DateTimeField(blank=True, null=True)
    record_status = models.BooleanField()
    report_name = models.CharField(unique=True, max_length=100)
    report_code = models.CharField(unique=True, max_length=8)
    description = models.TextField(blank=True, null=True)
    is_active = models.BooleanField()
    created_by = models.ForeignKey('UsersUser', models.DO_NOTHING, to_field='username', blank=True, null=True)
    group_code = models.ForeignKey(ReportsGroupsMaster, models.DO_NOTHING, db_column='group_code', to_field='group_code')
    modified_by = models.ForeignKey('UsersUser', models.DO_NOTHING, to_field='username', related_name='reportsmaster_modified_by_set', blank=True, null=True)
    plant = models.ForeignKey(PlantPlant, models.DO_NOTHING, to_field='plant_id')
    default_columns = models.JSONField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'reports_master'
        unique_together = (('report_code', 'group_code'),)
        db_table_comment = 'It holds the Reports'


class ReportsVariantFilters(models.Model):
    id = models.BigAutoField(primary_key=True)
    created_at = models.DateTimeField()
    modified_at = models.DateTimeField(blank=True, null=True)
    record_status = models.BooleanField()
    filter_key = models.CharField(max_length=100)
    filter_value = models.JSONField()
    created_by = models.ForeignKey('UsersUser', models.DO_NOTHING, to_field='username', blank=True, null=True)
    modified_by = models.ForeignKey('UsersUser', models.DO_NOTHING, to_field='username', related_name='reportsvariantfilters_modified_by_set', blank=True, null=True)
    plant = models.ForeignKey(PlantPlant, models.DO_NOTHING, to_field='plant_id')
    variant = models.ForeignKey('ReportsVariants', models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'reports_variant_filters'
        db_table_comment = 'Stores dynamic filters for report variants'


class ReportsVariants(models.Model):
    id = models.BigAutoField(primary_key=True)
    created_at = models.DateTimeField()
    modified_at = models.DateTimeField(blank=True, null=True)
    name = models.CharField(max_length=100)
    record_status = models.BooleanField()
    is_public = models.BooleanField()
    columns = models.JSONField()
    created_by = models.ForeignKey('UsersUser', models.DO_NOTHING, to_field='username', blank=True, null=True)
    modified_by = models.ForeignKey('UsersUser', models.DO_NOTHING, to_field='username', related_name='reportsvariants_modified_by_set', blank=True, null=True)
    plant = models.ForeignKey(PlantPlant, models.DO_NOTHING, to_field='plant_id')
    report_code = models.ForeignKey(ReportsMaster, models.DO_NOTHING, db_column='report_code', to_field='report_code')
    group_code = models.ForeignKey(ReportsGroupsMaster, models.DO_NOTHING, db_column='group_code', to_field='group_code')
    kpis = models.JSONField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'reports_variants'
        db_table_comment = 'Stores saved report configurations'


class UserAssociatedPlant(models.Model):
    id = models.BigAutoField(primary_key=True)
    associated_plant = models.ForeignKey(PlantPlant, models.DO_NOTHING, to_field='plant_id')
    username = models.ForeignKey('UsersUser', models.DO_NOTHING, db_column='username', to_field='username')

    class Meta:
        managed = False
        db_table = 'user_associated_plant'
        unique_together = (('username', 'associated_plant'),)
        db_table_comment = 'It holds the Plant config  parameters'


class UserSession(models.Model):
    id = models.BigAutoField(primary_key=True)
    session_data = models.JSONField()
    record_status = models.BooleanField()
    created_at = models.DateTimeField()
    updated_at = models.DateTimeField()
    user = models.OneToOneField('UsersUser', models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'user_session'


class UsersKpiGroupsMaster(models.Model):
    id = models.BigAutoField(primary_key=True)
    created_at = models.DateTimeField()
    modified_at = models.DateTimeField(blank=True, null=True)
    record_status = models.BooleanField()
    group_name = models.CharField(unique=True, max_length=100)
    group_code = models.CharField(unique=True, max_length=8)
    created_by = models.ForeignKey('UsersUser', models.DO_NOTHING, to_field='username', blank=True, null=True)
    modified_by = models.ForeignKey('UsersUser', models.DO_NOTHING, to_field='username', related_name='userskpigroupsmaster_modified_by_set', blank=True, null=True)
    plant = models.ForeignKey(PlantPlant, models.DO_NOTHING, to_field='plant_id')

    class Meta:
        managed = False
        db_table = 'users_kpi_groups_master'
        db_table_comment = 'It holds the KPI Groups'


class UsersKpiMetricMaster(models.Model):
    id = models.BigAutoField(primary_key=True)
    created_at = models.DateTimeField()
    modified_at = models.DateTimeField(blank=True, null=True)
    record_status = models.BooleanField()
    kpi_metric_name = models.CharField(unique=True, max_length=100)
    kpi_metric_code = models.CharField(unique=True, max_length=8)
    created_by = models.ForeignKey('UsersUser', models.DO_NOTHING, to_field='username', blank=True, null=True)
    group_code = models.ForeignKey(UsersKpiGroupsMaster, models.DO_NOTHING, db_column='group_code', to_field='group_code')
    modified_by = models.ForeignKey('UsersUser', models.DO_NOTHING, to_field='username', related_name='userskpimetricmaster_modified_by_set', blank=True, null=True)
    plant = models.ForeignKey(PlantPlant, models.DO_NOTHING, to_field='plant_id')

    class Meta:
        managed = False
        db_table = 'users_kpi_metric_master'
        unique_together = (('kpi_metric_code', 'group_code'),)
        db_table_comment = 'It holds the KPIs'


class UsersRole(models.Model):
    id = models.BigAutoField(primary_key=True)
    created_at = models.DateTimeField()
    modified_at = models.DateTimeField(blank=True, null=True)
    record_status = models.BooleanField()
    role_name = models.CharField(max_length=255)
    is_delete = models.BooleanField()
    is_superuser = models.BooleanField()
    created_by = models.ForeignKey('UsersUser', models.DO_NOTHING, to_field='username', blank=True, null=True)
    modified_by = models.ForeignKey('UsersUser', models.DO_NOTHING, to_field='username', related_name='usersrole_modified_by_set', blank=True, null=True)
    plant = models.ForeignKey(PlantPlant, models.DO_NOTHING, to_field='plant_id')

    class Meta:
        managed = False
        db_table = 'users_role'
        unique_together = (('role_name', 'plant'),)


class UsersRoleKpis(models.Model):
    id = models.BigAutoField(primary_key=True)
    created_at = models.DateTimeField()
    modified_at = models.DateTimeField(blank=True, null=True)
    record_status = models.BooleanField()
    created_by = models.ForeignKey('UsersUser', models.DO_NOTHING, to_field='username', blank=True, null=True)
    kpi_metric_code = models.ForeignKey(UsersKpiMetricMaster, models.DO_NOTHING, db_column='kpi_metric_code', to_field='kpi_metric_code')
    modified_by = models.ForeignKey('UsersUser', models.DO_NOTHING, to_field='username', related_name='usersrolekpis_modified_by_set', blank=True, null=True)
    plant = models.ForeignKey(PlantPlant, models.DO_NOTHING, to_field='plant_id')
    role = models.ForeignKey(UsersRole, models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'users_role_kpis'
        unique_together = (('role', 'kpi_metric_code'),)
        db_table_comment = 'It holds the Role KPIs'


class UsersRolepermission(models.Model):
    id = models.BigAutoField(primary_key=True)
    created_at = models.DateTimeField()
    modified_at = models.DateTimeField(blank=True, null=True)
    record_status = models.BooleanField()
    create = models.BooleanField()
    view = models.BooleanField()
    edit = models.BooleanField()
    delete = models.BooleanField()
    created_by = models.ForeignKey('UsersUser', models.DO_NOTHING, to_field='username', blank=True, null=True)
    function_master = models.ForeignKey('UtilsFunction', models.DO_NOTHING, to_field='function_code')
    modified_by = models.ForeignKey('UsersUser', models.DO_NOTHING, to_field='username', related_name='usersrolepermission_modified_by_set', blank=True, null=True)
    role = models.ForeignKey(UsersRole, models.DO_NOTHING)
    plant = models.ForeignKey(PlantPlant, models.DO_NOTHING, to_field='plant_id')

    class Meta:
        managed = False
        db_table = 'users_rolepermission'
        unique_together = (('role', 'function_master'),)


class UsersUser(models.Model):
    id = models.BigAutoField(primary_key=True)
    password = models.CharField(max_length=128)
    last_login = models.DateTimeField(blank=True, null=True)
    created_at = models.DateTimeField()
    modified_at = models.DateTimeField(blank=True, null=True)
    record_status = models.BooleanField()
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    phone = models.CharField(max_length=20, blank=True, null=True)
    email = models.CharField(max_length=254, blank=True, null=True)
    department = models.CharField(max_length=50, blank=True, null=True)
    login_type = models.CharField(max_length=50)
    username = models.CharField(unique=True, max_length=50)
    is_delete = models.BooleanField()
    is_superuser = models.BooleanField()
    created_by = models.ForeignKey('self', models.DO_NOTHING, to_field='username', blank=True, null=True)
    modified_by = models.ForeignKey('self', models.DO_NOTHING, to_field='username', related_name='usersuser_modified_by_set', blank=True, null=True)
    plant = models.ForeignKey(PlantPlant, models.DO_NOTHING, to_field='plant_id')
    is_staff = models.BooleanField()

    class Meta:
        managed = False
        db_table = 'users_user'


class UsersUserrole(models.Model):
    id = models.BigAutoField(primary_key=True)
    date_assigned = models.DateTimeField()
    role = models.ForeignKey(UsersRole, models.DO_NOTHING)
    user = models.ForeignKey(UsersUser, models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'users_userrole'
        unique_together = (('user', 'role'),)


class UsersUsertoken(models.Model):
    id = models.BigAutoField(primary_key=True)
    token = models.TextField(blank=True, null=True)
    user = models.OneToOneField(UsersUser, models.DO_NOTHING)
    plant = models.ForeignKey(PlantPlant, models.DO_NOTHING, to_field='plant_id')

    class Meta:
        managed = False
        db_table = 'users_usertoken'


class UtilsFunction(models.Model):
    id = models.BigAutoField(primary_key=True)
    function_name = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    record_status = models.BooleanField()
    function_code = models.CharField(unique=True, max_length=8)
    sort_order = models.SmallIntegerField()
    module = models.ForeignKey('UtilsModule', models.DO_NOTHING, to_field='module_code')
    menu_level = models.IntegerField()
    parent = models.ForeignKey('self', models.DO_NOTHING, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'utils_function'


class UtilsGlobalunit(models.Model):
    id = models.BigAutoField(primary_key=True)
    name = models.CharField(max_length=50)
    imperial = models.CharField(max_length=10)
    metric = models.CharField(max_length=10)

    class Meta:
        managed = False
        db_table = 'utils_globalunit'


class UtilsMaster(models.Model):
    id = models.BigAutoField(primary_key=True)
    category = models.CharField(max_length=100)
    value = models.CharField(max_length=100)
    description = models.TextField()
    master_code = models.CharField(unique=True, max_length=8)

    class Meta:
        managed = False
        db_table = 'utils_master'


class UtilsModule(models.Model):
    id = models.BigAutoField(primary_key=True)
    module_name = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    module_code = models.CharField(unique=True, max_length=8)
    sort_order = models.IntegerField(unique=True)

    class Meta:
        managed = False
        db_table = 'utils_module'


class UtilsVariant(models.Model):
    id = models.BigAutoField(primary_key=True)
    created_at = models.DateTimeField()
    modified_at = models.DateTimeField(blank=True, null=True)
    record_status = models.BooleanField()
    furnace_flag = models.BooleanField()
    size_flag = models.BooleanField()
    variant_name = models.CharField(max_length=50, blank=True, null=True)
    private = models.BooleanField()
    report_json = models.JSONField()
    created_by = models.ForeignKey(UsersUser, models.DO_NOTHING, to_field='username', blank=True, null=True)
    furnace = models.ForeignKey(FurnaceFurnaceconfig, models.DO_NOTHING, to_field='furnace_no', blank=True, null=True)
    modified_by = models.ForeignKey(UsersUser, models.DO_NOTHING, to_field='username', related_name='utilsvariant_modified_by_set', blank=True, null=True)
    user = models.ForeignKey(UsersUser, models.DO_NOTHING, related_name='utilsvariant_user_set', blank=True, null=True)
    plant = models.ForeignKey(PlantPlant, models.DO_NOTHING, to_field='plant_id')
    plant_furnace_code = models.CharField(max_length=10, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'utils_variant'


class WipAdditionalinformation(models.Model):
    id = models.BigAutoField(primary_key=True)
    created_at = models.DateTimeField()
    modified_at = models.DateTimeField(blank=True, null=True)
    record_status = models.BooleanField()
    density = models.DecimalField(max_digits=10, decimal_places=2)
    effective_date = models.DateField()
    created_by = models.ForeignKey(UsersUser, models.DO_NOTHING, to_field='username', blank=True, null=True)
    material_master = models.ForeignKey(MaterialMasterMaterialmaster, models.DO_NOTHING, to_field='mes_mat_code')
    modified_by = models.ForeignKey(UsersUser, models.DO_NOTHING, to_field='username', related_name='wipadditionalinformation_modified_by_set', blank=True, null=True)
    plant = models.ForeignKey(PlantPlant, models.DO_NOTHING, to_field='plant_id')
    plant_material_code = models.CharField(max_length=50, blank=True, null=True)
    actual_cost = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    standard_cost = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    unit_weight = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'wip_additionalinformation'
        unique_together = (('material_master', 'effective_date'),)
