# utils/supi_generator.py
import random

def generate_random_supi(mcc='999', mnc='70'):
    """
    Generate a random SUPI (IMSI-based) in the format 'imsi-MCCMNCMSIN'
    - MCC: Mobile Country Code (3 digits)
    - MNC: Mobile Network Code (2 or 3 digits)
    - MSIN: Mobile Subscriber Identification Number (9 to 10 digits)
    """
    # Ensure MNC is padded to 3 digits
    mnc = mnc.zfill(3)

    # Generate a random MSIN (10 digits)
    msin = ''.join(random.choices('0123456789', k=10))

    # Combine to form IMSI
    imsi = f'imsi-{mcc}{mnc}{msin}'
    return imsi