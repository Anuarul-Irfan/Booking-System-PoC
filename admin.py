from flask import Blueprint, render_template, redirect, url_for, session, request, flash
from auth import admin_required
from firebase_config import create_slot, get_all_slots, create_user, delete_slot, db
import firestore
import traceback

admin_bp = Blueprint("admin", __name__)

@admin_bp.route("/test-form", methods=["POST"])
@admin_required
def test_form():
    print("Test form received")
    print("Form data:", request.form)
    return "Form received"

@admin_bp.route("/admin")
@admin_required
def admin_dashboard():
    try:
        # Check if user has admin role
        if session.get("user", {}).get("role") != "admin":
            flash("Access denied. Admin privileges required.", "error")
            return redirect(url_for("auth.login"))
        
        # Get all slots from Firestore
        slots = get_all_slots()
        print("Retrieved slots:", slots)  # Debug log
        
        return render_template("admin_dashboard.html", slots=slots)
    except Exception as e:
        print("Error in admin_dashboard:", str(e))
        print("Full traceback:", traceback.format_exc())
        flash("An error occurred while loading the dashboard.", "error")
        return redirect(url_for("auth.login"))

@admin_bp.route("/add-slot", methods=["POST"])
@admin_required
def add_slot():
    try:
        print("\n=== Add Slot Request ===")
        print("Request form data:", request.form)
        print("Request headers:", request.headers)
        print("Session data:", session)
        
        # Check if user has admin role
        if session.get("user", {}).get("role") != "admin":
            print("Access denied: User is not admin")
            flash("Access denied. Admin privileges required.", "error")
            return redirect(url_for("auth.login"))
        
        time = request.form.get("time")
        product = request.form.get("product")
        
        print(f"Form data - Time: {time}, Product: {product}")
        
        if not time or not product:
            print("Missing required fields")
            flash("Please provide both time and product type", "error")
            return redirect(url_for("admin.admin_dashboard"))
        
        # Create slot using the create_slot function
        try:
            doc_ref = create_slot(time, product)
            print("Slot created successfully with ID:", doc_ref.id)
            flash("Slot added successfully!", "success")
        except Exception as db_error:
            print("Database error:", str(db_error))
            print("Full traceback:", traceback.format_exc())
            flash(f"Database error: {str(db_error)}", "error")
            
    except Exception as e:
        print("General error in add_slot:", str(e))
        print("Full traceback:", traceback.format_exc())
        flash(f"Error adding slot: {str(e)}", "error")
    
    return redirect(url_for("admin.admin_dashboard"))

@admin_bp.route("/add-haulier", methods=["POST"])
@admin_required
def add_haulier():
    try:
        email = request.form["email"]
        password = request.form["password"]
        
        if not email or not password:
            flash("Email and password are required", "error")
            return redirect(url_for("admin.admin_dashboard"))
        
        create_user(email, password, role="haulier")
        flash("Haulier added successfully", "success")
    except Exception as e:
        flash(f"Error adding haulier: {str(e)}", "error")
    
    return redirect(url_for("admin.admin_dashboard"))

@admin_bp.route("/delete-slot/<slot_id>", methods=["POST"])
@admin_required
def delete_slot_route(slot_id):
    try:
        print(f"Received delete request for slot: {slot_id}")
        
        # Check if user has admin role
        if session.get("user", {}).get("role") != "admin":
            flash("Access denied. Admin privileges required.", "error")
            return redirect(url_for("auth.login"))
        
        # Delete slot from Firestore
        delete_slot(slot_id)
        print(f"Slot {slot_id} deleted successfully")
        
        flash("Slot deleted successfully!", "success")
    except Exception as e:
        print("Error in delete_slot_route:", str(e))
        print("Full traceback:", traceback.format_exc())
        flash(f"Error deleting slot: {str(e)}", "error")
    
    return redirect(url_for("admin.admin_dashboard"))
