import unittest
from src.core.config import Config, LJParams, generate_default_lj_params
from ase.data import atomic_numbers, covalent_radii

class TestConfig(unittest.TestCase):
    def test_explicit_lj_params(self):
        config_data = {
            "elements": ["Fe", "C"],
            "lj_params": {
                "epsilon": 0.5,
                "sigma": 2.0,
                "cutoff": 5.0
            }
        }
        config = Config.from_dict(config_data)
        self.assertEqual(config.lj_params.epsilon, 0.5)
        self.assertEqual(config.lj_params.sigma, 2.0)
        self.assertEqual(config.lj_params.cutoff, 5.0)

    def test_generated_lj_params(self):
        """Test that lj_params are generated correctly when missing."""
        elements = ["Fe", "C"]
        config_data = {
            "elements": elements
        }
        config = Config.from_dict(config_data)

        # Calculate expected values manually
        r_fe = covalent_radii[atomic_numbers["Fe"]]
        r_c = covalent_radii[atomic_numbers["C"]]
        r_avg = (r_fe + r_c) / 2
        expected_sigma = (2 * r_avg) * (2 ** (-1/6))
        expected_cutoff = 2.5 * expected_sigma

        self.assertAlmostEqual(config.lj_params.epsilon, 1.0)
        self.assertAlmostEqual(config.lj_params.sigma, expected_sigma)
        self.assertAlmostEqual(config.lj_params.cutoff, expected_cutoff)

    def test_single_element(self):
        """Test generation with a single element."""
        elements = ["Ar"]
        config_data = {"elements": elements}
        config = Config.from_dict(config_data)

        r_ar = covalent_radii[atomic_numbers["Ar"]]
        expected_sigma = (2 * r_ar) * (2 ** (-1/6))

        self.assertAlmostEqual(config.lj_params.sigma, expected_sigma)

    def test_missing_elements_raises_error(self):
        """Test that missing elements when lj_params is also missing raises ValueError."""
        config_data = {} # No elements, no lj_params
        with self.assertRaisesRegex(ValueError, "No elements provided"):
            Config.from_dict(config_data)

    def test_invalid_element(self):
        config_data = {"elements": ["Unobtanium"]}
        with self.assertRaisesRegex(ValueError, "Unknown element symbol"):
            Config.from_dict(config_data)

if __name__ == "__main__":
    unittest.main()
