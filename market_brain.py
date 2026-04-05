import firebase_admin
from firebase_admin import credentials, db
import time
from nsepython import nse_quote_ltp

# 1. FIREBASE INITIALIZATION
if not firebase_admin._apps:
    try:
        cred = credentials.Certificate("serviceAccountKey.json")
        firebase_admin.initialize_app(cred, {
            'databaseURL': 'https://garg-enterprise-default-rtdb.asia-southeast1.firebasedatabase.app'
        })
    except Exception as e:
        print(f"CRITICAL ERROR: {e}")
        exit()

def get_market_analysis():
    """
    Advanced Engine: Tracks Nifty, Bank Nifty, and VIX 
    to determine if Calls or Puts are safe.
    """
    try:
        # PULLING MULTIPLE INDICES
        nifty = nse_quote_ltp("NIFTY 50")
        bank_nifty = nse_quote_ltp("NIFTY BANK")
        vix = nse_quote_ltp("INDIA VIX")
        
        # Scoring based on Index Correlation
        score = 0
        
        # Nifty & Bank Nifty alignment is strong for CALLs
        if nifty > 22600 and bank_nifty > 48000:
            score += 40 
        elif nifty < 22500 and bank_nifty < 47800:
            score -= 40

        # VIX Effect (High VIX kills Call confidence)
        if vix > 16: score -= 20
        else: score += 10

        # Verdict Logic
        if score >= 30:
            res = {"v": "CALL", "col": "#10b981", "msg": "Nifty + BankNifty Bullish"}
        elif score <= -30:
            res = {"v": "PUT", "col": "#ef4444", "msg": "Major Index Sell-off"}
        else:
            res = {"v": "WAIT", "col": "#94a3b8", "msg": "Indices Diverging"}

        return {
            **res,
            "nifty": nifty,
            "banknifty": bank_nifty,
            "vix": vix,
            "score": score,
            "strike": round(nifty / 50) * 50
        }

    except:
        return {"v": "WAIT", "nifty": 0, "banknifty": 0, "vix": 0, "score": 0, "strike": 0, "col": "#64748b", "msg": "NSE Syncing..."}

def start_brain():
    print("GARG AI: Tracking Multi-Index Trend...")
    while True:
        data = get_market_analysis()
        current_time = time.strftime("%H:%M:%S")
        
        # Sending all indices to Firebase for your Graph
        db.reference('/live_signal').set({
            "verdict": data['v'],
            "strike": data['strike'],
            "nifty": data['nifty'],
            "banknifty": data['banknifty'],
            "vix": data['vix'],
            "market_strength": data['score'], # Use this for your Graph!
            "color": data['col'],
            "scenario": data['msg'],
            "timestamp": current_time
        })
        
        print(f"[{current_time}] {data['v']} | Nifty: {data['nifty']} | VIX: {data['vix']}")
        time.sleep(20)

if __name__ == "__main__":
    start_brain()
