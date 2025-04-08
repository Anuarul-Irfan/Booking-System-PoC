from firebase_admin import credentials, initialize_app, firestore, auth
import os
import traceback

def initialize_firebase():
    try:
        print("\n=== Checking Firebase Initialization ===")
        print("Current working directory:", os.getcwd())
        print("Looking for serviceAccountKey.json...")
        
        if not os.path.exists("serviceAccountKey.json"):
            print("ERROR: serviceAccountKey.json not found!")
            raise FileNotFoundError("serviceAccountKey.json not found")
            
        print("serviceAccountKey.json found")
        
        # Try to get the default app, which will raise an exception if not initialized
        try:
            db = firestore.client()
            print("Firebase already initialized, returning existing client")
            return db, None
        except Exception as e:
            print("Firebase not initialized, initializing now...")
            print("Error:", str(e))
            
            # Initialize Firebase Admin SDK
            try:
                cred = credentials.Certificate("serviceAccountKey.json")
                print("Credentials loaded successfully")
                firebase_app = initialize_app(cred)
                print("Firebase app initialized")
                db = firestore.client()
                print("Firestore client created")
                return db, firebase_app
            except Exception as init_error:
                print("Error initializing Firebase:", str(init_error))
                print("Full traceback:", traceback.format_exc())
                raise
                
    except Exception as e:
        print("Critical error in Firebase initialization:", str(e))
        print("Full traceback:", traceback.format_exc())
        raise

# Initialize Firebase and get db instance
print("\n=== Starting Firebase Initialization ===")
try:
    db, firebase_app = initialize_firebase()
    print("Firebase initialization complete")
except Exception as e:
    print("Failed to initialize Firebase:", str(e))
    raise

# Collection references
try:
    users_ref = db.collection('users')
    slots_ref = db.collection('slots')
    print("Collection references created successfully")
except Exception as e:
    print("Error creating collection references:", str(e))
    raise

# User management functions
def create_user(email, password, role):
    try:
        user = auth.create_user(
            email=email,
            password=password
        )
        # Store additional user data in Firestore
        users_ref.document(user.uid).set({
            'email': email,
            'role': role,
            'created_at': firestore.SERVER_TIMESTAMP
        })
        return user
    except Exception as e:
        raise Exception(f"Error creating user: {str(e)}")

def get_user(uid):
    try:
        return users_ref.document(uid).get()
    except Exception as e:
        raise Exception(f"Error getting user: {str(e)}")

# Slot management functions
def create_slot(time, product):
    try:
        print(f"\n=== Creating Slot ===")
        print(f"Time: {time}, Product: {product}")
        
        # Verify database connection
        if not db:
            print("ERROR: Database connection not initialized")
            raise Exception("Database connection not initialized")
            
        # Verify collection reference
        if not slots_ref:
            print("ERROR: Slots collection reference not initialized")
            raise Exception("Slots collection reference not initialized")
            
        slot_data = {
            'time': time,
            'product': product,
            'bookedBy': None,
            'created_at': firestore.SERVER_TIMESTAMP
        }
        print("Slot data to be created:", slot_data)
        
        # Create the document
        try:
            doc_ref = slots_ref.document()
            print("Document reference created with ID:", doc_ref.id)
        except Exception as doc_error:
            print("ERROR creating document reference:", str(doc_error))
            raise
        
        # Set the data
        try:
            doc_ref.set(slot_data)
            print("Slot data successfully written to Firestore")
            return doc_ref
        except Exception as set_error:
            print("ERROR writing data to Firestore:", str(set_error))
            print("Full traceback:", traceback.format_exc())
            raise
            
    except Exception as e:
        print("Critical error in create_slot:", str(e))
        print("Full traceback:", traceback.format_exc())
        raise Exception(f"Error creating slot: {str(e)}")

def get_all_slots():
    try:
        print("\n=== Getting All Slots ===")
        if not db:
            raise Exception("Database connection not initialized")
            
        slots = [doc.to_dict() | {'id': doc.id} for doc in slots_ref.stream()]
        print(f"Found {len(slots)} slots")
        return slots
    except Exception as e:
        print("Error getting slots:", str(e))
        print("Full traceback:", traceback.format_exc())
        raise Exception(f"Error getting slots: {str(e)}")

def book_slot(slot_id, user_id):
    try:
        slot_ref = slots_ref.document(slot_id)
        slot = slot_ref.get()
        
        if not slot.exists:
            raise Exception("Slot not found")
            
        if slot.to_dict().get('bookedBy'):
            raise Exception("Slot already booked")
            
        slot_ref.update({
            'bookedBy': user_id,
            'booked_at': firestore.SERVER_TIMESTAMP
        })
        return True
    except Exception as e:
        raise Exception(f"Error booking slot: {str(e)}")

def get_user_bookings(user_id):
    try:
        return [doc.to_dict() | {'id': doc.id} 
                for doc in slots_ref.where('bookedBy', '==', user_id).stream()]
    except Exception as e:
        raise Exception(f"Error getting user bookings: {str(e)}")

def delete_slot(slot_id):
    try:
        print(f"\n=== Deleting Slot {slot_id} ===")
        if not db:
            raise Exception("Database connection not initialized")
            
        slot_ref = slots_ref.document(slot_id)
        slot_ref.delete()
        print("Slot deleted successfully")
        return True
    except Exception as e:
        print("Error deleting slot:", str(e))
        print("Full traceback:", traceback.format_exc())
        raise e 