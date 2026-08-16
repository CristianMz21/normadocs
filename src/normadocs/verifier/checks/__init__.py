"""Checks package for APA 7th Edition verification."""

from .citations import CitationsCheck
from .cover_page import CoverPageCheck
from .equations import EquationsCheck
from .figures import FiguresCheck
from .fonts import FontsCheck
from .headings import HeadingsCheck
from .margins import MarginsCheck
from .page_setup import PageSetupCheck
from .paragraphs import ParagraphsCheck
from .references import ReferencesCheck
from .running_head import RunningHeadCheck
from .spacing import SpacingCheck
from .structure import StructureCheck
from .tables import TablesCheck

__all__ = [
    "CitationsCheck",
    "CoverPageCheck",
    "EquationsCheck",
    "FiguresCheck",
    "FontsCheck",
    "HeadingsCheck",
    "MarginsCheck",
    "PageSetupCheck",
    "ParagraphsCheck",
    "ReferencesCheck",
    "RunningHeadCheck",
    "SpacingCheck",
    "StructureCheck",
    "TablesCheck",
]
