import pandas as pd
import numpy as np
from scipy.signal import find_peaks

class PatternDetector:
    """Detect various trading patterns in stock data"""
    
    def __init__(self):
        self.min_confidence = 0.5
    
    def detect_bull_flag(self, df: pd.DataFrame) -> tuple[bool, float]:
        """
        Detect bull flag pattern:
        - Strong upward move (flagpole)
        - Followed by downward consolidation (flag)
        - Recent price near top of consolidation
        """
        if len(df) < 30:
            return False, 0.0
        
        try:
            # Look at last 30 periods
            recent = df.tail(30)
            closes = recent['Close'].values
            
            # Find the flagpole (strong upward move in first half)
            first_half = closes[:15]
            flagpole_gain = (first_half[-1] - first_half[0]) / first_half[0]
            
            # Need significant upward move (>5%)
            if flagpole_gain < 0.05:
                return False, 0.0
            
            # Check for consolidation/pullback in second half
            second_half = closes[15:]
            consolidation_change = (second_half[-1] - second_half[0]) / second_half[0]
            
            # Flag should be relatively flat or slight downward (-5% to +2%)
            if consolidation_change < -0.05 or consolidation_change > 0.02:
                return False, 0.0
            
            # Check if recent price is near top of consolidation range
            recent_price = closes[-1]
            consolidation_high = max(second_half)
            consolidation_low = min(second_half)
            consolidation_range = consolidation_high - consolidation_low
            
            if consolidation_range == 0:
                return False, 0.0
            
            position_in_range = (recent_price - consolidation_low) / consolidation_range
            
            # Calculate confidence based on pattern strength
            confidence = min(1.0, (
                0.3 * min(1.0, flagpole_gain / 0.15) +  # Flagpole strength
                0.4 * (1 - abs(consolidation_change) / 0.05) +  # Consolidation tightness
                0.3 * position_in_range  # Position in range
            ))
            
            return confidence > self.min_confidence, confidence
        
        except Exception as e:
            print(f"Error in bull_flag detection: {e}")
            return False, 0.0
    
    def detect_bear_flag(self, df: pd.DataFrame) -> tuple[bool, float]:
        """
        Detect bear flag pattern (inverse of bull flag):
        - Strong downward move
        - Followed by upward consolidation
        - Recent price near bottom of consolidation
        """
        if len(df) < 30:
            return False, 0.0
        
        try:
            recent = df.tail(30)
            closes = recent['Close'].values
            
            # Find the flagpole (strong downward move in first half)
            first_half = closes[:15]
            flagpole_drop = (first_half[0] - first_half[-1]) / first_half[0]
            
            if flagpole_drop < 0.05:
                return False, 0.0
            
            # Check for consolidation/bounce in second half
            second_half = closes[15:]
            consolidation_change = (second_half[-1] - second_half[0]) / second_half[0]
            
            # Flag should be relatively flat or slight upward (-2% to +5%)
            if consolidation_change < -0.02 or consolidation_change > 0.05:
                return False, 0.0
            
            # Check if recent price is near bottom of consolidation range
            recent_price = closes[-1]
            consolidation_high = max(second_half)
            consolidation_low = min(second_half)
            consolidation_range = consolidation_high - consolidation_low
            
            if consolidation_range == 0:
                return False, 0.0
            
            position_in_range = (consolidation_high - recent_price) / consolidation_range
            
            confidence = min(1.0, (
                0.3 * min(1.0, flagpole_drop / 0.15) +
                0.4 * (1 - abs(consolidation_change) / 0.05) +
                0.3 * position_in_range
            ))
            
            return confidence > self.min_confidence, confidence
        
        except Exception as e:
            return False, 0.0
    
    def detect_head_shoulders(self, df: pd.DataFrame) -> tuple[bool, float]:
        """
        Detect head and shoulders pattern:
        - Three peaks with middle peak (head) higher than other two (shoulders)
        - Neckline connects the troughs
        """
        if len(df) < 40:
            return False, 0.0
        
        try:
            recent = df.tail(40)
            closes = recent['Close'].values
            
            # Find peaks
            peaks, properties = find_peaks(closes, distance=5)
            
            if len(peaks) < 3:
                return False, 0.0
            
            # Get last 3 peaks
            last_3_peaks = peaks[-3:]
            peak_values = closes[last_3_peaks]
            
            # Check if middle peak is highest (head)
            if peak_values[1] <= peak_values[0] or peak_values[1] <= peak_values[2]:
                return False, 0.0
            
            # Check if shoulders are roughly similar height
            shoulder_diff = abs(peak_values[0] - peak_values[2]) / peak_values[0]
            
            if shoulder_diff > 0.10:  # Shoulders should be within 10% of each other
                return False, 0.0
            
            # Check if price has broken below neckline
            troughs_between_peaks = []
            for i in range(len(last_3_peaks) - 1):
                segment = closes[last_3_peaks[i]:last_3_peaks[i+1]]
                troughs_between_peaks.append(min(segment))
            
            if len(troughs_between_peaks) >= 2:
                neckline = np.mean(troughs_between_peaks)
                current_price = closes[-1]
                
                # Pattern complete if price breaks below neckline
                below_neckline = current_price < neckline
                
                # Calculate confidence
                head_prominence = (peak_values[1] - np.mean([peak_values[0], peak_values[2]])) / peak_values[1]
                
                confidence = min(1.0, (
                    0.4 * (1 - shoulder_diff / 0.10) +
                    0.3 * min(1.0, head_prominence / 0.05) +
                    0.3 * (1.0 if below_neckline else 0.5)
                ))
                
                return confidence > self.min_confidence, confidence
            
            return False, 0.0
        
        except Exception as e:
            return False, 0.0
    
    def detect_double_top(self, df: pd.DataFrame) -> tuple[bool, float]:
        """
        Detect double top pattern:
        - Two peaks at roughly the same level
        - Trough between them
        - Price declining after second peak
        """
        if len(df) < 30:
            return False, 0.0
        
        try:
            recent = df.tail(30)
            closes = recent['Close'].values
            
            # Find peaks
            peaks, _ = find_peaks(closes, distance=5)
            
            if len(peaks) < 2:
                return False, 0.0
            
            # Get last 2 peaks
            last_2_peaks = peaks[-2:]
            peak_values = closes[last_2_peaks]
            
            # Check if peaks are at similar levels (within 3%)
            peak_diff = abs(peak_values[0] - peak_values[1]) / peak_values[0]
            
            if peak_diff > 0.03:
                return False, 0.0
            
            # Check for trough between peaks
            segment_between = closes[last_2_peaks[0]:last_2_peaks[1]]
            trough = min(segment_between)
            trough_depth = (max(peak_values) - trough) / max(peak_values)
            
            if trough_depth < 0.02:  # Trough should be at least 2% below peaks
                return False, 0.0
            
            # Check if price is declining after second peak
            current_price = closes[-1]
            price_from_peak = (peak_values[1] - current_price) / peak_values[1]
            
            confidence = min(1.0, (
                0.4 * (1 - peak_diff / 0.03) +
                0.3 * min(1.0, trough_depth / 0.05) +
                0.3 * min(1.0, price_from_peak / 0.05)
            ))
            
            return confidence > self.min_confidence, confidence
        
        except Exception as e:
            return False, 0.0
    
    def detect_double_bottom(self, df: pd.DataFrame) -> tuple[bool, float]:
        """
        Detect double bottom pattern:
        - Two troughs at roughly the same level
        - Peak between them
        - Price rising after second trough
        """
        if len(df) < 30:
            return False, 0.0
        
        try:
            recent = df.tail(30)
            closes = recent['Close'].values
            
            # Find troughs (inverted peaks)
            troughs, _ = find_peaks(-closes, distance=5)
            
            if len(troughs) < 2:
                return False, 0.0
            
            # Get last 2 troughs
            last_2_troughs = troughs[-2:]
            trough_values = closes[last_2_troughs]
            
            # Check if troughs are at similar levels (within 3%)
            trough_diff = abs(trough_values[0] - trough_values[1]) / trough_values[0]
            
            if trough_diff > 0.03:
                return False, 0.0
            
            # Check for peak between troughs
            segment_between = closes[last_2_troughs[0]:last_2_troughs[1]]
            peak = max(segment_between)
            peak_height = (peak - min(trough_values)) / min(trough_values)
            
            if peak_height < 0.02:
                return False, 0.0
            
            # Check if price is rising after second trough
            current_price = closes[-1]
            price_from_trough = (current_price - trough_values[1]) / trough_values[1]
            
            confidence = min(1.0, (
                0.4 * (1 - trough_diff / 0.03) +
                0.3 * min(1.0, peak_height / 0.05) +
                0.3 * min(1.0, price_from_trough / 0.05)
            ))
            
            return confidence > self.min_confidence, confidence
        
        except Exception as e:
            return False, 0.0
    
    def detect_gap_up(self, df: pd.DataFrame) -> tuple[bool, float]:
        """
        Detect gap up:
        - Today's low is higher than yesterday's high
        - Gap size is significant (>2%)
        """
        if len(df) < 2:
            return False, 0.0
        
        try:
            yesterday_high = df['High'].iloc[-2]
            today_low = df['Low'].iloc[-1]
            
            if today_low > yesterday_high:
                gap_size = (today_low - yesterday_high) / yesterday_high
                
                if gap_size >= 0.02:  # At least 2% gap
                    confidence = min(1.0, 0.5 + (gap_size / 0.10))  # Scale confidence with gap size
                    return True, confidence
            
            return False, 0.0
        
        except Exception as e:
            return False, 0.0
    
    def detect_gap_down(self, df: pd.DataFrame) -> tuple[bool, float]:
        """
        Detect gap down:
        - Today's high is lower than yesterday's low
        - Gap size is significant (>2%)
        """
        if len(df) < 2:
            return False, 0.0
        
        try:
            yesterday_low = df['Low'].iloc[-2]
            today_high = df['High'].iloc[-1]
            
            if today_high < yesterday_low:
                gap_size = (yesterday_low - today_high) / yesterday_low
                
                if gap_size >= 0.02:
                    confidence = min(1.0, 0.5 + (gap_size / 0.10))
                    return True, confidence
            
            return False, 0.0
        
        except Exception as e:
            return False, 0.0
    
    def detect_volume_spike(self, df: pd.DataFrame) -> tuple[bool, float]:
        """
        Detect volume spike:
        - Current volume significantly higher than average
        - At least 2x the 20-period average
        """
        if len(df) < 21:
            return False, 0.0
        
        try:
            current_volume = df['Volume'].iloc[-1]
            avg_volume = df['Volume'].iloc[-21:-1].mean()
            
            if avg_volume == 0:
                return False, 0.0
            
            volume_ratio = current_volume / avg_volume
            
            if volume_ratio >= 2.0:
                # Scale confidence with volume ratio
                confidence = min(1.0, 0.4 + (volume_ratio / 10))
                return True, confidence
            
            return False, 0.0
        
        except Exception as e:
            return False, 0.0
    
    def detect_ma_crossover(self, df: pd.DataFrame, bullish: bool = True) -> tuple[bool, float]:
        """
        Detect moving average crossover:
        - Bullish: Fast MA crosses above slow MA
        - Bearish: Fast MA crosses below slow MA
        """
        if len(df) < 51:
            return False, 0.0
        
        try:
            # Calculate moving averages
            df['SMA_20'] = df['Close'].rolling(window=20).mean()
            df['SMA_50'] = df['Close'].rolling(window=50).mean()
            
            # Get recent values
            sma20_current = df['SMA_20'].iloc[-1]
            sma20_previous = df['SMA_20'].iloc[-2]
            sma50_current = df['SMA_50'].iloc[-1]
            sma50_previous = df['SMA_50'].iloc[-2]
            
            if bullish:
                # Bullish crossover: SMA20 crosses above SMA50
                if sma20_previous <= sma50_previous and sma20_current > sma50_current:
                    separation = (sma20_current - sma50_current) / sma50_current
                    confidence = min(1.0, 0.6 + (separation / 0.02))
                    return True, confidence
            else:
                # Bearish crossover: SMA20 crosses below SMA50
                if sma20_previous >= sma50_previous and sma20_current < sma50_current:
                    separation = (sma50_current - sma20_current) / sma50_current
                    confidence = min(1.0, 0.6 + (separation / 0.02))
                    return True, confidence
            
            return False, 0.0
        
        except Exception as e:
            return False, 0.0
