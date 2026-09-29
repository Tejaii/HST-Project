# ============================================================
# PANINIAN PRATYAHARA ENGINE  (validated version)
# Based on the 14 Shiva Sutras + Panini's attested inventory
# ============================================================
#
# Two separate questions are kept apart:
#
#   1. RANGE      - what does start + marker cover?
#                   (Panini 1.1.71 adir antyena sahetA; computable)
#   2. VALIDITY   - is that notation a pratyahara Panini actually
#                   uses?  (NOT computable from the sutra order;
#                   determined by usage in the Ashtadhyayi, so it
#                   comes from an inventory.)
# ============================================================

VIRAMA = "\u094d"

# ------------------------------------------------------------
# 1. SHIVA SUTRAS   (sound, is_anubandha)
# ------------------------------------------------------------
# CORRECTION: sutra 11 is  kha pha chha tha tha ca Ta ta v(marker).
# The earlier version ended it at "च्", dropping च ट त व्.
# Everything else is unchanged.
# ------------------------------------------------------------

SHIVA_SUTRAS = [
    [("अ", False), ("इ", False), ("उ", False), ("ण्", True)],
    [("ऋ", False), ("ऌ", False), ("क्", True)],
    [("ए", False), ("ओ", False), ("ङ्", True)],
    [("ऐ", False), ("औ", False), ("च्", True)],
    [("ह्", False), ("य्", False), ("व्", False), ("र्", False), ("ट्", True)],
    [("ल्", False), ("ण्", True)],
    [("ञ्", False), ("म्", False), ("ङ्", False), ("ण्", False),
     ("न्", False), ("म्", True)],
    [("झ्", False), ("भ्", False), ("ञ्", True)],
    [("घ्", False), ("ढ्", False), ("ध्", False), ("ष्", True)],
    [("ज्", False), ("ब्", False), ("ग्", False), ("ड्", False),
     ("द्", False), ("श्", True)],
    [("ख्", False), ("फ्", False), ("छ्", False), ("ठ्", False),
     ("थ्", False), ("च्", False), ("ट्", False), ("त्", False),
     ("व्", True)],                                   # corrected sutra 11
    [("क्", False), ("प्", False), ("य्", True)],
    [("श्", False), ("ष्", False), ("स्", False), ("र्", True)],
    [("ह्", False), ("ल्", True)],
]

SEQUENCE = []
for sutra_number, sutra in enumerate(SHIVA_SUTRAS, start=1):
    for position, (symbol, is_anubandha) in enumerate(sutra):
        SEQUENCE.append({
            "symbol": symbol,
            "is_anubandha": is_anubandha,
            "sutra": sutra_number,
            "position": position,
        })


# ------------------------------------------------------------
# 2. INVENTORIES OF VALID PRATYAHARAS  (configurable)
# ------------------------------------------------------------
# Format: "notation" or "notation:N" where N is the number of the
# Shiva Sutra holding the ending marker.  N is needed only where
# the marker letter occurs more than once (currently only ण्).
#
# NOTE: compiled from the standard lists of pratyaharas used in
# the Ashtadhyayi.  Scholarly sources differ slightly in how they
# count/list them.  VERIFY against the Kashika or your preferred
# edition and edit here; nothing else in the code needs to change.
# ------------------------------------------------------------

ASHTADHYAYI_INVENTORY = [
    "अक्", "अच्", "अट्", "अण्:1", "अण्:6", "अम्", "अल्", "अश्",
    "इक्", "इच्", "इण्:6",
    "उक्",
    "एङ्", "एच्", "ऐच्",
    "ङम्", "ञम्",
    "खय्", "खर्", "चय्", "चर्", "छव्",
    "जश्", "झय्", "झर्", "झल्", "झश्", "झष्",
    "बश्", "भष्", "मय्",
    "यञ्", "यण्", "यम्", "यय्", "यर्",
    "रल्", "वल्", "वश्",
    "शर्", "शल्",
    "हल्", "हश्",
]

INVENTORIES = {
    "ashtadhyayi": ASHTADHYAYI_INVENTORY,
    "custom": [],          # put your own list here
    "mechanical": None,    # NO validation: every start/marker pair passes
}


class InvalidPratyaharaError(ValueError):
    """Range is computable, but the notation is not an attested pratyahara."""


def display_start(sound):
    """Traditional notation drops the virama on the first letter (हल्, यण्)."""
    return sound[:-1] if sound.endswith(VIRAMA) else sound


# ------------------------------------------------------------
# 3. ENGINE
# ------------------------------------------------------------

class PratyaharaEngine:

    def __init__(self, sequence, convention="ashtadhyayi"):
        self.sequence = sequence

        self.sounds = []
        for item in sequence:
            if not item["is_anubandha"] and item["symbol"] not in self.sounds:
                self.sounds.append(item["symbol"])

        self.anubandhas = {i["symbol"] for i in sequence if i["is_anubandha"]}
        self.set_convention(convention)

    # ---------------- configuration ----------------

    def set_convention(self, convention):
        if convention not in INVENTORIES:
            raise ValueError(f"Unknown convention '{convention}'. "
                             f"Choose from {list(INVENTORIES)}.")
        self.convention = convention
        entries = INVENTORIES[convention]

        if entries is None:
            self._inventory = None       # mechanical mode
            return

        # (start, marker) -> sorted list of end-sutra numbers
        inv = {}
        for entry in entries:
            base, explicit = self._split_sense(entry)
            start, marker = self._parse_pair(base)
            sutra_no = explicit or self._mechanical_end_sutra(start, marker)
            inv.setdefault((start, marker), [])
            if sutra_no not in inv[(start, marker)]:
                inv[(start, marker)].append(sutra_no)
        for senses in inv.values():
            senses.sort()
        self._inventory = inv

    # ---------------- parsing helpers ----------------

    @staticmethod
    def _split_sense(text):
        text = text.strip()
        if ":" in text:
            base, n = text.rsplit(":", 1)
            return base.strip(), int(n)
        return text, None

    def _normalize_marker(self, text):
        if text in self.anubandhas:
            return text
        if text + VIRAMA in self.anubandhas:
            return text + VIRAMA
        raise ValueError(f"'{text}' is not an anubandha in the Shiva Sutras.")

    def _normalize_sound(self, text):
        if text in self.sounds:
            return text
        if text + VIRAMA in self.sounds:
            return text + VIRAMA
        raise ValueError(f"Starting sound '{text}' is not present "
                         f"in the Shiva Sutras.")

    def _parse_pair(self, base):
        """Split e.g. 'हल्' or 'ह्ल्' or 'ऋष्' into (start, marker)."""
        forms = []
        for s in self.sounds:
            forms.append((s, s))
            if s.endswith(VIRAMA):
                forms.append((s[:-1], s))       # traditional spelling
        forms.sort(key=lambda f: len(f[0]), reverse=True)

        for form, sound in forms:
            if base.startswith(form):
                try:
                    marker = self._normalize_marker(base[len(form):])
                except ValueError:
                    continue
                return sound, marker

        raise ValueError(f"Could not parse '{base}'. "
                         f"Expected something like 'अण्', 'इक्', 'ऋष्', 'हल्'.")

    # ---------------- mechanical range (1.1.71) ----------------

    def find_start(self, start):
        for i, item in enumerate(self.sequence):
            if item["symbol"] == start and not item["is_anubandha"]:
                return i
        raise ValueError(f"Starting sound '{start}' is not present "
                         f"in the Shiva Sutras.")

    def find_end(self, start_index, marker, end_sutra=None):
        for i in range(start_index + 1, len(self.sequence)):
            item = self.sequence[i]
            if item["symbol"] == marker and item["is_anubandha"]:
                if end_sutra is None or item["sutra"] == end_sutra:
                    return i
        where = f" in sutra {end_sutra}" if end_sutra else ""
        raise ValueError(f"Anubandha '{marker}' does not occur after the "
                         f"starting sound{where}.")

    def _mechanical_end_sutra(self, start, marker):
        s = self.find_start(start)
        return self.sequence[self.find_end(s, marker)]["sutra"]

    def compute_range(self, start, marker, end_sutra=None):
        """Pure computation. Says NOTHING about grammatical validity."""
        s = self.find_start(start)
        e = self.find_end(s, marker, end_sutra)
        result = []
        for item in self.sequence[s:e]:
            if not item["is_anubandha"] and item["symbol"] not in result:
                result.append(item["symbol"])
        return result

    # ---------------- validated lookup ----------------

    def senses(self, start, marker):
        """Attested end-sutra numbers for this notation (empty if none)."""
        if self._inventory is None:
            return []
        return list(self._inventory.get((start, marker), []))

    def get_pratyahara(self, notation, ending_marker=None,
                       end_sutra=None, strict=True):
        """
        get_pratyahara("अण्")            get_pratyahara("ऋ", "ष्")
        get_pratyahara("अण्:6")          get_pratyahara("उण्", strict=False)
        """
        if ending_marker is not None:
            start = self._normalize_sound(notation)
            marker = self._normalize_marker(ending_marker)
        else:
            base, explicit = self._split_sense(notation)
            start, marker = self._parse_pair(base)
            end_sutra = end_sutra or explicit

        attested = self.senses(start, marker)

        # choose which occurrence of the marker to use
        if end_sutra is None and attested:
            end_sutra = attested[0]          # default = first attested sense

        result = self.compute_range(start, marker, end_sutra)   # may raise

        if strict and self._inventory is not None:
            actual = end_sutra or self._mechanical_end_sutra(start, marker)
            if actual not in attested:
                name = display_start(start) + marker
                raise InvalidPratyaharaError(
                    f"Invalid pratyahara: {name}\n"
                    f"Reason: The combination is mechanically constructible "
                    f"from the Shiva Sutras but is not a recognized "
                    f"Paninian pratyahara "
                    f"(convention: '{self.convention}')."
                )
        return result

    def is_valid(self, notation, ending_marker=None, end_sutra=None):
        try:
            self.get_pratyahara(notation, ending_marker, end_sutra)
            return True
        except ValueError:
            return False

    # ---------------- generation ----------------

    def generate_all(self):
        """ONLY validated pratyaharas, in Shiva-Sutra order."""
        if self._inventory is None:
            return self.generate_mechanical()

        rows = []
        for (start, marker), senses in self._inventory.items():
            for sutra_no in senses:
                label = display_start(start) + marker
                if len(senses) > 1:
                    label += f":{sutra_no}"
                rows.append({
                    "notation": label,
                    "start": start,
                    "ending_marker": marker,
                    "end_sutra": sutra_no,
                    "sounds": self.compute_range(start, marker, sutra_no),
                    "_order": (self.find_start(start), sutra_no),
                })
        rows.sort(key=lambda r: r["_order"])
        for r in rows:
            del r["_order"]
        return rows

    def generate_mechanical(self):
        """Every start/marker pair. NOT valid pratyaharas - diagnostics only."""
        rows = []
        for si, s_item in enumerate(self.sequence):
            if s_item["is_anubandha"]:
                continue
            for ei in range(si + 1, len(self.sequence)):
                e_item = self.sequence[ei]
                if not e_item["is_anubandha"]:
                    continue
                rows.append({
                    "notation": display_start(s_item["symbol"]) + e_item["symbol"],
                    "start": s_item["symbol"],
                    "ending_marker": e_item["symbol"],
                    "end_sutra": e_item["sutra"],
                    "sounds": self.compute_range(
                        s_item["symbol"], e_item["symbol"], e_item["sutra"]),
                })
        return rows

    def print_all(self):
        rows = self.generate_all()
        for r in rows:
            print(f"{r['notation']} → {r['sounds']}")
        print(f"\nTotal validated entries: {len(rows)} "
              f"(convention: '{self.convention}')")

    # ---------------- optional helper ----------------

    def filter_with_array(self, notation, allowed_sounds):
        return [s for s in self.get_pratyahara(notation)
                if s in allowed_sounds]


# ------------------------------------------------------------
# 4. EXAMPLES
# ------------------------------------------------------------

def demo(engine):
    print("=" * 70)
    print("PRATYAHARA GENERATOR")
    print("=" * 70)

    print("\n--- Valid (attested) pratyaharas ---")
    for label, args in [
        ("अण्", ("अण्",)),
        ("अण्:6", ("अण्:6",)),
        ("इक्", ("इक्",)),
        ("हल्", ("हल्",)),
        ("एङ् + separate args (ए + ङ्)", ("ए", "ङ्")),
    ]:
        print(f"\n{label}")
        print(engine.get_pratyahara(*args))

    print("\n--- Range only (strict=False): computable, NOT attested ---")
    for label, args in [
        ("ऋष्", ("ऋष्",)),
        ("ऋ + ष् (separate arguments)", ("ऋ", "ष्")),
    ]:
        print(f"\n{label}")
        print(engine.get_pratyahara(*args, strict=False))

    print("\n--- Rejected in strict mode ---")
    for bad in ["ऋष्", "उण्", "ऌक्", "ओङ्", "रट्", "सर्"]:
        try:
            engine.get_pratyahara(bad)
        except ValueError as e:
            print(f"  {bad}: {str(e).splitlines()[-1]}")

# ------------------------------------------------------------
# 5. INTERACTIVE MODE
# ------------------------------------------------------------

def interactive(engine):
    print("\n" + "=" * 70)
    print("INTERACTIVE MODE   (type a pratyahara, 'all', or 'quit')")
    print("Ambiguous markers: use e.g. अण्:6 for the sutra-6 sense.")
    print("=" * 70)

    while True:
        text = input("\nEnter a pratyahara: ").strip()

        if text.lower() == "quit":
            print("Program ended.")
            break
        if text.lower() == "all":
            engine.print_all()
            continue
        if not text:
            continue

        try:
            result = engine.get_pratyahara(text)
            print(f"\n{text} → {result}")
            print(f"Number of sounds = {len(result)}")

            base, explicit = engine._split_sense(text)
            start, marker = engine._parse_pair(base)
            senses = engine.senses(start, marker)
            if len(senses) > 1 and explicit is None:
                others = ", ".join(f"{base}:{n}" for n in senses[1:])
                print(f"(Default sense shown. Other attested sense: {others})")

        except InvalidPratyaharaError as error:
            print(f"\n{error}")
        except ValueError as error:
            print(f"\nInvalid input: {error}")


if __name__ == "__main__":
    engine = PratyaharaEngine(SEQUENCE, convention="ashtadhyayi")
    demo(engine)
    interactive(engine)