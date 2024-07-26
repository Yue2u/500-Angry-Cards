import random
import string


def generate_room_code():
    return "".join(random.choices(string.ascii_uppercase, k=6))


def generate_nickname():
    fp = [
        "Furious",
        "Happy",
        "Cool",
        "Funny",
        "Pretty",
        "Estetic",
        "Active",
        "Curious",
        "Kind",
        "Patient",
        "Crazy",
        "Courageous",
        "Bold",
        "Brave",
        "Reliable",
    ]
    sp = [
        "Cat",
        "Tiger",
        "Capybara",
        "Mammoth",
        "Elephant",
        "Lion",
        "Chinchilla",
        "Flamingo",
        "Pelican",
        "Collibri",
        "Wombat",
        "Crocodile",
    ]
    return random.choice(fp) + random.choice(sp) + str(random.randint(1000, 9999))
