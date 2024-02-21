import random
import string


def generate_number_string() -> str:
    number = random.randint(1, 21)
    return str(number)


def random_number() -> int:
    return random.randint(0, 99999999)


def random_string(length: int = 10) -> str:
    return "".join(random.choices(string.ascii_letters + string.digits, k=length))


def generate_taxonomy_import_data() -> dict:
    return {
        "namespace": "CERT-XLM",
        "description": "CERT-XLM Security Incident Classification.",
        "version": 2,
        "exclusive": "false",
        "predicates": [
            {"value": "abusive-content", "expanded": "Abusive Content", "description": "Abusive Content."},
        ],
        "values": [
            {
                "predicate": "abusive-content",
                "entry": [
                    {
                        "value": "spam",
                        "expanded": "spam",
                        "description": (
                            "Spam or ‘unsolicited bulk e-mail’, meaning that the recipient has not "
                            "granted verifiable permission for the message to be sent and that the "
                            "message is sent as part of a larger collection of messages, all having"
                            " identical content."
                        ),
                    },
                    {
                        "value": "harmful-speech",
                        "expanded": "Harmful Speech",
                        "description": (
                            "Discretization or discrimination of somebody (e.g. cyber stalking, racism "
                            "and threats against one or more individuals) May be found on a forum, email, "
                            "tweet etc…"
                        ),
                    },
                    {
                        "value": "violence",
                        "expanded": "Child/Sexual/Violence/...",
                        "description": (
                            "Any Child pornography, glorification of violence, may be found on a website, "
                            "forum, email, tweet etc…"
                        ),
                    },
                ],
            }
        ],
    }
