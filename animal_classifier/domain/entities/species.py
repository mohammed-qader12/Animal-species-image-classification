from dataclasses import dataclass

@dataclass(frozen=True)
class Species:
    """
    Represents an animal species category.
    """
    id: int
    name: str          # The directory name (e.g., 'panthera-tigris')
    common_name: str   # Human readable name (e.g., 'Tiger')
