import yaml
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Optional, List, Dict
from ase.data import atomic_numbers, covalent_radii

@dataclass
class LJParams:
    """Parameters for Lennard-Jones potential."""
    epsilon: float
    sigma: float
    cutoff: float

def generate_default_lj_params(elements: List[str], epsilon: float = 1.0, cutoff_factor: float = 2.5) -> LJParams:
    """
    Generates default Lennard-Jones parameters based on chemical elements.

    Args:
        elements: List of chemical element symbols (e.g., ['Fe', 'C']).
        epsilon: The depth of the potential well in eV. Defaults to 1.0 for stability.
        cutoff_factor: Multiplier for sigma to determine cutoff. Defaults to 2.5.

    Returns:
        LJParams object with calculated sigma and provided epsilon/cutoff.
    """
    if not elements:
        raise ValueError("Cannot generate LJ params: No elements provided.")

    radii = []
    for elem in elements:
        # atomic_numbers is a dict mapping symbol -> int (Z)
        # covalent_radii is an array where index is Z
        z = atomic_numbers.get(elem)
        if z is None:
            raise ValueError(f"Unknown element symbol: {elem}")
        radii.append(covalent_radii[z])

    r_avg = sum(radii) / len(radii)

    # Sigma calculation:
    # We estimate the equilibrium bond distance (r_m) as the sum of diameters?
    # Wait, sum of radii is r_avg * 2?
    # The prompt says: "sigma ... derived from the sum of covalent radii".
    # And: "Compute sigma = 2 * r_avg * 0.8909".
    # If we have multiple elements, "sum of covalent radii" usually implies checking pairs.
    # But the prompt explicitly says: "Compute average radius r_avg. Compute sigma = 2 * r_avg * 0.8909".
    # So we take the average radius of the species present, multiply by 2 (to get a diameter/distance),
    # and then scale by 2^(-1/6) to get sigma.

    sigma = (2 * r_avg) * (2 ** (-1/6))

    cutoff = sigma * cutoff_factor

    return LJParams(epsilon=epsilon, sigma=sigma, cutoff=cutoff)

@dataclass
class Config:
    # ... other params ...
    elements: List[str]
    lj_params: LJParams
    # ... other params ...

    @classmethod
    def from_dict(cls, config_dict: dict[str, Any]) -> "Config":
        # ... existing logic ...

        elements = config_dict.get("elements", [])

        lj_params_data = config_dict.get("lj_params")
        if lj_params_data:
            lj_params = LJParams(**lj_params_data)
        else:
            # Generate defaults if missing
            # We need elements to be present
            if not elements:
                 # If elements are also missing, we can't generate.
                 # Original behavior was empty dict -> fail.
                 # Failing with a clearer message is better, or let it fail downstream.
                 # But sticking to prompt: "if lj_params are missing ... these defaults are used"
                 pass

            # Using the helper function
            # Note: We rely on elements being populated.
            lj_params = generate_default_lj_params(elements)

        return cls(
            # ...
            elements=elements,
            lj_params=lj_params,
            # ...
        )
