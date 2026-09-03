import pandas as pd
import numpy as np
from datetime import datetime, timedelta

def generate_market_data(num_markets=10, crops=None):
    """
    Generates synthetic market pricing data for various crops across different locations.
    """
    if crops is None:
        crops = ['Tomatoes', 'Kale', 'Avocados', 'Bananas', 'Onions']

    np.random.seed(42)
    
    market_names = [f"Market_{chr(65+i)}" for i in range(num_markets)]
    
    data = []
    for market in market_names:
        lat = np.random.uniform(-1.5, 0.5)  # Roughly Kenya
        lon = np.random.uniform(36.5, 41.0)
        
        for crop in crops:
            # Base price with some random noise
            base_price = np.random.uniform(50, 200)
            for _ in range(30):  # 30 days of price data
                date = datetime.now() - timedelta(days=np.random.randint(0, 365))
                price = base_price + np.random.normal(0, 10)
                data.append([market, date, crop, max(price, 10), lat, lon])

    df = pd.DataFrame(data, columns=['market_id', 'date', 'crop', 'price_per_kg', 'market_lat', 'market_lon'])
    return df

if __name__ == "__main__":
    df = generate_market_data()
    print(df.head())
