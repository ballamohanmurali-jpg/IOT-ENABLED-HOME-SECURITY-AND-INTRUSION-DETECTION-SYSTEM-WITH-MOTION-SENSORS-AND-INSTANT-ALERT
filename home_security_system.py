"""
IoT-Enabled Home Security and Intrusion Detection System
Using Motion Sensors and Instant Alert Notifications
"""

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime, timedelta
import json
from collections import defaultdict
import warnings
warnings.filterwarnings('ignore')

# Set style for better visualizations
sns.set_style("whitegrid")
plt.rcParams['figure.figsize'] = (12, 7)
plt.rcParams['font.size'] = 10

class PIRMotionSensor:
    """Simulates Passive Infrared (PIR) motion sensor for intrusion detection"""
    
    def __init__(self, sensor_id, location, sensitivity=0.85, false_positive_rate=0.05):
        self.sensor_id = sensor_id
        self.location = location
        self.sensitivity = sensitivity  # 0-1, higher = more sensitive
        self.false_positive_rate = false_positive_rate
        self.current_state = False  # True if motion detected
        self.measurement_history = []
        self.last_detection_time = None
        self.total_detections = 0
        
    def detect_motion(self, actual_motion, current_time, environmental_noise=0):
        """
        Detect motion with realistic sensor characteristics
        actual_motion: boolean indicating if motion is actually present
        environmental_noise: noise level (0-1) affecting detection accuracy
        Returns: detected_motion (boolean)
        """
        # Calculate detection probability based on sensitivity and noise
        detection_probability = self.sensitivity * (1 - environmental_noise * 0.3)
        
        if actual_motion:
            # Probability of detecting actual motion
            detected = np.random.random() < detection_probability
        else:
            # Probability of false positive
            detected = np.random.random() < self.false_positive_rate
        
        self.current_state = detected
        
        if detected:
            self.last_detection_time = current_time
            self.total_detections += 1
        
        self.measurement_history.append({
            'timestamp': current_time,
            'actual_motion': actual_motion,
            'detected_motion': detected,
            'sensor_id': self.sensor_id,
            'location': self.location
        })
        
        return detected


class DoorWindowSensor:
    """Simulates magnetic door/window sensors for entry point monitoring"""
    
    def __init__(self, sensor_id, location, sensor_type='door'):
        self.sensor_id = sensor_id
        self.location = location
        self.sensor_type = sensor_type  # 'door' or 'window'
        self.is_open = False
        self.measurement_history = []
        self.last_change_time = None
        self.total_open_events = 0
        
    def check_status(self, actual_status, current_time):
        """
        Check door/window status
        actual_status: boolean indicating if door/window is open
        Returns: detected_status (boolean)
        """
        # Door/window sensors are highly accurate (99.9%)
        detected_status = actual_status if np.random.random() > 0.001 else not actual_status
        
        if detected_status != self.is_open:
            self.last_change_time = current_time
            if detected_status:
                self.total_open_events += 1
        
        self.is_open = detected_status
        
        self.measurement_history.append({
            'timestamp': current_time,
            'status': detected_status,
            'sensor_id': self.sensor_id,
            'location': self.location,
            'type': self.sensor_type
        })
        
        return detected_status


class SecurityAlert:
    """Manages security alerts and notifications"""
    
    def __init__(self, alert_threshold=1, critical_threshold=3):
        self.alert_threshold = alert_threshold  # number of simultaneous alerts
        self.critical_threshold = critical_threshold
        self.alerts = []
        self.alert_history = []
        
    def generate_alert(self, sensor_id, location, alert_type, current_time, severity='medium'):
        """
        Generate a security alert
        alert_type: 'motion', 'door_open', 'window_open', 'unauthorized_entry'
        severity: 'low', 'medium', 'high', 'critical'
        """
        alert = {
            'timestamp': current_time,
            'sensor_id': sensor_id,
            'location': location,
            'alert_type': alert_type,
            'severity': severity,
            'message': f"{alert_type.upper()} detected at {location} by {sensor_id}"
        }
        
        self.alerts.append(alert)
        self.alert_history.append(alert)
        
        return alert


class SecurityZone:
    """Represents a security zone (room) with multiple sensors"""
    
    def __init__(self, zone_id, zone_name, zone_type='room'):
        self.zone_id = zone_id
        self.zone_name = zone_name
        self.zone_type = zone_type  # 'room', 'hallway', 'entrance'
        self.motion_sensors = {}
        self.door_sensors = {}
        self.window_sensors = {}
        self.alert_manager = SecurityAlert()
        self.zone_status = 'normal'  # normal, warning, alert, critical
        self.intrusion_detected = False
        self.last_alert_time = None
        
    def add_motion_sensor(self, sensor_id, location):
        """Add a motion sensor to the zone"""
        self.motion_sensors[sensor_id] = PIRMotionSensor(sensor_id, location)
        
    def add_door_sensor(self, sensor_id, location):
        """Add a door sensor to the zone"""
        self.door_sensors[sensor_id] = DoorWindowSensor(sensor_id, location, 'door')
        
    def add_window_sensor(self, sensor_id, location):
        """Add a window sensor to the zone"""
        self.window_sensors[sensor_id] = DoorWindowSensor(sensor_id, location, 'window')
        
    def evaluate_zone_security(self, current_time):
        """Evaluate overall zone security status"""
        active_alerts = len([a for a in self.alert_manager.alerts if 
                           (current_time - a['timestamp']).total_seconds() < 300])
        
        if active_alerts >= self.alert_manager.critical_threshold:
            self.zone_status = 'critical'
            self.intrusion_detected = True
        elif active_alerts >= self.alert_manager.alert_threshold:
            self.zone_status = 'alert'
        else:
            self.zone_status = 'normal'
            self.intrusion_detected = False


class HomeSecuritySystem:
    """Main system managing home security and intrusion detection"""
    
    def __init__(self, home_name='Smart Home'):
        self.home_name = home_name
        self.zones = {}
        self.system_status = 'armed'  # armed, disarmed
        self.daily_statistics = []
        self.all_alerts = []
        
    def add_zone(self, zone_id, zone_name, zone_type='room'):
        """Add a security zone to the system"""
        self.zones[zone_id] = SecurityZone(zone_id, zone_name, zone_type)
        
    def simulate_day(self, date=None, num_intervals=96):
        """
        Simulate a full day with 15-minute intervals (96 intervals in 24 hours)
        """
        if date is None:
            date = datetime.now().date()
        
        daily_data = []
        total_alerts = 0
        intrusion_attempts = 0
        
        for interval in range(num_intervals):
            quarter_hour = (interval * 15) / 60  # Convert interval to hours
            hour = int(quarter_hour)
            minutes = int((quarter_hour % 1) * 60)
            
            current_time = datetime.combine(date, datetime.min.time()) + timedelta(hours=quarter_hour)
            
            for zone_id, zone in self.zones.items():
                # Simulate motion patterns
                actual_motion = self._generate_motion_pattern(zone.zone_type, hour)
                
                # Simulate door/window activity
                door_open = self._generate_door_pattern(hour)
                window_open = self._generate_window_pattern(hour)
                
                # Process motion sensors
                for sensor_id, sensor in zone.motion_sensors.items():
                    detected_motion = sensor.detect_motion(actual_motion, current_time)
                    
                    if detected_motion and self.system_status == 'armed':
                        alert = zone.alert_manager.generate_alert(
                            sensor_id, zone.zone_name, 'motion', current_time, 'medium'
                        )
                        total_alerts += 1
                        self.all_alerts.append(alert)
                
                # Process door sensors
                for sensor_id, sensor in zone.door_sensors.items():
                    status = sensor.check_status(door_open, current_time)
                    
                    if status and self.system_status == 'armed':
                        alert = zone.alert_manager.generate_alert(
                            sensor_id, zone.zone_name, 'door_open', current_time, 'high'
                        )
                        total_alerts += 1
                        intrusion_attempts += 1
                        self.all_alerts.append(alert)
                
                # Process window sensors
                for sensor_id, sensor in zone.window_sensors.items():
                    status = sensor.check_status(window_open, current_time)
                    
                    if status and self.system_status == 'armed':
                        alert = zone.alert_manager.generate_alert(
                            sensor_id, zone.zone_name, 'window_open', current_time, 'high'
                        )
                        total_alerts += 1
                        intrusion_attempts += 1
                        self.all_alerts.append(alert)
                
                # Evaluate zone security
                zone.evaluate_zone_security(current_time)
                
                daily_data.append({
                    'date': date,
                    'time': f"{hour:02d}:{minutes:02d}",
                    'hour': hour,
                    'zone_id': zone_id,
                    'zone_name': zone.zone_name,
                    'zone_type': zone.zone_type,
                    'zone_status': zone.zone_status,
                    'motion_detected': actual_motion,
                    'door_open': door_open,
                    'window_open': window_open,
                    'intrusion_detected': zone.intrusion_detected,
                    'active_alerts': len(zone.alert_manager.alerts)
                })
        
        self.daily_statistics.append({
            'date': date,
            'total_alerts': total_alerts,
            'intrusion_attempts': intrusion_attempts,
            'num_zones': len(self.zones),
            'system_status': self.system_status
        })
        
        return pd.DataFrame(daily_data)
    
    def _generate_motion_pattern(self, zone_type, hour):
        """Generate realistic motion patterns based on zone type and time"""
        if zone_type == 'entrance':
            # High motion during morning (6-9) and evening (17-20)
            if 6 <= hour < 9 or 17 <= hour < 20:
                return np.random.random() < 0.4
            elif 9 <= hour < 17:
                return np.random.random() < 0.1
            else:
                return np.random.random() < 0.05
        
        elif zone_type == 'room':
            # Motion during daytime and early evening
            if 7 <= hour < 23:
                return np.random.random() < 0.2
            else:
                return np.random.random() < 0.05
        
        else:  # hallway
            # Sporadic motion throughout day
            return np.random.random() < 0.15
    
    def _generate_door_pattern(self, hour):
        """Generate realistic door opening patterns"""
        if 6 <= hour < 9 or 17 <= hour < 20:
            return np.random.random() < 0.15
        elif 9 <= hour < 17:
            return np.random.random() < 0.05
        else:
            return np.random.random() < 0.02
    
    def _generate_window_pattern(self, hour):
        """Generate realistic window opening patterns"""
        # Windows rarely open, especially at night
        if 9 <= hour < 18:
            return np.random.random() < 0.08
        else:
            return np.random.random() < 0.01
    
    def get_system_report(self):
        """Generate comprehensive system report"""
        report = {
            'home_name': self.home_name,
            'total_zones': len(self.zones),
            'total_alerts': len(self.all_alerts),
            'intrusion_attempts': sum([stat['intrusion_attempts'] for stat in self.daily_statistics]),
            'simulation_days': len(self.daily_statistics),
            'system_status': self.system_status,
            'avg_daily_alerts': np.mean([stat['total_alerts'] for stat in self.daily_statistics]) if self.daily_statistics else 0
        }
        return report


def generate_visualizations(system, daily_data):
    """Generate comprehensive visualizations for the report"""
    
    # 1. Security Status and Alert Distribution
    fig, axes = plt.subplots(2, 2, figsize=(14, 10))
    fig.suptitle('IoT-Enabled Home Security System - Alert Analysis', fontsize=16, fontweight='bold')
    
    # Alert types distribution
    alert_types = [a['alert_type'] for a in system.all_alerts]
    alert_counts = pd.Series(alert_types).value_counts()
    colors_map = {'motion': 'yellow', 'door_open': 'red', 'window_open': 'orange', 'unauthorized_entry': 'darkred'}
    colors = [colors_map.get(alert, 'gray') for alert in alert_counts.index]
    
    axes[0, 0].bar(alert_counts.index, alert_counts.values, color=colors, edgecolor='black')
    axes[0, 0].set_title('Alert Types Distribution', fontweight='bold')
    axes[0, 0].set_ylabel('Count')
    axes[0, 0].set_xlabel('Alert Type')
    axes[0, 0].tick_params(axis='x', rotation=45)
    for i, v in enumerate(alert_counts.values):
        axes[0, 0].text(i, v + 2, str(v), ha='center', fontweight='bold')
    
    # Alerts by hour
    alerts_by_hour = daily_data.groupby('hour')['active_alerts'].mean()
    axes[0, 1].plot(alerts_by_hour.index, alerts_by_hour.values, marker='o', 
                    linewidth=2, markersize=6, color='red')
    axes[0, 1].fill_between(alerts_by_hour.index, alerts_by_hour.values, alpha=0.3, color='red')
    axes[0, 1].set_title('Average Active Alerts by Hour', fontweight='bold')
    axes[0, 1].set_ylabel('Number of Alerts')
    axes[0, 1].set_xlabel('Hour of Day')
    axes[0, 1].grid(True, alpha=0.3)
    
    # Zone status distribution
    zone_status_counts = daily_data['zone_status'].value_counts()
    colors_status = {'normal': 'green', 'warning': 'yellow', 'alert': 'orange', 'critical': 'red'}
    colors = [colors_status.get(status, 'gray') for status in zone_status_counts.index]
    
    axes[1, 0].bar(zone_status_counts.index, zone_status_counts.values, color=colors, edgecolor='black')
    axes[1, 0].set_title('Zone Status Distribution', fontweight='bold')
    axes[1, 0].set_ylabel('Frequency')
    axes[1, 0].set_xlabel('Zone Status')
    for i, v in enumerate(zone_status_counts.values):
        axes[1, 0].text(i, v + 5, str(v), ha='center', fontweight='bold')
    
    # Intrusion detection timeline
    intrusion_by_hour = daily_data.groupby('hour')['intrusion_detected'].sum()
    axes[1, 1].bar(intrusion_by_hour.index, intrusion_by_hour.values, color='darkred', 
                   edgecolor='black', alpha=0.7)
    axes[1, 1].set_title('Intrusion Detection Events by Hour', fontweight='bold')
    axes[1, 1].set_ylabel('Number of Events')
    axes[1, 1].set_xlabel('Hour of Day')
    
    plt.tight_layout()
    plt.savefig('/home/ubuntu/security_report_project/fig_alert_analysis.png', dpi=300, bbox_inches='tight')
    print("Saved: fig_alert_analysis.png")
    plt.close()
    
    # 2. Sensor Activity Heatmap
    fig, ax = plt.subplots(figsize=(12, 6))
    
    sensor_activity = daily_data.pivot_table(values='active_alerts', index='zone_name', 
                                             columns='hour', aggfunc='mean', fill_value=0)
    
    sns.heatmap(sensor_activity, cmap='YlOrRd', annot=True, fmt='.1f', cbar_kws={'label': 'Avg Alerts'},
                ax=ax, linewidths=0.5, linecolor='gray')
    ax.set_title('Sensor Activity Heatmap - Alerts by Zone and Hour', fontweight='bold', fontsize=14)
    ax.set_xlabel('Hour of Day', fontweight='bold')
    ax.set_ylabel('Zone Name', fontweight='bold')
    
    plt.tight_layout()
    plt.savefig('/home/ubuntu/security_report_project/fig_sensor_heatmap.png', dpi=300, bbox_inches='tight')
    print("Saved: fig_sensor_heatmap.png")
    plt.close()
    
    # 3. Entry Point Security Analysis
    fig, axes = plt.subplots(1, 2, figsize=(14, 6))
    
    # Door events
    door_events = daily_data['door_open'].sum()
    window_events = daily_data['window_open'].sum()
    motion_events = daily_data['motion_detected'].sum()
    
    entry_data = [door_events, window_events, motion_events]
    entry_labels = ['Door Open', 'Window Open', 'Motion Detected']
    colors_entry = ['#FF6B6B', '#FFA500', '#FFD700']
    
    axes[0].bar(entry_labels, entry_data, color=colors_entry, edgecolor='black', alpha=0.7)
    axes[0].set_title('Entry Point Activity Summary', fontweight='bold')
    axes[0].set_ylabel('Number of Events')
    for i, v in enumerate(entry_data):
        axes[0].text(i, v + 5, str(int(v)), ha='center', fontweight='bold')
    
    # Alert severity distribution
    alert_severities = [a['severity'] for a in system.all_alerts]
    severity_counts = pd.Series(alert_severities).value_counts()
    colors_severity = {'low': 'yellow', 'medium': 'orange', 'high': 'red', 'critical': 'darkred'}
    colors = [colors_severity.get(sev, 'gray') for sev in severity_counts.index]
    
    axes[1].pie(severity_counts.values, labels=severity_counts.index, autopct='%1.1f%%',
                colors=colors, startangle=90, textprops={'fontsize': 11, 'fontweight': 'bold'})
    axes[1].set_title('Alert Severity Distribution', fontweight='bold')
    
    plt.tight_layout()
    plt.savefig('/home/ubuntu/security_report_project/fig_entry_security.png', dpi=300, bbox_inches='tight')
    print("Saved: fig_entry_security.png")
    plt.close()
    
    # 4. System Architecture Diagram
    fig, ax = plt.subplots(figsize=(12, 8))
    ax.axis('off')
    
    ax.text(0.5, 0.95, 'IoT-Enabled Home Security System Architecture', 
            ha='center', fontsize=16, fontweight='bold', transform=ax.transAxes)
    
    components = [
        ('PIR Motion\nSensors', 0.15, 0.75),
        ('Door/Window\nSensors', 0.5, 0.75),
        ('IoT\nCommunication', 0.85, 0.75),
        ('Alert\nManagement', 0.5, 0.50),
        ('Cloud\nServer', 0.15, 0.50),
        ('User\nNotifications', 0.85, 0.50),
    ]
    
    for label, x, y in components:
        bbox = dict(boxstyle='round,pad=0.6', facecolor='lightblue', edgecolor='black', linewidth=2)
        ax.text(x, y, label, ha='center', va='center', fontsize=11, fontweight='bold',
                transform=ax.transAxes, bbox=bbox)
    
    connections = [
        ((0.25, 0.75), (0.4, 0.75)),
        ((0.6, 0.75), (0.75, 0.75)),
        ((0.5, 0.65), (0.5, 0.60)),
        ((0.25, 0.65), (0.25, 0.60)),
        ((0.75, 0.65), (0.75, 0.60)),
    ]
    
    for start, end in connections:
        ax.annotate('', xy=end, xytext=start, transform=ax.transAxes,
                   arrowprops=dict(arrowstyle='->', lw=2, color='black'))
    
    features_text = 'Key Features:\n• Real-time Motion Detection\n• Entry Point Monitoring\n• Instant Alert Notifications\n• Remote Monitoring\n• 24/7 Security Coverage'
    ax.text(0.5, 0.20, features_text, ha='center', va='top', fontsize=10,
            transform=ax.transAxes, bbox=dict(boxstyle='round', facecolor='lightyellow', 
            edgecolor='black', linewidth=1.5))
    
    plt.tight_layout()
    plt.savefig('/home/ubuntu/security_report_project/fig_system_architecture.png', dpi=300, bbox_inches='tight')
    print("Saved: fig_system_architecture.png")
    plt.close()
    
    # 5. Daily Security Performance
    fig, ax = plt.subplots(figsize=(12, 6))
    
    daily_stats = pd.DataFrame(system.daily_statistics)
    
    x = np.arange(len(daily_stats))
    width = 0.35
    
    ax.bar(x - width/2, daily_stats['total_alerts'], width, label='Total Alerts', 
           color='orange', edgecolor='black')
    ax2 = ax.twinx()
    ax2.bar(x + width/2, daily_stats['intrusion_attempts'], width, label='Intrusion Attempts', 
            color='red', alpha=0.7, edgecolor='black')
    
    ax.set_xlabel('Day', fontweight='bold')
    ax.set_ylabel('Total Alerts', fontweight='bold', color='orange')
    ax2.set_ylabel('Intrusion Attempts', fontweight='bold', color='red')
    ax.set_title('Daily Security Performance', fontweight='bold', fontsize=14)
    ax.set_xticks(x)
    ax.set_xticklabels([f"Day {i+1}" for i in range(len(daily_stats))])
    ax.grid(True, alpha=0.3, axis='y')
    
    lines1, labels1 = ax.get_legend_handles_labels()
    lines2, labels2 = ax2.get_legend_handles_labels()
    ax.legend(lines1 + lines2, labels1 + labels2, loc='upper left')
    
    plt.tight_layout()
    plt.savefig('/home/ubuntu/security_report_project/fig_daily_performance.png', dpi=300, bbox_inches='tight')
    print("Saved: fig_daily_performance.png")
    plt.close()


def main():
    """Main execution function"""
    print("=" * 70)
    print("IOT-ENABLED HOME SECURITY AND INTRUSION DETECTION SYSTEM SIMULATION")
    print("=" * 70)
    
    # Initialize system
    system = HomeSecuritySystem("Smart Home Security System")
    
    # Add security zones
    zones_config = {
        'ZONE-001': {'name': 'Living Room', 'type': 'room'},
        'ZONE-002': {'name': 'Main Entrance', 'type': 'entrance'},
        'ZONE-003': {'name': 'Bedroom', 'type': 'room'},
        'ZONE-004': {'name': 'Kitchen', 'type': 'room'},
        'ZONE-005': {'name': 'Hallway', 'type': 'hallway'},
    }
    
    for zone_id, config in zones_config.items():
        system.add_zone(zone_id, config['name'], config['type'])
        zone = system.zones[zone_id]
        
        # Add sensors to each zone
        zone.add_motion_sensor(f"{zone_id}-PIR-01", config['name'])
        zone.add_door_sensor(f"{zone_id}-DOOR-01", config['name'])
        zone.add_window_sensor(f"{zone_id}-WINDOW-01", config['name'])
    
    print(f"\nSystem initialized with {len(zones_config)} security zones:")
    for zone_id, config in zones_config.items():
        print(f"  - {zone_id}: {config['name']} ({config['type']})")
    
    # Simulate 7 days
    print("\nSimulating 7 days of security monitoring...")
    all_data = []
    
    for day in range(7):
        simulation_date = datetime.now().date() - timedelta(days=6-day)
        daily_data = system.simulate_day(simulation_date)
        all_data.append(daily_data)
        
        daily_stats = system.daily_statistics[-1]
        print(f"Day {day+1}: Alerts={daily_stats['total_alerts']}, "
              f"Intrusions={daily_stats['intrusion_attempts']}, "
              f"Status={daily_stats['system_status']}")
    
    # Combine all data
    combined_data = pd.concat(all_data, ignore_index=True)
    
    # Generate visualizations
    print("\nGenerating visualizations...")
    generate_visualizations(system, combined_data)
    
    # Generate report data
    report = system.get_system_report()
    
    print("\n" + "=" * 70)
    print("SYSTEM REPORT")
    print("=" * 70)
    print(f"Home Name: {report['home_name']}")
    print(f"Total Security Zones: {report['total_zones']}")
    print(f"Total Alerts Generated: {report['total_alerts']}")
    print(f"Intrusion Attempts Detected: {report['intrusion_attempts']}")
    print(f"Average Daily Alerts: {report['avg_daily_alerts']:.1f}")
    print(f"System Status: {report['system_status']}")
    print(f"Simulation Period: {report['simulation_days']} days")
    print("=" * 70)
    
    # Save data to CSV
    combined_data.to_csv('/home/ubuntu/security_report_project/simulation_data.csv', index=False)
    print("\nSimulation data saved to: simulation_data.csv")
    
    # Save report to JSON
    report_json = {
        'system_report': report,
        'zones': list(zones_config.keys()),
        'simulation_date': datetime.now().isoformat(),
        'daily_statistics': system.daily_statistics,
        'total_alerts': len(system.all_alerts)
    }
    
    with open('/home/ubuntu/security_report_project/system_report.json', 'w') as f:
        json.dump(report_json, f, indent=2, default=str)
    
    print("System report saved to: system_report.json")
    
    return system, combined_data


if __name__ == "__main__":
    system, data = main()
