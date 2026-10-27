"""Arm B2 answer sets: for each entity, every valid answer from Wikidata, frozen before any model runs.

Relations (untyped, so as not to miss real works): any item with author (P50), director (P57) or performer (P175) =
entity. Entities with fewer than 3 works are excluded at scoring (thin coverage).
English labels and aliases are both kept as accepted answers.

  python scripts/open_factual_sets.py --out FILE
"""
import argparse
import json
import time
import urllib.parse
import urllib.request

UA = "yupi-research/0.1 (exact-world epistemic observability research; https://wamason.com)"
EP = "https://query.wikidata.org/sparql"

# (relation, entity QID, entity label). QIDs resolved by wbsearchentities with a description keyword check (2026-10-27);
# names that did not resolve, and two that resolved to the wrong entity (Khan, Steve Hillage), were dropped.
ENTITIES: list[tuple[str, str, str]] = [
    ('novel', 'Q36322', 'Jane Austen'),
    ('novel', 'Q5686', 'Charles Dickens'),
    ('novel', 'Q39829', 'Stephen King'),
    ('novel', 'Q35064', 'Agatha Christie'),
    ('novel', 'Q23434', 'Ernest Hemingway'),
    ('novel', 'Q72334', 'Toni Morrison'),
    ('novel', 'Q134798', 'Haruki Murakami'),
    ('novel', 'Q183492', 'Margaret Atwood'),
    ('novel', 'Q318399', 'Anthony Trollope'),
    ('novel', 'Q217495', 'Iris Murdoch'),
    ('novel', 'Q272585', 'Barbara Pym'),
    ('novel', 'Q237687', 'Anita Brookner'),
    ('novel', 'Q235308', 'Elizabeth Bowen'),
    ('novel', 'Q233956', 'Muriel Spark'),
    ('novel', 'Q267748', 'Penelope Fitzgerald'),
    ('novel', 'Q432322', 'Ivy Compton-Burnett'),
    ('novel', 'Q528576', 'Rose Macaulay'),
    ('novel', 'Q462270', 'Sylvia Townsend Warner'),
    ('novel', 'Q5423968', 'F. M. Mayor'),
    ('novel', 'Q2306224', 'Mary Webb'),
    ('novel', 'Q243130', 'Olivia Manning'),
    ('novel', 'Q7129165', 'Pamela Hansford Johnson'),
    ('novel', 'Q541812', 'Storm Jameson'),
    ('novel', 'Q523578', 'Winifred Holtby'),
    ('novel', 'Q1252645', 'Stella Gibbons'),
    ('novel', 'Q1334230', 'Hammond Innes'),
    ('novel', 'Q524782', 'Desmond Bagley'),
    ('novel', 'Q333713', 'Alistair MacLean'),
    ('novel', 'Q1331244', 'Elizabeth Jenkins'),
    ('novel', 'Q3442258', 'Rosamond Lehmann'),
    ('novel', 'Q5321911', 'E. H. Young'),
    ('novel', 'Q369526', 'Margaret Kennedy'),
    ('film', 'Q8877', 'Steven Spielberg'),
    ('film', 'Q7374', 'Alfred Hitchcock'),
    ('film', 'Q8006', 'Akira Kurosawa'),
    ('film', 'Q41148', 'Martin Scorsese'),
    ('film', 'Q315756', 'Mike Leigh'),
    ('film', 'Q55375', 'Claude Chabrol'),
    ('film', 'Q167475', 'Jacques Rivette'),
    ('film', 'Q55401', 'Kenji Mizoguchi'),
    ('film', 'Q8873', 'Satyajit Ray'),
    ('film', 'Q55238', 'Ken Loach'),
    ('film', 'Q229990', 'Agnès Varda'),
    ('film', 'Q50764', 'Éric Rohmer'),
    ('film', 'Q537232', 'Hiroshi Shimizu'),
    ('film', 'Q55381', 'Jacques Becker'),
    ('film', 'Q453683', 'Julien Duvivier'),
    ('film', 'Q810020', 'Basil Dearden'),
    ('film', 'Q722890', 'Michael Winner'),
    ('film', 'Q1351727', 'Val Guest'),
    ('film', 'Q711178', 'Roy Ward Baker'),
    ('film', 'Q456979', 'J. Lee Thompson'),
    ('film', 'Q303891', 'Lewis Gilbert'),
    ('film', 'Q433960', 'Ralph Thomas'),
    ('film', 'Q457250', 'Henry Hathaway'),
    ('film', 'Q959677', 'Allan Dwan'),
    ('film', 'Q72756', 'Raoul Walsh'),
    ('film', 'Q95119', 'Delmer Daves'),
    ('film', 'Q727753', 'Charles Crichton'),
    ('film', 'Q518366', 'Robert Hamer'),
    ('film', 'Q530235', 'Seth Holt'),
    ('film', 'Q329438', 'Wolf Rilla'),
    ('album', 'Q1299', 'The Beatles'),
    ('album', 'Q44190', 'Radiohead'),
    ('album', 'Q2306', 'Pink Floyd'),
    ('album', 'Q392', 'Bob Dylan'),
    ('album', 'Q26876', 'Taylor Swift'),
    ('album', 'Q909916', 'The Fall'),
    ('album', 'Q588820', 'Cocteau Twins'),
    ('album', 'Q285966', 'Hawkwind'),
    ('album', 'Q767871', 'Caravan'),
    ('album', 'Q752170', 'Van der Graaf Generator'),
    ('album', 'Q153616', 'Tangerine Dream'),
    ('album', 'Q170132', 'Can'),
    ('album', 'Q1319707', 'Amon Düül II'),
    ('album', 'Q943241', 'Gentle Giant'),
    ('album', 'Q280077', 'Kevin Ayers'),
    ('album', 'Q931909', 'Robyn Hitchcock'),
    ('album', 'Q1421042', 'Television Personalities'),
    ('album', 'Q2393477', 'The Monochrome Set'),
    ('album', 'Q1634063', 'The Chills'),
    ('album', 'Q2410301', 'The Clean'),
    ('album', 'Q1891138', 'The Go-Betweens'),
    ('album', 'Q1404436', 'Felt'),
    ('album', 'Q3312181', 'Microdisney'),
    ('album', 'Q354508', 'Sun Ra'),
    ('album', 'Q972623', 'Hatfield and the North'),
    ('album', 'Q1474555', 'Henry Cow'),
    ('album', 'Q729505', 'Soft Machine'),
]

# Untyped (2026-10-27, before any model ran): the typed version missed works such as The Prime of Miss Jean Brodie,
# and every gap turns a correct answer into a false "wrong". Leniency here only makes O1 harder to support.
QUERY = {
    "novel": "?w wdt:P50 wd:{q} .",
    "film": "?w wdt:P57 wd:{q} .",
    "album": "?w wdt:P175 wd:{q} .",
}


def sparql(q):
    url = EP + "?" + urllib.parse.urlencode({"query": q, "format": "json"})
    req = urllib.request.Request(url, headers={"User-Agent": UA, "Accept": "application/sparql-results+json"})
    with urllib.request.urlopen(req, timeout=60) as r:
        return json.load(r)["results"]["bindings"]


def labels(ids):
    """English label and aliases for each Wikidata item, via wbgetentities in batches of 50."""
    out = {}
    for i in range(0, len(ids), 50):
        url = "https://www.wikidata.org/w/api.php?" + urllib.parse.urlencode(dict(
            action="wbgetentities", ids="|".join(ids[i:i + 50]), props="labels|aliases", languages="en", format="json"))
        with urllib.request.urlopen(urllib.request.Request(url, headers={"User-Agent": UA}), timeout=60) as r:
            for qid, e in json.load(r)["entities"].items():
                names = [e["labels"]["en"]["value"]] if "en" in e.get("labels", {}) else []
                names += [a["value"] for a in e.get("aliases", {}).get("en", [])]
                if names:
                    out[qid] = sorted(set(names))
        time.sleep(0.5)
    return out


def answers(rel, qid):
    """Stage 1: item IDs by SPARQL (fast without labels). Stage 2: labels and aliases by the entity API."""
    for attempt in range(4):
        try:
            ids = sorted({b["w"]["value"].rsplit("/", 1)[1] for b in sparql("SELECT DISTINCT ?w WHERE { " + QUERY[rel].format(q=qid) + " }")})
            break
        except Exception:
            time.sleep(10 * (attempt + 1))
    else:
        raise RuntimeError(f"SPARQL failed for {rel} {qid}")
    return list(labels(ids).values())


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", required=True)
    a = ap.parse_args()
    rows = []
    for rel, qid, label in ENTITIES:
        works = answers(rel, qid)
        rows.append(dict(relation=rel, qid=qid, entity=label, n_works=len(works), works=works))
        print(rel, label, len(works), flush=True)
        time.sleep(1.0)
    json.dump(dict(source=EP, fetched=time.strftime("%Y-%m-%dT%H:%M:%S%z"), rows=rows), open(a.out, "w"), indent=1)


if __name__ == "__main__":
    main()
