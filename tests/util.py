from ev3dev2.button import Button, MissingButton


def get_user_answer(question):
    question += " (Y/N)"
    while True:
        result = input(question).rstrip()
        if result == "Y":
            return True
        elif result == "N":
            return False

        print("Could not read input. Try again.")


def is_running_on_ev3():
    try:
        Button().enter()
    except MissingButton:
        return False
    return True
