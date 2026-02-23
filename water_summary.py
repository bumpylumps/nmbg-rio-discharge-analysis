import pandas as pd
import requests 
import io
import json

# Configs
SITE_ID = "08358400" # Rio Grande Floodway, San Marcial, NM 
PARAM_CODE = "00060" # USGS code for Discharge (Flow)
DATA_TOTAL_DAYS = 30

# Fetch data
def fetch_raw_data():
    url = "https://nwis.waterservices.usgs.gov/nwis/iv/"

    params = {
        "format": "rdb",
        "sites": SITE_ID,
        "parameterCd": PARAM_CODE,
        "period": f"P{DATA_TOTAL_DAYS}D", 
        "siteStatus": "all"
    }

    print(f"Connecting to USGS NWIS for Site: {SITE_ID} (Param: {PARAM_CODE})...")

    response = requests.get(url, params=params)

    if response.status_code != 200:
        print(f"Server response: {response.text}")

    response.raise_for_status() 
    return response.text 

# clean data
def process_data(csv_text):

    df = pd.read_csv(io.StringIO(csv_text), comment='#', sep='\t') 

    if df.empty:
        print("No data returned from USGS.")
        return None, None 
    
    df.columns = df.columns.str.strip() 
    
    df.iloc[1:] 

    val_col_list = [c for c in df.columns if PARAM_CODE in c and "_cd" not in c] 

    if not val_col_list or 'datetime' not in df.columns:
        print(f"Error: Could not find required columns. Actual Columns: {df.columns.tolist()}")
        return None, None

    val_col = val_col_list[0] # grab discharge column

    df = df.rename(columns={
        'datetime': 'ActivityTimestamp',
        val_col: 'discharge_cfs',
        f"{val_col}_cd": 'approval_status',
    })

    df['ActivityTimestamp'] = pd.to_datetime(df['ActivityTimestamp'], errors='coerce')
    df['discharge_cfs'] = pd.to_numeric(df['discharge_cfs'], errors='coerce')

    df = df.dropna(subset=['ActivityTimestamp', 'discharge_cfs']) 

    if df.empty:
        print("DataFrame is empty after cleaning metadata.")
        return None, None 

    summary = {
        "count": len(df),
        "min": df['discharge_cfs'].min(),
        "max": df['discharge_cfs'].max(),
        "avg": df['discharge_cfs'].mean(),
        "latest": df.sort_values('ActivityTimestamp').iloc[-1] 
    }

    return df, summary 

# save results to file
def export_results(df, summary) -> None:

    csv_filename= 'rio_grande_data.csv'
    df.to_csv(csv_filename, index=False) 
    print(f"Successfully saved sanitized data to {csv_filename}")

    
    json_summary = {
        "count": int(summary["count"]),
        "min": float(summary["min"]),
        "max": float(summary["max"]),
        "avg": round(float(summary["avg"]), 2),
        "latest_reading": {
            "date": str(summary["latest"]["ActivityTimestamp"]),
            "value": float(summary["latest"]["discharge_cfs"]),
            "unit": "cfs"
        }
    }

    
    json_filename = "water_summary.json"
    with open(json_filename, 'w') as f:
        json.dump(json_summary, f, indent=4)

    print(f"Successfully saved summary to {json_filename}")


# main() - run the brain
if __name__ == "__main__":
    try: 
        raw_data = fetch_raw_data()
        clean_df, stats = process_data(raw_data)


    # Print for CLI dash
        if clean_df is not None:
            export_results(clean_df, stats)
            print("\n" + "="*30)
            print("   NEW MEXICO WATER SUMMARY")
            print("="*30)
            print(f"Site ID:     {SITE_ID}")
            print(f"Readings:    {stats['count']}")
            print(f"Min Flow:    {stats['min']:.2f} cfs")
            print(f"Max Flow:    {stats['max']:.2f} cfs")
            print(f"Avg Flow:    {stats['avg']:.2f} cfs")
            print("-"*30)
            print(f"Latest:      {stats['latest']['discharge_cfs']} cfs")
            print(f"As of:       {stats['latest']['ActivityTimestamp']}")
            print("="*30)
            print("\n--- PIPELINE SUCCESS ---")
            print(f"Processed {stats['count']} records for Site {SITE_ID}")
        
    except Exception as e:
        print(f"FAILURE: {e}")

