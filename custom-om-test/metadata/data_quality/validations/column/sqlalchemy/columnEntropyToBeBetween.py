
from itertools import chain

from sqlalchemy import Column, inspect
from scipy import stats

from metadata.data_quality.validations.base_test_handler import BaseTestValidator
from metadata.generated.schema.tests.basic import TestCaseResult, TestResultValue
from metadata.utils.entity_link import get_decoded_column

class ColumnEntropyToBeBetweenValidator(BaseTestValidator):
    """Implements custom test validator for OpenMetadata.

    Args:
        BaseTestValidator (_type_): inherits from BaseTestValidator
    """

    def _get_column_name(self) -> Column:
        """get column name from the test case entity link

        Returns:
            Column: column
        """
        column = get_decoded_column(self.test_case.entityLink.__root__)
        columns = inspect(self.runner.table).c
        column_obj = next(
            (col for col in columns if col.name == column),
            None,
        )
        if column_obj is None:
            raise ValueError(f"Cannot find column {column}")
        return column_obj


    def run_validation(self) -> TestCaseResult:
        """Run test validation"""
        rows = self.runner.select_all_from_table(self._get_column_name())
        list_of_values = list(chain.from_iterable(rows))
        entropy = stats.entropy(list_of_values)

        min_bound = self.get_min_bound("minEntropy")
        max_bound = self.get_max_bound("maxEntropy")

        return self.get_test_case_result_object(
            self.execution_date,
            self.get_test_case_status(min_bound <= entropy <= max_bound),
            f"Found entropy={entropy} vs. the expected  min={min_bound} and max={max_bound}].",
            [TestResultValue(name="entropy", value=str(entropy))],
        )

