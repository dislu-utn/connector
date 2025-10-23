from typing import TypedDict

class DisluCreateInstitutionPayload(TypedDict):
    name: str
    domain: str

# Dictionary interface using TypedDict
class AdaptariaCreateInstitutionPayload(TypedDict):
    name: str
    address: str
    phone: str
