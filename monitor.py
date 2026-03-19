import subprocess
import platform
import csv
import os
from dotenv import load_dotenv
from datetime import datetime
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.application import MIMEApplication

def check_ping(ip_address):
    param = '-n' if platform.system().lower() == 'windows' else '-c'
    command = ['ping', param, '1', ip_address]
    response = subprocess.call(command, stdout=subprocess.DEVNULL, stderr=subprocess.STDOUT)
    return response == 0

def generate_html_dashboard(results):
    html_file = "status_dashboard.html"
    html_content = """
    <html><head><title>IT Operations Status Board</title>
    <style>
        body { font-family: Arial, sans-serif; background-color: #f4f4f9; padding: 20px; }
        table { width: 100%; border-collapse: collapse; margin-top: 20px; }
        th, td { padding: 12px; text-align: left; border-bottom: 1px solid #ddd; font-weight: bold; }
        th { background-color: #333; color: white; }
        .up { background-color: #d4edda; color: #155724; }
        .down { background-color: #f8d7da; color: #721c24; }
    </style></head><body>
    <h1>Live Infrastructure Status</h1>
    <table><tr><th>Device Name</th><th>IP Address</th><th>Status</th></tr>
    """
    for row in results:
        row_class = "up" if row['status'] == "UP" else "down"
        html_content += f'<tr class="{row_class}"><td>{row["name"]}</td><td>{row["ip"]}</td><td>{row["status"]}</td></tr>'
    html_content += "</table></body></html>"
    
    with open(html_file, "w") as file:
        file.write(html_content)

load_dotenv()

# NEW: Enterprise Email Function
def send_email_alert(down_devices, log_file_path):
    print("\n📧 Preparing to send batch email alert...")
    
    # --- YOUR EMAIL CONFIGURATION GOES HERE ---
    sender_email = os.getenv("EMAIL_USER")       
    sender_password = os.getenv("EMAIL_PASS")       
    receiver_email = os.getenv("RECEIVER_EMAIL")     

    if not sender_email or not sender_password:
        print("❌ Error: Missing email credentials. Check your .env file!")
        return
    
    # Build the email
    msg = MIMEMultipart()
    msg['From'] = sender_email
    msg['To'] = receiver_email
    msg['Subject'] = f"🚨 URGENT: {len(down_devices)} Network Devices DOWN"
    
    # Create the body text
    body = "The following critical infrastructure devices are currently DOWN:\n\n"
    for device in down_devices:
        body += f"- {device['name']} ({device['ip']})\n"
    body += "\nPlease check the attached CSV log for a complete history."
    msg.attach(MIMEText(body, 'plain'))
    
    # Attach the CSV file
    try:
        with open(log_file_path, "rb") as attachment:
            part = MIMEApplication(attachment.read(), Name=os.path.basename(log_file_path))
            part['Content-Disposition'] = f'attachment; filename="{os.path.basename(log_file_path)}"'
            msg.attach(part)
    except Exception as e:
        print(f"Could not attach file: {e}")

    # Connect to Gmail and send
    try:
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login(sender_email, sender_password)
        server.send_message(msg)
        server.quit()
        print("✅ Alert email sent successfully with CSV attached!")
    except Exception as e:
        print(f"❌ Failed to send email: {e}")

# --- MAIN EXECUTION ---

targets = {
    "Gateway Router": "192.168.1.1",
    "Main ERP Node": "10.0.0.5",                 
    "Hardware Tool Controller": "127.0.0.1",
    "Failing System (Test)": "192.0.2.1" 
}

log_file = "network_health_log.csv"
file_exists = os.path.isfile(log_file)
current_scan_results = []
down_systems = [] # NEW: We will collect failed systems here

print("--- Running Scan, Updating Logs, and Generating Dashboard ---")

with open(log_file, mode='a', newline='') as file:
    writer = csv.writer(file)
    if not file_exists:
        writer.writerow(["Timestamp", "Device Name", "IP Address", "Status"])

    for name, ip in targets.items():
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        is_up = check_ping(ip)
        status = "UP" if is_up else "DOWN"
        
        # Save data for dashboard and email
        device_data = {"name": name, "ip": ip, "status": status}
        current_scan_results.append(device_data)
        
        if not is_up:
            down_systems.append(device_data) # Add to our failure list
        
        print(f"[{now}] [{status}] {name} ({ip})")
        writer.writerow([now, name, ip, status])

generate_html_dashboard(current_scan_results)

# NEW: If any systems went down, send the email after the CSV is safely closed
if len(down_systems) > 0:
    send_email_alert(down_systems, log_file)

print("--- Scan Complete. ---")