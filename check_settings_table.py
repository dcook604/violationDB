#!/usr/bin/env python
from app import create_app, db
from app.models import Settings
import sqlalchemy as sa
from sqlalchemy import inspect, text

app = create_app()
with app.app_context():
    inspector = inspect(db.engine)
    table_names = inspector.get_table_names()
    
    print(f"Tables in database: {', '.join(table_names)}")
    
    # Check if settings table exists
    if 'settings' in table_names:
        print("\nSettings table found. Checking structure:")
        columns = inspector.get_columns('settings')
        for column in columns:
            print(f"  {column['name']}: {column['type']}")
        
        # Check if any settings exist
        try:
            settings_count = db.session.query(sa.func.count(Settings.id)).scalar()
            print(f"\nNumber of settings rows: {settings_count}")
            
            if settings_count > 0:
                settings = Settings.query.first()
                print(f"Settings ID: {settings.id}")
                print(f"SMTP Server: {settings.smtp_server}")
                print(f"Updated at: {settings.updated_at}")
            else:
                print("No settings found. Creating default settings...")
                settings = Settings()
                db.session.add(settings)
                db.session.commit()
                print(f"Created default settings with ID: {settings.id}")
        except Exception as e:
            print(f"Error accessing settings: {str(e)}")
    else:
        print("\nSettings table not found. Creating the table...")
        try:
            # Create the settings table
            db.create_all()
            print("Created all missing tables including settings.")
            
            # Create default settings
            settings = Settings()
            db.session.add(settings)
            db.session.commit()
            print(f"Created default settings with ID: {settings.id}")
        except Exception as e:
            print(f"Error creating settings table: {str(e)}") 