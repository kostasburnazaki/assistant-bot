import difflib
import shlex


def parse_input(user_input: str):
    try:
        parts = shlex.split(user_input.strip())
    except ValueError as error:
        raise ValueError("Invalid command format. Check quotes in your input.") from error

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
