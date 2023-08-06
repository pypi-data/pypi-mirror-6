
possible_args = [
    ("discordian", ["-d", "--discord", "--discordian", "--discordianism"]),
    ("eve_game", ["-e", "--eve", "--eve-game"]),
    ("eve_real", ["-r", "--eve-real", "--eve-is-real"]),
    ("help", ["-h", "--help"]),
]



print("Dateandtime usage:\n  dateandtime [calendar] [-h/--help]\n"
      "Alternate calendars (usage flags):\n  {0}".format(
        "\n  ".join(
            "{0}{1}{2}{3}: [{4}]".format(
                name.split("_")[0],
                " (" * int("_" in name),
                " ".join(name.split("_")[1:]),
                ")" * int("_" in name),
                ", ".join(flags),
            )
            for name, flags in possible_args[:-1]
    ))
)

