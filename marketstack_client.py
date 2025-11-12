"""
Efficient Marketstack API Client
- Batch requests (100 stocks in 1 API call)
- 15-minute aggressive caching
- Rate limit tracking
- Automatic retry logic
"""

import requests
import pandas as pd
from datetime import datetime, timedelta
from typing import Dict, List, Optional
import os
import time

class MarketstackClient:
    """Highly optimized Marketstack API client"""
    
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.base_url = "http://api.marketstack.com/v1"
        self.cache = {}
        self.cache_timestamps = {}
        self.cache_duration = 900  # 15 minutes in seconds
        self.api_calls_made = 0
        self.last_request_time = None
        
    def _is_cache_valid(self, cache_key: str) -> bool:
        """Check if cached data is still valid"""
        if cache_key not in self.cache_timestamps:
            return False
        
        age = time.time() - self.cache_timestamps[cache_key]
        return age < self.cache_duration
    
    def _get_from_cache(self, cache_key: str) -> Optional[Dict]:
        """Get data from cache if valid"""
        if self._is_cache_valid(cache_key):
            print(f"✅ Cache hit: {cache_key[:50]}... (saved 1 API call)")
            return self.cache[cache_key]
        return None
    
    def _save_to_cache(self, cache_key: str, data: Dict):
        """Save data to cache"""
        self.cache[cache_key] = data
        self.cache_timestamps[cache_key] = time.time()
    
    def _make_request(self, endpoint: str, params: dict) -> dict:
        """Make API request with rate limiting"""
        # Add API key to params
        params['access_key'] = self.api_key
        
        # Rate limiting: 1 request per second (conservative)
        if self.last_request_time:
            elapsed = time.time() - self.last_request_time
            if elapsed < 1.0:
                time.sleep(1.0 - elapsed)
        
        url = f"{self.base_url}/{endpoint}"
        
        try:
            print(f"🌐 API Call #{self.api_calls_made + 1}: {endpoint}")
            response = requests.get(url, params=params, timeout=30)
            self.last_request_time = time.time()
            self.api_calls_made += 1
            
            if response.status_code == 200:
                return response.json()
            elif response.status_code == 429:
                raise Exception("Rate limit exceeded. Please wait before making more requests.")
            else:
                raise Exception(f"API Error: {response.status_code} - {response.text}")
        
        except requests.exceptions.Timeout:
            raise Exception("Request timed out. Please try again.")
        except requests.exceptions.RequestException as e:
            raise Exception(f"Network error: {str(e)}")
    
    def get_eod_data_batch(
        self, 
        symbols: List[str], 
        date_from: Optional[str] = None,
        date_to: Optional[str] = None,
        limit: int = 100
    ) -> Dict[str, pd.DataFrame]:
        """
        Fetch EOD data for multiple symbols in ONE API call
        This is the most efficient method!
        
        Args:
            symbols: List of stock symbols (up to 100)
            date_from: Start date (YYYY-MM-DD)
            date_to: End date (YYYY-MM-DD)
            limit: Max data points per symbol (default: 100)
        
        Returns:
            Dict mapping symbol -> DataFrame
        """
        # Create cache key
        symbols_str = ','.join(sorted(symbols))
        cache_key = f"eod_batch_{symbols_str}_{date_from}_{date_to}_{limit}"
        
        # Check cache first
        cached_data = self._get_from_cache(cache_key)
        if cached_data:
            return cached_data
        
        # Prepare request parameters
        params = {
            'symbols': ','.join(symbols),  # Batch request!
            'limit': limit
        }
        
        if date_from:
            params['date_from'] = date_from
        if date_to:
            params['date_to'] = date_to
        
        # Make single API call for all symbols
        data = self._make_request('eod', params)
        
        # Parse response into DataFrames
        result = {}
        
        if 'data' not in data:
            print(f"⚠️  No data returned from API")
            return result
        
        # Group data by symbol
        for item in data['data']:
            symbol = item['symbol']
            
            if symbol not in result:
                result[symbol] = []
            
            result[symbol].append({
                'Date': item['date'],
                'Open': item['open'],
                'High': item['high'],
                'Low': item['low'],
                'Close': item['close'],
                'Volume': item['volume']
            })
        
        # Convert to DataFrames - FIXED VERSION
        for symbol in list(result.keys()):
            try:
                df = pd.DataFrame(result[symbol])
                # Convert Date column to datetime
                df['Date'] = pd.to_datetime(df['Date'])
                # Sort by date
                df = df.sort_values('Date')
                # Set Date as index properly
                df.index = pd.DatetimeIndex(df['Date'])
                # Drop the Date column
                df = df.drop(columns=['Date'])
                result[symbol] = df
            except Exception as e:
                print(f"⚠️  Error processing {symbol}: {e}")
                del result[symbol]
        
        # Cache the result
        self._save_to_cache(cache_key, result)
        
        print(f"📊 Fetched data for {len(result)} symbols in 1 API call")
        
        return result
    
    def get_intraday_data_batch(
        self,
        symbols: List[str],
        interval: str = '1hour',
        date_from: Optional[str] = None,
        date_to: Optional[str] = None,
        limit: int = 100
    ) -> Dict[str, pd.DataFrame]:
        """
        Fetch intraday data for multiple symbols in ONE API call
        
        Args:
            symbols: List of stock symbols
            interval: '1min', '5min', '15min', '30min', '1hour'
            date_from: Start date (YYYY-MM-DD)
            date_to: End date (YYYY-MM-DD)
            limit: Max data points per symbol
        
        Returns:
            Dict mapping symbol -> DataFrame
        """
        # Create cache key
        symbols_str = ','.join(sorted(symbols))
        cache_key = f"intraday_batch_{symbols_str}_{interval}_{date_from}_{date_to}_{limit}"
        
        # Check cache first
        cached_data = self._get_from_cache(cache_key)
        if cached_data:
            return cached_data
        
        # Prepare request
        params = {
            'symbols': ','.join(symbols),
            'interval': interval,
            'limit': limit
        }
        
        if date_from:
            params['date_from'] = date_from
        if date_to:
            params['date_to'] = date_to
        
        # Make single API call
        data = self._make_request('intraday', params)
        
        # Parse response
        result = {}
        
        if 'data' not in data:
            return result
        
        for item in data['data']:
            symbol = item['symbol']
            
            if symbol not in result:
                result[symbol] = []
            
            result[symbol].append({
                'Date': item['date'],
                'Open': item['open'],
                'High': item['high'],
                'Low': item['low'],
                'Close': item['close'],
                'Volume': item['volume']
            })
        
        # Convert to DataFrames - FIXED VERSION
        for symbol in list(result.keys()):
            try:
                df = pd.DataFrame(result[symbol])
                df['Date'] = pd.to_datetime(df['Date'])
                df = df.sort_values('Date')
                df.index = pd.DatetimeIndex(df['Date'])
                df = df.drop(columns=['Date'])
                result[symbol] = df
            except Exception as e:
                print(f"⚠️  Error processing {symbol}: {e}")
                del result[symbol]
        
        # Cache the result
        self._save_to_cache(cache_key, result)
        
        print(f"📊 Fetched intraday data for {len(result)} symbols in 1 API call")
        
        return result
    
    def get_historical_data(
        self,
        symbols: List[str],
        timeframe: str = '1d',
        period: str = '1mo'
    ) -> Dict[str, pd.DataFrame]:
        """
        Unified method to fetch historical data based on timeframe
        Automatically chooses EOD or intraday endpoint
        
        Args:
            symbols: List of stock symbols
            timeframe: '1d', '1h', '30m', '15m', '5m', '1m'
            period: '1d', '5d', '1mo', '3mo', '6mo', '1y', '2y'
        
        Returns:
            Dict mapping symbol -> DataFrame
        """
        # Calculate date range
        end_date = datetime.now()
        
        period_map = {
            '1d': timedelta(days=1),
            '5d': timedelta(days=5),
            '1mo': timedelta(days=30),
            '3mo': timedelta(days=90),
            '6mo': timedelta(days=180),
            '1y': timedelta(days=365),
            '2y': timedelta(days=730)
        }
        
        start_date = end_date - period_map.get(period, timedelta(days=30))
        
        date_from = start_date.strftime('%Y-%m-%d')
        date_to = end_date.strftime('%Y-%m-%d')
        
        # Calculate limit based on timeframe and period
        days = (end_date - start_date).days
        
        if timeframe == '1d':
            limit = min(days + 5, 1000)  # Add buffer
        elif timeframe == '1h':
            limit = min(days * 24, 1000)
        elif timeframe == '30m':
            limit = min(days * 48, 1000)
        elif timeframe == '15m':
            limit = min(days * 96, 1000)
        elif timeframe == '5m':
            limit = min(days * 288, 1000)
        else:  # 1m
            limit = 1000
        
        # Choose endpoint based on timeframe
        if timeframe == '1d':
            # Use EOD endpoint (more efficient)
            return self.get_eod_data_batch(
                symbols=symbols,
                date_from=date_from,
                date_to=date_to,
                limit=limit
            )
        else:
            # Use intraday endpoint
            interval_map = {
                '1h': '1hour',
                '30m': '30min',
                '15m': '15min',
                '5m': '5min',
                '1m': '1min'
            }
            
            interval = interval_map.get(timeframe, '1hour')
            
            return self.get_intraday_data_batch(
                symbols=symbols,
                interval=interval,
                date_from=date_from,
                date_to=date_to,
                limit=limit
            )
    
    def get_usage_stats(self) -> dict:
        """Get API usage statistics"""
        return {
            'total_api_calls': self.api_calls_made,
            'cache_entries': len(self.cache),
            'cache_hit_rate': self._calculate_cache_hit_rate()
        }
    
    def _calculate_cache_hit_rate(self) -> float:
        """Calculate cache hit rate"""
        total_requests = self.api_calls_made + len([
            k for k in self.cache_timestamps 
            if self._is_cache_valid(k)
        ])
        
        if total_requests == 0:
            return 0.0
        
        cache_hits = total_requests - self.api_calls_made
        return (cache_hits / total_requests) * 100
    
    def clear_cache(self):
        """Clear all cached data"""
        self.cache.clear()
        self.cache_timestamps.clear()
        print("🗑️  Cache cleared")