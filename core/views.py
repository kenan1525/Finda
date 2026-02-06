from django.shortcuts import render, redirect
from django.http import JsonResponse
from .utils import get_all_products
from .ai_service import analyze_products
from .chat_service import analyze_user_message


def home(request):
    if request.GET.get("new_chat") == "true":
        if 'chat_history' in request.session:
            del request.session['chat_history']
        return redirect('home')

    if 'chat_history' not in request.session:
        request.session['chat_history'] = []

    chat_history = request.session['chat_history']
    user_message = request.POST.get("query", "") or request.GET.get("query", "")
    compare_mode = request.GET.get("compare") == "true"  # Deep analysis modu

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
        "ai_summary": ai_summary,  # AI JSON (highlights, pros, cons, verdict)
        "user_message": user_message,
        "compare_mode": compare_mode
    })
