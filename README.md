# Network Health Monitor

A lightweight Python script that monitors the status of critical network infrastructure by pinging devices, logging their availability, and sending email alerts when systems go down.

## Features

- **Real-time Monitoring**: Pings a list of target IP addresses to check availability.
- **CSV Logging**: Maintains a historical log of all scans in `network_health_log.csv`.
- **HTML Dashboard**: Generates a visually appealing `status_dashboard.html` for a quick status overview.
- **Email Alerts**: Automatically sends an email alert with the CSV log attached if any device is detected as "DOWN".
- **Environment Variable Support**: Securely manages email credentials using a `.env` file.

## Prerequisites

- [Python 3.x](https://www.python.org/downloads/) installed.
- `python-dotenv` library installed.

## Setup

1. **Install Dependencies**:
   ```powershell
   pip install python-dotenv
   ```

2. **Configure Environment Variables**:
   Create a file named `.env` in the root directory (based on `.env.example` if available) and add your email credentials:
   ```env
   EMAIL_USER=your_email@gmail.com
   EMAIL_PASS=your_16_letter_app_password
   RECEIVER_EMAIL=where_to_send_alerts@gmail.com
   ```
   > [!IMPORTANT]
   > For Gmail users, you must use an [App Password](https://myaccount.google.com/apppasswords) instead of your regular account password.

3. **Configure Targets**:
   Open `monitor.py` and modify the `targets` dictionary with the device names and IP addresses you want to monitor.

## Usage

Run the script using the following command:

```powershell
python monitor.py
```

## Output Files

- `network_health_log.csv`: Historical data of every scan performed.
- `status_dashboard.html`: A live status board that can be opened in any web browser.

## Security

The `.env` file and `network_health_log.csv` are included in the `.gitignore` to prevent sensitive data from being committed to version control.
