# ============================================================
# PANINIAN PRATYAHARA ENGINE
# Based on the 14 Shiva Sutras
# ============================================================


# ============================================================
# 1. SHIVA SUTRAS
# ============================================================
#
# Each sutra is represented as:
#
#     (sound, is_anubandha)
#
# True  = anubandha / it marker
# False = actual phoneme
#
# IMPORTANT:
# The anubandha is NOT included in the final pratyahara.
# ============================================================

SHIVA_SUTRAS = [
    [
        ("अ", False),
        ("इ", False),
        ("उ", False),
        ("ण्", True)
    ],

    [
        ("ऋ", False),
        ("ऌ", False),
        ("क्", True)
    ],

    [
        ("ए", False),
        ("ओ", False),
        ("ङ्", True)
    ],

    [
        ("ऐ", False),
        ("औ", False),
        ("च्", True)
    ],

    [
        ("ह्", False),
        ("य्", False),
        ("व्", False),
        ("र्", False),
        ("ट्", True)
    ],

    [
        ("ल्", False),
        ("ण्", True)
    ],

    [
        ("ञ्", False),
        ("म्", False),
        ("ङ्", False),
        ("ण्", False),
        ("न्", False),
        ("म्", True)
    ],

    [
        ("झ्", False),
        ("भ्", False),
        ("ञ्", True)
    ],

    [
        ("घ्", False),
        ("ढ्", False),
        ("ध्", False),
        ("ष्", True)
    ],

    [
        ("ज्", False),
        ("ब्", False),
        ("ग्", False),
        ("ड्", False),
        ("द्", False),
        ("श्", True)
    ],

    [
        ("ख्", False),
        ("फ्", False),
        ("छ्", False),
        ("ठ्", False),
        ("थ्", False),
        ("च्", True)
    ],

    [
        ("क्", False),
        ("प्", False),
        ("य्", True)
    ],

    [
        ("श्", False),
        ("ष्", False),
        ("स्", False),
        ("र्", True)
    ],

    [
        ("ह्", False),
        ("ल्", True)
    ]
]


# ============================================================
# 2. BUILD ONE LINEAR SHIVA-SUTRA SEQUENCE
# ============================================================

SEQUENCE = []

for sutra_number, sutra in enumerate(SHIVA_SUTRAS, start=1):

    for position, (symbol, is_anubandha) in enumerate(sutra):

        SEQUENCE.append({
            "symbol": symbol,
            "is_anubandha": is_anubandha,
            "sutra": sutra_number,
            "position": position
        })


# ============================================================
# 3. PRATYAHARA ENGINE
# ============================================================

class PratyaharaEngine:

    def __init__(self, sequence):

        self.sequence = sequence

        # ----------------------------------------------------
        # Actual phonemes
        # ----------------------------------------------------

        self.sounds = [
            item["symbol"]
            for item in sequence
            if not item["is_anubandha"]
        ]

        # ----------------------------------------------------
        # All anubandhas
        # ----------------------------------------------------

        self.anubandhas = [
            item["symbol"]
            for item in sequence
            if item["is_anubandha"]
        ]


    # ========================================================
    # FIND A STARTING PHONEME
    # ========================================================

    def find_start(self, start):

        for index, item in enumerate(self.sequence):

            if (
                item["symbol"] == start
                and not item["is_anubandha"]
            ):
                return index

        raise ValueError(
            f"Starting sound '{start}' is not present "
            f"in the Shiva Sutras."
        )


    # ========================================================
    # FIND THE FIRST VALID ANUBANDHA AFTER START
    # ========================================================

    def find_end(self, start_index, ending_marker):

        for index in range(
            start_index + 1,
            len(self.sequence)
        ):

            item = self.sequence[index]

            if (
                item["symbol"] == ending_marker
                and item["is_anubandha"]
            ):
                return index

        raise ValueError(
            f"Anubandha '{ending_marker}' "
            f"does not occur after the starting sound."
        )


    # ========================================================
    # CALCULATE A PRATYAHARA
    #
    # Examples:
    #
    #     get_pratyahara("अण्")
    #     get_pratyahara("इक्")
    #     get_pratyahara("ऋष्")
    #     get_pratyahara("ऋश्")
    #
    # OR:
    #
    #     get_pratyahara("ऋ", "ष्")
    # ========================================================

    def get_pratyahara(
        self,
        notation,
        ending_marker=None
    ):

        # ----------------------------------------------------
        # CASE 1:
        #
        # get_pratyahara("ऋ", "ष्")
        # ----------------------------------------------------

        if ending_marker is not None:

            start = notation

        # ----------------------------------------------------
        # CASE 2:
        #
        # get_pratyahara("ऋष्")
        # ----------------------------------------------------

        else:

            start = None
            ending_marker = None

            # ------------------------------------------------
            # Try every possible actual sound as the start.
            #
            # Longest sounds are tried first.
            # This makes Unicode parsing safer.
            # ------------------------------------------------

            possible_starts = sorted(
                self.sounds,
                key=len,
                reverse=True
            )

            for candidate in possible_starts:

                if notation.startswith(candidate):

                    remaining = notation[len(candidate):]

                    # ----------------------------------------
                    # The remaining part must be an anubandha
                    # ----------------------------------------

                    if remaining in self.anubandhas:

                        start = candidate
                        ending_marker = remaining
                        break

            if start is None:

                raise ValueError(
                    f"Could not parse '{notation}'.\n"
                    f"Expected something like 'अण्', "
                    f"'इक्', 'ऋष्', 'हल्', etc."
                )

        # ----------------------------------------------------
        # Find starting position
        # ----------------------------------------------------

        start_index = self.find_start(start)

        # ----------------------------------------------------
        # Find ending anubandha
        # ----------------------------------------------------

        end_index = self.find_end(
            start_index,
            ending_marker
        )

        # ----------------------------------------------------
        # Collect sounds
        #
        # IMPORTANT:
        # The ending anubandha is excluded.
        # ----------------------------------------------------

        result = []

        for item in self.sequence[
            start_index:end_index
        ]:

            if not item["is_anubandha"]:

                result.append(
                    item["symbol"]
                )

        return result


    # ========================================================
    # CHECK WHETHER A PRATYAHARA IS VALID
    # ========================================================

    def is_valid(self, notation, ending_marker=None):

        try:

            self.get_pratyahara(
                notation,
                ending_marker
            )

            return True

        except ValueError:

            return False


    # ========================================================
    # GENERATE ALL POSSIBLE PRATYAHARAS
    # ========================================================
    #
    # For every actual phoneme:
    #
    #     find every later anubandha
    #
    # Each pair creates a possible pratyahara.
    # ========================================================

    def generate_all(self):

        all_pratyaharas = []

        for start_index, start_item in enumerate(
            self.sequence
        ):

            # ----------------------------------------------
            # We can only start from actual phonemes.
            # ----------------------------------------------

            if start_item["is_anubandha"]:
                continue

            start = start_item["symbol"]

            # ----------------------------------------------
            # Look at everything after the starting sound.
            # ----------------------------------------------

            for end_index in range(
                start_index + 1,
                len(self.sequence)
            ):

                end_item = self.sequence[end_index]

                # ------------------------------------------
                # Only anubandhas can terminate a pratyahara
                # ------------------------------------------

                if not end_item["is_anubandha"]:
                    continue

                ending_marker = end_item["symbol"]

                # ------------------------------------------
                # Get actual sounds
                # ------------------------------------------

                sounds = []

                for item in self.sequence[
                    start_index:end_index
                ]:

                    if not item["is_anubandha"]:

                        sounds.append(
                            item["symbol"]
                        )

                # ------------------------------------------
                # Store result
                # ------------------------------------------

                all_pratyaharas.append({

                    "notation":
                        start + ending_marker,

                    "start":
                        start,

                    "ending_marker":
                        ending_marker,

                    "sounds":
                        sounds
                })

        return all_pratyaharas


    # ========================================================
    # PRINT ALL PRATYAHARAS
    # ========================================================

    def print_all(self):

        all_pratyaharas = self.generate_all()

        for item in all_pratyaharas:

            print(
                f"{item['notation']} → "
                f"{item['sounds']}"
            )


    # ========================================================
    # FILTER A PRATYAHARA USING ARRAY B
    # ========================================================
    #
    # If you have a separate set/list of sounds and want only
    # those sounds which belong to both:
    #
    #     pratyahara result
    #
    # and:
    #
    #     ARRAY_B
    #
    # use this function.
    # ========================================================

    def filter_with_array(
        self,
        notation,
        allowed_sounds
    ):

        result = self.get_pratyahara(notation)

        return [
            sound
            for sound in result
            if sound in allowed_sounds
        ]


# ============================================================
# 4. CREATE ENGINE
# ============================================================

engine = PratyaharaEngine(SEQUENCE)


# ============================================================
# 5. EXAMPLES
# ============================================================

print("=" * 70)
print("PRATYAHARA GENERATOR")
print("=" * 70)


# ------------------------------------------------------------
# Example 
# ------------------------------------------------------------

print("\n1. अण्")

print(
    engine.get_pratyahara("अण्")
)


print("\n2. इक्")

print(
    engine.get_pratyahara("इक्")
)


print("\n3. ऋष्")

print(
    engine.get_pratyahara("ऋष्")
)


print("\n4. ऋश्")

print(
    engine.get_pratyahara("ऋश्")
)


print("\n5. Separate arguments: ऋ + ष्")

print(
    engine.get_pratyahara("ऋ", "ष्")
)



# ============================================================
# 6. INTERACTIVE MODE
# ============================================================
#
# You can type ANY pratyahara.
# ============================================================

print("\n" + "=" * 70)
print("INTERACTIVE MODE")
print("=" * 70)

while True:

    user_input = input(
        "\nEnter a pratyahara "
        "(or type 'all' / 'quit'): "
    ).strip()

    if user_input.lower() == "quit":
        print("Program ended.")
        break

    if user_input.lower() == "all":

        engine.print_all()
        continue

    try:

        result = engine.get_pratyahara(
            user_input
        )

        print(
            f"\n{user_input} →"
        )

        print(result)

        print(
            f"Number of sounds = {len(result)}"
        )

    except ValueError as error:

        print(
            "\nInvalid pratyahara:"
        )

        print(error)