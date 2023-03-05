from aiotaipit import helpers


class TestTaipitApi:
    def test_regions(self):
        assert helpers.get_region_name(61) == 'Ростовская область'
        assert helpers.get_region_name(133) == '133'

    def test_model_names(self):
        assert helpers.get_model_name(21) == ('НЕВА', 'МТ 124 (Wi-Fi)')
        assert helpers.get_model_name(0) == (None, '0')
