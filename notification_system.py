"""
Turtle Trader - Notification System
Multi-channel notification system for trading alerts
"""

import smtplib
import requests
import json
from datetime import datetime
from typing import Dict, List, Optional, Any
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from loguru import logger

from core.config import config, Utils

class NotificationLevel:
    """Notification priority levels"""
    CRITICAL = "CRITICAL"
    HIGH = "HIGH"
    MEDIUM = "MEDIUM"
    LOW = "LOW"
    INFO = "INFO"

class NotificationChannel:
    """Notification delivery channels"""
    EMAIL = "EMAIL"
    TELEGRAM = "TELEGRAM"
    SLACK = "SLACK"
    WEBHOOK = "WEBHOOK"
    SMS = "SMS"

class EmailNotifier:
    """Email notification handler"""
    
    def __init__(self):
        self.smtp_server = config.get("NOTIFICATIONS", "SMTP_SERVER", "smtp.gmail.com")
        self.smtp_port = config.getint("NOTIFICATIONS", "SMTP_PORT", 587)
        self.email = config.get("NOTIFICATIONS", "EMAIL_FROM", "")
        self.password = config.get("NOTIFICATIONS", "EMAIL_PASSWORD", "")
        self.recipients = config.get("NOTIFICATIONS", "EMAIL_RECIPIENTS", "").split(",")
        self.enabled = all([self.email, self.password, self.recipients[0]])
        
        if not self.enabled:
            logger.warning("Email notifications disabled - missing configuration")
    
    def send(self, subject: str, message: str, level: str = NotificationLevel.INFO) -> bool:
        """Send email notification"""
        if not self.enabled:
            return False
        
        try:
            # Create message
            msg = MIMEMultipart()
            msg['From'] = self.email
            msg['To'] = ", ".join(self.recipients)
            msg['Subject'] = f"[{level}] Turtle Trader - {subject}"
            
            # Format message with timestamp
            formatted_message = f"""
            <html>
            <body>
                <h2>Turtle Trader Alert</h2>
                <p><strong>Level:</strong> {level}</p>
                <p><strong>Time:</strong> {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
                <p><strong>Subject:</strong> {subject}</p>
                <div style="margin-top: 20px; padding: 10px; background-color: #f5f5f5;">
                    <pre>{message}</pre>
                </div>
            </body>
            </html>
            """
            
            msg.attach(MIMEText(formatted_message, 'html'))
            
            # Send email
            with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                server.starttls()
                server.login(self.email, self.password)
                server.send_message(msg)
            
            logger.info(f"Email notification sent: {subject}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to send email notification: {e}")
            return False

class TelegramNotifier:
    """Telegram notification handler"""
    
    def __init__(self):
        self.bot_token = config.get("NOTIFICATIONS", "TELEGRAM_BOT_TOKEN", "")
        self.chat_ids = config.get("NOTIFICATIONS", "TELEGRAM_CHAT_IDS", "").split(",")
        self.enabled = all([self.bot_token, self.chat_ids[0]])
        
        if not self.enabled:
            logger.warning("Telegram notifications disabled - missing configuration")
    
    def send(self, subject: str, message: str, level: str = NotificationLevel.INFO) -> bool:
        """Send Telegram notification"""
        if not self.enabled:
            return False
        
        try:
            # Format message
            emoji_map = {
                NotificationLevel.CRITICAL: "🚨",
                NotificationLevel.HIGH: "⚠️",
                NotificationLevel.MEDIUM: "📊",
                NotificationLevel.LOW: "ℹ️",
                NotificationLevel.INFO: "💡"
            }
            
            emoji = emoji_map.get(level, "📈")
            
            formatted_message = f"""
{emoji} *Turtle Trader Alert*

*Level:* {level}
*Time:* {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
*Subject:* {subject}

```
{message}
```
            """
            
            # Send to each chat
            success = True
            for chat_id in self.chat_ids:
                chat_id = chat_id.strip()
                if not chat_id:
                    continue
                
                url = f"https://api.telegram.org/bot{self.bot_token}/sendMessage"
                data = {
                    'chat_id': chat_id,
                    'text': formatted_message,
                    'parse_mode': 'Markdown'
                }
                
                response = requests.post(url, data=data, timeout=10)
                if not response.ok:
                    logger.error(f"Failed to send Telegram message to {chat_id}: {response.text}")
                    success = False
            
            if success:
                logger.info(f"Telegram notification sent: {subject}")
            
            return success
            
        except Exception as e:
            logger.error(f"Failed to send Telegram notification: {e}")
            return False

class SlackNotifier:
    """Slack notification handler"""
    
    def __init__(self):
        self.webhook_url = config.get("NOTIFICATIONS", "SLACK_WEBHOOK_URL", "")
        self.channel = config.get("NOTIFICATIONS", "SLACK_CHANNEL", "#trading")
        self.enabled = bool(self.webhook_url)
        
        if not self.enabled:
            logger.warning("Slack notifications disabled - missing webhook URL")
    
    def send(self, subject: str, message: str, level: str = NotificationLevel.INFO) -> bool:
        """Send Slack notification"""
        if not self.enabled:
            return False
        
        try:
            # Color coding based on level
            color_map = {
                NotificationLevel.CRITICAL: "danger",
                NotificationLevel.HIGH: "warning",
                NotificationLevel.MEDIUM: "good",
                NotificationLevel.LOW: "#36a64f",
                NotificationLevel.INFO: "#2eb886"
            }
            
            payload = {
                "channel": self.channel,
                "username": "Turtle Trader",
                "icon_emoji": ":chart_with_upwards_trend:",
                "attachments": [{
                    "color": color_map.get(level, "good"),
                    "title": f"[{level}] {subject}",
                    "text": message,
                    "footer": "Turtle Trader",
                    "ts": int(datetime.now().timestamp()),
                    "fields": [
                        {
                            "title": "Level",
                            "value": level,
                            "short": True
                        },
                        {
                            "title": "Time",
                            "value": datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                            "short": True
                        }
                    ]
                }]
            }
            
            response = requests.post(
                self.webhook_url,
                data=json.dumps(payload),
                headers={'Content-Type': 'application/json'},
                timeout=10
            )
            
            if response.ok:
                logger.info(f"Slack notification sent: {subject}")
                return True
            else:
                logger.error(f"Failed to send Slack notification: {response.text}")
                return False
            
        except Exception as e:
            logger.error(f"Failed to send Slack notification: {e}")
            return False

class WebhookNotifier:
    """Custom webhook notification handler"""
    
    def __init__(self):
        self.webhook_urls = config.get("NOTIFICATIONS", "WEBHOOK_URLS", "").split(",")
        self.enabled = bool(self.webhook_urls[0])
        
        if not self.enabled:
            logger.warning("Webhook notifications disabled - no URLs configured")
    
    def send(self, subject: str, message: str, level: str = NotificationLevel.INFO) -> bool:
        """Send webhook notification"""
        if not self.enabled:
            return False
        
        try:
            payload = {
                "timestamp": datetime.now().isoformat(),
                "level": level,
                "subject": subject,
                "message": message,
                "source": "turtle_trader"
            }
            
            success = True
            for url in self.webhook_urls:
                url = url.strip()
                if not url:
                    continue
                
                response = requests.post(
                    url,
                    json=payload,
                    headers={'Content-Type': 'application/json'},
                    timeout=10
                )
                
                if not response.ok:
                    logger.error(f"Failed to send webhook notification to {url}: {response.text}")
                    success = False
            
            if success:
                logger.info(f"Webhook notification sent: {subject}")
            
            return success
            
        except Exception as e:
            logger.error(f"Failed to send webhook notification: {e}")
            return False

class NotificationManager:
    """Central notification management system"""
    
    def __init__(self):
        # Initialize notifiers
        self.email = EmailNotifier()
        self.telegram = TelegramNotifier()
        self.slack = SlackNotifier()
        self.webhook = WebhookNotifier()
        
        # Configuration
        self.enabled_channels = self._get_enabled_channels()
        self.level_filters = self._get_level_filters()
        
        # Rate limiting
        self.last_notifications = {}
        self.min_interval = config.getint("NOTIFICATIONS", "MIN_INTERVAL_SECONDS", 60)
        
        logger.info(f"Notification Manager initialized with channels: {self.enabled_channels}")
    
    def send_trading_signal(self, symbol: str, action: str, price: float, 
                          strategy: str, confidence: float):
        """Send trading signal notification"""
        subject = f"Trading Signal: {action} {symbol}"
        message = f"""
Symbol: {symbol}
Action: {action}
Price: ₹{price:,.2f}
Strategy: {strategy}
Confidence: {confidence:.2%}
        """
        
        level = NotificationLevel.HIGH if confidence > 0.8 else NotificationLevel.MEDIUM
        self.send_notification(subject, message, level, channels=[NotificationChannel.TELEGRAM, NotificationChannel.SLACK])
    
    def send_order_update(self, symbol: str, order_id: str, status: str, 
                         quantity: int, price: float):
        """Send order status update"""
        subject = f"Order {status}: {symbol}"
        message = f"""
Order ID: {order_id}
Symbol: {symbol}
Status: {status}
Quantity: {quantity}
Price: ₹{price:,.2f}
        """
        
        level = NotificationLevel.INFO if status in ['EXECUTED', 'COMPLETE'] else NotificationLevel.MEDIUM
        self.send_notification(subject, message, level)
    
    def send_risk_alert(self, alert_type: str, details: Dict[str, Any]):
        """Send risk management alert"""
        subject = f"Risk Alert: {alert_type}"
        message = f"""
Alert Type: {alert_type}
Details: {json.dumps(details, indent=2)}
        """
        
        self.send_notification(subject, message, NotificationLevel.CRITICAL)
    
    def send_portfolio_update(self, total_value: float, daily_pnl: float, 
                            daily_return: float):
        """Send portfolio performance update"""
        subject = "Daily Portfolio Update"
        message = f"""
Portfolio Value: ₹{total_value:,.2f}
Daily P&L: ₹{daily_pnl:,.2f}
Daily Return: {daily_return:.2%}
        """
        
        level = NotificationLevel.INFO
        if abs(daily_return) > 0.05:  # >5% daily change
            level = NotificationLevel.HIGH
        
        self.send_notification(subject, message, level)
    
    def send_system_alert(self, alert_type: str, message: str):
        """Send system/technical alert"""
        subject = f"System Alert: {alert_type}"
        
        level = NotificationLevel.HIGH
        if "error" in alert_type.lower() or "failed" in alert_type.lower():
            level = NotificationLevel.CRITICAL
        
        self.send_notification(subject, message, level)
    
    def send_notification(self, subject: str, message: str, 
                         level: str = NotificationLevel.INFO,
                         channels: List[str] = None):
        """Send notification through specified channels"""
        
        # Rate limiting check
        notification_key = f"{subject}_{level}"
        current_time = datetime.now()
        
        if notification_key in self.last_notifications:
            time_diff = (current_time - self.last_notifications[notification_key]).total_seconds()
            if time_diff < self.min_interval:
                logger.debug(f"Notification rate limited: {subject}")
                return
        
        self.last_notifications[notification_key] = current_time
        
        # Use default channels if none specified
        if channels is None:
            channels = self.enabled_channels
        
        # Filter by level
        if not self._should_send_level(level):
            logger.debug(f"Notification filtered by level: {level}")
            return
        
        # Send through each channel
        results = {}
        
        if NotificationChannel.EMAIL in channels and self.email.enabled:
            results[NotificationChannel.EMAIL] = self.email.send(subject, message, level)
        
        if NotificationChannel.TELEGRAM in channels and self.telegram.enabled:
            results[NotificationChannel.TELEGRAM] = self.telegram.send(subject, message, level)
        
        if NotificationChannel.SLACK in channels and self.slack.enabled:
            results[NotificationChannel.SLACK] = self.slack.send(subject, message, level)
        
        if NotificationChannel.WEBHOOK in channels and self.webhook.enabled:
            results[NotificationChannel.WEBHOOK] = self.webhook.send(subject, message, level)
        
        # Log results
        successful_channels = [channel for channel, success in results.items() if success]
        failed_channels = [channel for channel, success in results.items() if not success]
        
        if successful_channels:
            logger.info(f"Notification sent via {', '.join(successful_channels)}: {subject}")
        
        if failed_channels:
            logger.warning(f"Notification failed via {', '.join(failed_channels)}: {subject}")
    
    def test_notifications(self):
        """Test all configured notification channels"""
        test_subject = "Test Notification"
        test_message = "This is a test notification from Turtle Trader system."
        
        logger.info("Testing notification channels...")
        
        results = {}
        
        if self.email.enabled:
            results[NotificationChannel.EMAIL] = self.email.send(test_subject, test_message)
        
        if self.telegram.enabled:
            results[NotificationChannel.TELEGRAM] = self.telegram.send(test_subject, test_message)
        
        if self.slack.enabled:
            results[NotificationChannel.SLACK] = self.slack.send(test_subject, test_message)
        
        if self.webhook.enabled:
            results[NotificationChannel.WEBHOOK] = self.webhook.send(test_subject, test_message)
        
        # Report results
        for channel, success in results.items():
            status = "SUCCESS" if success else "FAILED"
            logger.info(f"{channel} test: {status}")
        
        return results
    
    def _get_enabled_channels(self) -> List[str]:
        """Get list of enabled notification channels"""
        channels = []
        
        if self.email.enabled:
            channels.append(NotificationChannel.EMAIL)
        
        if self.telegram.enabled:
            channels.append(NotificationChannel.TELEGRAM)
        
        if self.slack.enabled:
            channels.append(NotificationChannel.SLACK)
        
        if self.webhook.enabled:
            channels.append(NotificationChannel.WEBHOOK)
        
        return channels
    
    def _get_level_filters(self) -> List[str]:
        """Get notification level filters from config"""
        level_filter = config.get("NOTIFICATIONS", "LEVEL_FILTER", "INFO,MEDIUM,HIGH,CRITICAL")
        return [level.strip() for level in level_filter.split(",")]
    
    def _should_send_level(self, level: str) -> bool:
        """Check if notification level should be sent"""
        return level in self.level_filters

# Create global notification manager instance
notification_manager = NotificationManager()

# Convenience functions
def send_trading_signal(symbol: str, action: str, price: float, strategy: str, confidence: float):
    """Send trading signal notification"""
    notification_manager.send_trading_signal(symbol, action, price, strategy, confidence)

def send_order_update(symbol: str, order_id: str, status: str, quantity: int, price: float):
    """Send order status update"""
    notification_manager.send_order_update(symbol, order_id, status, quantity, price)

def send_risk_alert(alert_type: str, details: Dict[str, Any]):
    """Send risk management alert"""
    notification_manager.send_risk_alert(alert_type, details)

def send_portfolio_update(total_value: float, daily_pnl: float, daily_return: float):
    """Send portfolio performance update"""
    notification_manager.send_portfolio_update(total_value, daily_pnl, daily_return)

def send_system_alert(alert_type: str, message: str):
    """Send system/technical alert"""
    notification_manager.send_system_alert(alert_type, message)

# Export main classes and functions
__all__ = [
    'NotificationManager', 'NotificationLevel', 'NotificationChannel',
    'notification_manager', 'send_trading_signal', 'send_order_update',
    'send_risk_alert', 'send_portfolio_update', 'send_system_alert'
]
