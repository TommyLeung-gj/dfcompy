"""
This module provides a framework for comparing two Pandas DataFrames. It includes a base Comparator class,
specific comparators for numeric and string data (NumberComparator and StringComparator), and a comprehensive
DataFrameComparator for comparing two DataFrames.

The DataFrameComparator class performs detailed comparisons of DataFrames, identifying rows that are deleted,
inserted, or updated based on specified key columns and subsets of columns. It can handle both numeric and string
data, allowing for customization in numerical tolerance and string case sensitivity during comparison.
"""
__all__ = ["DataFrameComparator"]

from pandas import DataFrame


class Comparator:
    """
    Base class for comparators, defining the basic structure of a comparator.
    This class initializes with two comparison objects.
    """

    def __init__(self, one, other):
        self.one = one
        self.other = other


class NumberComparator(Comparator):
    """
    Number comparator for comparing two numerical values.
    Supports two modes of comparison: 'absolute' and 'relative'.
    The comparison mode and tolerance level can be specified.
    """

    TOLERANCE_MODES = ("absolute", "relative")

    def __init__(self, one, other, tol_mode="absolute", tolerance=0.001):
        super().__init__(one, other)
        self.tol_mode = tol_mode
        self.tolerance = tolerance

    def compare(self):
        """
        Perform the comparison based on the specified tolerance mode and return the result.
        """
        one_value, other_value = float(self.one), float(self.other)
        if self.tol_mode == "relative":
            return self.relatively_compare(one_value, other_value, self.tolerance)
        else:
            return self.absolutely_compare(one_value, other_value, self.tolerance)

    @staticmethod
    def absolutely_compare(one_value, other_value, tolerance):
        """
        Absolute tolerance comparison. Returns True if the difference is less than the tolerance.
        """
        return abs(one_value - other_value) < tolerance

    @staticmethod
    def relatively_compare(one_value, other_value, tolerance):
        """
        Relative tolerance comparison. Returns True if the relative difference is less than the tolerance.
        """
        if other_value == one_value == 0:
            return True
        return abs((one_value - other_value) / max(abs(one_value), abs(other_value))) < tolerance

    def __bool__(self):
        """
        Boolean representation of the comparison result.
        """
        return bool(self.compare())


class StringComparator(Comparator):
    """
    String comparator for comparing two string values.
    Supports case-sensitive and case-insensitive comparisons.
    """

    def __init__(self, one, other, ignore_case=False):
        super().__init__(one, other)
        self.ignore_case = ignore_case

    def compare(self):
        """
        Perform the string comparison and return the result.
        If ignore_case is True, performs a case-insensitive comparison.
        """
        if self.ignore_case:
            return self.one.lower() == self.other.lower()
        return self.one == self.other

    def __bool__(self):
        """
        Boolean representation of the string comparison result.
        """
        return bool(self.compare())


class DataFrameComparator(Comparator):
    """
    Comparator for DataFrames. It compares two DataFrames based on specified key columns (on)
    and a subset of columns for comparison. It can identify rows that are deleted, inserted, or updated.
    Supports customization for numeric comparison modes and tolerances, and string case sensitivity.
    """

    def __init__(self, one: DataFrame, other: DataFrame, on: list, subset: list = None, number_mode: str = "absolute",
                 number_tolerance: float = 0.001, ignore_case: bool = False) -> None:
        super().__init__(one, other)
        self.on = on
        self.subset = subset or one.columns.tolist()
        self.number_mode = number_mode
        self.number_tolerance = number_tolerance
        self.ignore_case = ignore_case

        self._check_subset()
        self._prepare_data()
        self._prepare_comparators()
        self._comparison, self._mask = self._compare()

    @property
    def abstract(self):
        data = {
            "old": self.one.shape[0],
            "new": self.other.shape[0],
            "deleted": self.rows_deleted.shape[0],
            "updated": self.rows_after_update.shape[0],
            "inserted": self.rows_inserted.shape[0],
            "common": self.rows_in_common.shape[0]
        }
        abstract = DataFrame(data, index=["count"])
        abstract.index.name = "Abstract"
        return abstract.to_markdown()

    def _check_subset(self) -> None:
        """
        Check the validity of the subset. Ensure that the 'on' columns are common to both DataFrames
        and are not included in the subset of columns to be compared.
        """
        join_columns = set(self.one.columns).intersection(set(self.other.columns))
        ons = set(self.on)
        subset = set(self.subset)
        assert (len(self.on) > 0
                and not ons.issubset(subset)
                and ons.issubset(
                    join_columns)), '"on" set must be a subset of common columns those not in param "subset" !'
        except_on_columns = join_columns - ons
        if len(except_on_columns) == 0:
            raise KeyError("There are no common columns between the two DataFrames except for the 'on' set.")
        if self.subset is None:
            self.subset = except_on_columns
        elif not subset.issubset(except_on_columns):
            invalid_subset_elements = subset - except_on_columns
            raise KeyError("Invalid subset elements : %s" % invalid_subset_elements)

    def _prepare_data(self):
        """
        Prepare data for comparison by setting the index and selecting the subset of columns.
        """
        self._one = self.one.set_index(self.on)[self.subset]
        self._other = self.other.set_index(self.on)[self.subset]

    def _prepare_comparators(self):
        """
        Prepare the appropriate comparators for each column based on the data type.
        """
        self.comparators = []
        for col in self.subset:
            try:
                _ = self._one[col].astype("float64")
                self.comparators.append(NumberComparator)
            except ValueError:
                self.comparators.append(StringComparator)

    def _compare(self) -> tuple:
        """
        Compare the DataFrames and return a tuple containing the comparison DataFrame
        and a mask indicating rows with no changes.
        """
        common_indexes = self._one.index.isin(self._other.index)
        comparison = DataFrame(index=self._one.index[common_indexes], columns=self.subset, dtype=bool)
        for i, col in enumerate(self.subset):
            is_numeric = self.comparators[i].__name__ == NumberComparator.__name__
            for idx in comparison.index:
                one_val = self._one.at[idx, col]
                other_val = self._other.at[idx, col] if idx in self._other.index else None
                comparator = (
                    NumberComparator(one_val, other_val, self.number_mode, self.number_tolerance)
                    if is_numeric else StringComparator(one_val, other_val, self.ignore_case)
                )
                comparison.at[idx, col] = comparator.compare()
        mask = comparison.apply(lambda x: all(x), axis=1)
        return comparison, mask

    @property
    def rows_deleted(self):
        """
        Identify rows that are present in the first DataFrame but not in the second.
        """
        return self._one.loc[~self._one.index.isin(self._other.index)]

    @property
    def rows_inserted(self):
        """
        Identify rows that are present in the second DataFrame but not in the first.
        """
        return self._other.loc[~self._other.index.isin(self._one.index)]

    @property
    def rows_in_common(self):
        """
        Identify rows that are common in both DataFrames with no changes.
        """
        mask = self._comparison.loc[self._mask].index
        return self._one.loc[mask]

    @property
    def rows_before_update(self):
        """
        Identify rows that are present in both DataFrames but have changes in the first DataFrame.
        """
        mask = self._comparison.loc[~self._mask].index
        return self._one.loc[mask]

    @property
    def rows_after_update(self):
        """
        Identify rows that are present in both DataFrames but have changes in the second DataFrame.
        """
        mask = self._comparison.loc[~self._mask].index
        return self._other.loc[mask]
