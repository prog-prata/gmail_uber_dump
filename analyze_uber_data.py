#!/usr/bin/env python3

import json
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime
import os

# File paths
DATA_FILE = 'data/emails.json'
OUTPUT_DIR = 'analysis_output'

def load_data(file_path):
    """Load data from JSON file"""
    try:
        with open(file_path, 'r') as file:
            return json.load(file)
    except (json.JSONDecodeError, FileNotFoundError) as e:
        print(f"Error loading data: {e}")
        return []

def process_data(data):
    """Process the data: add work_related field, remove duplicates, order by date, anonymize addresses"""
    # Convert to DataFrame for easier manipulation
    df = pd.DataFrame(data)
    
    # Add work_related field based on subject NOT containing "Família" (inverse of previous logic)
    df['work_related'] = ~df['subject'].str.contains('Família', case=False, na=False)
    
    # Remove duplicates based on id
    df = df.drop_duplicates(subset=['id'])
    
    # Convert date to datetime for sorting
    # Ensure proper parsing of the date format '%Y-%m-%d %H:%M:%S'
    df['date'] = pd.to_datetime(df['date'], format='%Y-%m-%d %H:%M:%S')
    
    # Add additional date-related columns for analysis
    df['day'] = df['date'].dt.day
    df['month'] = df['date'].dt.month
    df['year'] = df['date'].dt.year
    df['hour'] = df['date'].dt.hour
    df['date_only'] = df['date'].dt.date
    
    # Sort by date
    df = df.sort_values('date')
    
    # Anonymize address columns (any column that starts with 'addr')
    address_columns = [col for col in df.columns if col.startswith('addr')]
    
    # Create a mapping of unique addresses to coded identifiers
    unique_addresses = {}
    address_id_counter = {'work': 1, 'home': 1}  # Separate counters for work and home
    
    # Process each address column
    for col in address_columns:
        # Create a new anonymized column
        new_col_name = f"{col}_anon"
        
        # Process each address in the column
        df[new_col_name] = df.apply(
            lambda row: anonymize_address(row[col], row['work_related'], unique_addresses, address_id_counter),
            axis=1
        )
        
        # Drop the original address column
        df = df.drop(columns=[col])
    
    # Save the address mapping to a file for reference
    with open(f"{OUTPUT_DIR}/address_mapping.json", 'w') as f:
        json.dump(unique_addresses, f, indent=4)
    
    return df

def anonymize_address(address, is_work_related, address_map, counter):
    """Create an anonymized code for an address"""
    if pd.isna(address) or address == "":
        return ""
    
    # If this address has already been mapped, use the existing code
    if address in address_map:
        return address_map[address]
    
    # Create a new code based on whether it's work-related
    if is_work_related:
        code = f"W{counter['work']:03d}"
        counter['work'] += 1
    else:
        code = f"H{counter['home']:03d}"
        counter['home'] += 1
    
    # Store the mapping
    address_map[address] = code
    
    return code

def generate_graphics(df):
    """Generate graphics relating price and date/time, separated by work_related field"""
    # Create output directory if it doesn't exist
    if not os.path.exists(OUTPUT_DIR):
        os.makedirs(OUTPUT_DIR)
    
    # Set the style
    sns.set(style="darkgrid")
    
    # 1. Price over time, colored by work_related
    plt.figure(figsize=(12, 6))
    sns.scatterplot(data=df, x='date', y='total', hue='work_related', palette='viridis', s=100)
    plt.title('Uber Ride Prices Over Time')
    plt.xlabel('Date')
    plt.ylabel('Price (R$)')
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.savefig(f'{OUTPUT_DIR}/price_over_time.png')
    plt.close()
    
    # 2. Price distribution by work_related
    plt.figure(figsize=(10, 6))
    sns.boxplot(data=df, x='work_related', y='total')
    plt.title('Price Distribution by Family/Work Category')
    plt.xlabel('Family/Work Related')
    plt.ylabel('Price (R$)')
    plt.tight_layout()
    plt.savefig(f'{OUTPUT_DIR}/price_distribution.png')
    plt.close()
    
    # 3. Price vs Distance, colored by work_related
    plt.figure(figsize=(10, 6))
    sns.scatterplot(data=df, x='distance', y='total', hue='work_related', palette='viridis', s=100)
    plt.title('Price vs Distance')
    plt.xlabel('Distance (km)')
    plt.ylabel('Price (R$)')
    plt.tight_layout()
    plt.savefig(f'{OUTPUT_DIR}/price_vs_distance.png')
    plt.close()
    
    # 4. Average price by hour of day, separated by work_related
    
    plt.figure(figsize=(12, 6))
    sns.lineplot(data=df, x='hour', y='total', hue='work_related', marker='o')
    plt.title('Average Price by Hour of Day')
    plt.xlabel('Hour of Day')
    plt.ylabel('Average Price (R$)')
    plt.xticks(range(0, 24))
    plt.tight_layout()
    plt.savefig(f'{OUTPUT_DIR}/price_by_hour.png')
    plt.close()
    
    # 5. Monthly average price trend
    # Create a proper year-month column for grouping
    df['year_month'] = df['date'].dt.strftime('%Y-%m')
    monthly_avg = df.groupby(['year_month', 'work_related'])['total'].mean().reset_index()
    
    plt.figure(figsize=(14, 6))
    sns.lineplot(data=monthly_avg, x='year_month', y='total', hue='work_related', marker='o')
    plt.title('Monthly Average Price Trend')
    plt.xlabel('Month')
    plt.ylabel('Average Price (R$)')
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.savefig(f'{OUTPUT_DIR}/monthly_price_trend.png')
    plt.close()
    
    # 6. Total monthly spend by category (family vs work)
    monthly_total = df.groupby(['year_month', 'work_related'])['total'].sum().reset_index()
    
    plt.figure(figsize=(14, 8))
    sns.barplot(data=monthly_total, x='year_month', y='total', hue='work_related', palette='viridis')
    plt.title('Total Monthly Spend by Category')
    plt.xlabel('Month')
    plt.ylabel('Total Spend (R$)')
    plt.xticks(rotation=45)
    plt.legend(title='Work Related', labels=['Family', 'Work'])
    
    # Add values on top of bars
    for i, p in enumerate(plt.gca().patches):
        height = p.get_height()
        plt.gca().text(p.get_x() + p.get_width()/2., height + 5,
                '{:.0f}'.format(height),
                ha="center", fontsize=9)
    
    plt.tight_layout()
    plt.savefig(f'{OUTPUT_DIR}/monthly_total_spend.png')
    plt.close()
    
    # Save processed data to CSV for further analysis
    df.to_csv(f'{OUTPUT_DIR}/processed_uber_data.csv', index=False)
    
    print(f"Graphics generated and saved to {OUTPUT_DIR} directory")
    
    # Return some basic statistics
    return {
        'total_rides': len(df),
        'work_rides': df['work_related'].sum(),
        'family_rides': len(df) - df['work_related'].sum(),
        'avg_price': df['total'].mean(),
        'avg_distance': df['distance'].mean(),
        'avg_work_price': df[df['work_related']]['total'].mean() if not df[df['work_related']].empty else 0,
        'avg_family_price': df[~df['work_related']]['total'].mean() if not df[~df['work_related']].empty else 0,
        'min_date': df['date'].min().strftime('%Y-%m-%d'),
        'max_date': df['date'].max().strftime('%Y-%m-%d'),
        'unique_days': df['date_only'].nunique()
    }

def main():
    # Load data
    print("Loading data from", DATA_FILE)
    data = load_data(DATA_FILE)
    
    if not data:
        print("No data found. Exiting.")
        return
    
    print(f"Loaded {len(data)} records")
    
    # Process data
    print("Processing data...")
    df = process_data(data)
    
    # Generate graphics
    print("Generating graphics...")
    stats = generate_graphics(df)
    
    # Print statistics
    print("\nAnalysis Summary:")
    print(f"Total rides: {stats['total_rides']}")
    print(f"Work-related rides: {stats['work_rides']} ({stats['work_rides']/stats['total_rides']*100:.1f}%)")
    print(f"Family-related rides: {stats['family_rides']} ({stats['family_rides']/stats['total_rides']*100:.1f}%)")
    print(f"Average price: R$ {stats['avg_price']:.2f}")
    print(f"Average distance: {stats['avg_distance']:.2f} km")
    print(f"Average work-related ride price: R$ {stats['avg_work_price']:.2f}")
    print(f"Average family-related ride price: R$ {stats['avg_family_price']:.2f}")
    
    # Print date range information
    print(f"\nDate range: {stats['min_date']} to {stats['max_date']}")
    print(f"Number of days with rides: {stats['unique_days']}")
    
    print("\nAnalysis complete. Results saved to", OUTPUT_DIR)

if __name__ == "__main__":
    main()
