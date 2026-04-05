import firebase_admin
from firebase_admin import credentials, db
import time
from nsepython import nse_quote_ltp

# 1. FIREBASE INITIALIZATION
# Ensure 'serviceAccountKey.json' is in your 'market' folder on the Desktop
if not firebase_admin._apps:
    try:
        cred = credentials.Certificate("serviceAccountKey.json")
        firebase_admin.initialize_app(cred, {
            'databaseURL': 'https://garg-enterprise-default-rtdb.asia-southeast1.firebasedatabase.app'
        })
    except Exception as e:
        print(f"CRITICAL ERROR: Could not load Firebase Key: {e}")
        exit()

def get_market_analysis():
    """
    Powerful Analysis Engine:
    Pulls live Nifty and VIX data and calculates a weighted verdict.
    """
    try:
        # AUTO-PICK Live Data from NSE
        nifty_spot = nse_quote_ltp("NIFTY 50")
        vix = nse_quote_ltp("INDIA VIX")
        
        # Determine ATM Strike Price (Nearest 50 points)
        atm_strike = round(nifty_spot / 50) * 50
        
        # SCORING SYSTEM (Base score of 0)
        score = 0
        reasons = []

        # Logic 1: Price Action Trend
        if nifty_spot > 22600: # Example Pivot Point
            score += 35
            reasons.append("Nifty Bullish Structure")
        else:
            score -= 35
            reasons.append("Nifty Under Pressure")

        # Logic 2: Volatility (The Fear Index)
        if vix < 15.5:
            score += 25
            reasons.append("Low Market Fear (VIX)")
        else:
            score -= 40
            reasons.append("High Volatility Danger")

        # LOGIC 3: Final Signal Determination
        if score >= 30:
            return {
                "v": "CALL", "s": atm_strike + 50, "c": f"{score}%", 
                "color": "#10b981", "msg": " & ".join(reasons), "nifty": nifty_spot
            }
        elif score <= -30:
            return {
                "v": "PUT", "s": atm_strike - 50, "c": f"{abs(score)}%", 
                "color": "#ef4444", "msg": " & ".join(reasons), "nifty": nifty_spot
            }
        else:
            return {
                "v": "WAIT", "s": "N/A", "c": "Low", 
                "color": "#94a3b8", "msg": "Mixed Signals - Sideways Market", "nifty": nifty_spot
            }

    except Exception as e:
        # If NSE website is busy/closed, provide safe fallback
        print(f"NSE Fetch Error (Likely Market Closed): {e}")
        return {
            "v": "WAIT", "s": "...", "c": "0%", 
            "color": "#64748b", "msg": "Waiting for NSE Live Data...", "nifty": "0.0"
        }

def start_brain():
    print("--------------------------------------------------")
    print("Starting GARG ENTERPRISE AI BRAIN v4.0 (PRO)")
    print("Frequency: 20 Seconds | Live NSE Data Tracking")
    print("--------------------------------------------------")
    
    while True:
        # 1. Run Analysis
        analysis = get_market_analysis()
        current_time = time.strftime("%H:%M:%S")
        
        # 2. Update Firebase Realtime Database
        try:
            db.reference('/live_signal').set({
                "verdict": analysis['v'],
                "strike": analysis['s'],
                "confidence": analysis['c'],
                "color": analysis['color'],
                "scenario": analysis['msg'],
                "nifty_spot": analysis['nifty'],
                "timestamp": current_time
            })
            
            # 3. Print status to your VS Code Terminal
            print(f"[{current_time}] {analysis['v']} | Nifty: {analysis['nifty']} | {analysis['msg']}")
            
        except Exception as e:
            print(f"Firebase Sync Error: {e}")

        # 4. 20-Second High-Frequency Loop
        time.sleep(20)

if __name__ == "__main__":
    start_brain()