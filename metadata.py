# Auto-generated flight dataset metadata & smart route helpers
import re

AIRLINES = [
  "Air Asia",
  "Air India",
  "GoAir",
  "IndiGo",
  "Jet Airways",
  "Jet Airways Business",
  "Multiple carriers",
  "Multiple carriers Premium economy",
  "SpiceJet",
  "Trujet",
  "Vistara",
  "Vistara Premium economy"
]

SOURCES = [
  "Banglore",
  "Chennai",
  "Delhi",
  "Kolkata",
  "Mumbai"
]

DESTINATIONS = [
  "Banglore",
  "Cochin",
  "Delhi",
  "Hyderabad",
  "Kolkata",
  "New Delhi"
]

ADDITIONAL_INFO = [
  "1 Long layover",
  "1 Short layover",
  "2 Long layover",
  "Business class",
  "Change airports",
  "In-flight meal not included",
  "No Info",
  "No check-in baggage included",
  "No info",
  "Red-eye flight"
]

ALL_ROUTES = [
  "BLR \u2192 AMD \u2192 DEL",
  "BLR \u2192 BBI \u2192 DEL",
  "BLR \u2192 BDQ \u2192 DEL",
  "BLR \u2192 BOM \u2192 AMD \u2192 DEL",
  "BLR \u2192 BOM \u2192 BHO \u2192 DEL",
  "BLR \u2192 BOM \u2192 DEL",
  "BLR \u2192 BOM \u2192 IDR \u2192 DEL",
  "BLR \u2192 BOM \u2192 IDR \u2192 GWL \u2192 DEL",
  "BLR \u2192 BOM \u2192 IXC \u2192 DEL",
  "BLR \u2192 BOM \u2192 JDH \u2192 DEL",
  "BLR \u2192 BOM \u2192 NAG \u2192 DEL",
  "BLR \u2192 BOM \u2192 UDR \u2192 DEL",
  "BLR \u2192 CCU \u2192 BBI \u2192 DEL",
  "BLR \u2192 CCU \u2192 BBI \u2192 HYD \u2192 DEL",
  "BLR \u2192 CCU \u2192 BBI \u2192 HYD \u2192 VGA \u2192 DEL",
  "BLR \u2192 CCU \u2192 DEL",
  "BLR \u2192 CCU \u2192 GAU \u2192 DEL",
  "BLR \u2192 COK \u2192 DEL",
  "BLR \u2192 DEL",
  "BLR \u2192 GAU \u2192 DEL",
  "BLR \u2192 GOI \u2192 DEL",
  "BLR \u2192 HBX \u2192 BOM \u2192 AMD \u2192 DEL",
  "BLR \u2192 HBX \u2192 BOM \u2192 BHO \u2192 DEL",
  "BLR \u2192 HBX \u2192 BOM \u2192 NAG \u2192 DEL",
  "BLR \u2192 HYD \u2192 DEL",
  "BLR \u2192 HYD \u2192 VGA \u2192 DEL",
  "BLR \u2192 IDR \u2192 DEL",
  "BLR \u2192 LKO \u2192 DEL",
  "BLR \u2192 MAA \u2192 DEL",
  "BLR \u2192 NAG \u2192 DEL",
  "BLR \u2192 PNQ \u2192 DEL",
  "BLR \u2192 STV \u2192 DEL",
  "BLR \u2192 TRV \u2192 COK \u2192 DEL",
  "BLR \u2192 VGA \u2192 DEL",
  "BLR \u2192 VGA \u2192 HYD \u2192 DEL",
  "BLR \u2192 VGA \u2192 VTZ \u2192 DEL",
  "BOM \u2192 AMD \u2192 ISK \u2192 HYD",
  "BOM \u2192 BBI \u2192 HYD",
  "BOM \u2192 BDQ \u2192 DEL \u2192 HYD",
  "BOM \u2192 BHO \u2192 DEL \u2192 HYD",
  "BOM \u2192 BLR \u2192 CCU \u2192 BBI \u2192 HYD",
  "BOM \u2192 BLR \u2192 HYD",
  "BOM \u2192 CCU \u2192 HYD",
  "BOM \u2192 COK \u2192 MAA \u2192 HYD",
  "BOM \u2192 DED \u2192 DEL \u2192 HYD",
  "BOM \u2192 DEL \u2192 HYD",
  "BOM \u2192 GOI \u2192 HYD",
  "BOM \u2192 GOI \u2192 PNQ \u2192 HYD",
  "BOM \u2192 HYD",
  "BOM \u2192 IDR \u2192 DEL \u2192 HYD",
  "BOM \u2192 JAI \u2192 DEL \u2192 HYD",
  "BOM \u2192 JDH \u2192 DEL \u2192 HYD",
  "BOM \u2192 JDH \u2192 JAI \u2192 DEL \u2192 HYD",
  "BOM \u2192 JLR \u2192 HYD",
  "BOM \u2192 MAA \u2192 HYD",
  "BOM \u2192 NDC \u2192 HYD",
  "BOM \u2192 RPR \u2192 VTZ \u2192 HYD",
  "BOM \u2192 UDR \u2192 DEL \u2192 HYD",
  "BOM \u2192 VNS \u2192 DEL \u2192 HYD",
  "CCU \u2192 AMD \u2192 BLR",
  "CCU \u2192 BBI \u2192 BLR",
  "CCU \u2192 BBI \u2192 BOM \u2192 BLR",
  "CCU \u2192 BBI \u2192 HYD \u2192 BLR",
  "CCU \u2192 BBI \u2192 IXR \u2192 DEL \u2192 BLR",
  "CCU \u2192 BLR",
  "CCU \u2192 BOM \u2192 AMD \u2192 BLR",
  "CCU \u2192 BOM \u2192 BLR",
  "CCU \u2192 BOM \u2192 COK \u2192 BLR",
  "CCU \u2192 BOM \u2192 GOI \u2192 BLR",
  "CCU \u2192 BOM \u2192 HBX \u2192 BLR",
  "CCU \u2192 BOM \u2192 PNQ \u2192 BLR",
  "CCU \u2192 BOM \u2192 TRV \u2192 BLR",
  "CCU \u2192 DEL \u2192 AMD \u2192 BLR",
  "CCU \u2192 DEL \u2192 BLR",
  "CCU \u2192 DEL \u2192 COK \u2192 BLR",
  "CCU \u2192 DEL \u2192 COK \u2192 TRV \u2192 BLR",
  "CCU \u2192 DEL \u2192 VGA \u2192 BLR",
  "CCU \u2192 GAU \u2192 BLR",
  "CCU \u2192 GAU \u2192 DEL \u2192 BLR",
  "CCU \u2192 GAU \u2192 IMF \u2192 DEL \u2192 BLR",
  "CCU \u2192 HYD \u2192 BLR",
  "CCU \u2192 IXA \u2192 BLR",
  "CCU \u2192 IXB \u2192 BLR",
  "CCU \u2192 IXB \u2192 DEL \u2192 BLR",
  "CCU \u2192 IXR \u2192 BBI \u2192 BLR",
  "CCU \u2192 IXR \u2192 DEL \u2192 BLR",
  "CCU \u2192 IXZ \u2192 MAA \u2192 BLR",
  "CCU \u2192 JAI \u2192 BOM \u2192 BLR",
  "CCU \u2192 JAI \u2192 DEL \u2192 BLR",
  "CCU \u2192 KNU \u2192 BLR",
  "CCU \u2192 MAA \u2192 BLR",
  "CCU \u2192 NAG \u2192 BLR",
  "CCU \u2192 PAT \u2192 BLR",
  "CCU \u2192 PNQ \u2192 BLR",
  "CCU \u2192 RPR \u2192 HYD \u2192 BLR",
  "CCU \u2192 VNS \u2192 DEL \u2192 BLR",
  "CCU \u2192 VTZ \u2192 BLR",
  "DEL \u2192 AMD \u2192 BOM \u2192 COK",
  "DEL \u2192 AMD \u2192 COK",
  "DEL \u2192 ATQ \u2192 BOM \u2192 COK",
  "DEL \u2192 BBI \u2192 COK",
  "DEL \u2192 BDQ \u2192 BOM \u2192 COK",
  "DEL \u2192 BHO \u2192 BOM \u2192 COK",
  "DEL \u2192 BLR \u2192 COK",
  "DEL \u2192 BOM \u2192 COK",
  "DEL \u2192 CCU \u2192 BOM \u2192 COK",
  "DEL \u2192 COK",
  "DEL \u2192 DED \u2192 BOM \u2192 COK",
  "DEL \u2192 GOI \u2192 BOM \u2192 COK",
  "DEL \u2192 GWL \u2192 IDR \u2192 BOM \u2192 COK",
  "DEL \u2192 HYD \u2192 BOM \u2192 COK",
  "DEL \u2192 HYD \u2192 COK",
  "DEL \u2192 HYD \u2192 MAA \u2192 COK",
  "DEL \u2192 IDR \u2192 BOM \u2192 COK",
  "DEL \u2192 IXC \u2192 BOM \u2192 COK",
  "DEL \u2192 IXU \u2192 BOM \u2192 COK",
  "DEL \u2192 JAI \u2192 BOM \u2192 COK",
  "DEL \u2192 JDH \u2192 BOM \u2192 COK",
  "DEL \u2192 LKO \u2192 BOM \u2192 COK",
  "DEL \u2192 LKO \u2192 COK",
  "DEL \u2192 MAA \u2192 BOM \u2192 COK",
  "DEL \u2192 MAA \u2192 COK",
  "DEL \u2192 NAG \u2192 BOM \u2192 COK",
  "DEL \u2192 PNQ \u2192 COK",
  "DEL \u2192 RPR \u2192 NAG \u2192 BOM \u2192 COK",
  "DEL \u2192 TRV \u2192 COK",
  "DEL \u2192 UDR \u2192 BOM \u2192 COK",
  "MAA \u2192 CCU"
]

CITY_CODE_MAP = {
  "Banglore": "BLR",
  "Chennai": "MAA",
  "Delhi": "DEL",
  "Kolkata": "CCU",
  "Mumbai": "BOM",
  "Cochin": "COK",
  "Hyderabad": "HYD",
  "New Delhi": "DEL"
}

CODE_TO_CITY = {
  "BLR": "Banglore",
  "MAA": "Chennai",
  "DEL": "Delhi",
  "CCU": "Kolkata",
  "BOM": "Mumbai",
  "COK": "Cochin",
  "HYD": "Hyderabad"
}

ROUTES_BY_PAIR = {
  "BLR->DEL": {
    "1": [
      "BLR \u2192 AMD \u2192 DEL",
      "BLR \u2192 BBI \u2192 DEL",
      "BLR \u2192 BDQ \u2192 DEL",
      "BLR \u2192 BOM \u2192 DEL",
      "BLR \u2192 CCU \u2192 DEL",
      "BLR \u2192 COK \u2192 DEL",
      "BLR \u2192 GAU \u2192 DEL",
      "BLR \u2192 GOI \u2192 DEL",
      "BLR \u2192 HYD \u2192 DEL",
      "BLR \u2192 IDR \u2192 DEL",
      "BLR \u2192 LKO \u2192 DEL",
      "BLR \u2192 MAA \u2192 DEL",
      "BLR \u2192 NAG \u2192 DEL",
      "BLR \u2192 PNQ \u2192 DEL",
      "BLR \u2192 STV \u2192 DEL",
      "BLR \u2192 VGA \u2192 DEL"
    ],
    "2": [
      "BLR \u2192 BOM \u2192 AMD \u2192 DEL",
      "BLR \u2192 BOM \u2192 BHO \u2192 DEL",
      "BLR \u2192 BOM \u2192 IDR \u2192 DEL",
      "BLR \u2192 BOM \u2192 IXC \u2192 DEL",
      "BLR \u2192 BOM \u2192 JDH \u2192 DEL",
      "BLR \u2192 BOM \u2192 NAG \u2192 DEL",
      "BLR \u2192 BOM \u2192 UDR \u2192 DEL",
      "BLR \u2192 CCU \u2192 BBI \u2192 DEL",
      "BLR \u2192 CCU \u2192 GAU \u2192 DEL",
      "BLR \u2192 HYD \u2192 VGA \u2192 DEL",
      "BLR \u2192 TRV \u2192 COK \u2192 DEL",
      "BLR \u2192 VGA \u2192 HYD \u2192 DEL",
      "BLR \u2192 VGA \u2192 VTZ \u2192 DEL"
    ],
    "3": [
      "BLR \u2192 BOM \u2192 IDR \u2192 GWL \u2192 DEL",
      "BLR \u2192 CCU \u2192 BBI \u2192 HYD \u2192 DEL",
      "BLR \u2192 HBX \u2192 BOM \u2192 AMD \u2192 DEL",
      "BLR \u2192 HBX \u2192 BOM \u2192 BHO \u2192 DEL",
      "BLR \u2192 HBX \u2192 BOM \u2192 NAG \u2192 DEL"
    ],
    "4": [
      "BLR \u2192 CCU \u2192 BBI \u2192 HYD \u2192 VGA \u2192 DEL"
    ],
    "0": [
      "BLR \u2192 DEL"
    ]
  },
  "BOM->HYD": {
    "2": [
      "BOM \u2192 AMD \u2192 ISK \u2192 HYD",
      "BOM \u2192 BDQ \u2192 DEL \u2192 HYD",
      "BOM \u2192 BHO \u2192 DEL \u2192 HYD",
      "BOM \u2192 COK \u2192 MAA \u2192 HYD",
      "BOM \u2192 DED \u2192 DEL \u2192 HYD",
      "BOM \u2192 GOI \u2192 PNQ \u2192 HYD",
      "BOM \u2192 IDR \u2192 DEL \u2192 HYD",
      "BOM \u2192 JAI \u2192 DEL \u2192 HYD",
      "BOM \u2192 JDH \u2192 DEL \u2192 HYD",
      "BOM \u2192 RPR \u2192 VTZ \u2192 HYD",
      "BOM \u2192 UDR \u2192 DEL \u2192 HYD",
      "BOM \u2192 VNS \u2192 DEL \u2192 HYD"
    ],
    "1": [
      "BOM \u2192 BBI \u2192 HYD",
      "BOM \u2192 BLR \u2192 HYD",
      "BOM \u2192 CCU \u2192 HYD",
      "BOM \u2192 DEL \u2192 HYD",
      "BOM \u2192 GOI \u2192 HYD",
      "BOM \u2192 JLR \u2192 HYD",
      "BOM \u2192 MAA \u2192 HYD",
      "BOM \u2192 NDC \u2192 HYD"
    ],
    "3": [
      "BOM \u2192 BLR \u2192 CCU \u2192 BBI \u2192 HYD",
      "BOM \u2192 JDH \u2192 JAI \u2192 DEL \u2192 HYD"
    ],
    "0": [
      "BOM \u2192 HYD"
    ]
  },
  "CCU->BLR": {
    "1": [
      "CCU \u2192 AMD \u2192 BLR",
      "CCU \u2192 BBI \u2192 BLR",
      "CCU \u2192 BOM \u2192 BLR",
      "CCU \u2192 DEL \u2192 BLR",
      "CCU \u2192 GAU \u2192 BLR",
      "CCU \u2192 HYD \u2192 BLR",
      "CCU \u2192 IXA \u2192 BLR",
      "CCU \u2192 IXB \u2192 BLR",
      "CCU \u2192 KNU \u2192 BLR",
      "CCU \u2192 MAA \u2192 BLR",
      "CCU \u2192 NAG \u2192 BLR",
      "CCU \u2192 PAT \u2192 BLR",
      "CCU \u2192 PNQ \u2192 BLR",
      "CCU \u2192 VTZ \u2192 BLR"
    ],
    "2": [
      "CCU \u2192 BBI \u2192 BOM \u2192 BLR",
      "CCU \u2192 BBI \u2192 HYD \u2192 BLR",
      "CCU \u2192 BOM \u2192 AMD \u2192 BLR",
      "CCU \u2192 BOM \u2192 COK \u2192 BLR",
      "CCU \u2192 BOM \u2192 GOI \u2192 BLR",
      "CCU \u2192 BOM \u2192 HBX \u2192 BLR",
      "CCU \u2192 BOM \u2192 PNQ \u2192 BLR",
      "CCU \u2192 BOM \u2192 TRV \u2192 BLR",
      "CCU \u2192 DEL \u2192 AMD \u2192 BLR",
      "CCU \u2192 DEL \u2192 COK \u2192 BLR",
      "CCU \u2192 DEL \u2192 VGA \u2192 BLR",
      "CCU \u2192 GAU \u2192 DEL \u2192 BLR",
      "CCU \u2192 IXB \u2192 DEL \u2192 BLR",
      "CCU \u2192 IXR \u2192 BBI \u2192 BLR",
      "CCU \u2192 IXR \u2192 DEL \u2192 BLR",
      "CCU \u2192 IXZ \u2192 MAA \u2192 BLR",
      "CCU \u2192 JAI \u2192 BOM \u2192 BLR",
      "CCU \u2192 JAI \u2192 DEL \u2192 BLR",
      "CCU \u2192 RPR \u2192 HYD \u2192 BLR",
      "CCU \u2192 VNS \u2192 DEL \u2192 BLR"
    ],
    "3": [
      "CCU \u2192 BBI \u2192 IXR \u2192 DEL \u2192 BLR",
      "CCU \u2192 DEL \u2192 COK \u2192 TRV \u2192 BLR",
      "CCU \u2192 GAU \u2192 IMF \u2192 DEL \u2192 BLR"
    ],
    "0": [
      "CCU \u2192 BLR"
    ]
  },
  "DEL->COK": {
    "2": [
      "DEL \u2192 AMD \u2192 BOM \u2192 COK",
      "DEL \u2192 ATQ \u2192 BOM \u2192 COK",
      "DEL \u2192 BDQ \u2192 BOM \u2192 COK",
      "DEL \u2192 BHO \u2192 BOM \u2192 COK",
      "DEL \u2192 CCU \u2192 BOM \u2192 COK",
      "DEL \u2192 DED \u2192 BOM \u2192 COK",
      "DEL \u2192 GOI \u2192 BOM \u2192 COK",
      "DEL \u2192 HYD \u2192 BOM \u2192 COK",
      "DEL \u2192 HYD \u2192 MAA \u2192 COK",
      "DEL \u2192 IDR \u2192 BOM \u2192 COK",
      "DEL \u2192 IXC \u2192 BOM \u2192 COK",
      "DEL \u2192 IXU \u2192 BOM \u2192 COK",
      "DEL \u2192 JAI \u2192 BOM \u2192 COK",
      "DEL \u2192 JDH \u2192 BOM \u2192 COK",
      "DEL \u2192 LKO \u2192 BOM \u2192 COK",
      "DEL \u2192 MAA \u2192 BOM \u2192 COK",
      "DEL \u2192 NAG \u2192 BOM \u2192 COK",
      "DEL \u2192 UDR \u2192 BOM \u2192 COK"
    ],
    "1": [
      "DEL \u2192 AMD \u2192 COK",
      "DEL \u2192 BBI \u2192 COK",
      "DEL \u2192 BLR \u2192 COK",
      "DEL \u2192 BOM \u2192 COK",
      "DEL \u2192 HYD \u2192 COK",
      "DEL \u2192 LKO \u2192 COK",
      "DEL \u2192 MAA \u2192 COK",
      "DEL \u2192 PNQ \u2192 COK",
      "DEL \u2192 TRV \u2192 COK"
    ],
    "0": [
      "DEL \u2192 COK"
    ],
    "3": [
      "DEL \u2192 GWL \u2192 IDR \u2192 BOM \u2192 COK",
      "DEL \u2192 RPR \u2192 NAG \u2192 BOM \u2192 COK"
    ]
  },
  "MAA->CCU": {
    "0": [
      "MAA \u2192 CCU"
    ]
  }
}

VALID_PAIRS = {
    'Banglore': ['New Delhi', 'Delhi'],
    'Mumbai': ['Hyderabad'],
    'Kolkata': ['Banglore'],
    'Delhi': ['Cochin'],
    'Chennai': ['Kolkata']
}

DEFAULT_DIRECT_ROUTES = {
    ('Banglore', 'New Delhi'): 'BLR → DEL',
    ('Banglore', 'Delhi'): 'BLR → DEL',
    ('Mumbai', 'Hyderabad'): 'BOM → HYD',
    ('Kolkata', 'Banglore'): 'CCU → BLR',
    ('Delhi', 'Cochin'): 'DEL → COK',
    ('Chennai', 'Kolkata'): 'MAA → CCU',
}

def get_best_route(source: str, destination: str, total_stops: int = 0) -> str:
    s_code = CITY_CODE_MAP.get(source, "DEL")
    d_code = CITY_CODE_MAP.get(destination, "COK")
    key = f"{s_code}->{d_code}"
    
    pair_routes = ROUTES_BY_PAIR.get(key, {})
    stop_key = str(total_stops)
    if stop_key in pair_routes and pair_routes[stop_key]:
        return pair_routes[stop_key][0]
    
    # Fallback to direct route if stops=0 or no stops match
    if total_stops == 0:
        return f"{s_code} → {d_code}"
    
    # Return any available route for this pair if possible
    for st in sorted(pair_routes.keys(), key=lambda x: int(x)):
        if pair_routes[st]:
            return pair_routes[st][0]
            
    return f"{s_code} → {d_code}"

def normalize_route(route_str: str, source: str = None, destination: str = None, total_stops: int = 0) -> str:
    if not route_str or not route_str.strip():
        if source and destination:
            return get_best_route(source, destination, total_stops)
        return "DEL → BOM → COK"
        
    s = route_str.strip()
    s = re.sub(r"\s*(?:-->|->|–>|—>|\sto\s|-|>|,)\s*", " → ", s, flags=re.IGNORECASE)
    parts = [p.strip().upper() for p in s.split("→") if p.strip()]
    if not parts:
        if source and destination:
            return get_best_route(source, destination, total_stops)
        return "DEL → BOM → COK"
        
    normalized = " → ".join(parts)
    if normalized in ALL_ROUTES:
        return normalized
        
    # Check if exact casing or spacing matches
    for r in ALL_ROUTES:
        if r.replace(" ", "") == normalized.replace(" ", ""):
            return r
            
    # If not recognized and source/destination provided, check if valid route can be matched
    if source and destination:
        s_code = CITY_CODE_MAP.get(source)
        d_code = CITY_CODE_MAP.get(destination)
        if s_code and d_code:
            key = f"{s_code}->{d_code}"
            pair_routes = ROUTES_BY_PAIR.get(key, {})
            stop_key = str(total_stops)
            if stop_key in pair_routes and pair_routes[stop_key]:
                # Check if parts match any intermediate stop
                if len(parts) > 2:
                    mid = parts[1]
                    for r in pair_routes[stop_key]:
                        if f"→ {mid} →" in r:
                            return r
                return pair_routes[stop_key][0]
                
    return normalized

def normalize_additional_info(info: str) -> str:
    if not info or not info.strip():
        return "No info"
    s = info.strip()
    if s in ADDITIONAL_INFO:
        return s
    if s.lower() == "no info":
        return "No info"
    for opt in ADDITIONAL_INFO:
        if opt.lower() == s.lower():
            return opt
    return "No info"
