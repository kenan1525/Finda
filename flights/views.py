# from django.shortcuts import render
# from .services import search_flights


# def flight_search(request):
#     """Handle flight search POST and render the shared home template.

#     This view only coordinates input and passes results from services.search_flights
#     into the template under the `flights` context key.
#     """
#     context = {}

#     if request.method == "POST":
#         origin = (request.POST.get("origin") or "").strip().upper()
#         destination = (request.POST.get("destination") or "").strip().upper()
#         date = request.POST.get("date")
#         adults = request.POST.get("adults") or 1

#         try:
#             adults = int(adults)
#             if adults < 1:
#                 adults = 1
#         except (ValueError, TypeError):
#             adults = 1

#         if origin and destination and date:
#             results = search_flights(origin, destination, date, adults=adults)
#             context["flights"] = results
#         else:
#             context["flights"] = {"error": "missing_parameters"}

#     return render(request, "home.html", context)
from django.shortcuts import render
from django.core.cache import cache
from .services import search_flights

CACHE_TIMEOUT = 300  # 5 dakika

def flight_search(request):
    """Handle flight search POST and render the shared home template with cache."""
    context = {"show_flight_form": True}

    if request.method == "POST":
        origin = (request.POST.get("origin") or "").strip().upper()
        destination = (request.POST.get("destination") or "").strip().upper()
        date = request.POST.get("date")
        adults = request.POST.get("adults") or 1

        try:
            adults = int(adults)
            if adults < 1:
                adults = 1
        except (ValueError, TypeError):
            adults = 1

        if origin and destination and date:
            # Cache key: origin+destination+date+adults
            cache_key = f"flights_{origin}_{destination}_{date}_{adults}"
            cached_results = cache.get(cache_key)

            if cached_results:
                flights = cached_results
            else:
                results = search_flights(origin, destination, date, adults=adults)
                flights = results.get("data", {}).get("flights", [])
                cache.set(cache_key, flights, CACHE_TIMEOUT)

            context["flights"] = flights
        else:
            context["flights"] = []
            context["error"] = "Lütfen tüm alanları doldurun."

    return render(request, "home.html", context)
