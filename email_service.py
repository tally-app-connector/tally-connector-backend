# import smtplib
# from email.mime.text import MIMEText
# from email.mime.multipart import MIMEMultipart
# from email.mime.base import MIMEBase
# from email import encoders
# import os
# from dotenv import load_dotenv

# load_dotenv()

# class EmailService:
#     def __init__(self):
#         self.smtp_host = os.getenv("SMTP_HOST", "smtp.gmail.com")
#         self.smtp_port = int(os.getenv("SMTP_PORT", "587"))
#         self.smtp_user = os.getenv("SMTP_USER")
#         self.smtp_password = os.getenv("SMTP_PASSWORD")
#         self.smtp_from = os.getenv("SMTP_FROM")
#         self.smtp_from_name = os.getenv("SMTP_FROM_NAME", "Tally Connector")
#         self.app_url = os.getenv("APP_URL", "http://localhost:8000")
#         self.frontend_url = os.getenv("FRONTEND_URL", "http://localhost:3000")

#     def send_email(self, to_email: str, subject: str, html_content: str):
#         """Send email using SMTP"""
#         try:
#             # Create message
#             message = MIMEMultipart("alternative")
#             message["Subject"] = subject
#             message["From"] = f"{self.smtp_from_name} <{self.smtp_from}>"
#             message["To"] = to_email

#             # Add HTML content
#             html_part = MIMEText(html_content, "html")
#             message.attach(html_part)

#             # Send email
#             with smtplib.SMTP(self.smtp_host, self.smtp_port) as server:
#                 server.starttls()
#                 server.login(self.smtp_user, self.smtp_password)
#                 server.send_message(message)

#             print(f"✅ Email sent successfully to {to_email}")
#             return True

#         except Exception as e:
#             print(f"❌ Email sending failed: {str(e)}")
#             return False

#     def send_verification_email(self, to_email: str, verification_token: str, user_name: str):
#         """Send email verification link"""
#         verification_link = f"{self.app_url}/api/auth/verify-email?token={verification_token}"
        
#         html_content = f"""
#         <!DOCTYPE html>
#         <html>
#         <head>
#             <style>
#                 body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
#                 .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
#                 .header {{ background-color: #4CAF50; color: white; padding: 20px; text-align: center; }}
#                 .content {{ padding: 20px; background-color: #f9f9f9; }}
#                 .button {{ 
#                     display: inline-block; 
#                     padding: 12px 30px; 
#                     background-color: #4CAF50; 
#                     color: white; 
#                     text-decoration: none; 
#                     border-radius: 5px;
#                     margin: 20px 0;
#                 }}
#                 .footer {{ padding: 20px; text-align: center; font-size: 12px; color: #666; }}
#             </style>
#         </head>
#         <body>
#             <div class="container">
#                 <div class="header">
#                     <h1>Welcome to Tally Connector!</h1>
#                 </div>
#                 <div class="content">
#                     <p>Hi {user_name},</p>
#                     <p>Thank you for signing up! Please verify your email address by clicking the button below:</p>
#                     <center>
#                         <a href="{verification_link}" class="button">Verify Email</a>
#                     </center>
#                     <p>Or copy and paste this link in your browser:</p>
#                     <p style="word-break: break-all; color: #666;">{verification_link}</p>
#                     <p>This link will expire in 24 hours.</p>
#                     <p>If you didn't create this account, please ignore this email.</p>
#                 </div>
#                 <div class="footer">
#                     <p>&copy; 2024 Tally Connector. All rights reserved.</p>
#                 </div>
#             </div>
#         </body>
#         </html>
#         """
        
#         return self.send_email(to_email, "Verify Your Email - Tally Connector", html_content)

#     def send_otp_email(self, to_email: str, otp: str, user_name: str):
#         """Send OTP for verification"""
#         html_content = f"""
#         <!DOCTYPE html>
#         <html>
#         <head>
#             <style>
#                 body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
#                 .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
#                 .header {{ background-color: #2196F3; color: white; padding: 20px; text-align: center; }}
#                 .content {{ padding: 20px; background-color: #f9f9f9; }}
#                 .otp-code {{ 
#                     font-size: 32px; 
#                     font-weight: bold; 
#                     color: #2196F3; 
#                     text-align: center;
#                     padding: 20px;
#                     background-color: #e3f2fd;
#                     border-radius: 8px;
#                     letter-spacing: 5px;
#                     margin: 20px 0;
#                 }}
#                 .footer {{ padding: 20px; text-align: center; font-size: 12px; color: #666; }}
#             </style>
#         </head>
#         <body>
#             <div class="container">
#                 <div class="header">
#                     <h1>Your Verification Code</h1>
#                 </div>
#                 <div class="content">
#                     <p>Hi {user_name},</p>
#                     <p>Your verification code is:</p>
#                     <div class="otp-code">{otp}</div>
#                     <p>This code will expire in 10 minutes.</p>
#                     <p>If you didn't request this code, please ignore this email.</p>
#                 </div>
#                 <div class="footer">
#                     <p>&copy; 2024 Tally Connector. All rights reserved.</p>
#                 </div>
#             </div>
#         </body>
#         </html>
#         """
        
#         return self.send_email(to_email, f"Your Verification Code: {otp}", html_content)

#     def send_password_reset_email(self, to_email: str, reset_token: str, user_name: str):
#         """Send password reset link"""
#         reset_link = f"{self.frontend_url}/reset-password?token={reset_token}"
        
#         html_content = f"""
#         <!DOCTYPE html>
#         <html>
#         <head>
#             <style>
#                 body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
#                 .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
#                 .header {{ background-color: #FF5722; color: white; padding: 20px; text-align: center; }}
#                 .content {{ padding: 20px; background-color: #f9f9f9; }}
#                 .button {{ 
#                     display: inline-block; 
#                     padding: 12px 30px; 
#                     background-color: #FF5722; 
#                     color: white; 
#                     text-decoration: none; 
#                     border-radius: 5px;
#                     margin: 20px 0;
#                 }}
#                 .footer {{ padding: 20px; text-align: center; font-size: 12px; color: #666; }}
#             </style>
#         </head>
#         <body>
#             <div class="container">
#                 <div class="header">
#                     <h1>Reset Your Password</h1>
#                 </div>
#                 <div class="content">
#                     <p>Hi {user_name},</p>
#                     <p>We received a request to reset your password. Click the button below to create a new password:</p>
#                     <center>
#                         <a href="{reset_link}" class="button">Reset Password</a>
#                     </center>
#                     <p>Or copy and paste this link in your browser:</p>
#                     <p style="word-break: break-all; color: #666;">{reset_link}</p>
#                     <p>This link will expire in 1 hour.</p>
#                     <p>If you didn't request this, please ignore this email and your password will remain unchanged.</p>
#                 </div>
#                 <div class="footer">
#                     <p>&copy; 2024 Tally Connector. All rights reserved.</p>
#                 </div>
#             </div>
#         </body>
#         </html>
#         """
        
#         return self.send_email(to_email, "Reset Your Password - Tally Connector", html_content)

# # Create global instance
# email_service = EmailService()


import resend
import os
from dotenv import load_dotenv

load_dotenv()

class EmailService:
    def __init__(self):
        resend.api_key = os.getenv("RESEND_API_KEY")
        self.smtp_from = os.getenv("SMTP_FROM", "onboarding@resend.dev")
        self.app_url = os.getenv("APP_URL", "http://localhost:8000")
        self.frontend_url = os.getenv("FRONTEND_URL", "http://localhost:3000")

    def send_email(self, to_email: str, subject: str, html_content: str):
        """Send email using Resend"""
        try:
            params = {
                "from": self.smtp_from,
                "to": [to_email],
                "subject": subject,
                "html": html_content,
            }
            
            email = resend.Emails.send(params)
            print(f"✅ Email sent successfully to {to_email}")
            print(f"Email ID: {email}")
            return True

        except Exception as e:
            print(f"❌ Email sending failed: {str(e)}")
            import traceback
            traceback.print_exc()
            return False

    def send_verification_email(self, to_email: str, verification_token: str, user_name: str):
        """Send email verification link"""
        verification_link = f"{self.app_url}/api/auth/verify-email?token={verification_token}"
        
        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <style>
                body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
                .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
                .header {{ background-color: #4CAF50; color: white; padding: 20px; text-align: center; border-radius: 10px 10px 0 0; }}
                .content {{ padding: 30px; background-color: #f9f9f9; }}
                .button {{ 
                    display: inline-block; 
                    padding: 15px 30px; 
                    background-color: #4CAF50; 
                    color: white !important; 
                    text-decoration: none; 
                    border-radius: 5px;
                    margin: 20px 0;
                    font-weight: bold;
                }}
                .footer {{ padding: 20px; text-align: center; font-size: 12px; color: #666; background-color: #f0f0f0; border-radius: 0 0 10px 10px; }}
                .code-box {{ background: #e8f5e9; padding: 15px; border-radius: 5px; margin: 15px 0; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>Welcome to Tally Connector!</h1>
                </div>
                <div class="content">
                    <p>Hi <strong>{user_name}</strong>,</p>
                    <p>Thank you for signing up with Tally Connector! Please verify your email address to get started.</p>
                    <center>
                        <a href="{verification_link}" class="button">Verify Email Address</a>
                    </center>
                    <p>Or copy and paste this link in your browser:</p>
                    <div class="code-box">
                        <code style="word-break: break-all; color: #2e7d32;">{verification_link}</code>
                    </div>
                    <p style="margin-top: 20px;">This link will expire in 24 hours.</p>
                    <p style="color: #666; font-size: 14px;">If you didn't create this account, please ignore this email.</p>
                </div>
                <div class="footer">
                    <p>&copy; 2025 Tally Connector. All rights reserved.</p>
                </div>
            </div>
        </body>
        </html>
        """
        
        return self.send_email(to_email, "Verify Your Email - Tally Connector", html_content)

    def send_otp_email(self, to_email: str, otp: str, user_name: str):
        """Send OTP for verification"""
        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <style>
                body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
                .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
                .header {{ background-color: #2196F3; color: white; padding: 20px; text-align: center; border-radius: 10px 10px 0 0; }}
                .content {{ padding: 30px; background-color: #f9f9f9; }}
                .otp-code {{ 
                    font-size: 36px; 
                    font-weight: bold; 
                    color: #2196F3; 
                    text-align: center;
                    padding: 25px;
                    background-color: #e3f2fd;
                    border-radius: 10px;
                    letter-spacing: 8px;
                    margin: 25px 0;
                    border: 2px solid #2196F3;
                }}
                .footer {{ padding: 20px; text-align: center; font-size: 12px; color: #666; background-color: #f0f0f0; border-radius: 0 0 10px 10px; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>Your Verification Code</h1>
                </div>
                <div class="content">
                    <p>Hi <strong>{user_name}</strong>,</p>
                    <p>Your verification code for Tally Connector is:</p>
                    <div class="otp-code">{otp}</div>
                    <p style="text-align: center; color: #666; margin-top: 20px;">Enter this code in the app to verify your email</p>
                    <p style="color: #f44336; text-align: center; margin-top: 15px;"><strong>This code will expire in 10 minutes.</strong></p>
                    <p style="color: #666; font-size: 14px; margin-top: 20px;">If you didn't request this code, please ignore this email.</p>
                </div>
                <div class="footer">
                    <p>&copy; 2025 Tally Connector. All rights reserved.</p>
                </div>
            </div>
        </body>
        </html>
        """
        
        return self.send_email(to_email, f"Your Verification Code: {otp}", html_content)

    def send_password_reset_email(self, to_email: str, reset_token: str, user_name: str):
        """Send password reset link"""
        reset_link = f"{self.frontend_url}/reset-password?token={reset_token}"
        
        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <style>
                body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
                .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
                .header {{ background-color: #FF5722; color: white; padding: 20px; text-align: center; border-radius: 10px 10px 0 0; }}
                .content {{ padding: 30px; background-color: #f9f9f9; }}
                .button {{ 
                    display: inline-block; 
                    padding: 15px 30px; 
                    background-color: #FF5722; 
                    color: white !important; 
                    text-decoration: none; 
                    border-radius: 5px;
                    margin: 20px 0;
                    font-weight: bold;
                }}
                .footer {{ padding: 20px; text-align: center; font-size: 12px; color: #666; background-color: #f0f0f0; border-radius: 0 0 10px 10px; }}
                .code-box {{ background: #ffebee; padding: 15px; border-radius: 5px; margin: 15px 0; border-left: 4px solid #FF5722; }}
                .warning {{ background: #fff3cd; padding: 15px; border-radius: 5px; border-left: 4px solid #ffc107; margin: 15px 0; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>🔐 Reset Your Password</h1>
                </div>
                <div class="content">
                    <p>Hi <strong>{user_name}</strong>,</p>
                    <p>We received a request to reset your password for your Tally Connector account.</p>
                    <p>Click the button below to create a new password:</p>
                    <center>
                        <a href="{reset_link}" class="button">Reset Password</a>
                    </center>
                    <p>Or copy and paste this link in your browser:</p>
                    <div class="code-box">
                        <code style="word-break: break-all; color: #d32f2f;">{reset_link}</code>
                    </div>
                    <div class="warning">
                        <strong>⏰ This link will expire in 1 hour.</strong>
                    </div>
                    <p style="color: #666; font-size: 14px; margin-top: 20px;">If you didn't request a password reset, please ignore this email and your password will remain unchanged.</p>
                    <p style="color: #666; font-size: 14px;">For security reasons, never share this link with anyone.</p>
                </div>
                <div class="footer">
                    <p>&copy; 2025 Tally Connector. All rights reserved.</p>
                    <p style="margin-top: 5px;">Questions? Contact us at support@tallyconnector.com</p>
                </div>
            </div>
        </body>
        </html>
        """
        
        return self.send_email(to_email, "Reset Your Password - Tally Connector", html_content)

# Create global instance
email_service = EmailService()