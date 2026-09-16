"""Corpus generator (learner sub-project 1, design v0.1, 2026-09-13).

Windows are the corpus: one Part II §2(a) window per exact episode,
projected to a rung, rendered through a per-episode keyed injection
(v0.2.9 Clause 4), serialized as fixed five-token records (Part I D5).
Firewall: this package imports the world definition only (simulator,
interfaces, records, window, config, programs); no posterior path.
"""
