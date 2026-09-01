from apps.pricing.constants import MakingFeeType


class TestMakingFeeType:

    def test_fixed_value(self):
        assert MakingFeeType.FIXED == "FIXED"

    def test_percentage_value(self):
        assert MakingFeeType.PERCENTAGE == "PERCENTAGE"

    def test_supported_values(self):
        assert {
            MakingFeeType.FIXED,
            MakingFeeType.PERCENTAGE,
        } == {
            "FIXED",
            "PERCENTAGE",
        }