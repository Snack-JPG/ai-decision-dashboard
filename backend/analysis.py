"""
AI Analysis Engine for Decision Support Dashboard

This module provides comprehensive statistical and AI-powered analysis capabilities:
- Trend detection using linear regression and moving averages
- Anomaly detection using Z-score and IQR methods
- Seasonal decomposition for pattern identification
- Correlation analysis between metrics
- Change point detection for trend shifts
- Natural language explanations with confidence scores
"""

import numpy as np
import pandas as pd
from typing import Dict, List, Any, Tuple, Optional
from datetime import datetime, timedelta
import json
import os
from dotenv import load_dotenv

try:
    from scipy import stats
    from scipy.signal import find_peaks
    from sklearn.linear_model import LinearRegression
    from sklearn.preprocessing import StandardScaler
    from sklearn.cluster import DBSCAN
    import statsmodels.api as sm
    from statsmodels.tsa.seasonal import seasonal_decompose
    from statsmodels.stats.diagnostic import het_breuschpagan
except ImportError as e:
    print(f"Warning: Some analysis dependencies not available: {e}")
    print("Install with: pip install scipy scikit-learn statsmodels")

# Load environment variables
load_dotenv()

class AnalysisEngine:
    """
    Main analysis engine that provides statistical insights and AI-powered explanations
    """
    
    def __init__(self):
        self.confidence_threshold = 0.6  # Minimum confidence for reporting insights
        
    def analyze_dataset(self, data: List[Dict], columns_metadata: List[Dict]) -> Dict[str, Any]:
        """
        Run comprehensive analysis on a dataset
        
        Args:
            data: List of data rows as dictionaries
            columns_metadata: Column information including types and roles
            
        Returns:
            Dictionary containing all analysis results
        """
        if not data:
            return {"error": "No data provided for analysis"}
            
        # Convert to DataFrame
        df = pd.DataFrame(data)
        
        # Get numeric and time columns
        numeric_cols = [col['name'] for col in columns_metadata if col['data_type'] == 'numeric']
        time_cols = [col['name'] for col in columns_metadata if col['data_type'] == 'datetime']
        
        # Ensure numeric columns are actually numeric (convert from strings if needed)
        for col in numeric_cols:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors='coerce')
        
        # Ensure time columns are datetime
        for col in time_cols:
            if col in df.columns:
                df[col] = pd.to_datetime(df[col], errors='coerce')
        
        if not numeric_cols:
            return {"error": "No numeric columns found for analysis"}
        
        results = {
            "dataset_summary": self._get_dataset_summary(df, columns_metadata),
            "trends": {},
            "anomalies": {},
            "correlations": {},
            "seasonal_patterns": {},
            "change_points": {},
            "key_insights": []
        }
        
        # Process time-series data if available
        if time_cols:
            time_col = time_cols[0]  # Use first time column
            try:
                df[time_col] = pd.to_datetime(df[time_col])
                df = df.sort_values(time_col)
                
                # Run time-series analyses
                for col in numeric_cols:
                    if col != time_col and col in df.columns:
                        series_data = df[[time_col, col]].dropna()
                        if len(series_data) > 2:
                            # Trend analysis
                            trend_result = self._analyze_trend(series_data, time_col, col)
                            if trend_result['confidence'] > self.confidence_threshold:
                                results["trends"][col] = trend_result
                            
                            # Anomaly detection
                            anomaly_result = self._detect_anomalies(series_data, time_col, col)
                            if anomaly_result['anomalies']:
                                results["anomalies"][col] = anomaly_result
                            
                            # Seasonal analysis (if enough data points)
                            if len(series_data) > 12:
                                seasonal_result = self._analyze_seasonal_patterns(series_data, time_col, col)
                                if seasonal_result['confidence'] > self.confidence_threshold:
                                    results["seasonal_patterns"][col] = seasonal_result
                            
                            # Change point detection
                            change_result = self._detect_change_points(series_data, time_col, col)
                            if change_result['change_points']:
                                results["change_points"][col] = change_result
                
            except Exception as e:
                print(f"Warning: Time series analysis failed: {e}")
        
        # Correlation analysis (works without time data)
        if len(numeric_cols) > 1:
            correlation_result = self._analyze_correlations(df, numeric_cols)
            if correlation_result['significant_correlations']:
                results["correlations"] = correlation_result
        
        # Generate key insights summary
        results["key_insights"] = self._generate_key_insights(results)
        
        return results
    
    def _get_dataset_summary(self, df: pd.DataFrame, columns_metadata: List[Dict]) -> Dict[str, Any]:
        """Generate basic dataset summary statistics"""
        numeric_cols = [col['name'] for col in columns_metadata if col['data_type'] == 'numeric']
        
        summary = {
            "total_rows": len(df),
            "total_columns": len(df.columns),
            "numeric_columns": len(numeric_cols),
            "missing_data_percentage": (df.isnull().sum().sum() / (len(df) * len(df.columns))) * 100,
            "date_range": None
        }
        
        # Add date range if available
        time_cols = [col['name'] for col in columns_metadata if col['data_type'] == 'datetime']
        if time_cols and time_cols[0] in df.columns:
            try:
                df_temp = df.copy()
                df_temp[time_cols[0]] = pd.to_datetime(df_temp[time_cols[0]])
                summary["date_range"] = {
                    "start": df_temp[time_cols[0]].min().isoformat(),
                    "end": df_temp[time_cols[0]].max().isoformat(),
                    "days_span": (df_temp[time_cols[0]].max() - df_temp[time_cols[0]].min()).days
                }
            except:
                pass
                
        return summary
    
    def _analyze_trend(self, data: pd.DataFrame, time_col: str, value_col: str) -> Dict[str, Any]:
        """Analyze trend using linear regression and moving averages"""
        
        # Prepare data
        clean_data = data[[time_col, value_col]].dropna()
        if len(clean_data) < 3:
            return {"confidence": 0, "explanation": "Insufficient data for trend analysis"}
        
        # Convert time to numeric for regression
        time_numeric = (clean_data[time_col] - clean_data[time_col].min()).dt.total_seconds()
        values = clean_data[value_col].values
        
        # Linear regression
        X = time_numeric.values.reshape(-1, 1)
        y = values
        
        model = LinearRegression()
        model.fit(X, y)
        
        slope = model.coef_[0]
        r_squared = model.score(X, y)
        
        # Calculate moving averages
        if len(clean_data) >= 7:
            clean_data = clean_data.copy()
            clean_data['ma_7'] = clean_data[value_col].rolling(window=min(7, len(clean_data)//2)).mean()
            short_term_trend = clean_data['ma_7'].iloc[-1] - clean_data['ma_7'].iloc[-min(3, len(clean_data)//3)]
        else:
            short_term_trend = 0
        
        # Determine trend direction and strength
        trend_direction = "increasing" if slope > 0 else "decreasing" if slope < 0 else "stable"
        trend_strength = abs(slope)
        
        confidence = min(r_squared * 0.8 + (trend_strength / (np.std(values) + 1e-6)) * 0.2, 1.0)
        
        # Generate explanation
        explanation = self._generate_trend_explanation(
            trend_direction, slope, r_squared, short_term_trend, 
            clean_data[value_col].iloc[0], clean_data[value_col].iloc[-1]
        )
        
        return {
            "trend_direction": trend_direction,
            "slope": float(slope),
            "r_squared": float(r_squared),
            "confidence": float(confidence),
            "short_term_trend": float(short_term_trend),
            "start_value": float(clean_data[value_col].iloc[0]),
            "end_value": float(clean_data[value_col].iloc[-1]),
            "explanation": explanation,
            "suggested_action": self._suggest_trend_action(trend_direction, confidence)
        }
    
    def _detect_anomalies(self, data: pd.DataFrame, time_col: str, value_col: str) -> Dict[str, Any]:
        """Detect anomalies using Z-score and IQR methods"""
        
        clean_data = data[[time_col, value_col]].dropna()
        if len(clean_data) < 5:
            return {"anomalies": [], "explanation": "Insufficient data for anomaly detection"}
        
        values = clean_data[value_col].values
        
        # Z-score method
        z_scores = np.abs(stats.zscore(values))
        z_anomalies = z_scores > 2.5  # 2.5 standard deviations
        
        # IQR method
        Q1 = np.percentile(values, 25)
        Q3 = np.percentile(values, 75)
        IQR = Q3 - Q1
        iqr_lower = Q1 - 1.5 * IQR
        iqr_upper = Q3 + 1.5 * IQR
        iqr_anomalies = (values < iqr_lower) | (values > iqr_upper)
        
        # Combine methods (must be flagged by both for high confidence)
        high_confidence_anomalies = z_anomalies & iqr_anomalies
        medium_confidence_anomalies = z_anomalies | iqr_anomalies
        
        anomalies = []
        expected_value = float(np.median(values))
        for i, is_anomaly in enumerate(medium_confidence_anomalies):
            if is_anomaly:
                confidence = 0.8 if high_confidence_anomalies[i] else 0.5
                anomaly_type = "severe" if values[i] > Q3 + 2 * IQR or values[i] < Q1 - 2 * IQR else "moderate"
                severity = "high" if confidence >= 0.8 else "medium" if anomaly_type == "moderate" else "low"
                
                anomalies.append({
                    "timestamp": clean_data[time_col].iloc[i].isoformat(),
                    "value": float(values[i]),
                    "expected": expected_value,
                    "z_score": float(z_scores[i]),
                    "confidence": confidence,
                    "type": anomaly_type,
                    "severity": severity,
                    "explanation": f"Value {values[i]:.1f} is {'significantly higher' if values[i] > np.median(values) else 'significantly lower'} than expected"
                })
        
        # Sort by confidence descending
        anomalies = sorted(anomalies, key=lambda x: x['confidence'], reverse=True)
        
        return {
            "anomalies": anomalies,
            "total_anomalies": len(anomalies),
            "anomaly_rate": len(anomalies) / len(values) * 100,
            "explanation": f"Found {len(anomalies)} anomalies ({len(anomalies)/len(values)*100:.1f}% of data points)",
            "suggested_action": "Investigate high-confidence anomalies for potential data quality issues or significant events"
        }
    
    def _analyze_correlations(self, df: pd.DataFrame, numeric_cols: List[str]) -> Dict[str, Any]:
        """Find correlations between numeric columns"""
        
        if len(numeric_cols) < 2:
            return {"significant_correlations": []}
        
        # Calculate correlation matrix
        numeric_data = df[numeric_cols].select_dtypes(include=[np.number])
        corr_matrix = numeric_data.corr()
        
        significant_correlations = []
        
        # Find significant correlations (above threshold and not self-correlation)
        for i in range(len(corr_matrix.columns)):
            for j in range(i+1, len(corr_matrix.columns)):
                corr_value = corr_matrix.iloc[i, j]
                
                if not np.isnan(corr_value) and abs(corr_value) > 0.5:  # Significant correlation threshold
                    col1, col2 = corr_matrix.columns[i], corr_matrix.columns[j]
                    
                    correlation_strength = "strong" if abs(corr_value) > 0.7 else "moderate"
                    correlation_direction = "positive" if corr_value > 0 else "negative"
                    
                    significant_correlations.append({
                        "column_1": col1,
                        "column_2": col2,
                        "correlation": float(corr_value),
                        "strength": correlation_strength,
                        "direction": correlation_direction,
                        "confidence": min(abs(corr_value), 0.95),
                        "explanation": f"{correlation_strength.title()} {correlation_direction} correlation between {col1} and {col2}"
                    })
        
        # Sort by absolute correlation value
        significant_correlations = sorted(significant_correlations, key=lambda x: abs(x['correlation']), reverse=True)
        
        return {
            "significant_correlations": significant_correlations,
            "correlation_matrix": corr_matrix.to_dict(),
            "explanation": f"Found {len(significant_correlations)} significant correlations in the data",
            "suggested_action": "Monitor correlated metrics together for comprehensive insights"
        }
    
    def _analyze_seasonal_patterns(self, data: pd.DataFrame, time_col: str, value_col: str) -> Dict[str, Any]:
        """Analyze seasonal patterns using time series decomposition"""
        
        clean_data = data[[time_col, value_col]].dropna()
        if len(clean_data) < 12:  # Need at least 12 points for seasonal analysis
            return {"confidence": 0, "explanation": "Insufficient data for seasonal analysis"}
        
        # Set time as index and ensure regular frequency
        ts_data = clean_data.set_index(time_col)[value_col]
        ts_data = ts_data.asfreq('D', method='pad')  # Assume daily data, pad missing
        
        try:
            # Seasonal decomposition
            decomposition = seasonal_decompose(ts_data, model='additive', period=min(30, len(ts_data)//3))
            
            # Calculate seasonality strength
            seasonal_var = np.var(decomposition.seasonal.dropna())
            residual_var = np.var(decomposition.resid.dropna())
            seasonality_strength = seasonal_var / (seasonal_var + residual_var) if (seasonal_var + residual_var) > 0 else 0
            
            # Find peak seasonal periods
            seasonal_values = decomposition.seasonal.dropna()
            if len(seasonal_values) > 0:
                peak_index = seasonal_values.idxmax()
                trough_index = seasonal_values.idxmin()
                
                seasonal_patterns = {
                    "seasonality_strength": float(seasonality_strength),
                    "peak_period": peak_index.strftime("%B %d") if hasattr(peak_index, 'strftime') else str(peak_index),
                    "trough_period": trough_index.strftime("%B %d") if hasattr(trough_index, 'strftime') else str(trough_index),
                    "seasonal_amplitude": float(seasonal_values.max() - seasonal_values.min()),
                    "confidence": min(seasonality_strength * 1.2, 0.95)
                }
                
                explanation = f"Data shows {'strong' if seasonality_strength > 0.3 else 'moderate'} seasonal patterns with peaks around {seasonal_patterns['peak_period']}"
                
                return {
                    **seasonal_patterns,
                    "explanation": explanation,
                    "suggested_action": "Plan resources and strategies around identified seasonal patterns"
                }
                
        except Exception as e:
            return {"confidence": 0, "explanation": f"Seasonal analysis failed: {str(e)}"}
        
        return {"confidence": 0, "explanation": "No significant seasonal patterns detected"}
    
    def _detect_change_points(self, data: pd.DataFrame, time_col: str, value_col: str) -> Dict[str, Any]:
        """Detect significant change points in the time series"""
        
        clean_data = data[[time_col, value_col]].dropna()
        if len(clean_data) < 10:
            return {"change_points": [], "explanation": "Insufficient data for change point detection"}
        
        values = clean_data[value_col].values
        
        # Simple change point detection using variance in moving windows
        window_size = max(3, len(values) // 10)
        change_points = []
        
        for i in range(window_size, len(values) - window_size):
            # Calculate variance before and after potential change point
            before_window = values[i-window_size:i]
            after_window = values[i:i+window_size]
            
            before_mean = np.mean(before_window)
            after_mean = np.mean(after_window)
            
            # Significant change in mean
            mean_change = abs(after_mean - before_mean)
            pooled_std = np.sqrt((np.var(before_window) + np.var(after_window)) / 2)
            
            if pooled_std > 0:
                t_statistic = mean_change / (pooled_std * np.sqrt(2/window_size))
                
                # Simple threshold for significance (approximates t-test)
                if t_statistic > 2.0:  # Roughly p < 0.05
                    change_points.append({
                        "timestamp": clean_data[time_col].iloc[i].isoformat(),
                        "value": float(values[i]),
                        "before_mean": float(before_mean),
                        "after_mean": float(after_mean),
                        "magnitude": float(mean_change),
                        "confidence": min(t_statistic / 5.0, 0.95),  # Normalize t-statistic to confidence
                        "explanation": f"Significant change from {before_mean:.1f} to {after_mean:.1f}"
                    })
        
        # Remove nearby change points (keep strongest)
        filtered_change_points = []
        for cp in sorted(change_points, key=lambda x: x['confidence'], reverse=True):
            if not any(abs(pd.to_datetime(cp['timestamp']) - pd.to_datetime(fcp['timestamp'])).days < 5 
                      for fcp in filtered_change_points):
                filtered_change_points.append(cp)
        
        return {
            "change_points": filtered_change_points[:5],  # Return top 5
            "total_change_points": len(filtered_change_points),
            "explanation": f"Detected {len(filtered_change_points)} significant change points in the data",
            "suggested_action": "Investigate events around change points for underlying causes"
        }
    
    def _generate_trend_explanation(self, direction: str, slope: float, r_squared: float, 
                                  short_term_trend: float, start_value: float, end_value: float) -> str:
        """Generate human-readable trend explanation"""
        
        change_percent = ((end_value - start_value) / start_value) * 100 if start_value != 0 else 0
        
        if direction == "increasing":
            explanation = f"The data shows an upward trend with a {change_percent:.1f}% increase from {start_value:.1f} to {end_value:.1f}."
        elif direction == "decreasing":
            explanation = f"The data shows a downward trend with a {abs(change_percent):.1f}% decrease from {start_value:.1f} to {end_value:.1f}."
        else:
            explanation = f"The data shows a stable pattern with minimal change from {start_value:.1f} to {end_value:.1f}."
        
        if r_squared > 0.7:
            explanation += " The trend is highly consistent."
        elif r_squared > 0.4:
            explanation += " The trend shows moderate consistency with some variation."
        else:
            explanation += " The trend is weak with high variation."
        
        return explanation
    
    def _suggest_trend_action(self, direction: str, confidence: float) -> str:
        """Suggest actions based on trend analysis"""
        
        if confidence < 0.5:
            return "Monitor for more data to establish clear trends"
        
        if direction == "increasing":
            return "Investigate drivers of positive trend and consider scaling successful practices"
        elif direction == "decreasing":
            return "Investigate causes of decline and implement corrective measures"
        else:
            return "Monitor for any emerging patterns and maintain current performance"
    
    def _generate_key_insights(self, results: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Generate ranked key insights from all analysis results"""
        
        insights = []
        
        # Add trend insights
        for col, trend in results.get("trends", {}).items():
            if trend.get("confidence", 0) > 0.6:
                insights.append({
                    "type": "trend",
                    "metric": col,
                    "priority": "high" if abs(trend.get("slope", 0)) > 1 else "medium",
                    "confidence": trend.get("confidence", 0),
                    "title": f"{col} shows {trend.get('trend_direction', 'stable')} trend",
                    "explanation": trend.get("explanation", ""),
                    "suggested_action": trend.get("suggested_action", "")
                })
        
        # Add anomaly insights
        for col, anomalies in results.get("anomalies", {}).items():
            high_conf_anomalies = [a for a in anomalies.get("anomalies", []) if a.get("confidence", 0) > 0.7]
            if high_conf_anomalies:
                insights.append({
                    "type": "anomaly",
                    "metric": col,
                    "priority": "high",
                    "confidence": max(a.get("confidence", 0) for a in high_conf_anomalies),
                    "title": f"{len(high_conf_anomalies)} significant anomalies in {col}",
                    "explanation": f"Found {len(high_conf_anomalies)} data points that deviate significantly from normal patterns",
                    "suggested_action": "Investigate these anomalies for data quality issues or significant events"
                })
        
        # Add correlation insights
        strong_corrs = [c for c in results.get("correlations", {}).get("significant_correlations", []) 
                       if abs(c.get("correlation", 0)) > 0.7]
        if strong_corrs:
            top_corr = strong_corrs[0]
            insights.append({
                "type": "correlation",
                "metric": f"{top_corr['column_1']} & {top_corr['column_2']}",
                "priority": "medium",
                "confidence": top_corr.get("confidence", 0),
                "title": f"Strong correlation between {top_corr['column_1']} and {top_corr['column_2']}",
                "explanation": top_corr.get("explanation", ""),
                "suggested_action": "Monitor these metrics together for comprehensive insights"
            })
        
        # Sort by priority and confidence
        priority_order = {"high": 3, "medium": 2, "low": 1}
        insights.sort(key=lambda x: (priority_order.get(x["priority"], 0), x["confidence"]), reverse=True)
        
        return insights[:10]  # Return top 10 insights


# AI-powered explanation generation using Claude
class AIExplainer:
    """Generate natural language explanations using Claude AI"""
    
    def __init__(self):
        try:
            import anthropic
            api_key = os.getenv("ANTHROPIC_API_KEY")
            if api_key:
                self.client = anthropic.Anthropic(api_key=api_key)
            else:
                self.client = None
                print("Warning: ANTHROPIC_API_KEY not found. AI explanations will be limited.")
        except ImportError:
            self.client = None
            print("Warning: anthropic package not available. Install with: pip install anthropic")
    
    def enhance_insight(self, insight: Dict[str, Any], context: Dict[str, Any]) -> str:
        """Enhance basic statistical insight with AI-powered explanation"""
        
        if not self.client:
            return insight.get("explanation", "Statistical analysis completed")
        
        try:
            prompt = f"""
            Based on this statistical analysis result, provide a clear, professional explanation suitable for decision makers:
            
            Analysis Type: {insight.get('type', 'unknown')}
            Metric: {insight.get('metric', 'unknown')}
            Finding: {insight.get('title', 'unknown')}
            Statistical Details: {insight.get('explanation', 'unknown')}
            Confidence: {insight.get('confidence', 0):.2f}
            
            Dataset Context:
            - Total rows: {context.get('total_rows', 'unknown')}
            - Date range: {context.get('date_range', 'unknown')}
            
            Provide a 2-3 sentence explanation that:
            1. Explains what this means in business terms
            2. Indicates the level of confidence/reliability
            3. Suggests potential implications
            
            Keep it professional and actionable.
            """
            
            response = self.client.messages.create(
                model="claude-3-haiku-20240307",
                max_tokens=200,
                messages=[{"role": "user", "content": prompt}]
            )
            
            return response.content[0].text.strip()
            
        except Exception as e:
            print(f"AI explanation failed: {e}")
            return insight.get("explanation", "Statistical analysis completed")


def analyze_dataset_full(data: List[Dict], columns_metadata: List[Dict]) -> Dict[str, Any]:
    """
    Main entry point for comprehensive dataset analysis
    
    Args:
        data: List of data rows as dictionaries
        columns_metadata: Column information including types and roles
        
    Returns:
        Complete analysis results with insights and explanations
    """
    engine = AnalysisEngine()
    explainer = AIExplainer()
    
    # Run statistical analysis
    results = engine.analyze_dataset(data, columns_metadata)
    
    # Enhance insights with AI explanations if available
    if explainer.client and "key_insights" in results:
        for insight in results["key_insights"]:
            try:
                enhanced_explanation = explainer.enhance_insight(insight, results.get("dataset_summary", {}))
                insight["ai_explanation"] = enhanced_explanation
            except Exception as e:
                print(f"Failed to enhance insight: {e}")
    
    return results
