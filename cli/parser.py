import difflib


def parse_input(user_input: str):
    parts = user_input.strip().split()
    if not parts:
        return "", []
    cmd = parts[0].lower()
    args = parts[1:]
    return cmd, args


def suggest_command(command: str, commands: list[str]):

    matches = difflib.get_close_matches(
        command,
        commands,
        n=1,
        cutoff=0.5
    )

    return matches[0] if matches else None
