from cryptography.fernet import Fernet

en = Fernet("VlD8h2tEiJkQpKKnDNKnu8ya2fpIBMOo5oc7JKNasvk=")

encrypt = en.encrypt("VirajLakshitha".encode())
print(encrypt.decode())

decrypt = en.decrypt(encrypt)
print(decrypt.decode())