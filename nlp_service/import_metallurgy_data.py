"""
Metallurgy Data Importer
Imports metallurgy and industrial materials data from CSV files into PostgreSQL.
"""
import os
import sys
import csv
import argparse
import psycopg2
from psycopg2 import sql
from typing import List, Dict, Any
import logging

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from config import settings

# Parse command-line arguments
def parse_args():
    parser = argparse.ArgumentParser(description='Import metallurgy data into PostgreSQL')
    parser.add_argument('--host', default=settings.db_host, help='Database host')
    parser.add_argument('--port', type=int, default=settings.db_port, help='Database port')
    parser.add_argument('--dbname', default=settings.db_name, help='Database name')
    parser.add_argument('--user', default=settings.db_user, help='Database user')
    parser.add_argument('--password', default=settings.db_password, help='Database password')
    return parser.parse_args()

args = parse_args()

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Database connection settings (can be overridden via command line)
DB_CONNECTION = {
    'host': args.host,
    'port': args.port,
    'dbname': args.dbname,
    'user': args.user,
    'password': args.password
}

# DDL for creating metallurgy tables
CREATE_TABLES_SQL = """
-- Drop existing tables if they exist (for re-import)
DROP TABLE IF EXISTS material_properties CASCADE;
DROP TABLE IF EXISTS materials CASCADE;
DROP TABLE IF EXISTS material_standards CASCADE;
DROP TABLE IF EXISTS material_categories CASCADE;
DROP TABLE IF EXISTS heat_treatments CASCADE;

-- Material Standards (ANSI, ISO, DIN)
CREATE TABLE material_standards (
    id SERIAL PRIMARY KEY,
    code VARCHAR(10) UNIQUE NOT NULL,
    name VARCHAR(100) NOT NULL,
    description TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Material Categories (Steel, Aluminum, Copper, etc.)
CREATE TABLE material_categories (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) UNIQUE NOT NULL,
    description TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Heat Treatments
CREATE TABLE heat_treatments (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) UNIQUE NOT NULL,
    description TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Main Materials Table
CREATE TABLE materials (
    id SERIAL PRIMARY KEY,
    material_id VARCHAR(50) UNIQUE,
    standard_id INTEGER REFERENCES material_standards(id),
    category_id INTEGER REFERENCES material_categories(id),
    name VARCHAR(200) NOT NULL,
    grade VARCHAR(100),
    heat_treatment_id INTEGER REFERENCES heat_treatments(id),
    description TEXT,
    is_stainless BOOLEAN DEFAULT FALSE,
    is_in_use BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Material Mechanical Properties
CREATE TABLE material_properties (
    id SERIAL PRIMARY KEY,
    material_id INTEGER REFERENCES materials(id) ON DELETE CASCADE,
    -- Strength Properties (MPa)
    ultimate_tensile_strength NUMERIC(10,2),  -- Su
    yield_strength NUMERIC(10,2),              -- Sy
    -- Elastic Properties (MPa)
    elastic_modulus NUMERIC(12,2),             -- E (Young's Modulus)
    shear_modulus NUMERIC(12,2),               -- G
    poisson_ratio NUMERIC(4,3),                -- mu (ν)
    -- Physical Properties
    density NUMERIC(10,2),                     -- Ro (kg/m³)
    -- Hardness
    brinell_hardness NUMERIC(10,2),           -- Bhn
    vickers_hardness NUMERIC(10,2),           -- HV
    surface_hardness NUMERIC(10,2),           -- pH
    -- Other
    elongation NUMERIC(6,2),                   -- A5 (%)
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(material_id)
);

-- Create indexes for faster queries
CREATE INDEX idx_materials_name ON materials(name);
CREATE INDEX idx_materials_grade ON materials(grade);
CREATE INDEX idx_materials_standard ON materials(standard_id);
CREATE INDEX idx_materials_category ON materials(category_id);
CREATE INDEX idx_properties_strength ON material_properties(ultimate_tensile_strength, yield_strength);
CREATE INDEX idx_properties_hardness ON material_properties(brinell_hardness);

-- Create a view for easy querying
CREATE OR REPLACE VIEW material_full_info AS
SELECT 
    m.id,
    m.material_id,
    ms.code as standard,
    mc.name as category,
    m.name as material_name,
    m.grade,
    ht.name as heat_treatment,
    mp.ultimate_tensile_strength as tensile_strength_mpa,
    mp.yield_strength as yield_strength_mpa,
    mp.elastic_modulus as elastic_modulus_mpa,
    mp.shear_modulus as shear_modulus_mpa,
    mp.poisson_ratio,
    mp.density as density_kg_m3,
    mp.brinell_hardness as bhn,
    mp.vickers_hardness as hv,
    mp.elongation as elongation_percent,
    m.is_stainless,
    m.is_in_use,
    m.description
FROM materials m
LEFT JOIN material_standards ms ON m.standard_id = ms.id
LEFT JOIN material_categories mc ON m.category_id = mc.id
LEFT JOIN heat_treatments ht ON m.heat_treatment_id = ht.id
LEFT JOIN material_properties mp ON mp.material_id = m.id;
"""

# Insert reference data
INSERT_STANDARDS_SQL = """
INSERT INTO material_standards (code, name, description) VALUES 
    ('ANSI', 'American National Standards Institute', 'US standard for materials designation'),
    ('ISO', 'International Organization for Standardization', 'International standard'),
    ('DIN', 'Deutsches Institut für Normung', 'German Institute for Standardization')
ON CONFLICT (code) DO NOTHING;
"""


def get_connection():
    """Create database connection."""
    return psycopg2.connect(**DB_CONNECTION)


def create_tables(conn):
    """Create database tables."""
    logger.info("Creating database tables...")
    with conn.cursor() as cur:
        cur.execute(CREATE_TABLES_SQL)
        cur.execute(INSERT_STANDARDS_SQL)
    conn.commit()
    logger.info("Tables created successfully!")


def parse_category(material_name: str) -> str:
    """Extract material category from material name."""
    material_lower = material_name.lower()
    
    if 'steel' in material_lower:
        if 'stainless' in material_lower:
            return 'Stainless Steel'
        return 'Steel'
    elif 'aluminum' in material_lower or 'aluminium' in material_lower:
        return 'Aluminum Alloy'
    elif 'copper' in material_lower:
        return 'Copper Alloy'
    elif 'brass' in material_lower:
        return 'Brass'
    elif 'bronze' in material_lower:
        return 'Bronze'
    elif 'cast iron' in material_lower:
        if 'grey' in material_lower or 'gray' in material_lower:
            return 'Grey Cast Iron'
        elif 'nodular' in material_lower:
            return 'Nodular Cast Iron'
        elif 'malleable' in material_lower:
            return 'Malleable Cast Iron'
        return 'Cast Iron'
    elif 'magnesium' in material_lower:
        return 'Magnesium Alloy'
    elif 'nickel' in material_lower:
        return 'Nickel Alloy'
    else:
        return 'Other'


def get_or_create_category(conn, category_name: str) -> int:
    """Get or create a material category and return its ID."""
    with conn.cursor() as cur:
        cur.execute("SELECT id FROM material_categories WHERE name = %s", (category_name,))
        result = cur.fetchone()
        if result:
            return result[0]
        
        cur.execute(
            "INSERT INTO material_categories (name) VALUES (%s) RETURNING id",
            (category_name,)
        )
        return cur.fetchone()[0]


def get_or_create_heat_treatment(conn, treatment_name: str) -> int:
    """Get or create a heat treatment and return its ID."""
    if not treatment_name or treatment_name.strip() == '':
        return None
    
    treatment_name = treatment_name.strip()
    
    with conn.cursor() as cur:
        cur.execute("SELECT id FROM heat_treatments WHERE name = %s", (treatment_name,))
        result = cur.fetchone()
        if result:
            return result[0]
        
        cur.execute(
            "INSERT INTO heat_treatments (name) VALUES (%s) RETURNING id",
            (treatment_name,)
        )
        return cur.fetchone()[0]


def get_standard_id(conn, std_code: str) -> int:
    """Get standard ID by code."""
    with conn.cursor() as cur:
        cur.execute("SELECT id FROM material_standards WHERE code = %s", (std_code,))
        result = cur.fetchone()
        return result[0] if result else None


def safe_float(value: str) -> float:
    """Safely convert string to float, returning None for empty/invalid values."""
    if not value or value.strip() == '':
        return None
    try:
        # Remove any non-numeric characters except . and -
        cleaned = ''.join(c for c in value if c.isdigit() or c in '.-')
        return float(cleaned) if cleaned and cleaned != '-' else None
    except (ValueError, TypeError):
        return None


def import_data_csv(conn, csv_path: str):
    """Import data from Data.csv file."""
    logger.info(f"Importing data from {csv_path}...")
    
    if not os.path.exists(csv_path):
        logger.error(f"File not found: {csv_path}")
        return
    
    imported_count = 0
    skipped_count = 0
    
    with open(csv_path, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        
        for row in reader:
            try:
                std_code = row.get('Std', '').strip()
                material_id = row.get('ID', '').strip()
                material_name = row.get('Material', '').strip()
                heat_treatment = row.get('Heat treatment', '').strip()
                description = row.get('Desc', '').strip()
                
                if not material_name or not std_code:
                    skipped_count += 1
                    continue
                
                # Get foreign keys
                standard_id = get_standard_id(conn, std_code)
                if not standard_id:
                    logger.warning(f"Unknown standard: {std_code}")
                    skipped_count += 1
                    continue
                
                category_name = parse_category(material_name)
                category_id = get_or_create_category(conn, category_name)
                
                heat_treatment_id = get_or_create_heat_treatment(conn, heat_treatment)
                
                # Check if stainless
                is_stainless = 'stainless' in description.lower() if description else False
                
                # Extract grade from material name (e.g., "SAE 1015" from "Steel SAE 1015")
                grade = None
                if 'SAE' in material_name:
                    parts = material_name.split('SAE')
                    if len(parts) > 1:
                        grade = 'SAE ' + parts[1].strip().split()[0]
                elif 'EN' in material_name:
                    parts = material_name.split('EN')
                    if len(parts) > 1:
                        grade = 'EN ' + parts[1].strip().split()[0]
                elif 'DIN' in material_name:
                    parts = material_name.split('DIN')
                    if len(parts) > 1:
                        grade = 'DIN ' + parts[1].strip().split()[0]
                
                # Insert material
                with conn.cursor() as cur:
                    cur.execute("""
                        INSERT INTO materials (
                            material_id, standard_id, category_id, name, grade, 
                            heat_treatment_id, description, is_stainless
                        ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                        ON CONFLICT (material_id) DO UPDATE SET
                            name = EXCLUDED.name,
                            heat_treatment_id = EXCLUDED.heat_treatment_id
                        RETURNING id
                    """, (
                        material_id, standard_id, category_id, material_name, grade,
                        heat_treatment_id, description, is_stainless
                    ))
                    mat_id = cur.fetchone()[0]
                    
                    # Insert properties
                    cur.execute("""
                        INSERT INTO material_properties (
                            material_id, ultimate_tensile_strength, yield_strength,
                            elastic_modulus, shear_modulus, poisson_ratio, density,
                            brinell_hardness, vickers_hardness, surface_hardness, elongation
                        ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                        ON CONFLICT (material_id) DO UPDATE SET
                            ultimate_tensile_strength = EXCLUDED.ultimate_tensile_strength,
                            yield_strength = EXCLUDED.yield_strength,
                            elastic_modulus = EXCLUDED.elastic_modulus,
                            shear_modulus = EXCLUDED.shear_modulus,
                            poisson_ratio = EXCLUDED.poisson_ratio,
                            density = EXCLUDED.density,
                            brinell_hardness = EXCLUDED.brinell_hardness,
                            vickers_hardness = EXCLUDED.vickers_hardness,
                            surface_hardness = EXCLUDED.surface_hardness,
                            elongation = EXCLUDED.elongation
                    """, (
                        mat_id,
                        safe_float(row.get('Su')),
                        safe_float(row.get('Sy')),
                        safe_float(row.get('E')),
                        safe_float(row.get('G')),
                        safe_float(row.get('mu')),
                        safe_float(row.get('Ro')),
                        safe_float(row.get('Bhn')),
                        safe_float(row.get('HV')),
                        safe_float(row.get('pH')),
                        safe_float(row.get('A5'))
                    ))
                
                imported_count += 1
                
                if imported_count % 100 == 0:
                    conn.commit()
                    logger.info(f"Imported {imported_count} materials...")
                    
            except Exception as e:
                logger.error(f"Error importing row: {e}")
                skipped_count += 1
                continue
    
    conn.commit()
    logger.info(f"Import complete! Imported: {imported_count}, Skipped: {skipped_count}")


def import_material_usage(conn, csv_path: str):
    """Import material usage flags from material.csv file."""
    logger.info(f"Updating material usage from {csv_path}...")
    
    if not os.path.exists(csv_path):
        logger.warning(f"File not found: {csv_path}")
        return
    
    updated_count = 0
    
    with open(csv_path, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        
        for row in reader:
            try:
                material_name = row.get('Material', '').strip()
                is_in_use = row.get('Use', 'False').strip().lower() == 'true'
                
                if material_name and is_in_use:
                    with conn.cursor() as cur:
                        # Match by similar name pattern
                        cur.execute("""
                            UPDATE materials 
                            SET is_in_use = TRUE 
                            WHERE name ILIKE %s OR name ILIKE %s
                        """, (f"%{material_name[:50]}%", material_name))
                        
                        if cur.rowcount > 0:
                            updated_count += cur.rowcount
                            
            except Exception as e:
                logger.error(f"Error updating usage: {e}")
                continue
    
    conn.commit()
    logger.info(f"Updated usage for {updated_count} materials")


def print_summary(conn):
    """Print import summary."""
    with conn.cursor() as cur:
        cur.execute("SELECT COUNT(*) FROM materials")
        mat_count = cur.fetchone()[0]
        
        cur.execute("SELECT COUNT(*) FROM material_properties")
        prop_count = cur.fetchone()[0]
        
        cur.execute("SELECT COUNT(*) FROM material_categories")
        cat_count = cur.fetchone()[0]
        
        cur.execute("SELECT COUNT(*) FROM heat_treatments")
        ht_count = cur.fetchone()[0]
        
        cur.execute("SELECT COUNT(*) FROM materials WHERE is_in_use = TRUE")
        in_use_count = cur.fetchone()[0]
        
        print("\n" + "=" * 60)
        print("METALLURGY DATABASE IMPORT SUMMARY")
        print("=" * 60)
        print(f"  Materials imported:     {mat_count:,}")
        print(f"  Properties records:     {prop_count:,}")
        print(f"  Material categories:    {cat_count:,}")
        print(f"  Heat treatments:        {ht_count:,}")
        print(f"  Materials in use:       {in_use_count:,}")
        print("=" * 60)
        
        # Show categories breakdown
        print("\nMaterial Categories:")
        cur.execute("""
            SELECT mc.name, COUNT(m.id) as count 
            FROM material_categories mc 
            LEFT JOIN materials m ON m.category_id = mc.id 
            GROUP BY mc.name 
            ORDER BY count DESC
        """)
        for row in cur.fetchall():
            print(f"  - {row[0]}: {row[1]:,}")
        
        print("\n" + "=" * 60)


def main():
    """Main import function."""
    print("\n" + "=" * 60)
    print("METALLURGY DATA IMPORTER")
    print("=" * 60)
    
    # Paths to CSV files
    data_dir = os.path.join(os.path.dirname(__file__), 'data_set')
    data_csv = os.path.join(data_dir, 'Data.csv')
    material_csv = os.path.join(data_dir, 'material.csv')
    
    print(f"\nDatabase: {args.host}:{args.port}/{args.dbname}")
    print(f"Data file: {data_csv}")
    print(f"Material file: {material_csv}")
    
    try:
        conn = get_connection()
        logger.info("Connected to database successfully!")
        
        # Create tables
        create_tables(conn)
        
        # Import data
        import_data_csv(conn, data_csv)
        
        # Update usage flags
        import_material_usage(conn, material_csv)
        
        # Print summary
        print_summary(conn)
        
        conn.close()
        logger.info("Import completed successfully!")
        
    except Exception as e:
        logger.error(f"Import failed: {e}")
        raise


if __name__ == "__main__":
    main()
