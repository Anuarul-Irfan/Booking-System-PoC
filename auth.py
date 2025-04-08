from flask import Blueprint, request, render_template, redirect, url_for, session, flash
from firebase_admin import auth, firestore
from functools import wraps
from firebase_config import create_user, get_user, users_ref
import requests
import json
import traceback

auth_bp = Blueprint("auth", __name__)

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if "user" not in session:
            return redirect(url_for("auth.login"))
        return f(*args, **kwargs)
    return decorated_function

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if "user" not in session or session["user"].get("role") != "admin":
            return redirect(url_for("auth.login"))
        return f(*args, **kwargs)
    return decorated_function

@auth_bp.route("/", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form["email"]
        password = request.form["password"]
        
        # Firebase Web API Key
        api_key = "AIzaSyBzDMMan-eweeVzEcq04ooMExxI3741Pfc"
        
        print(f"Login attempt for email: {email}")  # Debug log
        
        try:
            # First, verify email/password with Firebase Auth REST API
            auth_url = f"https://identitytoolkit.googleapis.com/v1/accounts:signInWithPassword?key={api_key}"
            auth_data = {
                "email": email,
                "password": password,
                "returnSecureToken": True
            }
            
            print("Sending request to Firebase Auth...")  # Debug log
            auth_response = requests.post(auth_url, json=auth_data)
            
            try:
                response_json = auth_response.json()
                print(f"Firebase Auth Response: {json.dumps(response_json, indent=2)}")  # Debug log
            except:
                print("Could not parse auth response as JSON")
                
            auth_response.raise_for_status()
            
            print("Firebase Auth successful, getting user...")  # Debug log
            
            # If we get here, the password was correct
            user = auth.get_user_by_email(email)
            print(f"Got user with UID: {user.uid}")  # Debug log
            
            # Try to get user data from Firestore
            print("Getting user data from Firestore...")  # Debug log
            user_doc = users_ref.document(user.uid).get()
            
            if not user_doc.exists:
                print(f"Creating new user data for {email}")  # Debug log
                # Create user data in Firestore if it doesn't exist
                user_data = {
                    'email': email,
                    'role': 'admin' if email == 'admin@example.com' else 'haulier',
                    'created_at': firestore.SERVER_TIMESTAMP
                }
                users_ref.document(user.uid).set(user_data)
            else:
                print("Found existing user data")  # Debug log
                user_data = user_doc.to_dict()
            
            print(f"User data: {user_data}")  # Debug log
            
            session["user"] = {
                "uid": user.uid,
                "email": email,
                "role": user_data.get("role", "haulier")
            }
            
            print(f"Final session data: {session['user']}")  # Debug log
            
            # Fix: Use the correct endpoint names with blueprint prefix
            if user_data.get("role") == "admin":
                return redirect(url_for("admin.admin_dashboard"))
            else:
                return redirect(url_for("slots.haulier_dashboard"))
            
        except requests.exceptions.HTTPError as e:
            print(f"HTTP Error: {str(e)}")  # Debug log
            print(f"Response: {e.response.text if e.response else 'No response'}")  # Debug log
            
            error_message = "Invalid email or password"
            if e.response is not None:
                try:
                    error_data = e.response.json()
                    print(f"Error data: {error_data}")  # Debug log
                    if 'error' in error_data:
                        if error_data['error'].get('message') == 'EMAIL_NOT_FOUND':
                            error_message = "Email not found"
                        elif error_data['error'].get('message') == 'INVALID_PASSWORD':
                            error_message = "Invalid password"
                except Exception as json_error:
                    print(f"Error parsing error response: {str(json_error)}")  # Debug log
            return render_template("login.html", error=error_message)
            
        except Exception as e:
            print(f"Unexpected error during login: {str(e)}")  # Debug log
            print("Full traceback:")  # Debug log
            traceback.print_exc()  # Print full traceback
            return render_template("login.html", error=f"Login error: {str(e)}")
            
    return render_template("login.html")

@auth_bp.route("/logout")
def logout():
    session.pop("user", None)
    return redirect(url_for("auth.login"))

# Optional: Add a route to check session data
@auth_bp.route("/check-session")
def check_session():
    return str(session.get("user", {}))

# You can remove or comment out the setup-admin route if you don't need it
# since you already have users set up in Firebase
