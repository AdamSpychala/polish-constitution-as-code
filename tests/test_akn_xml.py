"""Tests for Akoma Ntoso 3.0 XML structural validity (akn/konstytucja_rp.xml)."""

import re
from pathlib import Path
from typing import ClassVar
from xml.etree import ElementTree as ET

import pytest

AKN_PATH = Path(__file__).resolve().parent.parent / "akn" / "konstytucja_rp.xml"
NS = {"akn": "http://docs.oasis-open.org/legaldocml/ns/akn/3.0"}


@pytest.fixture(scope="module")
def tree() -> ET.ElementTree:
    return ET.parse(AKN_PATH)


@pytest.fixture(scope="module")
def root(tree: ET.ElementTree) -> ET.Element:
    return tree.getroot()


# ---------------------------------------------------------------------------
# Well-formedness / basic structure
# ---------------------------------------------------------------------------


class TestAknWellFormedness:
    """XML is well-formed and follows Akoma Ntoso 3.0 structure."""

    def test_xml_parseable(self, tree: ET.ElementTree) -> None:
        assert tree is not None

    def test_root_is_akoma_ntoso(self, root: ET.Element) -> None:
        assert root.tag == f"{{{NS['akn']}}}akomaNtoso"

    def test_act_element_exists(self, root: ET.Element) -> None:
        act = root.find("akn:act", NS)
        assert act is not None

    def test_meta_section_exists(self, root: ET.Element) -> None:
        meta = root.find(".//akn:meta", NS)
        assert meta is not None

    def test_body_element_exists(self, root: ET.Element) -> None:
        body = root.find(".//akn:body", NS)
        assert body is not None

    def test_chapters_present(self, root: ET.Element) -> None:
        chapters = root.findall(".//akn:chapter", NS)
        assert len(chapters) >= 4, f"Expected >=4 chapters, got {len(chapters)}"


# ---------------------------------------------------------------------------
# Art. 55: Extradition [2006 amendment]
# ---------------------------------------------------------------------------


class TestAknArt55:
    """Art. 55 AKN entry has all 5 paragraphs with bilingual content."""

    def test_art55_exists(self, root: ET.Element) -> None:
        art = root.find(".//akn:article[@eId='art_55']", NS)
        assert art is not None, "Art. 55 missing from AKN XML"

    def test_art55_has_five_paragraphs(self, root: ET.Element) -> None:
        art = root.find(".//akn:article[@eId='art_55']", NS)
        assert art is not None
        paragraphs = art.findall("akn:paragraph", NS)
        assert len(paragraphs) == 5, f"Expected 5 paragraphs, got {len(paragraphs)}"

    def test_art55_paragraph_eids(self, root: ET.Element) -> None:
        art = root.find(".//akn:article[@eId='art_55']", NS)
        assert art is not None
        eids = [p.get("eId") for p in art.findall("akn:paragraph", NS)]
        expected = [f"art_55__para_{i}" for i in range(1, 6)]
        assert eids == expected

    def test_art55_bilingual(self, root: ET.Element) -> None:
        art = root.find(".//akn:article[@eId='art_55']", NS)
        assert art is not None
        for para in art.findall("akn:paragraph", NS):
            ps = para.findall(".//akn:p", NS)
            polish = [p for p in ps if p.get("{http://www.w3.org/XML/1998/namespace}lang") is None]
            english = [p for p in ps if p.get("{http://www.w3.org/XML/1998/namespace}lang") == "en"]
            eid = para.get("eId")
            assert len(polish) >= 1, f"{eid}: missing Polish text"
            assert len(english) >= 1, f"{eid}: missing English translation"


# ---------------------------------------------------------------------------
# Bilingual convention
# ---------------------------------------------------------------------------


class TestAknBilingualConvention:
    """Articles with code implementations should have bilingual text."""

    KNOWN_MISSING_ENGLISH: ClassVar[set[str]] = {
        "art_4",
        "art_8",
        "art_121",
        "art_230",
        "art_232",
    }

    def test_articles_have_english_translation(self, root: ET.Element) -> None:
        articles = root.findall(".//akn:article", NS)
        missing: list[str] = []
        for art in articles:
            eid = art.get("eId", "")
            if eid in self.KNOWN_MISSING_ENGLISH:
                continue
            english = art.findall(".//*[@xml:lang='en']", {"xml": "http://www.w3.org/XML/1998/namespace"})
            # Try alternate xpath approach
            if not english:
                english = [
                    p
                    for p in art.iter(f"{{{NS['akn']}}}p")
                    if p.get("{http://www.w3.org/XML/1998/namespace}lang") == "en"
                ]
            if not english:
                missing.append(eid)
        assert not missing, f"Articles missing English translations: {missing}"


# ---------------------------------------------------------------------------
# Cross-reference: article= values in Python ↔ AKN entries
# ---------------------------------------------------------------------------


class TestAknCodeCrossReference:
    """Every article referenced in Python raises should have an AKN entry."""

    def test_code_articles_in_akn(self, root: ET.Element) -> None:
        src_dir = Path(__file__).resolve().parent.parent / "src" / "konstytucja"
        article_re = re.compile(r'article="(\d+)')
        code_articles: set[int] = set()
        for py_file in src_dir.rglob("*.py"):
            for line in py_file.read_text(encoding="utf-8").splitlines():
                for m in article_re.finditer(line):
                    code_articles.add(int(m.group(1)))

        akn_articles: set[int] = set()
        for art in root.findall(".//akn:article", NS):
            eid = art.get("eId", "")
            m = re.match(r"art_(\d+)", eid)
            if m:
                akn_articles.add(int(m.group(1)))

        # Articles referenced in code but not yet in AKN XML.
        # As AKN coverage grows, remove from this set.
        known_missing = {
            103, 105,   # chapter 04: Sejm/Senate incompatibility, immunity
            119,        # chapter 04: legislative process
            125,        # chapter 04: referendum
            147, 154, 155, 156, 158, 159, 160,  # chapter 06: Council of Ministers
            164, 169, 171,  # chapter 07: local government
            176, 178, 179, 190, 191, 198, 199,  # chapter 08: courts
            205, 209, 214,  # chapter 09: oversight bodies
            227,        # chapter 10: central bank
            233,        # chapter 11: emergency
        }

        actually_missing = code_articles - akn_articles - known_missing
        assert not actually_missing, (
            f"Articles in code but not in AKN XML (and not in known_missing): "
            f"{sorted(actually_missing)}"
        )
