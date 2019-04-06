import ev3dev2.button


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
        ev3dev2.button.Button().enter
    except ev3dev2.button.MissingButton:
        return False
    return True
