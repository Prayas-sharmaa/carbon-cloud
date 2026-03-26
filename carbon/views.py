from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Sum, Count
from .models import CarbonEntry
from .forms import CarbonEntryForm, RegisterForm
from .loyalty_service import LoyaltyService

#  APIs
from .services.cloudmail_service import CloudMailService
from .services.currency_service import CurrencyService  # For points → currency conversion
from .services.carbon_intensity_service import CarbonIntensityService  # UK Carbon Intensity

# Autentication

def register_view(request):
    if request.method == "POST":
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, f"Welcome {user.first_name}! Account created.")
            return redirect("home")
    else:
        form = RegisterForm()
    return render(request, "carbon/register.html", {"form": form})


def login_view(request):
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            messages.success(request, f"Welcome back, {user.first_name}!")
            return redirect("home")
        else:
            messages.error(request, "Invalid username or password.")
    return render(request, "carbon/login.html")


def logout_view(request):
    LoyaltyService.disconnect(request)
    logout(request)
    messages.success(request, "Logged out successfully.")
    return redirect("login")


# Home

@login_required
def home_view(request):
    user_entries = CarbonEntry.objects.filter(user=request.user)
    entries = user_entries[:5]

    stats = user_entries.aggregate(
        total_emissions=Sum("emission_amount"),
        entry_count=Count("id"),
    )

    total_emissions = stats["total_emissions"] or 0
    entry_count = stats["entry_count"] or 0

    breakdown = user_entries.values("activity_type").annotate(
        total=Sum("emission_amount"), count=Count("id")
    ).order_by("-total")

    # Loyalty
    loyalty_balance = None
    loyalty_connected = LoyaltyService.is_connected(request)
    loyalty_value_eur = None
    conversion_rate = "100 points = €10"

    if loyalty_connected:
        balance_result = LoyaltyService.get_balance(request)
        if balance_result.get("success"):
            loyalty_balance = balance_result["data"]
            points = loyalty_balance.get("total_points", 0)
            loyalty_value_eur = points / 10

    # UK Carbon Intensity
    carbon_intensity = CarbonIntensityService.get_current_intensity()

    context = {
        "entries": entries,
        "total_emissions": total_emissions,
        "entry_count": entry_count,
        "breakdown": breakdown,
        "loyalty_connected": loyalty_connected,
        "loyalty_balance": loyalty_balance,
        "loyalty_value_eur": loyalty_value_eur,
        "conversion_rate": conversion_rate,
        "carbon_intensity": carbon_intensity,
    }

    return render(request, "carbon/home.html", context)


# Loyalty

@login_required
def loyalty_connect_view(request):
    if request.method == "POST":
        action = request.POST.get("action")
        username = request.POST.get("username")
        password = request.POST.get("password")

        if action == "login":
            result = LoyaltyService.connect_user(request, username, password)
        elif action == "register":
            email = request.POST.get("email", request.user.email)
            result = LoyaltyService.register_and_connect(
                request, username, email, password, request.user.first_name, request.user.last_name
            )
        else:
            result = {"success": False, "error": "Invalid action"}

        if result["success"]:
            messages.success(request, "Connected to Loyalty Points!")
            return redirect("home")
        else:
            messages.error(request, f"Failed: {result['error']}")

    return render(
        request,
        "carbon/loyalty_connect.html",
        {"loyalty_connected": LoyaltyService.is_connected(request)},
    )


@login_required
def loyalty_disconnect_view(request):
    LoyaltyService.disconnect(request)
    messages.success(request, "Disconnected from Loyalty Points.")
    return redirect("home")


@login_required
def loyalty_dashboard_view(request):
    summary_result = LoyaltyService.get_summary(request)
    transactions_result = LoyaltyService.get_transactions(request)
    leaderboard_result = LoyaltyService.get_leaderboard()

    context = {
        "summary": summary_result.get("data") if summary_result.get("success") else None,
        "transactions": transactions_result.get("data", []) if transactions_result.get("success") else [],
        "leaderboard": leaderboard_result.get("data", []) if leaderboard_result.get("success") else [],
        "loyalty_connected": LoyaltyService.is_connected(request),
    }
    return render(request, "carbon/loyalty_dashboard.html", context)


# Caarbon CRUD entries

@login_required
def entry_list(request):
    entries = CarbonEntry.objects.filter(user=request.user)
    activity = request.GET.get("activity")
    if activity:
        entries = entries.filter(activity_type=activity)
    total_emissions = entries.aggregate(total=Sum("emission_amount"))["total"] or 0
    return render(
        request,
        "carbon/entry_list.html",
        {"entries": entries, "total_emissions": total_emissions, "selected_activity": activity},
    )


@login_required
def entry_create(request):
    if request.method == "POST":
        form = CarbonEntryForm(request.POST)
        if form.is_valid():
            entry = form.save(commit=False)
            entry.user = request.user
            entry.save()

            # Loyalty points
            points_result = LoyaltyService.award_points_for_entry(request, entry)

            # CloudMail email
            email_result = None
            if request.user.email:
                subject = "Carbon Entry Recorded"
                message = f"""
Hello {request.user.first_name},

Your carbon activity has been successfully recorded in CarbonCloud.

Activity Type: {entry.activity_type}
CO₂ Amount: {entry.emission_amount} kg
Date: {entry.date}

Thank you for helping reduce carbon emissions!

— CarbonCloud Team
"""
                email_result = CloudMailService.send_email(
                    to_email=request.user.email, subject=subject, message=message
                )

            # User feedback
            if points_result.get("success"):
                pts = points_result["data"].get("points_earned", 0)
                messages.success(request, f"Entry saved! You earned {pts} loyalty points.")
            elif LoyaltyService.is_connected(request):
                messages.warning(request, f"Entry saved, but points failed: {points_result.get('error')}")
            else:
                messages.success(request, "Entry saved! Connect to Loyalty to earn rewards.")

            if email_result and not email_result.get("success"):
                messages.warning(request, f"Entry saved but email failed: {email_result.get('error')}")

            return redirect("entry-list")
    else:
        form = CarbonEntryForm()

    return render(request, "carbon/entry_create.html", {"form": form})


@login_required
def entry_update(request, pk):
    entry = get_object_or_404(CarbonEntry, pk=pk, user=request.user)
    if request.method == "POST":
        form = CarbonEntryForm(request.POST, instance=entry)
        if form.is_valid():
            form.save()
            messages.success(request, "Entry updated.")
            return redirect("entry-list")
    else:
        form = CarbonEntryForm(instance=entry)
    return render(request, "carbon/entry_update.html", {"form": form, "entry": entry})


@login_required
def entry_delete(request, pk):
    entry = get_object_or_404(CarbonEntry, pk=pk, user=request.user)
    if request.method == "POST":
        entry.delete()
        messages.success(request, "Entry deleted.")
        return redirect("entry-list")
    return render(request, "carbon/entry_delete.html", {"entry": entry})