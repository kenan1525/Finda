from django.shortcuts import render, redirect
from django.http import JsonResponse
from .utils import get_all_products
from .ai_service import analyze_products
from .chat_service import analyze_user_message
from .intent import detect_flight_intent
from flights.services import search_flights


def home(request):
    if request.GET.get("new_chat") == "true":
        if 'chat_history' in request.session:
            del request.session['chat_history']
        if 'flight_results' in request.session:
            del request.session['flight_results']
        if 'flight_form_data' in request.session:
            del request.session['flight_form_data']
        if 'show_flight_section' in request.session:
            del request.session['show_flight_section']
        return redirect('home')

    if 'chat_history' not in request.session:
        request.session['chat_history'] = []

    chat_history = request.session['chat_history']
    user_message = request.POST.get("query", "") or request.GET.get("query", "")
    compare_mode = request.GET.get("compare") == "true"  # Deep analysis modu
    
    # Flight state (persist on page until new chat)
    flight_results = request.session.get("flight_results")
    flight_form_data = request.session.get("flight_form_data", {})
    show_flight_section = request.session.get("show_flight_section", False)
    flight_scroll = request.session.pop("flight_scroll", False)
    origin = request.POST.get("origin", "").strip().upper()
    destination = request.POST.get("destination", "").strip().upper()
    date = request.POST.get("date", "")
    adults_input = request.POST.get("adults", "1")
    
    # If flight form is submitted, process it
    if origin and destination and date and not user_message:
        try:
            adults = int(adults_input) if adults_input else 1
            adults = max(1, adults)
        except (ValueError, TypeError):
            adults = 1
        
        flight_results = search_flights(origin, destination, date, adults=adults)
        flight_form_data = {
            "origin": origin,
            "destination": destination,
            "date": date,
            "adults": adults
        }
        show_flight_section = True
        request.session["flight_results"] = flight_results
        request.session["flight_form_data"] = flight_form_data
        request.session["show_flight_section"] = True
        request.session["flight_scroll"] = True

    # Check for flight intent - if detected, don't process as product search
    if user_message:
        flight_check = detect_flight_intent(user_message)
        if flight_check['is_flight'] and flight_check['confidence'] > 0.7:
            # This is a flight query, don't add to chat history for products
            show_flight_section = True
            request.session["show_flight_section"] = True
            return render(request, "home.html", {
                "chat_history": chat_history,
                "products": [],
                "ai_summary": {},
                "user_message": "",
                "compare_mode": compare_mode,
                "flight_intent_detected": True,
                "flight_query": user_message,
                "flight_results": None,
                "flight_form_data": flight_form_data,
                "show_flight_section": True
            })

    results = []
    ai_summary = {}

    if user_message:
        chat_history.append({
            'role': 'user',
            'content': user_message
        })

        analysis = analyze_user_message(user_message, chat_history)

        if analysis.get('error'):
            chat_history.append({
                'role': 'assistant',
                'content': f"Üzgünüm, bir hata oluştu: {analysis['error']}"
            })

        elif analysis['intent'] == 'shopping' and analysis.get('query'):
            query = analysis['query']
            products = get_all_products(query, compare_mode=compare_mode)

            if products:
                # 🔹 AI ürün etiketleme + analiz
                ai_result = analyze_products(products)

                results = ai_result.get("products", products)
                ai_summary = ai_result # Full result passes 'data', 'error', etc.

                if compare_mode:
                    # COMPARE MODE: Sonuncu assistant message'ına compare_products ekle
                    # Böyle orijinal products kaybolmaz
                    for msg in reversed(chat_history):
                        if msg.get('role') == 'assistant' and msg.get('products'):
                            msg['compare_products'] = results
                            msg['compare_ai_summary'] = ai_summary
                            break
                else:
                    # NORMAL MODE: Yeni message oluştur
                    chat_history.append({
                        'role': 'assistant',
                        'content': analysis['response'] or f'"{query}" için {len(results)} ürün buldum:',
                        'products': results,
                        'ai_summary': ai_summary
                    })

            else:
                chat_history.append({
                    'role': 'assistant',
                    'content': f'"{query}" için ürün bulunamadı. Başka bir şey aramak ister misiniz?'
                })

        else:
            chat_history.append({
                'role': 'assistant',
                'content': analysis['response']
            })

        request.session['chat_history'] = chat_history
        request.session.modified = True

    return render(request, "home.html", {
        "chat_history": chat_history,
        "results": results,      # etiketli ürünler
        "products": results,
        "ai_summary": ai_summary,  # AI JSON (highlights, pros, cons, verdict)
        "user_message": user_message,
        "compare_mode": compare_mode,
        "flight_results": flight_results,  # Flight search results if any
        "flight_form_data": flight_form_data,  # Form values to repopulate
        "show_flight_section": show_flight_section,
        "flight_scroll": flight_scroll
    })
