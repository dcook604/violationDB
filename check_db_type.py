#!/usr/bin/env python3
"""Check database type"""
from app import create_app, db
 
app = create_app()
with app.app_context():
    print(f"Database URI: {db.engine.url}")
    print(f"Database type: {db.engine.dialect.name}") 