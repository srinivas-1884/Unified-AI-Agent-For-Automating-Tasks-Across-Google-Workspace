# ai_email_agent.py

import re
import base64
import json
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email.mime.text import MIMEText
from email import encoders


# -------------------------------
# EMAIL UTILITIES
# -------------------------------

def parse_recipients(text: str, friend_model, user_id):
    """Extract emails or resolve names using DB."""

    words = re.findall(r'[\w\.-]+@[\w\.-]+\.\w+|\w+', text.lower())

    recipients = []
    seen = set()

    for w in words:
        # Case 1: Direct email
        if "@" in w:
            email = w

        # Case 2: Name → DB lookup
        else:
            email = friend_model.resolve_name_to_email(user_id, w)

        if email and email not in seen:
            seen.add(email)
            recipients.append(email)

    return recipients

def get_sender_profile(gmail_service):
    try:
        profile = gmail_service.users().getProfile(userId="me").execute()
        email = profile.get("emailAddress")

        # Better name formatting
        name = email.split("@")[0]
        name = name.replace(".", " ").replace("_", " ").title()

        return name, email
    except:
        return "User", None
        
def _make_attachment_part(filename: str, file_data: bytes):
    part = MIMEBase("application", "octet-stream")
    part.set_payload(file_data)
    encoders.encode_base64(part)
    part.add_header("Content-Disposition", f'attachment; filename="{filename}"')
    return part


def send_email_with_attachments(gmail_service, recipients, subject, body_text, attachments=None):
    if not recipients:
        raise ValueError("No recipients provided.")

    message = MIMEMultipart()
    message["to"] = ", ".join(recipients)
    message["subject"] = subject

    message.attach(MIMEText(body_text, "plain"))

    if attachments:
        for filename, filedata in attachments:
            message.attach(_make_attachment_part(filename, filedata))

    raw = base64.urlsafe_b64encode(message.as_bytes()).decode()
    gmail_service.users().messages().send(userId="me", body={"raw": raw}).execute()


# -------------------------------
# AI EMAIL GENERATION
# -------------------------------

def generate_email_draft(co_client, context: str):
    if not context or len(context.strip()) < 5:
        return None, "Provide more details."

    prompt = f"""
You are an email generator.

STRICT RULES:
- Output ONLY JSON
- No markdown, no explanation
- Format: {{"subject":"...","body":"..."}}

TASK:
{context}
"""

    try:
        resp = co_client.chat(
            model="command-r-plus-08-2024",
            message=prompt,
            temperature=0.3,
            max_tokens=400
        )

        text = (resp.text or "").strip()

        # Remove markdown
        text = re.sub(r"^```.*?\n|```$", "", text, flags=re.DOTALL).strip()

        try:
            data = json.loads(text)
            return data.get("subject", ""), data.get("body", "")
        except:
            # Strong fallback
            subject_match = re.search(r'subject[:\-]\s*(.*)', text, re.I)
            body_match = re.search(r'body[:\-]\s*(.*)', text, re.I | re.S)

            subject = subject_match.group(1).strip() if subject_match else "Generated Email"
            body = body_match.group(1).strip() if body_match else text

            return subject, body

    except Exception as e:
        return None, f"Error: {e}"


def refine_email_draft(co_client, instruction, subject, body):
    prompt = f"""
Refine this email.

Return ONLY JSON:
{{"subject":"...","body":"..."}}

Current Subject: {subject}
Current Body: {body[:300]}

Change:
{instruction}
"""

    try:
        resp = co_client.chat(
            model="command-r-plus-08-2024",
            message=prompt,
            temperature=0.2,
            max_tokens=400
        )

        text = re.sub(r"^```.*?\n|```$", "", resp.text.strip(), flags=re.DOTALL)

        data = json.loads(text)
        return data.get("subject", subject), data.get("body", body)

    except:
        return subject, body + "\n\n[Refinement failed]"


# -------------------------------
# CLI INTERFACE (SMART FLOW)
# -------------------------------

def run_agent(co_client, gmail_service=None):
    print("\n📧 AI Email Agent\n")

    context = input("Describe your email: ").strip()
    subject, body = generate_email_draft(co_client, context)

    if not subject:
        print(body)
        return

    print("\n--- GENERATED EMAIL ---")
    print("Subject:", subject)
    print("Body:\n", body)

    while True:
        action = input("\nOptions: [refine / send / exit]: ").lower()

        if action == "refine":
            instruction = input("What changes? ")
            subject, body = refine_email_draft(co_client, instruction, subject, body)

            print("\n--- UPDATED EMAIL ---")
            print("Subject:", subject)
            print("Body:\n", body)

        elif action == "send":
            if not gmail_service:
                print("⚠️ Gmail service not configured.")
                continue

            recipients_input = input("Enter recipient emails: ")
            recipients = parse_recipients(recipients_input)

            send_email_with_attachments(
                gmail_service,
                recipients,
                subject,
                body
            )

            print("✅ Email sent successfully!")
            break

        elif action == "exit":
            break

        else:
            print("Invalid option.")