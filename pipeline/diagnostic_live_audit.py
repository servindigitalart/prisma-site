#!/usr/local/bin/python3
"""
PRISMA LIVE DATABASE DIAGNOSTIC AUDIT
=====================================
Real-time introspection and analysis of Supabase database.

DESIGN:
1. Introspect schema from information_schema
2. Build queries using confirmed column names
3. Execute READ-ONLY diagnostics
4. Report findings with severity flags

USAGE:
    python3 pipeline/diagnostic_live_audit.py

REQUIRES:
    SUPABASE_URL and SUPABASE_SERVICE_KEY in environment
"""

import os
import sys
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from dotenv import load_dotenv
from supabase import create_client, Client

# Load environment variables
load_dotenv('.env.local')

# ─── Schema Models ────────────────────────────────────────────────────────────

@dataclass
class TableSchema:
    """Introspected table metadata."""
    name: str
    columns: Dict[str, str]  # column_name -> data_type
    primary_key: Optional[str] = None


@dataclass
class DiagnosticResult:
    """Single diagnostic check result."""
    category: str
    check: str
    severity: str  # 'ERROR', 'WARNING', 'INFO'
    count: Optional[int]
    details: str
    query: str


# ─── Database Introspection ───────────────────────────────────────────────────

class SchemaIntrospector:
    """Query information_schema to discover actual database structure."""
    
    def __init__(self, client: Client):
        self.client = client
        self.tables: Dict[str, TableSchema] = {}
    
    def introspect_all(self) -> Dict[str, TableSchema]:
        """Discover all tables and their columns."""
        print("🔍 Introspecting database schema...")
        
        # Get all tables in public schema
        tables_query = """
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = 'public' 
            AND table_type = 'BASE TABLE'
            ORDER BY table_name
        """
        
        result = self.client.rpc('exec_sql', {'query': tables_query}).execute()
        
        # If RPC doesn't exist, try direct approach
        if not result.data:
            # Fallback: try to query known tables directly
            known_tables = ['works', 'people', 'studios', 'colors', 'dimensions', 
                          'media_types', 'work_colors', 'work_dimensions', 
                          'work_people', 'work_studios']
            
            for table_name in known_tables:
                try:
                    self._introspect_table(table_name)
                except Exception as e:
                    print(f"  ⚠️  Could not introspect {table_name}: {e}")
        else:
            for row in result.data:
                table_name = row['table_name']
                self._introspect_table(table_name)
        
        print(f"✅ Introspected {len(self.tables)} tables\n")
        return self.tables
    
    def _introspect_table(self, table_name: str):
        """Get columns for a specific table."""
        # Try to select one row to get column names and types
        try:
            result = self.client.table(table_name).select('*').limit(1).execute()
            
            # Get column names from the first row (if exists)
            columns = {}
            if result.data:
                for col_name in result.data[0].keys():
                    # We can't get exact types easily, so we'll infer from values
                    value = result.data[0][col_name]
                    if isinstance(value, int):
                        col_type = 'integer'
                    elif isinstance(value, float):
                        col_type = 'numeric'
                    elif isinstance(value, bool):
                        col_type = 'boolean'
                    elif isinstance(value, dict):
                        col_type = 'jsonb'
                    elif isinstance(value, list):
                        col_type = 'array'
                    else:
                        col_type = 'text'
                    columns[col_name] = col_type
            else:
                # Empty table - try to infer from schema
                # For now, we'll mark it as unknown
                columns = {}
            
            # Assume 'id' is primary key if it exists
            pk = 'id' if 'id' in columns else None
            
            self.tables[table_name] = TableSchema(
                name=table_name,
                columns=columns,
                primary_key=pk
            )
            
            print(f"  ✓ {table_name}: {len(columns)} columns")
            
        except Exception as e:
            print(f"  ✗ {table_name}: {e}")


# ─── Diagnostic Checks ────────────────────────────────────────────────────────

class DatabaseDiagnostics:
    """Execute diagnostic queries on confirmed schema."""
    
    def __init__(self, client: Client, schema: Dict[str, TableSchema]):
        self.client = client
        self.schema = schema
        self.results: List[DiagnosticResult] = []
    
    def run_all(self):
        """Execute all diagnostic checks."""
        print("🔬 Running diagnostic checks...\n")
        
        self._check_table_counts()
        self._check_orphaned_records()
        self._check_duplicate_tmdb_ids()
        self._check_color_usage()
        self._check_dimension_distribution()
        self._check_film_completeness()
        
        return self.results
    
    def _check_table_counts(self):
        """Count records in each table."""
        print("📊 PART 1: Table Record Counts")
        print("─" * 60)
        
        for table_name in sorted(self.schema.keys()):
            try:
                result = self.client.table(table_name).select('*', count='exact').execute()
                count = result.count
                
                severity = 'INFO'
                if count == 0:
                    severity = 'WARNING'
                
                self.results.append(DiagnosticResult(
                    category='table_counts',
                    check=f'{table_name}_count',
                    severity=severity,
                    count=count,
                    details=f'{table_name} has {count} records',
                    query=f"SELECT COUNT(*) FROM {table_name}"
                ))
                
                flag = '⚠️ ' if count == 0 else '📊'
                print(f"{flag} {table_name}: {count} records")
                
            except Exception as e:
                print(f"  ✗ Error counting {table_name}: {e}")
        
        print()
    
    def _check_orphaned_records(self):
        """Find orphaned records in junction tables."""
        print("🔗 PART 2: Orphaned Records")
        print("─" * 60)
        
        # Check work_colors
        if 'work_colors' in self.schema and 'works' in self.schema:
            try:
                # Find work_colors with non-existent work_id
                result = self.client.table('work_colors').select('work_id').execute()
                work_ids_in_colors = {row['work_id'] for row in result.data}
                
                works_result = self.client.table('works').select('id').execute()
                valid_work_ids = {row['id'] for row in works_result.data}
                
                orphaned = work_ids_in_colors - valid_work_ids
                
                severity = 'ERROR' if orphaned else 'INFO'
                self.results.append(DiagnosticResult(
                    category='orphaned_records',
                    check='work_colors_orphaned',
                    severity=severity,
                    count=len(orphaned),
                    details=f'Found {len(orphaned)} orphaned work_colors (work_id not in works)',
                    query="SELECT DISTINCT wc.work_id FROM work_colors wc LEFT JOIN works w ON wc.work_id = w.id WHERE w.id IS NULL"
                ))
                
                flag = '❌' if orphaned else '✅'
                print(f"{flag} work_colors orphaned: {len(orphaned)}")
                if orphaned and len(orphaned) <= 5:
                    print(f"     IDs: {orphaned}")
                
            except Exception as e:
                print(f"  ✗ Error checking work_colors: {e}")
        
        # Check work_people
        if 'work_people' in self.schema and 'works' in self.schema and 'people' in self.schema:
            try:
                result = self.client.table('work_people').select('work_id,person_id').execute()
                
                works_result = self.client.table('works').select('id').execute()
                valid_work_ids = {row['id'] for row in works_result.data}
                
                people_result = self.client.table('people').select('id').execute()
                valid_person_ids = {row['id'] for row in people_result.data}
                
                orphaned_works = sum(1 for row in result.data if row['work_id'] not in valid_work_ids)
                orphaned_people = sum(1 for row in result.data if row['person_id'] not in valid_person_ids)
                
                flag_works = '❌' if orphaned_works > 0 else '✅'
                flag_people = '❌' if orphaned_people > 0 else '✅'
                
                print(f"{flag_works} work_people orphaned (work_id): {orphaned_works}")
                print(f"{flag_people} work_people orphaned (person_id): {orphaned_people}")
                
            except Exception as e:
                print(f"  ✗ Error checking work_people: {e}")
        
        print()
    
    def _check_duplicate_tmdb_ids(self):
        """Find duplicate tmdb_ids in people table."""
        print("👥 PART 3: People Identity Duplicates")
        print("─" * 60)
        
        if 'people' not in self.schema:
            print("  ⚠️  'people' table not found")
            print()
            return
        
        try:
            # Get all people with tmdb_id
            result = self.client.table('people').select('id,tmdb_id').execute()
            
            # Group by tmdb_id
            tmdb_groups: Dict[int, List[str]] = {}
            for row in result.data:
                tmdb_id = row.get('tmdb_id')
                if tmdb_id is not None:
                    if tmdb_id not in tmdb_groups:
                        tmdb_groups[tmdb_id] = []
                    tmdb_groups[tmdb_id].append(row['id'])
            
            # Find duplicates
            duplicates = {k: v for k, v in tmdb_groups.items() if len(v) > 1}
            
            severity = 'ERROR' if duplicates else 'INFO'
            self.results.append(DiagnosticResult(
                category='identity_conflicts',
                check='people_duplicate_tmdb_id',
                severity=severity,
                count=len(duplicates),
                details=f'Found {len(duplicates)} duplicate tmdb_ids in people table',
                query="SELECT tmdb_id, COUNT(*) FROM people WHERE tmdb_id IS NOT NULL GROUP BY tmdb_id HAVING COUNT(*) > 1"
            ))
            
            flag = '❌' if duplicates else '✅'
            print(f"{flag} Duplicate tmdb_ids: {len(duplicates)}")
            
            if duplicates:
                print("\n  Duplicate tmdb_ids (showing first 10):")
                for tmdb_id, person_ids in list(duplicates.items())[:10]:
                    print(f"    tmdb_id={tmdb_id}: {len(person_ids)} records → {person_ids[:3]}")
            
        except Exception as e:
            print(f"  ✗ Error checking duplicates: {e}")
        
        print()
    
    def _check_color_usage(self):
        """Analyze color assignment distribution."""
        print("🎨 PART 4: Color Distribution")
        print("─" * 60)
        
        if 'work_colors' not in self.schema:
            print("  ⚠️  'work_colors' table not found")
            print()
            return
        
        try:
            result = self.client.table('work_colors').select('color_id').execute()
            
            # Count by color_id
            color_counts: Dict[str, int] = {}
            for row in result.data:
                color_id = row['color_id']
                color_counts[color_id] = color_counts.get(color_id, 0) + 1
            
            # Sort by usage
            sorted_colors = sorted(color_counts.items(), key=lambda x: x[1], reverse=True)
            
            total_assignments = sum(color_counts.values())
            
            print(f"📊 Total color assignments: {total_assignments}")
            print(f"📊 Unique colors used: {len(color_counts)}")
            print()
            print("  Top 10 colors by usage:")
            
            for color_id, count in sorted_colors[:10]:
                percentage = (count / total_assignments * 100) if total_assignments > 0 else 0
                bar = '█' * int(percentage / 2)
                print(f"    {color_id:20s}: {count:4d} ({percentage:5.1f}%) {bar}")
            
            # Flag overused colors (>20% of total)
            overused = [(c, n) for c, n in sorted_colors if n / total_assignments > 0.2]
            if overused:
                print(f"\n  ⚠️  Potentially overused colors (>20% of assignments):")
                for color_id, count in overused:
                    percentage = count / total_assignments * 100
                    print(f"    {color_id}: {percentage:.1f}%")
            
        except Exception as e:
            print(f"  ✗ Error analyzing colors: {e}")
        
        print()
    
    def _check_dimension_distribution(self):
        """Analyze dimension assignment distribution."""
        print("📐 PART 5: Dimension Distribution")
        print("─" * 60)
        
        if 'work_dimensions' not in self.schema:
            print("  ⚠️  'work_dimensions' table not found")
            print()
            return
        
        try:
            result = self.client.table('work_dimensions').select('dimension_id').execute()
            
            # Count by dimension_id
            dim_counts: Dict[str, int] = {}
            for row in result.data:
                dim_id = row['dimension_id']
                dim_counts[dim_id] = dim_counts.get(dim_id, 0) + 1
            
            # Sort by usage
            sorted_dims = sorted(dim_counts.items(), key=lambda x: x[1], reverse=True)
            
            total_assignments = sum(dim_counts.values())
            
            print(f"📊 Total dimension assignments: {total_assignments}")
            print(f"📊 Unique dimensions used: {len(dim_counts)}")
            print()
            print("  All dimensions by usage:")
            
            for dim_id, count in sorted_dims:
                percentage = (count / total_assignments * 100) if total_assignments > 0 else 0
                bar = '█' * int(percentage / 2)
                print(f"    {dim_id:30s}: {count:4d} ({percentage:5.1f}%) {bar}")
            
        except Exception as e:
            print(f"  ✗ Error analyzing dimensions: {e}")
        
        print()
    
    def _check_film_completeness(self):
        """Check which films have complete metadata."""
        print("🎬 PART 6: Film Completeness")
        print("─" * 60)
        
        if 'works' not in self.schema:
            print("  ⚠️  'works' table not found")
            print()
            return
        
        try:
            works = self.client.table('works').select('id,title,release_date').execute()
            
            incomplete_films = []
            
            for work in works.data:
                work_id = work['id']
                issues = []
                
                # Check for colors
                if 'work_colors' in self.schema:
                    colors = self.client.table('work_colors').select('color_id').eq('work_id', work_id).execute()
                    if not colors.data:
                        issues.append('no_colors')
                
                # Check for people
                if 'work_people' in self.schema:
                    people = self.client.table('work_people').select('person_id').eq('work_id', work_id).execute()
                    if not people.data:
                        issues.append('no_people')
                
                # Check for dimensions
                if 'work_dimensions' in self.schema:
                    dims = self.client.table('work_dimensions').select('dimension_id').eq('work_id', work_id).execute()
                    if not dims.data:
                        issues.append('no_dimensions')
                
                if issues:
                    incomplete_films.append({
                        'id': work_id,
                        'title': work.get('title', 'Unknown'),
                        'release_date': work.get('release_date'),
                        'issues': issues
                    })
            
            print(f"📊 Total films: {len(works.data)}")
            print(f"⚠️  Incomplete films: {len(incomplete_films)}")
            
            if incomplete_films:
                print(f"\n  Showing first 20 incomplete films:")
                for film in incomplete_films[:20]:
                    issues_str = ', '.join(film['issues'])
                    print(f"    {film['id']:50s} | {film['title'][:40]:40s} | {issues_str}")
            
        except Exception as e:
            print(f"  ✗ Error checking completeness: {e}")
        
        print()
    
    def print_summary(self):
        """Print summary of diagnostic results."""
        print("\n" + "=" * 60)
        print("📋 DIAGNOSTIC SUMMARY")
        print("=" * 60)
        
        errors = [r for r in self.results if r.severity == 'ERROR']
        warnings = [r for r in self.results if r.severity == 'WARNING']
        
        print(f"\n❌ ERRORS: {len(errors)}")
        for result in errors:
            print(f"   • {result.check}: {result.details}")
        
        print(f"\n⚠️  WARNINGS: {len(warnings)}")
        for result in warnings:
            print(f"   • {result.check}: {result.details}")
        
        print(f"\nℹ️  INFO: {len([r for r in self.results if r.severity == 'INFO'])}")
        print()


# ─── Main ─────────────────────────────────────────────────────────────────────

def main():
    """Execute live database diagnostic audit."""
    
    # Load credentials
    supabase_url = os.environ.get("SUPABASE_URL") or os.environ.get("PUBLIC_SUPABASE_URL")
    service_key = os.environ.get("SUPABASE_SERVICE_KEY")
    
    if not supabase_url or not service_key:
        print("❌ ERROR: Missing Supabase credentials")
        print("   Required environment variables:")
        print("   - SUPABASE_URL")
        print("   - SUPABASE_SERVICE_KEY")
        sys.exit(1)
    
    # Connect
    print("🔌 Connecting to Supabase...")
    client = create_client(supabase_url, service_key)
    print("✅ Connected\n")
    
    # Introspect schema
    introspector = SchemaIntrospector(client)
    schema = introspector.introspect_all()
    
    if not schema:
        print("❌ ERROR: Could not introspect any tables")
        sys.exit(1)
    
    # Print schema summary
    print("📋 DISCOVERED SCHEMA")
    print("─" * 60)
    for table_name, table_schema in sorted(schema.items()):
        print(f"  {table_name}:")
        for col_name, col_type in sorted(table_schema.columns.items()):
            pk_marker = ' (PK)' if col_name == table_schema.primary_key else ''
            print(f"    • {col_name}: {col_type}{pk_marker}")
    print()
    
    # Run diagnostics
    diagnostics = DatabaseDiagnostics(client, schema)
    diagnostics.run_all()
    diagnostics.print_summary()
    
    print("✅ Diagnostic audit complete")


if __name__ == "__main__":
    main()
