# ============================================================
# PANINIAN PRATYAHARA ENGINE  (rule-based: works for ALL valid cases)
# ============================================================
# 1. RANGE     - start + marker -> sounds (Panini 1.1.71 adir antyena saheta)
# 2. VALIDITY  - three conventions:
#      "rule_based"  (DEFAULT) every sound -> any LATER marker is accepted,
#                    EXCEPT the degenerate case where fewer than two
#                    sounds lie in the range (i.e. the sound immediately
#                    before the marker paired with that marker).
#                    Cross-sutra ranges of any length are allowed.
#      "ashtadhyayi" only the attested inventory below (restrictive)
#      "custom"      your own list
#      "mechanical"  no validation at all (diagnostics)
# ============================================================

VIRAMA = "\u094d"

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
     ("व्", True)],
    [("क्", False), ("प्", False), ("य्", True)],
    [("श्", False), ("ष्", False), ("स्", False), ("र्", True)],
    [("ह्", False), ("ल्", True)],
]

SEQUENCE = []
for sutra_number, sutra in enumerate(SHIVA_SUTRAS, start=1):
    for position, (symbol, is_anubandha) in enumerate(sutra):
        SEQUENCE.append({"symbol": symbol, "is_anubandha": is_anubandha,
                         "sutra": sutra_number, "position": position})

# Optional restrictive list (only used by convention="ashtadhyayi").
ASHTADHYAYI_INVENTORY = [
    "अक्", "अच्", "अट्", "अण्:1", "अण्:6", "अम्", "अल्", "अश्",
    "इक्", "इच्", "इण्:6", "उक्", "एङ्", "एच्", "ऐच्", "ङम्", "ञम्",
    "खय्", "खर्", "चय्", "चर्", "छव्", "जश्", "झय्", "झर्", "झल्",
    "झश्", "झष्", "बश्", "भष्", "मय्", "यञ्", "यण्", "यम्", "यय्", "यर्",
    "रल्", "वल्", "वश्", "शर्", "शल्", "हल्", "हश्",
]

# Optional manual exclusions (kept empty on purpose).  The 14 "ultimate"
# combinations (last sound of each sutra + its own marker) are already
# removed by the rule itself, so nothing needs to be listed here.
# Format if you ever need it: "हल्"  (all senses)  or  "अण्:1"  (one sense).
EXCLUDED_NOTATIONS = []

RULE_BASED = "RULE_BASED"   # sentinel

INVENTORIES = {
    "rule_based": RULE_BASED,
    "ashtadhyayi": ASHTADHYAYI_INVENTORY,
    "custom": [],
    "mechanical": None,
}


class InvalidPratyaharaError(ValueError):
    """Range is computable, but the notation is not a valid pratyahara."""


def display_start(sound):
    return sound[:-1] if sound.endswith(VIRAMA) else sound


class PratyaharaEngine:

    def __init__(self, sequence, convention="rule_based"):
        self.sequence = sequence
        self.sounds = []
        for item in sequence:
            if not item["is_anubandha"] and item["symbol"] not in self.sounds:
                self.sounds.append(item["symbol"])
        self.anubandhas = {i["symbol"] for i in sequence if i["is_anubandha"]}
        self.set_convention(convention)

    # ---------------- configuration ----------------

    def _build_rule_based_inventory(self):
        """Every (start, marker) with >= 2 sounds in the range.
        A repeated sound (ह) is only used from its FIRST occurrence."""
        inv, seen = {}, set()
        for si, s in enumerate(self.sequence):
            if s["is_anubandha"] or s["symbol"] in seen:
                continue
            seen.add(s["symbol"])
            count = 0
            for ei in range(si, len(self.sequence)):
                e = self.sequence[ei]
                if not e["is_anubandha"]:
                    count += 1
                elif count >= 2:
                    inv.setdefault((s["symbol"], e["symbol"]), []).append(e["sutra"])
        return inv

    def set_convention(self, convention):
        if convention not in INVENTORIES:
            raise ValueError(f"Unknown convention '{convention}'. "
                             f"Choose from {list(INVENTORIES)}.")
        self.convention = convention
        self._excluded = set()
        self._excluded_senses = set()
        entries = INVENTORIES[convention]

        if entries is None:
            self._inventory = None
            return
        if entries is RULE_BASED:
            self._inventory = self._build_rule_based_inventory()
            self._apply_exclusions()
            return

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
        self._apply_exclusions()

    def _apply_exclusions(self):
        """Remove every EXCLUDED_NOTATIONS entry from the inventory.
        'उण्'   -> blocks the notation in every sense
        'अण्:1' -> blocks only the sense ending in sutra 1"""
        self._excluded = set()
        self._excluded_senses = set()
        for text in EXCLUDED_NOTATIONS:
            base, sense = self._split_sense(text)
            try:
                pair = self._parse_pair(base)
            except ValueError:
                continue
            if sense is None:
                self._excluded.add(pair)
                self._inventory.pop(pair, None)
            else:
                self._excluded_senses.add((pair[0], pair[1], sense))
                lst = self._inventory.get(pair)
                if lst and sense in lst:
                    lst.remove(sense)
                    if not lst:
                        del self._inventory[pair]

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
        raise ValueError(f"Starting sound '{text}' is not present in the Shiva Sutras.")

    def _parse_pair(self, base):
        forms = []
        for s in self.sounds:
            forms.append((s, s))
            if s.endswith(VIRAMA):
                forms.append((s[:-1], s))
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

    # ---------------- range (1.1.71) ----------------

    def find_start(self, start):
        for i, item in enumerate(self.sequence):
            if item["symbol"] == start and not item["is_anubandha"]:
                return i
        raise ValueError(f"Starting sound '{start}' is not present in the Shiva Sutras.")

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
        return self.sequence[self.find_end(self.find_start(start), marker)]["sutra"]

    def compute_range(self, start, marker, end_sutra=None, unique=True):
        """Pure computation. unique=True lists a repeated sound (ह) once;
        unique=False returns every occurrence in Shiva-Sutra order."""
        s = self.find_start(start)
        e = self.find_end(s, marker, end_sutra)
        result = []
        for item in self.sequence[s:e]:
            if item["is_anubandha"]:
                continue
            if unique and item["symbol"] in result:
                continue
            result.append(item["symbol"])
        return result

    # ---------------- validated lookup ----------------

    def senses(self, start, marker):
        if self._inventory is None:
            return []
        return list(self._inventory.get((start, marker), []))

    def get_pratyahara(self, notation, ending_marker=None,
                       end_sutra=None, strict=True, unique=True):
        if ending_marker is not None:
            start = self._normalize_sound(notation)
            marker = self._normalize_marker(ending_marker)
        else:
            base, explicit = self._split_sense(notation)
            start, marker = self._parse_pair(base)
            end_sutra = end_sutra or explicit

        attested = self.senses(start, marker)
        if end_sutra is None and attested:
            end_sutra = attested[0]

        result = self.compute_range(start, marker, end_sutra, unique)

        if strict and self._inventory is not None:
            actual = end_sutra or self._mechanical_end_sutra(start, marker)
            if actual not in attested:
                name = display_start(start) + marker
                if (start, marker, actual) in self._excluded_senses:
                    reason = (f"the sense ending at the marker in sutra {actual} "
                              f"is on the exception list.")
                elif (start, marker) in self._excluded:
                    reason = ("this is on the exception list: a pratyahara cannot "
                              "be formed from the sound immediately before a "
                              "marker with that marker.")
                elif self.convention == "rule_based":
                    reason = ("fewer than two sounds lie between the start and "
                              "the marker (the sound immediately before a marker "
                              "cannot form a pratyahara with it), or the marker "
                              "does not occur after the start.")
                else:
                    reason = "not in the inventory for this convention."
                raise InvalidPratyaharaError(
                    f"Invalid pratyahara: {name}\nReason: {reason} "
                    f"(convention: '{self.convention}')")
        return result

    def is_valid(self, notation, ending_marker=None, end_sutra=None):
        try:
            self.get_pratyahara(notation, ending_marker, end_sutra)
            return True
        except ValueError:
            return False

    # ---------------- generation ----------------

    def generate_all(self, unique=True):
        if self._inventory is None:
            return self.generate_mechanical()
        rows = []
        for (start, marker), senses in self._inventory.items():
            for sutra_no in senses:
                label = display_start(start) + marker
                if len(senses) > 1:
                    label += f":{sutra_no}"
                rows.append({
                    "notation": label, "start": start, "ending_marker": marker,
                    "end_sutra": sutra_no,
                    "sounds": self.compute_range(start, marker, sutra_no, unique),
                    "_order": (self.find_start(start), sutra_no),
                })
        rows.sort(key=lambda r: r["_order"])
        for r in rows:
            del r["_order"]
        return rows

    def generate_mechanical(self):
        rows = []
        for si, s_item in enumerate(self.sequence):
            if s_item["is_anubandha"]:
                continue
            for ei in range(si + 1, len(self.sequence)):
                e_item = self.sequence[ei]
                if e_item["is_anubandha"]:
                    rows.append({
                        "notation": display_start(s_item["symbol"]) + e_item["symbol"],
                        "start": s_item["symbol"], "ending_marker": e_item["symbol"],
                        "end_sutra": e_item["sutra"],
                        "sounds": self.compute_range(s_item["symbol"],
                                                     e_item["symbol"], e_item["sutra"]),
                    })
        return rows

    def count_all(self):
        """Total number of pratyaharas under the current convention.
        Both senses of an ambiguous marker (e.g. अण्:1 and अण्:6) count separately."""
        return len(self.generate_all())

    def ultimate_pairs(self):
        """The 14 'ultimate' combinations: the last sound of each sutra paired
        with that sutra's own marker.  They cover a single sound, so they are
        never pratyaharas."""
        out = []
        for i, item in enumerate(self.sequence):
            if item["is_anubandha"] and i > 0 and not self.sequence[i - 1]["is_anubandha"]:
                prev = self.sequence[i - 1]
                out.append({"notation": display_start(prev["symbol"]) + item["symbol"],
                            "sutra": item["sutra"]})
        return out

    def count_summary(self):
        rows = self.generate_all()
        names = {display_start(r["start"]) + r["ending_marker"] for r in rows}
        mech = len(self.generate_mechanical())
        return {"total": len(rows), "distinct_names": len(names),
                "all_start_marker_pairs": mech,
                "ultimate_excluded": len(self.ultimate_pairs()),
                "convention": self.convention}

    def print_all(self):
        rows = self.generate_all()
        for r in rows:
            print(f"{r['notation']} → {r['sounds']}")
        print(f"\nTotal pratyaharas: {len(rows)} (convention: '{self.convention}')")

    def filter_with_array(self, notation, allowed_sounds):
        return [s for s in self.get_pratyahara(notation) if s in allowed_sounds]


# ------------------------------------------------------------
def demo(engine):
    print("=" * 70)
    print("PRATYAHARA GENERATOR  (convention:", engine.convention + ")")
    print("=" * 70)
    for label, args in [("अण्", ("अण्",)), ("इक्", ("इक्",)),
                        ("ऋष् (crosses sutras 2-9)", ("ऋष्",)),
                        ("यञ्", ("यञ्",)),
                        ("ए + च् (separate args)", ("ए", "च्"))]:
        print(f"\n{label}\n{engine.get_pratyahara(*args)}")
    c = engine.count_summary()
    print(f"\nTotal pratyaharas: {c['total']} "
          f"({c['distinct_names']} distinct names, convention: '{c['convention']}')")
    print(f"All start/marker pairs : {c['all_start_marker_pairs']}")
    print(f"Ultimate pairs removed : {c['ultimate_excluded']}  ->  "
          + "  ".join(u["notation"] for u in engine.ultimate_pairs()))
    print(f"Valid pratyaharas      : {c['total']}")
    print("\n--- Rejected ---")
    for bad in ["ऌक्", "ओङ्", "औच्", "रट्", "लण्", "नम्", "भञ्",
                "धष्", "दश्", "तव्", "पय्", "सर्", "उण्:1"]:
        try:
            engine.get_pratyahara(bad)
            print(f"  {bad}: ACCEPTED (unexpected)")
        except ValueError as e:
            print(f"  {bad}: rejected")


def interactive(engine):
    print("\nINTERACTIVE MODE  (type a pratyahara, 'all', 'count', or 'quit')")
    print("Ambiguous ण् marker: use अण्:1 / अण्:6")
    while True:
        text = input("\nEnter a pratyahara: ").strip()
        if text.lower() == "quit":
            break
        if text.lower() == "all":
            engine.print_all()
            continue
        if text.lower() == "count":
            c = engine.count_summary()
            print(f"\nTotal pratyaharas: {c['total']} "
                  f"({c['distinct_names']} distinct names, "
                  f"convention: '{c['convention']}')")
            continue
        if not text:
            continue
        try:
            result = engine.get_pratyahara(text)
            print(f"\n{text} → {result}\nNumber of sounds = {len(result)}")
            base, explicit = engine._split_sense(text)
            start, marker = engine._parse_pair(base)
            senses = engine.senses(start, marker)
            if len(senses) > 1 and explicit is None:
                print("(Default sense shown. Others: " +
                      ", ".join(f"{base}:{n}" for n in senses[1:]) + ")")
        except InvalidPratyaharaError as error:
            print(f"\n{error}")
        except ValueError as error:
            print(f"\nInvalid input: {error}")


if __name__ == "__main__":
    engine = PratyaharaEngine(SEQUENCE, convention="rule_based")
    demo(engine)
    interactive(engine)