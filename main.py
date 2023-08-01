import json
import data_processing_weekly
import email_sender

def main():
    # Load configuration
    with open("config.json", "r") as config_file:
        config = json.load(config_file)

    # Process data and generate summary report
    summary_report = data_processing_weekly.generate_summary_report(config["data_directory"])

    # Send summary report via email
    email_sender.send_email(
        recipient=config["email_recipient"],
        subject=config["email_subject"],
        body=summary_report,
        smtp_server=config["smtp_server"],
        smtp_port=config["smtp_port"],
        smtp_username=config["smtp_username"],
        smtp_password=config["smtp_password"]
    )

if __name__ == "__main__":
    main()