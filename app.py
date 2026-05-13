import os
import hmac
import hashlib
import json
import requests
from flask import Flask, request, jsonify
import google.generativeai as genai

app = Flask(__name__)

# ── Configuration ─────────────────────────────────────────────────────────────
GEMINI_API_KEY      = os.environ.get("GEMINI_API_KEY")
PAGE_ACCESS_TOKEN   = os.environ.get("PAGE_ACCESS_TOKEN")
APP_SECRET          = os.environ.get("APP_SECRET")
VERIFY_TOKEN        = os.environ.get("VERIFY_TOKEN", "myanmar_souvenir_verify_2024")

genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel("gemini-1.5-flash")

# ── Stock Knowledge Base ───────────────────────────────────────────────────────
STOCK_DATA = """
MYANMAR SOUVENIR SHOP — FULL STOCK LIST

=== ENAMEL TIFFIN CARRIERS ===

Mohinga Single-Tier (14.5cm) — 58,000 MMK each:
- Premium Blue: In Stock (15 pcs)
- Forest Green: In Stock (14 pcs)
- Pastel Pink: In Stock (13 pcs)
- Hot Pink: In Stock (10 pcs)
- Sunset Orange: In Stock (12 pcs)
- Turquoise: In Stock (12 pcs)

Classic Single-Tier (14cm) — 58,000 MMK each:
- Neutral Lavender, Pastel Blue, Premium Blue, Light Pink, Rare Violet: Low Stock (1 pc each)
- Soft Yellow, Super Lemon, Hot Pink, Pastel Lavender, Pale Sage Green: Low Stock

Classic 2-Tier (11cm) — 48,000 MMK each:
- Super Lemon: Low Stock (2 pcs)
- Mix Color: Low Stock (various 1-7 pcs)

Classic 3-Tier (11cm) — 65,000 MMK each:
- Lavender Theme: In Stock (11 pcs)
- Pink Theme: In Stock (11 pcs)
- Mix Color: In Stock (14 pcs)
- Sticker versions (Girl, Cry Baby, Stitch, Pink Flower): Low Stock (1 pc each)

Cup Style 3-Tier (12cm) — 65,000 MMK each:
- Mix Color: In Stock (6 pcs)

Classic 4-Tier (11cm) — 78,000 MMK each:
- White: In Stock (7 pcs)

Classic 5-Tier (14cm) — 120,000 MMK each:
- Mix Color: Low Stock (4-5 pcs)

=== BLIND BOX MYANMAR PALACE SERIES ===

Size M (4 inches, Resin) — 77,000 MMK each — In Stock (100 pcs each):
- 01 Queen Irra
- 02 Tha Nak Khar Princess
- 03 Innwa Warrior
- 04 Poppa Zaw Gyi
- 05 Yin Laung Heir
- 06 Rangoon Prince
- Secret 01 King
- Secret 02 Phoe Wa

Size L (8 inches, Resin) — 250,000 MMK each — In Stock (10 pcs each):
- Same 8 characters as Size M above

=== BLIND BOX SUPPORT CHARMS ===
- 01 Owl (2cm): 5,000 MMK — In Stock (500 pcs)
- 02 Pyit Taing Htaung (2cm): 5,000 MMK — In Stock (500 pcs)
- 03 Giraffe (2.5cm): 5,000 MMK — In Stock (300 pcs)
- 04 Cow (1.5cm): 5,000 MMK — In Stock (300 pcs)
- 05 Myanmar Map (1.5cm): 6,500 MMK — In Stock (300 pcs)

=== WOODEN PRODUCTS ===
- Wooden Owe Pote Set (20 pcs): 50,000 MMK — In Stock (120 sets)
- Wooden Plane Toy: 18,000 MMK — In Stock (130 pcs)
- Wooden Luxury Ball Pen & Bamboo Case: 65,000 MMK — In Stock (45 pcs)
- Wooden Tray Size S: 25,000 MMK — In Stock (10 pcs)
- Wooden Tray Size M: 32,000 MMK — Low Stock (3 pcs)
- Wooden Folk and Spoon: 6,000 MMK — In Stock
- Comb (Bimga Wood): 6,000 MMK — In Stock
- Luxury Padauk Phone Stand: 35,000 MMK — In Stock
- Wooden Toothpicks Holder: 18,000 MMK — In Stock (5 pcs)
- Wooden Soap Plate: 15,000 MMK — In Stock
- Wooden Visiting Card Holder: 15,000 MMK — In Stock
- Wooden Clock Violin Style: 65,000 MMK — In Stock
- Prayer Book Stand (Kokko): 50,000–110,000 MMK — In Stock
- Wooden Display Stand Circle/Square: 60,000 MMK each

=== WOODEN JEWEL CASES ===
- Rectangle Mahogany Jewel Case (Big): 28,000 MMK — In Stock (10 pcs)
- Square Double Window Mahogany Jewel Case (Small): 15,000 MMK — In Stock (10 pcs)
- Heart Mahogany Jewel Case (Small): 15,000 MMK — In Stock (10 pcs)
- Heart Double Boxes Mahogany Jewel Case: 10,000 MMK — In Stock (10 pcs)
- Luxury Kokko Jewel Chest Drawer (Size L): 120,000 MMK — In Stock (15 pcs)
- Luxury Padauk Jewel Chest Drawer (Size M): 110,000 MMK — Low Stock (2 pcs)
- Luxury Padauk Jewel Chest Drawer (Size S): 100,000 MMK — Low Stock (2 pcs)

=== BAMBOO PACKAGING ===
- Luxury Bamboo Box Rectangle (L, 12x10x7cm): 45,000 MMK — In Stock (10 pcs)
- Bamboo Box Rectangle (M): 7,500 MMK — In Stock (10 pcs)
- Bamboo Basket Style (L): 6,000 MMK — Low Stock (3 pcs)
- Bamboo Basket Style (S): 4,500 MMK — Low Stock (3 pcs)
- Bamboo School Basket: 4,000 MMK — Low Stock (5 pcs)
- Bamboo Tiffin Basket with Cover & Handle: 16,000 MMK — In Stock (10 pcs)

=== ENAMEL OTHER ITEMS ===
- Enamel Spoon + Fork Set: 15,000 MMK — In Stock (30 sets)
- Enamel Short Spoon: 6,500 MMK — In Stock (100+ pcs)
- Enamel Budget Plate: 6,500 MMK — In Stock (20 pcs)
- Enamel Hi Tea Set (Kettle + Big Plate + 2 Teacups): 75,000 MMK — In Stock
- Enamel Lat Phet Bowl with Handle+Cover (S): 28,000 MMK — In Stock
- Enamel Lat Phet Bowl with Handle+Cover (M): 35,000 MMK — In Stock
- Enamel Curry Bowl with Handle+Cover (M): 48,000 MMK — In Stock
- Enamel Rice Bowl with Handle+Cover: 65,000 MMK — In Stock
- Enamel Budget Noodle Shop Bowl (13cm): 15,000–18,000 MMK — In Stock
- Budget Enamel Steel Handcarry 2-Tier: 38,000 MMK — In Stock
- Budget Enamel Mug with Cover: 35,000 MMK — In Stock
- Budget Enamel Mug with Plate: 10,000–18,000 MMK — In Stock
- Budget Giant Enamel Mug with Cover: 18,000 MMK — In Stock
- Budget 90s Enamel Mug with Cover: 18,000 MMK — In Stock

=== MIRROR & ACCESSORIES ===
- Mirror Stand Styler from Kyone Pyaw (Kokko): 35,000 MMK — In Stock (25 pcs)

=== PAPER MACHE & DOLLS ===
- Mache Pyit Taing Htaung Money Bank (5 inches): 18,000 MMK — In Stock (Red/Pink/Soft Grey)
- Paper Mache Pyit Taing Htaung (3 inches): 5,500 MMK — In Stock (Pink/Blue/Grey/Red)
- Paper Mache Myanmar Ethnic Doll (4 inches): 18,000 MMK — In Stock (10 pcs)
- Sample Paper Mache Ethnic Doll (no coloring): 10,000 MMK — In Stock (20 pcs)
- Sample Paper Mache Paper Doll (3 inches): 3,800 MMK — In Stock (10 pcs)
- Surprise Paper Mache Gift Box (12 items, cannot choose): 50,000 MMK — In Stock (10 boxes)
- Special 90s Doh Ywer Surprise Blind Box Set (Big Box, cannot choose): 100,000 MMK — In Stock (20 sets)
"""

SYSTEM_PROMPT = f"""You are a helpful and friendly customer service assistant for a Myanmar souvenir shop.
Your job is to answer customer questions about products, prices, colors, stock availability, and anything related to the shop.

IMPORTANT LANGUAGE RULE:
- If the customer writes in Burmese (Myanmar language), you MUST reply in Burmese.
- If the customer writes in English, reply in English.
- If they mix both languages, reply in Burmese.

Here is the complete stock information for the shop:

{STOCK_DATA}

Guidelines:
- Be warm, friendly and helpful like a real shop assistant
- If a product is Low Stock, mention it politely and suggest they order soon
- If asked about something not in the stock list, say you don't have it currently
- Always mention the price when talking about a product
- Keep replies short and easy to read on a phone screen
- Use line breaks to make lists readable
- Never make up products or prices not in the list above
"""

# ── Gemini AI Response ─────────────────────────────────────────────────────────
def get_ai_response(user_message):
    try:
        full_prompt = SYSTEM_PROMPT + f"\n\nCustomer message: {user_message}"
        response = model.generate_content(full_prompt)
        return response.text
    except Exception as e:
        print(f"Gemini error: {e}")
        return "မင်္ဂလာပါ! Sorry, I'm having a little trouble right now. Please try again in a moment. 🙏"

# ── Send message back to Messenger ────────────────────────────────────────────
def send_message(recipient_id, message_text):
    # Split long messages (Messenger limit is 2000 chars)
    chunks = [message_text[i:i+1900] for i in range(0, len(message_text), 1900)]
    for chunk in chunks:
        payload = {
            "recipient": {"id": recipient_id},
            "message": {"text": chunk}
        }
        requests.post(
            f"https://graph.facebook.com/v18.0/me/messages?access_token={PAGE_ACCESS_TOKEN}",
            json=payload
        )

# ── Webhook verification (Facebook requires this) ─────────────────────────────
@app.route("/webhook", methods=["GET"])
def verify_webhook():
    token = request.args.get("hub.verify_token")
    challenge = request.args.get("hub.challenge")
    if token == VERIFY_TOKEN:
        return challenge, 200
    return "Verification failed", 403

# ── Receive messages from Messenger ───────────────────────────────────────────
@app.route("/webhook", methods=["POST"])
def receive_message():
    # Verify the request is from Facebook
    signature = request.headers.get("X-Hub-Signature-256", "")
    body = request.get_data()
    expected = "sha256=" + hmac.new(APP_SECRET.encode(), body, hashlib.sha256).hexdigest()
    if not hmac.compare_digest(signature, expected):
        return "Invalid signature", 403

    data = request.json
    if data.get("object") == "page":
        for entry in data.get("entry", []):
            for event in entry.get("messaging", []):
                sender_id = event["sender"]["id"]
                if "message" in event and "text" in event["message"]:
                    user_text = event["message"]["text"]
                    print(f"Message from {sender_id}: {user_text}")
                    ai_reply = get_ai_response(user_text)
                    send_message(sender_id, ai_reply)
    return jsonify({"status": "ok"}), 200

# ── Health check ───────────────────────────────────────────────────────────────
@app.route("/")
def home():
    return "Myanmar Souvenir Bot is running! 🇲🇲"

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
