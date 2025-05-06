from app import create_app, db
from app.models import User, UnitProfile

app = create_app('development')

with app.app_context():
    # Check if we have any unit profiles
    unit_count = UnitProfile.query.count()
    print(f"Current unit count: {unit_count}")
    
    # Create a test unit profile if needed
    if unit_count == 0:
        try:
            test_unit = UnitProfile(
                unit_number="101",
                owner_first_name="Test",
                owner_last_name="Owner",
                owner_email="test@example.com",
                owner_telephone="555-123-4567",
                has_dog=False,
                has_cat=True,
                is_rented=False
            )
            db.session.add(test_unit)
            db.session.commit()
            print(f"Created test unit: {test_unit.unit_number}")
        except Exception as e:
            print(f"Error creating unit: {str(e)}")
            db.session.rollback()
            
    # Display all units
    units = UnitProfile.query.all()
    for unit in units:
        print(f"Unit: {unit.unit_number}, Owner: {unit.owner_first_name} {unit.owner_last_name}")
