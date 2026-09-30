import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

PREAMBLE = r"""\documentclass[
  beameroptions={aspectratio=169,ignorenonframetext,11pt},
]{beamerswitch}
\usepackage{yjtalk}
\title{Prices imply a density}
\subtitle{The sentence the talk proves}
\author{Ada}
\date{1 October 2026}
"""

FRAME = r"""\begin{frame}{A frame states its finding}
  Body.
  \note{Stress this.}
\end{frame}
"""


@pytest.fixture
def make_talk(tmp_path):
    """Write talks/<slug>/talk.tex under a temp dir from a preamble and a body."""

    def make(body=FRAME, preamble=PREAMBLE, slug="demo", files=None):
        talk_dir = tmp_path / "talks" / slug
        talk_dir.mkdir(parents=True)
        (talk_dir / "talk.tex").write_text(preamble + "\\begin{document}\n" + body + "\\end{document}\n")
        for name, text in (files or {}).items():
            (talk_dir / name).parent.mkdir(parents=True, exist_ok=True)
            (talk_dir / name).write_text(text)
        return talk_dir

    return make
