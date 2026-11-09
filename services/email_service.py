"""SMTP Email Service for User Registration and Password Reset OTPs.

Default sender: bommareddymanoharreddy0@gmail.com
Protocol: SMTP (smtp.gmail.com:587 TLS)
"""
import logging
import os
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from typing import Tuple

logger = logging.getLogger(__name__)

# SMTP Configuration
SMTP_HOST = os.getenv("SMTP_HOST", "smtp.gmail.com")
SMTP_PORT = int(os.getenv("SMTP_PORT", 587))
DEFAULT_SENDER = "bommareddymanoharreddy0@gmail.com"
SMTP_USER = os.getenv("SMTP_USER", DEFAULT_SENDER).strip() or DEFAULT_SENDER
SMTP_PASSWORD = os.getenv("SMTP_PASSWORD") or os.getenv("GMAIL_APP_PASSWORD") or os.getenv("EMAIL_PASSWORD", "")
SENDER_NAME = "AI Resume Analyzer"


def is_smtp_configured() -> bool:
    """Return True if live SMTP credentials are provided in the environment."""
    return bool(SMTP_PASSWORD and SMTP_PASSWORD.strip())


def send_otp_email(
    to_email: str,
    otp: str,
    purpose: str = "Registration",
    recipient_name: str = ""
) -> Tuple[bool, str]:
    """
    Send a 6-digit OTP email using SMTP protocol via bommareddymanoharreddy0@gmail.com.
    
    Args:
        to_email: Destination email address.
        otp: 6-digit one-time password.
        purpose: 'Registration' or 'Password Reset'.
        recipient_name: Optional user display name.
        
    Returns:
        (success: bool, status_message: str)
    """
    to_email = (to_email or "").strip()
    if not to_email or "@" not in to_email:
        return False, "Invalid recipient email address."

    is_reset = "reset" in purpose.lower()
    subject_action = "Password Reset" if is_reset else "Account Registration"
    subject = f"[{subject_action}] Your Verification Code: {otp}"

    display_name = recipient_name.strip() if recipient_name else "Candidate"
    action_description = (
        "reset your password" if is_reset
        else "verify your email address and activate your account"
    )

    # HTML Email Template
    html_body = f"""<!DOCTYPE html>
<html>
<head>
  <meta charset="utf-8">
  <style>
    body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif; background-color: #f8fafc; margin: 0; padding: 24px; color: #1e293b; }}
    .card {{ max-width: 520px; margin: 0 auto; background: #ffffff; border-radius: 12px; border: 1px solid #e2e8f0; padding: 36px 32px; box-shadow: 0 4px 6px -1px rgba(0,0,0,0.05); }}
    .header {{ text-align: center; margin-bottom: 24px; }}
    .logo {{ font-size: 20px; font-weight: 800; color: #0f172a; text-decoration: none; }}
    .logo span {{ color: #2563eb; }}
    .title {{ font-size: 22px; font-weight: 700; color: #0f172a; margin-top: 16px; margin-bottom: 8px; }}
    .subtitle {{ font-size: 14px; color: #64748b; line-height: 1.5; }}
    .otp-box {{ background: #eff6ff; border: 2px dashed #93c5fd; border-radius: 10px; padding: 20px; text-align: center; margin: 28px 0; }}
    .otp-code {{ font-size: 34px; font-weight: 800; letter-spacing: 8px; color: #1d4ed8; font-family: 'Courier New', monospace; }}
    .otp-expiry {{ font-size: 12px; color: #64748b; margin-top: 8px; }}
    .notice {{ font-size: 12px; color: #94a3b8; border-top: 1px solid #f1f5f9; padding-top: 18px; margin-top: 24px; line-height: 1.5; }}
    .footer {{ text-align: center; font-size: 11px; color: #94a3b8; margin-top: 20px; }}
  </style>
</head>
<body>
  <div class="card">
    <div class="header">
      <div class="logo">AI <span>Resume</span> Analyzer</div>
      <div class="title">{subject_action} Verification</div>
      <div class="subtitle">Hello {display_name}, use the verification code below to {action_description}.</div>
    </div>
    
    <div class="otp-box">
      <div class="otp-code">{otp}</div>
      <div class="otp-expiry">This code is valid for <strong>10 minutes</strong>. Do not share it with anyone.</div>
    </div>

    <div class="notice">
      If you did not request this verification code, please ignore this email or contact support. No changes have been made to your account.
    </div>
  </div>
  <div class="footer">
    Sent securely via SMTP from {SMTP_USER} &bull; AI Resume Analyzer Platform
  </div>
</body>
</html>
"""

    text_body = (
        f"AI Resume Analyzer - {subject_action}\n\n"
        f"Hello {display_name},\n\n"
        f"Your verification code is: {otp}\n\n"
        f"This code will expire in 10 minutes.\n"
        f"Sent from: {SMTP_USER}\n"
    )

    # Testing mode simulation for automated test suites
    try:
        from flask import current_app
        if current_app and current_app.config.get("TESTING"):
            return True, f"Verification OTP sent to {to_email} (Testing Mode)."
    except Exception:
        pass

    # If live SMTP password is configured, send through SMTP protocol
    if is_smtp_configured():
        try:
            msg = MIMEMultipart("alternative")
            msg["Subject"] = subject
            msg["From"] = f"{SENDER_NAME} <{SMTP_USER}>"
            msg["To"] = to_email
            msg.attach(MIMEText(text_body, "plain"))
            msg.attach(MIMEText(html_body, "html"))

            with smtplib.SMTP(SMTP_HOST, SMTP_PORT, timeout=12) as server:
                server.ehlo()
                server.starttls()
                server.ehlo()
                server.login(SMTP_USER, SMTP_PASSWORD.strip())
                server.sendmail(SMTP_USER, [to_email], msg.as_string())

            logger.info("Successfully sent %s OTP email to %s via SMTP.", purpose, to_email)
            return True, f"Verification OTP sent to {to_email}."
        except Exception as exc:
            logger.error("SMTP delivery failed to %s: %s", to_email, exc)
            return False, f"Failed to deliver email: {str(exc)}"

    # If SMTP is not configured, fail closed without leaking OTP
    logger.warning("SMTP credentials are not configured. Cannot dispatch live email to %s.", to_email)
    return False, "SMTP email service is not configured. Please set SMTP_PASSWORD in environment variables."
