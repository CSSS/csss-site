def validate_phone_number(phone_number):
    if (f"{phone_number}".isdigit() and len(phone_number == 9)) or int(phone_number) == 0:
        return True, None
    return False, "Invalid phone number specified, please specify all 9 digits [area code and 7 digit number]"
