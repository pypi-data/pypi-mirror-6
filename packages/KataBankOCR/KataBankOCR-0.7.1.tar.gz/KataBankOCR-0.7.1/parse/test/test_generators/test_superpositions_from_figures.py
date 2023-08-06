"test the superpositions_from_figures generator"

from parse.generators.superpositions_from_figures import superpositions_from_figures

import check_generator
from fixture_methods import Figures, Superpositions, Strokes

test_iterability = check_generator.raises_on_non_iterable(generator=superpositions_from_figures)

test_element_type = \
    check_generator.raises_on_bad_element_type(generator=superpositions_from_figures,
                                               value_or_type=basestring)

test_element_length = \
    check_generator.raises_on_bad_element_length(generator=superpositions_from_figures,
                                                 valid_element=Figures.get_random())

test_element_composition = check_generator.raises_on_bad_element_composition(
    generator=superpositions_from_figures,
    valid_element=Figures.get_random(),
    adulterants=Strokes.invalid(),
    )

def test_parses_figures_to_superpositions():
    "confirm figures yield expected superpositions"
    expected_superpositions = (Superpositions.of_valid_figures()
                               + Superpositions.of_flawed_figures())
    iterator = superpositions_from_figures(Figures.valid() + Figures.flawed())
    found_superpositions = list(iterator)
    assert expected_superpositions == found_superpositions
