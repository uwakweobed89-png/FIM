"""
LOGIN ATTEMPT DETECTOR - MODERNIZED VERSION
Production-ready security monitoring with mode switching.
Features: Environment-based config, SIEM integration, email alerts.
"""

import json
import logging
import os
import random
import signal
import sys
import time
from collections import defaultdict
from dataclasses import dataclass, asdict
from datetime import datetime, timedelta
from pathlib import Path
from typing import Optional, List, Dict
import yaml

import requests
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart


# ======================================================================
# CONFIGURATION MANAGEMENT
# ======================================================================

@dataclass
class Config:
    """Centralized configuration using dataclass for type safety."""
    mode: str  # 'active' or 'practice'
    max_attempts: int
    lockout_minutes: int
    log_file: str
    siem_enabled: bool
    siem_type: str
    siem_url: str
    siem_index: str
    siem_api_key: str
    email_enabled: bool
    email_sender: str
    email_password: str
    email_recipient: str
    smtp_server: str
    smtp_port: int
    use_tls: bool
    simulate_ips: bool
    simulation_interval: int
    log_level: str

    @classmethod
    def load_from_file(cls, config_path: str = "config.yaml"):
        """Load configuration from YAML file and env variables."""
        # Load YAML config
        try:
            with open(config_path, 'r') as f:
                config_data = yaml.safe_load(f)
        except FileNotFoundError:
            logging.warning(
                f"Config file {config_path} not found, using defaults"
            )
            config_data = cls._get_defaults()

        mode = config_data.get('mode', 'practice')
        mode_config = config_data.get(mode, {})
        siem_config = config_data.get('siem', {})
        email_config = config_data.get('email', {})
        logging_config = config_data.get('logging', {})

        # Environment variables override config file (for security)
        return cls(
            mode=mode,
            max_attempts=mode_config.get('max_attempts', 5),
            lockout_minutes=mode_config.get('lockout_minutes', 15),
            log_file=mode_config.get('log_file', 'auth.log'),
            siem_enabled=siem_config.get('enabled', False),
            siem_type=siem_config.get('type', 'elastic'),
            siem_url=siem_config.get(
                'elastic_url',
                'http://localhost:9200'
            ),
            siem_index=siem_config.get('elastic_index', 'siem_alerts'),
            siem_api_key=os.getenv(
                'ELASTIC_API_KEY',
                siem_config.get('elastic_api_key', '')
            ),
            email_enabled=email_config.get('enabled', False),
            email_sender=os.getenv('EMAIL_SENDER', ''),
            email_password=os.getenv('EMAIL_PASSWORD', ''),
            email_recipient=os.getenv('EMAIL_RECIPIENT', ''),
            smtp_server=email_config.get(
                'smtp_server',
                'smtp.gmail.com'
            ),
            smtp_port=email_config.get('smtp_port', 587),
            use_tls=email_config.get('use_tls', True),
            simulate_ips=mode_config.get('simulate_ips', False),
            simulation_interval=mode_config.get(
                'simulation_interval',
                2
            ),
            log_level=logging_config.get('level', 'INFO')
        )

    @staticmethod
    def _get_defaults() -> dict:
        """Return default configuration."""
        return {
            'mode': 'practice',
            'practice': {
                'max_attempts': 4,
                'lockout_minutes': 5,
                'simulate_ips': True,
                'simulation_interval': 2
            },
            'active': {
                'log_file': 'auth.log',
                'max_attempts': 5,
                'lockout_minutes': 15
            },
            'siem': {'enabled': False},
            'email': {'enabled': False},
            'logging': {'level': 'INFO'}
        }


# ======================================================================
# DATA STRUCTURES
# ======================================================================

@dataclass
class LogEvent:
    """Structured log event with type safety."""
    timestamp: str
    status: str
    user: str
    ip: str

    @classmethod
    def from_log_line(cls, line: str) -> Optional["LogEvent"]:
        """Parse a raw log line into a LogEvent object."""
        try:
            parts = line.strip().split()
            if len(parts) < 6:
                return None

            timestamp = f"{parts[0]} {parts[1]}"
            status = parts[2]
            user = parts[4].split("=")[1]
            ip = parts[5].split("=")[1]

            return cls(
                timestamp=timestamp,
                status=status,
                user=user,
                ip=ip
            )
        except (IndexError, ValueError) as e:
            logging.debug(f"Failed to parse line: {line.strip()} - {e}")
            return None


@dataclass
class Alert:
    """Security alert structure."""
    alert_level: str
    source_ip: str
    user: str
    attempts: int
    timestamp: str
    mode: str  # Track which mode generated the alert

    def to_dict(self) -> dict:
        """Convert to dictionary for JSON serialization."""
        return asdict(self)


# ======================================================================
# MAIN DETECTOR CLASS
# ======================================================================

class LoginDetector:
    """Main detector class with mode switching."""

    def __init__(self, config: Config):
        self.config = config
        self.failed_attempts: Dict[str, int] = defaultdict(int)
        self.lockout_registry: Dict[str, datetime] = {}
        self.siem_alert_queue: List[Alert] = []
        self.running = True
        self.last_position = 0  # Track file position for tailing

        # Setup logging
        self._setup_logging()

        # Register signal handlers for graceful shutdown
        signal.signal(signal.SIGINT, self._signal_handler)
        signal.signal(signal.SIGTERM, self._signal_handler)

        logging.info(
            f"LoginDetector initialized in {config.mode.upper()} mode"
        )
        logging.info(
            f"Max attempts: {config.max_attempts}, "
            f"Lockout: {config.lockout_minutes} min"
        )

    def _setup_logging(self):
        """Configure logging with file and console handlers."""
        log_level = getattr(
            logging,
            self.config.log_level.upper(),
            logging.INFO
        )

        # Create formatter
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )

        # Console handler
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(formatter)
        console_handler.setLevel(log_level)

        # File handler
        file_handler = logging.FileHandler('login_detector.log')
        file_handler.setFormatter(formatter)
        file_handler.setLevel(log_level)

        # Configure root logger
        logger = logging.getLogger()
        logger.setLevel(log_level)
        logger.addHandler(console_handler)
        logger.addHandler(file_handler)

    def _signal_handler(self, signum, frame):
        """Handle shutdown signals gracefully."""
        logging.info(
            f"Received signal {signum}, shutting down gracefully..."
        )
        self.running = False
        self.export_siem_alerts()
        sys.exit(0)

    # ==================================================================
    # CORE DETECTION LOGIC
    # ==================================================================

    def is_locked_out(self, ip: str) -> bool:
        """Check if an IP is currently locked out."""
        if ip not in self.lockout_registry:
            return False

        locked_at = self.lockout_registry[ip]
        now = datetime.now()
        elapsed = now - locked_at

        if elapsed < timedelta(minutes=self.config.lockout_minutes):
            return True
        else:
            # Clean up expired lockout
            del self.lockout_registry[ip]
            self.failed_attempts[ip] = 0
            logging.info(f"Lockout expired for {ip}")
            return False

    def handle_failed_login(self, event: LogEvent) -> None:
        """Process a failed login attempt."""
        if self.is_locked_out(event.ip):
            logging.debug(f"BLOCKED: {event.ip} is already locked out")
            return

        self.failed_attempts[event.ip] += 1
        count = self.failed_attempts[event.ip]

        logging.warning(
            f"Failed login #{count} for {event.user} "
            f"from {event.ip}"
        )

        # Decision tree based on attempt count
        if count >= self.config.max_attempts:
            self.trigger_lockout(event, count)
        elif count >= 3:
            self.raise_alert("SUSPICIOUS", event, count)
        else:
            self.log_event("FAILED_LOGIN", event)

    def trigger_lockout(self, event: LogEvent, count: int) -> None:
        """Lock out an IP address and raise critical alert."""
        self.lockout_registry[event.ip] = datetime.now()
        self.failed_attempts[event.ip] = 0

        logging.critical(
            f"LOCKOUT TRIGGERED for {event.ip} ({event.user})"
        )
        self.raise_alert("LOCKOUT", event, count)

    def handle_successful_login(self, event: LogEvent) -> None:
        """Process a successful login (resets counters)."""
        if event.ip in self.failed_attempts:
            previous_failures = self.failed_attempts[event.ip]
            self.failed_attempts[event.ip] = 0
            logging.info(
                f"Successful login for {event.user} from {event.ip} "
                f"(cleared {previous_failures} previous failures)"
            )
        else:
            logging.info(
                f"Successful login for {event.user} from {event.ip}"
            )

    def log_event(self, event_type: str, event: LogEvent) -> None:
        """Write structured log entry."""
        entry = (
            f"[{event_type}] {event.timestamp} | "
            f"user={event.user} | ip={event.ip}\n"
        )
        try:
            with open(self.config.log_file, "a") as f:
                f.write(entry)
        except IOError as e:
            logging.error(f"Failed to write to log file: {e}")

    # ==================================================================
    # ALERT MANAGEMENT
    # ==================================================================

    def raise_alert(
        self,
        level: str,
        event: LogEvent,
        count: int
    ) -> None:
        """Create and queue a security alert."""
        alert = Alert(
            alert_level=level,
            source_ip=event.ip,
            user=event.user,
            attempts=count,
            timestamp=event.timestamp,
            mode=self.config.mode
        )

        self.siem_alert_queue.append(alert)
        logging.info(
            f"Alert queued: {level} - {event.ip} ({count} attempts)"
        )

        # Immediate processing for critical alerts
        if level == "LOCKOUT":
            if self.config.siem_enabled:
                self.send_to_siem(alert)
            if self.config.email_enabled:
                self.send_email_alert(alert)

    def export_siem_alerts(self) -> None:
        """Export all queued alerts to JSON file and/or SIEM."""
        if not self.siem_alert_queue:
            logging.info("No alerts to export")
            return

        # Export to JSON file
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"siem_alerts_{timestamp}.json"

        try:
            with open(filename, "w") as f:
                json.dump(
                    [alert.to_dict() for alert in self.siem_alert_queue],
                    f,
                    indent=2
                )
            logging.info(
                f"Exported {len(self.siem_alert_queue)} "
                f"alerts to {filename}"
            )
        except IOError as e:
            logging.error(f"Failed to export alerts: {e}")

        # Send to SIEM if enabled
        if self.config.siem_enabled:
            for alert in self.siem_alert_queue:
                self.send_to_siem(alert)

        self.siem_alert_queue.clear()

    # ==================================================================
    # SIEM INTEGRATION
    # ==================================================================

    def send_to_siem(self, alert: Alert) -> None:
        """Send alert to SIEM platform (Elastic/Splunk/QRadar)."""
        if self.config.siem_type == "elastic":
            self._send_to_elastic(alert)
        elif self.config.siem_type == "splunk":
            self._send_to_splunk(alert)
        else:
            logging.warning(
                f"Unsupported SIEM type: {self.config.siem_type}"
            )

    def _send_to_elastic(self, alert: Alert) -> None:
        """Send alert to Elasticsearch."""
        url = (
            f"{self.config.siem_url}/"
            f"{self.config.siem_index}/_doc/"
        )
        headers = {"Content-Type": "application/json"}

        if self.config.siem_api_key:
            headers["Authorization"] = (
                f"ApiKey {self.config.siem_api_key}"
            )

        try:
            response = requests.post(
                url,
                json=alert.to_dict(),
                headers=headers,
                timeout=5
            )
            if response.status_code in [200, 201]:
                logging.info(
                    f"Alert sent to Elastic: {alert.alert_level}"
                )
            else:
                logging.error(
                    f"Elastic error {response.status_code}: "
                    f"{response.text}"
                )
        except requests.RequestException as e:
            logging.error(f"Failed to send to Elastic: {e}")

    def _send_to_splunk(self, alert: Alert) -> None:
        """Send alert to Splunk HEC."""
        # Placeholder for Splunk integration
        logging.info(f"Splunk integration: {alert.alert_level}")

    # ==================================================================
    # EMAIL ALERTS
    # ==================================================================

    def send_email_alert(self, alert: Alert) -> None:
        """Send email notification for critical alerts."""
        if not all([
            self.config.email_sender,
            self.config.email_password,
            self.config.email_recipient
        ]):
            logging.warning(
                "Email credentials not configured, "
                "skipping email alert"
            )
            return

        subject = (
            f"[SECURITY ALERT] {alert.alert_level} - "
            f"{alert.source_ip}"
        )
        body = f"""
Security Alert Detected!

Alert Level:  {alert.alert_level}
Source IP:    {alert.source_ip}
User:         {alert.user}
Attempts:     {alert.attempts}
Timestamp:    {alert.timestamp}
Mode:         {alert.mode}

This is an automated alert from the Login Detector system.
"""

        msg = MIMEMultipart()
        msg["From"] = self.config.email_sender
        msg["To"] = self.config.email_recipient
        msg["Subject"] = subject
        msg.attach(MIMEText(body, "plain"))

        try:
            with smtplib.SMTP(
                self.config.smtp_server,
                self.config.smtp_port
            ) as server:
                if self.config.use_tls:
                    server.starttls()
                server.login(
                    self.config.email_sender,
                    self.config.email_password
                )
                server.send_message(msg)
            logging.info("Email alert sent successfully")
        except Exception as e:
            logging.error(f"Failed to send email alert: {e}")

    # ==================================================================
    # LOG PROCESSING
    # ==================================================================

    def process_log_line(self, line: str) -> None:
        """Process a single log line."""
        if not line.strip():
            return

        event = LogEvent.from_log_line(line)

        if event is None:
            logging.debug(f"Skipped unparseable line: {line.strip()}")
            return

        if event.status == "FAILED":
            self.handle_failed_login(event)
        elif event.status == "SUCCESS":
            self.handle_successful_login(event)
        else:
            logging.debug(f"Unhandled status: {event.status}")

    def tail_log_file(self) -> List[str]:
        """Read only new lines from log file (efficient tailing)."""
        try:
            with open(self.config.log_file, 'r') as f:
                f.seek(self.last_position)
                new_lines = f.readlines()
                self.last_position = f.tell()
                return new_lines
        except FileNotFoundError:
            logging.warning(
                f"Log file {self.config.log_file} not found"
            )
            return []
        except IOError as e:
            logging.error(f"Error reading log file: {e}")
            return []

    # ==================================================================
    # PRACTICE MODE - SIMULATION
    # ==================================================================

    def generate_random_ip(self) -> str:
        """Generate a random IP address for practice mode."""
        return (
            f"{random.randint(1, 255)}."
            f"{random.randint(1, 255)}."
            f"{random.randint(1, 255)}."
            f"{random.randint(1, 255)}"
        )

    def generate_simulated_event(self) -> str:
        """Generate a simulated log line for practice mode."""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        # Weighted random: more failures for interesting scenarios
        status = random.choices(
            ["FAILED", "SUCCESS"],
            weights=[0.7, 0.3]
        )[0]

        # Pool of IPs with some repeating (to trigger lockouts)
        ip_pool = [
            self.generate_random_ip() if random.random() > 0.6
            else random.choice([
                "192.168.1.10",
                "10.0.0.5",
                "172.16.0.20",
                "192.168.1.50",
                "10.0.0.100"
            ])
        ]
        ip = ip_pool[0]

        users = ["admin", "root", "user", "service", "test"]
        user = random.choice(users)

        return f"{timestamp} {status} login user={user} ip={ip}"

    def run_practice_mode(self) -> None:
        """Run detector in practice mode with simulated data."""
        logging.info("=== PRACTICE MODE ===")
        logging.info(
            "Generating random login attempts to test detection..."
        )
        logging.info(
            f"Threshold: {self.config.max_attempts} failed attempts"
        )

        iteration = 0
        while self.running:
            iteration += 1
            logging.info(f"\n--- Simulation Iteration {iteration} ---")

            # Generate 3-5 events per iteration
            num_events = random.randint(3, 5)
            for _ in range(num_events):
                simulated_line = self.generate_simulated_event()
                logging.debug(f"Simulated: {simulated_line}")
                self.process_log_line(simulated_line)
                time.sleep(0.5)

            # Export alerts periodically
            if iteration % 5 == 0:
                self.export_siem_alerts()

            time.sleep(self.config.simulation_interval)

    # ==================================================================
    # ACTIVE MODE - REAL MONITORING
    # ==================================================================

    def run_active_mode(self) -> None:
        """Run detector in active mode (monitor real log files)."""
        logging.info("=== ACTIVE MODE ===")
        logging.info(f"Monitoring log file: {self.config.log_file}")
        logging.info("Press Ctrl+C to stop gracefully...")

        # Initial read to get current position
        if Path(self.config.log_file).exists():
            with open(self.config.log_file, 'r') as f:
                f.seek(0, 2)  # Seek to end
                self.last_position = f.tell()

        iteration = 0
        while self.running:
            iteration += 1
            new_lines = self.tail_log_file()

            if new_lines:
                logging.info(
                    f"Processing {len(new_lines)} new log lines..."
                )
                for line in new_lines:
                    self.process_log_line(line)

            # Periodic export (every 60 iterations = 10 minutes)
            if iteration % 60 == 0:
                self.export_siem_alerts()

            time.sleep(10)  # Check for new logs every 10 seconds

    # ==================================================================
    # MAIN RUN METHOD
    # ==================================================================

    def run(self) -> None:
        """Main entry point - routes to appropriate mode."""
        try:
            if self.config.mode == "practice":
                self.run_practice_mode()
            elif self.config.mode == "active":
                self.run_active_mode()
            else:
                logging.error(f"Invalid mode: {self.config.mode}")
                sys.exit(1)
        except KeyboardInterrupt:
            logging.info("Interrupted by user")
        finally:
            self.export_siem_alerts()
            logging.info("Detector shutdown complete")


# ======================================================================
# ENTRY POINT
# ======================================================================

def main():
    """Application entry point."""
    print("=" * 70)
    print("  LOGIN ATTEMPT DETECTOR - MODERNIZED VERSION")
    print("  Production-ready security monitoring with mode switching")
    print("=" * 70)

    # Load configuration
    config = Config.load_from_file()

    # Create and run detector
    detector = LoginDetector(config)
    detector.run()


if __name__ == "__main__":
    main()
