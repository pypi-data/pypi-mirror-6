import subprocess

try:
    subprocess.call(["xdg-email", "--version"],
                    stdout=subprocess.DEVNULL)
except (OSError, FileNotFoundException):
    raise RuntimeError("Couldn't find xdg-email, needed for feedback module")

DESTINATION = "ramon100.black@gmail.com"
SUBJECT = "Bat-man feedback"
    
def open_email_sender_for_feedback():
    subprocess.call(["xdg-email", "--subject", SUBJECT, DESTINATION])

