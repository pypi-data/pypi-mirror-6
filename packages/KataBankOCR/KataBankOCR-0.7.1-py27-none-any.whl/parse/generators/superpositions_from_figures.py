"""generator that yields Superpositions and the functions that support it

A Superposition tracks the relationship between a given Figure and all
the valid Numerals. It does this by counting the differences between
the provided Figure and actual Figure for each valid Numeral.
The generator yields this relationship as a dictionary:
  superposition[difference_count] = numeral_set
  {difference_count: set of valid numerals with that many differences}
"""

from parse import settings
from parse.validators import Validate

def superpositions_from_figures(figures):
    "generator that consumes Figures and yields SuperPositions"
    for figure in figures:
        _validate_figure(figure)
        yield _superposition_from_figure(figure)

def _validate_figure(figure):
    "confirm figure type, length, and composition or raise ValueError"
    Validate.type(basestring, figure, 'Figure')
    Validate.length(settings.strokes_per_figure, figure, 'Figure')
    Validate.composition(settings.valid_strokes, figure, 'Figure')

def _superposition_from_figure(figure):
    "return Superposition represented by Figure"
    d = {}
    for valid_figure, numeral in settings.figures.items():
        difference_count = _count_differences(figure, valid_figure)
        d.setdefault(difference_count, set()).add(numeral)
    return d

def _count_differences(figure_a, figure_b):
    "return count of differing Strokes between two Figures"
    paired_strokes = zip(figure_a, figure_b)
    return len(['' for a, b in paired_strokes if a != b])
