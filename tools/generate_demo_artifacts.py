import os

def create_artifact(filename, content):
    path = os.path.join(os.path.dirname(__file__), filename)
    with open(path, "wb") as f:
        # A minimal dummy PDF structure so it gets identified as PDF if needed,
        # but with custom content so hashes differ.
        pdf_content = f"%PDF-1.4\n% {content}\n%%EOF\n"
        f.write(pdf_content.encode("utf-8"))
    print(f"Created: {path}")

if __name__ == "__main__":
    create_artifact("QSHIELD_Demo_Firmware_Legitimate.pdf", "FIRMWARE_VERSION: 2.4\nAUTHORIZATION: ACME-INDUSTRIAL-ROOT\nSTATUS: APPROVED")
    create_artifact("QSHIELD_Demo_Firmware_Modified_Forgery.pdf", "FIRMWARE_VERSION: 2.4\nAUTHORIZATION: ACME-INDUSTRIAL-ROOT\nSTATUS: APPROVED\nMALICIOUS_PAYLOAD: TRUE")
    create_artifact("QSHIELD_Demo_High_Value_Transfer.pdf", "TRANSACTION_ID: 994821\nAMOUNT: $500,000,000\nAUTHORIZATION: ROOT-QUORUM")
    print("All demo artifacts generated successfully.")
