"""
Layout dimensions are used to give the minimum, maximum and preferred
dimensions for containers and controls.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any, Callable, Union

__all__ = [
    "Dimension",
    "D",
    "sum_layout_dimensions",
    "max_layout_dimensions",
    "AnyDimension",
    "to_dimension",
    "is_dimension",
]

if TYPE_CHECKING:
    from typing_extensions import TypeGuard


class Dimension:
    """
    Specified dimension (width/height) of a user control or window.

    The layout engine tries to honor the preferred size. If that is not
    possible, because the terminal is larger or smaller, it tries to keep in
    between min and max.

    :param min: Minimum size.
    :param max: Maximum size.
    :param weight: For a VSplit/HSplit, the actual size will be determined
                   by taking the proportion of weights from all the children.
                   E.g. When there are two children, one with a weight of 1,
                   and the other with a weight of 2, the second will always be
                   twice as big as the first, if the min/max values allow it.
    :param preferred: Preferred size.
    """

    def __init__(
        self,
        min: int | None = None,
        max: int | None = None,
        weight: int | None = None,
        preferred: int | None = None,
    ) -> None:
        if weight is not None:
            assert weight >= 0  # Also cannot be a float.

        assert min is None or min >= 0
        assert max is None or max >= 0
        assert preferred is None or preferred >= 0

        self.min_specified = min is not None
        self.max_specified = max is not None
        self.preferred_specified = preferred is not None
        self.weight_specified = weight is not None

        if min is None:
            min = 0  # Smallest possible value.
        if max is None:  # 0-values are allowed, so use "is None"
            max = 1000**10  # Something huge.
        if preferred is None:
            preferred = min
        if weight is None:
            weight = 1

        self.min = min
        self.max = max
        self.preferred = preferred
        self.weight = weight

        # Don't allow situations where max < min. (This would be a bug.)
        if max < min:
            raise ValueError("Invalid Dimension: max < min.")

        # Make sure that the 'preferred' size is always in the min..max range.
        if self.preferred < self.min:
            self.preferred = self.min

        if self.preferred > self.max:
            self.preferred = self.max

    @classmethod
    def exact(cls, amount: int) -> Dimension:
        """
        Return a :class:`.Dimension` with an exact size. (min, max and
        preferred set to ``amount``).
        """
        return cls(min=amount, max=amount, preferred=amount)

    @classmethod
    def zero(cls) -> Dimension:
        """
        Create a dimension that represents a zero size. (Used for 'invisible'
        controls.)
        """
        return cls.exact(amount=0)

    def is_zero(self) -> bool:
        "True if this `Dimension` represents a zero size."
        return self.preferred == 0 or self.max == 0

    def __repr__(self) -> str:
        fields = []
        if self.min_specified:
            fields.append(f"min={self.min!r}")
        if self.max_specified:
            fields.append(f"max={self.max!r}")
        if self.preferred_specified:
            fields.append(f"preferred={self.preferred!r}")
        if self.weight_specified:
            fields.append(f"weight={self.weight!r}")

        return "Dimension({})".format(", ".join(fields))


def sum_layout_dimensions(dimensions: list[Dimension]) -> Dimension:
    """
    Sum a list of :class:`.Dimension` instances.
    """
    min = sum(d.min for d in dimensions)
    max = sum(d.max for d in dimensions)
    preferred = sum(d.preferred for d in dimensions)

    return Dimension(min=min, max=max, preferred=preferred)


def max_layout_dimensions(dimensions: list[Dimension]) -> Dimension:
    """
    Take the maximum of a list of :class:`.Dimension` instances.
    Used when we have a HSplit/VSplit, and we want to get the best width/height.)
    """
    if not len(dimensions):
        return Dimension.zero()

    # If all dimensions are size zero. Return zero.
    # (This is important for HSplit/VSplit, to report the right values to their
    # parent when all children are invisible.)
    if all(d.is_zero() for d in dimensions):
        return dimensions[0]

    # Ignore empty dimensions. (They should not reduce the size of others.)
    dimensions = [d for d in dimensions if not d.is_zero()]

    if dimensions:
        # Take the highest minimum dimension.
        min_ = max(d.min for d in dimensions)

        # For the maximum, we would prefer not to go larger than then smallest
        # 'max' value, unless other dimensions have a bigger preferred value.
        # This seems to work best:
        #  - We don't want that a widget with a small height in a VSplit would
        #    shrink other widgets in the split.
        # If it doesn't work well enough, then it's up to the UI designer to
        # explicitly pass dimensions.
        max_ = min(d.max for d in dimensions)
        max_ = max(max_, max(d.preferred for d in dimensions))

        # Make sure that min>=max. In some scenarios, when certain min..max
        # ranges don't have any overlap, we can end up in such an impossible
        # situation. In that case, give priority to the max value.
        # E.g. taking (1..5) and (8..9) would return (8..5). Instead take (8..8).
        if min_ > max_:
            max_ = min_

        preferred = max(d.preferred for d in dimensions)

        return Dimension(min=min_, max=max_, preferred=preferred)
    else:
        return Dimension()


# Anything that can be converted to a dimension.
AnyDimension = Union[
    None,  # None is a valid dimension that will fit anything.
    int,
    Dimension,
    # Callable[[], 'AnyDimension']  # Recursive definition not supported by mypy.
    Callable[[], Any],
]

from typing import Any, Callable, Union

to_dimension_coverage = {
    "to_dimension_1": False,  
    "to_dimension_2": False, 
    "to_dimension_3": False,  
    "to_dimension_4": False,  
    "to_dimension_5": False,
    "to_dimension_else_1": False,
    "to_dimension_else_2": False,
    "to_dimension_else_3": False,
    "to_dimension_else_4": False
}

def to_dimension(value: AnyDimension) -> Dimension:
    """
    Turn the given object into a `Dimension` object.
    """
    if value is None:
        to_dimension_coverage["to_dimension_1"] = True
        print("Branch 1 was hit")
        return Dimension()
    else:
        to_dimension_coverage["to_dimension_else_1"] = True

    if isinstance(value, int):
        to_dimension_coverage["to_dimension_2"] = True
        print("Branch 2 was hit")
        return Dimension.exact(value)
    else:
        to_dimension_coverage["to_dimension_else_2"] = True

    if isinstance(value, Dimension):
        to_dimension_coverage["to_dimension_3"] = True
        print("Branch 3 was hit")
        return value
    else:
        to_dimension_coverage["to_dimension_else_3"] = True

    if callable(value):
        to_dimension_coverage["to_dimension_4"] = True
        print("Branch 4 was hit")
        return to_dimension(value())
    else:
        to_dimension_coverage["to_dimension_else_4"] = True

    to_dimension_coverage["to_dimension_5"] = True
    print("Branch 5 was hit")
    raise ValueError("Not an integer or Dimension object.")


# Initialize coverage tracking global variable
branch_coverage = {
    "is_dimension_1": False,  # Branch for checking if value is None
    "is_dimension_1_else": False,  # Branch for else case of checking if value is None
    "is_dimension_2": False,  # Branch for checking if value is callable
    "is_dimension_2_else": False,  # Branch for else case of checking if value is callable
    "is_dimension_3": False,  # Branch for checking if value is int or Dimension
    "is_dimension_3_else": False,  # Branch for else case of checking if value is int or Dimension
    "is_dimension_4": False  # Branch for default case
}

def is_dimension(value: object) -> bool:
    if value is None:
        branch_coverage["is_dimension_1"] = True
        print("Branch 1 was hit")
        return True
    else:
        branch_coverage["is_dimension_1_else"] = True
        print("Branch 1 was not hit")

    if callable(value):
        branch_coverage["is_dimension_2"] = True
        print("Branch 2 was hit")
        return True
    else:
        branch_coverage["is_dimension_2_else"] = True
        print("Branch 2 was not hit")

    if isinstance(value, (int, Dimension)):
        branch_coverage["is_dimension_3"] = True
        print("Branch 3 was hit")
        return True
    else:
        branch_coverage["is_dimension_3_else"] = True
        print("Branch 3 was not hit")

    branch_coverage["is_dimension_4"] = True
    print("Branch 4 was hit")
    return False



# Common alias.
D = Dimension

# For backward-compatibility.
LayoutDimension = Dimension
