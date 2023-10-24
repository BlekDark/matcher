from jellyfish import metaphone
from fastDamerauLevenshtein import damerauLevenshtein
from polyleven import levenshtein


def get_similarity(s1: str, s2: str):
    l = 100 * (1 - levenshtein(s1, s2) / max(map(len, [s1, s2])))
    dl = 100 * damerauLevenshtein(s1, s2)
    # s1_sound = metaphone(s1)
    # s2_sound = metaphone(s2)
    # m = 100 * levenshtein.normalized_similarity(s1_sound, s2_sound)
    return round((l + dl) / 2, 4)
