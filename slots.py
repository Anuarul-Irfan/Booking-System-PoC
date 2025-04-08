# slots.py
from flask import Blueprint, render_template, redirect, url_for, session, flash
from auth import login_required
from firebase_config import get_all_slots, book_slot, get_user_bookings

slots_bp = Blueprint("slots", __name__)

@slots_bp.route("/haulier", endpoint="haulier_dashboard")
@login_required
def haulier_dashboard():
    try:
        if session.get("user", {}).get("role") != "haulier":
            return redirect(url_for("auth.login"))
        
        slots = get_all_slots()
        return render_template("haulier_dashboard.html", slots=slots)
    except Exception as e:
        flash(f"Error loading slots: {str(e)}", "error")
        return render_template("haulier_dashboard.html", slots=[])

@slots_bp.route("/book/<slot_id>", methods=["POST"])
@login_required
def book_slot_route(slot_id):
    try:
        if session.get("user", {}).get("role") != "haulier":
            flash("Only hauliers can book slots", "error")
            return redirect(url_for("auth.login"))
        
        user_id = session["user"]["uid"]
        
        # Check if user already has bookings
        user_bookings = get_user_bookings(user_id)
        if len(user_bookings) >= 3:  # Limit to 3 bookings per user
            flash("You have reached the maximum number of bookings", "error")
            return redirect(url_for("slots.haulier_dashboard"))
        
        # Try to book the slot
        book_slot(slot_id, user_id)
        flash("Slot booked successfully", "success")
    except Exception as e:
        flash(f"Error booking slot: {str(e)}", "error")
    
    return redirect(url_for("slots.haulier_dashboard"))