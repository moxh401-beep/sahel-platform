class SaudiCodeValidator:
    """
    A class to validate compliance with the Saudi Building Code.
    """

    def __init__(self, building_design):
        """
        Initialize the validator with the building design data.
        Args:
            building_design (dict): A dictionary containing building design parameters.
        """
        self.building_design = building_design

    def validate(self):
        """
        Validate the building design against the Saudi Building Code.
        Returns:
            bool: True if compliant, False otherwise.
        """
        # Example checks (to be replaced with actual compliance checks)
        compliant = True

        # Check height
        if self.building_design.get('height') > 30:
            compliant = False

        # Check area
        if self.building_design.get('area') > 500:
            compliant = False

        return compliant

    def get_errors(self):
        """
        Get errors if the building is non-compliant.
        Returns:
            list: List of errors found.
        """
        errors = []

        # Example error checks
        if self.building_design.get('height') > 30:
            errors.append('Height exceeds the limit.')

        if self.building_design.get('area') > 500:
            errors.append('Area exceeds the limit.')

        return errors
