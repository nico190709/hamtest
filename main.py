from flask import Flask, jsonify, request
from flask_cors import CORS
import google.generativeai as genai
import os
import json
from dotenv import load_dotenv

# .env Datei laden
load_dotenv()

app = Flask(__name__)
CORS(app)

# Wissensdatenbank aus JSON-Datei laden
def load_knowledge_base():
    """Lädt die Wissensdatenbank aus knowledge.json"""
    try:
        with open('knowledge.json', 'r', encoding='utf-8') as f:
            knowledge = json.load(f)
        print("✅ Wissensdatenbank aus knowledge.json geladen")
        return knowledge
    except FileNotFoundError:
        print("❌ knowledge.json nicht gefunden - verwende Fallback-Datenbank")
        return create_fallback_knowledge()
    except json.JSONDecodeError:
        print("❌ Fehler beim Parsen der knowledge.json - verwende Fallback-Datenbank")
        return create_fallback_knowledge()

def create_fallback_knowledge():
    """Erstellt eine Fallback-Wissensdatenbank falls JSON-Datei nicht verfügbar"""
    return {
        "reisen": {
            "bahn": {
                "co2_pro_km": 0.032,
                "vorteile": ["Niedrigste CO2-Emissionen", "Produktiv während der Fahrt"],
                "tipps": ["Bahncard nutzen", "Frühbucher-Rabatte"]
            }
        },
        "meetings": {
            "virtuell": {
                "co2_ersparnis": "95% weniger als Präsenz",
                "tools": ["Teams", "Zoom", "Google Meet"]
            }
        }
    }

# Wissensdatenbank beim Start laden
SUSTAINABILITY_KNOWLEDGE = load_knowledge_base()

def setup_gemini():
    """Konfiguriert Gemini API für Nachhaltigkeits-Beratung"""
    api_key = os.getenv('GEMINI_API_KEY')
    if not api_key:
        raise ValueError("GEMINI_API_KEY environment variable not set")

    genai.configure(api_key=api_key)

    generation_config = {
        "temperature": 0.3,  # Konsistente, sachliche Antworten
        "response_mime_type": "application/json",
        "max_output_tokens": 1000
    }

    return genai.GenerativeModel(
        model_name="gemini-2.0-flash-exp",
        generation_config=generation_config
    )

# Gemini Model initialisieren
try:
    gemini_model = setup_gemini()
    print("✅ GreenBot Gemini API erfolgreich konfiguriert")
except Exception as e:
    print(f"❌ Fehler bei Gemini Setup: {e}")
    gemini_model = None

def get_relevant_knowledge(query):
    """Extrahiert relevante Informationen aus der Wissensdatenbank"""
    query_lower = query.lower()
    relevant_data = {}
    
    # Reise-Themen
    if any(word in query_lower for word in ['reise', 'fahren', 'fliegen', 'bahn', 'auto', 'berlin', 'münchen']):
        if 'reisen' in SUSTAINABILITY_KNOWLEDGE:
            relevant_data['reisen'] = SUSTAINABILITY_KNOWLEDGE['reisen']
    
    # Meeting-Themen
    if any(word in query_lower for word in ['meeting', 'konferenz', 'zoom', 'teams', 'hybrid']):
        if 'meetings' in SUSTAINABILITY_KNOWLEDGE:
            relevant_data['meetings'] = SUSTAINABILITY_KNOWLEDGE['meetings']
    
    # Büromaterial-Themen
    if any(word in query_lower for word in ['stift', 'papier', 'büromaterial', 'kugelschreiber', 'ordner']):
        if 'buero_material' in SUSTAINABILITY_KNOWLEDGE:
            relevant_data['buero_material'] = SUSTAINABILITY_KNOWLEDGE['buero_material']
    
    # Energie-Themen
    if any(word in query_lower for word in ['energie', 'strom', 'heizung', 'licht', 'computer']):
        if 'energie' in SUSTAINABILITY_KNOWLEDGE:
            relevant_data['energie'] = SUSTAINABILITY_KNOWLEDGE['energie']
    
    # Kantinen-Themen
    if any(word in query_lower for word in ['kantine', 'essen', 'food', 'mensa', 'catering']):
        if 'kantine' in SUSTAINABILITY_KNOWLEDGE:
            relevant_data['kantine'] = SUSTAINABILITY_KNOWLEDGE['kantine']
    
    return relevant_data

def reload_knowledge_base():
    """Lädt die Wissensdatenbank neu (für Live-Updates)"""
    global SUSTAINABILITY_KNOWLEDGE
    SUSTAINABILITY_KNOWLEDGE = load_knowledge_base()
    return SUSTAINABILITY_KNOWLEDGE

@app.route('/')
def landing_page():
    """GreenBot Hauptseite"""
    return jsonify({
        "message": "🌱 GreenBot - Nachhaltigkeits-Assistent",
        "version": "1.0.0",
        "purpose": "Hilft bei nachhaltigen Entscheidungen im Büroalltag",
        "endpoints": {
            "/": "API Information",
            "/ai/sustainability/<message>": "Nachhaltigkeits-Beratung",
            "/knowledge": "Wissensdatenbank anzeigen",
            "/knowledge/reload": "Wissensdatenbank neu laden",
            "/health": "Health Check"
        },
        "status": "🌿 Bereit für grüne Beratung"
    })

@app.route('/knowledge')
def show_knowledge():
    """Zeigt die Wissensdatenbank"""
    return jsonify({
        "knowledge_base": SUSTAINABILITY_KNOWLEDGE,
        "categories": list(SUSTAINABILITY_KNOWLEDGE.keys()),
        "total_entries": sum(len(v) if isinstance(v, dict) else 1 for v in SUSTAINABILITY_KNOWLEDGE.values()),
        "source": "knowledge.json"
    })

@app.route('/knowledge/reload', methods=['POST'])
def reload_knowledge():
    """Lädt die Wissensdatenbank neu"""
    try:
        old_count = len(SUSTAINABILITY_KNOWLEDGE)
        new_knowledge = reload_knowledge_base()
        new_count = len(new_knowledge)
        
        return jsonify({
            "message": "✅ Wissensdatenbank erfolgreich neu geladen",
            "old_categories": old_count,
            "new_categories": new_count,
            "categories": list(new_knowledge.keys()),
            "timestamp": "2025-07-05T13:25:00Z"
        })
    except Exception as e:
        return jsonify({
            "error": f"Fehler beim Neuladen: {str(e)}",
            "message": "Wissensdatenbank konnte nicht neu geladen werden"
        }), 500

@app.route('/health')
def health_check():
    """Health Check für GreenBot"""
    return jsonify({
        "status": "🌱 healthy",
        "gemini_available": gemini_model is not None,
        "knowledge_base_loaded": len(SUSTAINABILITY_KNOWLEDGE) > 0,
        "knowledge_source": "knowledge.json",
        "categories_loaded": list(SUSTAINABILITY_KNOWLEDGE.keys()),
        "timestamp": "2025-07-05T13:25:00Z"
    })

@app.route('/ai/sustainability/<path:message>')
def sustainability_chat(message):
    """
    Hauptendpunkt für Nachhaltigkeits-Beratung
    Kombiniert AI mit vordefinierter Wissensdatenbank aus JSON
    """
    if not gemini_model:
        return jsonify({
            "error": "Gemini API nicht verfügbar",
            "details": "API-Schlüssel fehlt oder ungültig"
        }), 503
    
    try:
        SUSTAINABILITY_KNOWLEDGE = load_knowledge_base()
        # Relevante Wissensdatenbank-Einträge finden
        relevant_knowledge = get_relevant_knowledge(message)
        
        # Erweiterte Prompt-Engineering für Nachhaltigkeit
        sustainability_prompt = f"""
Du bist GreenBot, ein spezialisierter Nachhaltigkeits-Assistent für Büroalltag.

WICHTIGE REGELN:
- Fokus auf Nachhaltigkeit und Umweltschutz
- Gib konkrete, umsetzbare Tipps
- Verwende NICHT den Namen des Nutzers
- Sei freundlich aber sachlich
- Bevorzuge immer die umweltfreundlichste Option
- Nutze die bereitgestellte Wissensdatenbank aus knowledge.json

WISSENSDATENBANK (aus knowledge.json):
{json.dumps(relevant_knowledge, indent=2, ensure_ascii=False)}

NACHHALTIGKEITS-PRINZIPIEN:
1. Vermeiden: Unnötige Aktivitäten reduzieren
2. Verringern: Ressourcenverbrauch minimieren  
3. Wiederverwenden: Materialien mehrfach nutzen
4. Recyceln: Kreislaufwirtschaft fördern

BENUTZER-FRAGE: {message}

Antworte im JSON-Format mit konkreten Handlungsempfehlungen:
{{
    "answer": "Deine strukturierte Antwort mit konkreten Tipps",
    "sustainability_score": "Bewertung 1-10 der Umweltfreundlichkeit",
    "action_items": ["Konkrete Handlungsschritte"],
    "co2_impact": "Geschätzte CO2-Einsparung falls relevant"
}}
"""
        
        response = gemini_model.generate_content(sustainability_prompt)
        
        try:
            parsed_response = json.loads(response.text)
            return jsonify({"response": parsed_response})
        except json.JSONDecodeError:
            # Fallback für ungültiges JSON
            return jsonify({
                "response": {
                    "answer": response.text,
                    "sustainability_score": "N/A",
                    "action_items": ["Antwort überprüfen"],
                    "co2_impact": "Nicht berechenbar"
                }
            })
            
    except Exception as e:
        print(f"GreenBot AI-Fehler: {str(e)}")
        return jsonify({
            "error": f"AI-Fehler: {str(e)}",
            "fallback_response": "Entschuldigung, ich konnte deine Nachhaltigkeitsfrage nicht verarbeiten. Versuche es bitte nochmal! 🌱"
        }), 500

# Fehlerbehandlung
@app.errorhandler(404)
def not_found(error):
    return jsonify({
        "error": "Endpoint nicht gefunden",
        "message": "Verfügbare Endpunkte: /, /health, /knowledge, /knowledge/reload, /ai/sustainability/<message>",
        "tip": "🌱 Frage mich zu Nachhaltigkeit im Büro!"
    }), 404

@app.errorhandler(500)
def internal_error(error):
    return jsonify({
        "error": "Interner Serverfehler",
        "message": "Etwas ist schiefgelaufen. Versuche es später nochmal.",
        "support": "🌱 GreenBot Support"
    }), 500

if __name__ == '__main__':
    print("🌱 Starte GreenBot - Nachhaltigkeits-Assistent...")
    print(f"📡 Server läuft auf: http://0.0.0.0:3000")
    print(f"🔑 Gemini API: {'✅ Verfügbar' if gemini_model else '❌ Nicht verfügbar'}")
    print(f"📚 Wissensdatenbank: {len(SUSTAINABILITY_KNOWLEDGE)} Kategorien aus knowledge.json geladen")
    print(f"📂 Kategorien: {', '.join(SUSTAINABILITY_KNOWLEDGE.keys())}")
    
    app.run(debug=True, host='0.0.0.0', port=3000)
