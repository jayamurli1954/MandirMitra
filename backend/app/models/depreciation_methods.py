"""
Depreciation Calculation Methods
Supports all standard depreciation methods for audit compliance and flexibility
"""

from enum import Enum
from typing import Optional
from datetime import date


class DepreciationMethod(str, Enum):
    """Depreciation methods available in the system"""
    STRAIGHT_LINE = "straight_line"
    WDV = "wdv"  # Written Down Value / Diminishing Balance
    DOUBLE_DECLINING = "double_declining"
    DECLINING_BALANCE = "declining_balance"
    UNITS_OF_PRODUCTION = "units_of_production"
    ANNUITY = "annuity"
    DEPLETION = "depletion"
    SINKING_FUND = "sinking_fund"
    NONE = "none"  # For non-depreciable assets (land, gold, etc.)


class DepreciationCalculator:
    """Calculate depreciation using various methods"""
    
    @staticmethod
    def calculate_straight_line(
        cost: float,
        salvage_value: float,
        useful_life_years: float,
        period_years: float = 1.0
    ) -> float:
        """
        Straight-Line Method
        Formula: (Cost - Salvage Value) / Useful Life
        """
        if useful_life_years <= 0:
            return 0.0
        annual_depreciation = (cost - salvage_value) / useful_life_years
        return annual_depreciation * period_years
    
    @staticmethod
    def calculate_wdv(
        opening_book_value: float,
        depreciation_rate_percent: float,
        period_years: float = 1.0
    ) -> float:
        """
        Written Down Value / Diminishing Balance Method
        Formula: (Book Value × Rate) / 100
        Note: Salvage value not considered
        """
        if opening_book_value <= 0 or depreciation_rate_percent <= 0:
            return 0.0
        return (opening_book_value * depreciation_rate_percent * period_years) / 100
    
    @staticmethod
    def calculate_double_declining(
        opening_book_value: float,
        useful_life_years: float,
        period_years: float = 1.0
    ) -> float:
        """
        Double Declining Balance Method
        Formula: 2 × Beginning Book Value × (100% / Useful Life)
        """
        if useful_life_years <= 0 or opening_book_value <= 0:
            return 0.0
        straight_line_rate = 100.0 / useful_life_years
        double_rate = 2.0 * straight_line_rate
        return (opening_book_value * double_rate * period_years) / 100
    
    @staticmethod
    def calculate_declining_balance(
        opening_book_value: float,
        depreciation_rate_percent: float,
        period_years: float = 1.0
    ) -> float:
        """
        Declining Balance Method
        Formula: Book Value × Depreciation Rate
        Similar to WDV but rate may be different
        """
        if opening_book_value <= 0 or depreciation_rate_percent <= 0:
            return 0.0
        return (opening_book_value * depreciation_rate_percent * period_years) / 100
    
    @staticmethod
    def calculate_units_of_production(
        cost: float,
        salvage_value: float,
        total_estimated_units: float,
        units_produced_this_period: float
    ) -> float:
        """
        Units of Production Method
        Formula: [(Cost - Salvage) / Total Units] × Actual Units
        """
        if total_estimated_units <= 0 or units_produced_this_period <= 0:
            return 0.0
        depreciation_per_unit = (cost - salvage_value) / total_estimated_units
        return depreciation_per_unit * units_produced_this_period
    
    @staticmethod
    def calculate_annuity(
        cost: float,
        salvage_value: float,
        useful_life_years: float,
        interest_rate_percent: float,
        opening_book_value: float,
        period_years: float = 1.0
    ) -> float:
        """
        Annuity Method
        Formula: Annuity = [i × TDA × (1+i)^n] / [(1+i)^n - 1]
        Depreciation = Annuity - (i × Book Value at Start)
        """
        if useful_life_years <= 0 or interest_rate_percent <= 0:
            return 0.0
        
        i = interest_rate_percent / 100.0
        total_depreciable_amount = cost - salvage_value
        n = useful_life_years
        
        # Calculate annuity factor
        if i == 0:
            # If no interest, fall back to straight-line
            return DepreciationCalculator.calculate_straight_line(
                cost, salvage_value, useful_life_years, period_years
            )
        
        annuity_factor = (i * (1 + i) ** n) / ((1 + i) ** n - 1)
        annuity = total_depreciable_amount * annuity_factor
        
        # Depreciation = Annuity - Interest on opening book value
        interest_component = opening_book_value * i * period_years
        depreciation = (annuity * period_years) - interest_component
        
        return max(0.0, depreciation)  # Cannot be negative
    
    @staticmethod
    def calculate_depletion(
        cost: float,
        salvage_value: float,
        total_units_of_resource: float,
        units_extracted_this_period: float
    ) -> float:
        """
        Depletion Method
        Formula: (Cost - Salvage Value) / Total Units × Units Extracted
        Similar to units of production but for natural resources
        """
        if total_units_of_resource <= 0 or units_extracted_this_period <= 0:
            return 0.0
        depletion_per_unit = (cost - salvage_value) / total_units_of_resource
        return depletion_per_unit * units_extracted_this_period
    
    @staticmethod
    def calculate_sinking_fund(
        cost: float,
        salvage_value: float,
        useful_life_years: float,
        interest_rate_percent: float,
        payments_per_year: int = 1
    ) -> float:
        """
        Sinking Fund Method
        Formula: A = [{1+(r/m)}^(n×m) - 1} / (r/m)] × P
        Annual contribution to sinking fund
        """
        if useful_life_years <= 0 or interest_rate_percent <= 0:
            return 0.0
        
        total_depreciable_amount = cost - salvage_value
        r = interest_rate_percent / 100.0
        n = useful_life_years
        m = payments_per_year
        
        if r == 0:
            # If no interest, simple division
            return total_depreciable_amount / (n * m)
        
        # Calculate sinking fund factor
        factor = ((1 + (r / m)) ** (n * m) - 1) / (r / m)
        
        # Periodic contribution
        periodic_contribution = total_depreciable_amount / factor
        
        # Annual depreciation (sum of all payments in a year)
        return periodic_contribution * m
    
    @staticmethod
    def calculate_depreciation(
        method: DepreciationMethod,
        cost: float,
        opening_book_value: float,
        salvage_value: float = 0.0,
        useful_life_years: float = 0.0,
        depreciation_rate_percent: float = 0.0,
        period_years: float = 1.0,
        # For units of production
        total_estimated_units: Optional[float] = None,
        units_produced_this_period: Optional[float] = None,
        # For annuity method
        interest_rate_percent: Optional[float] = None,
        # For sinking fund
        payments_per_year: int = 1
    ) -> float:
        """
        Main calculation method that routes to appropriate depreciation method
        """
        if method == DepreciationMethod.NONE:
            return 0.0
        
        elif method == DepreciationMethod.STRAIGHT_LINE:
            return DepreciationCalculator.calculate_straight_line(
                cost, salvage_value, useful_life_years, period_years
            )
        
        elif method == DepreciationMethod.WDV:
            return DepreciationCalculator.calculate_wdv(
                opening_book_value, depreciation_rate_percent, period_years
            )
        
        elif method == DepreciationMethod.DOUBLE_DECLINING:
            return DepreciationCalculator.calculate_double_declining(
                opening_book_value, useful_life_years, period_years
            )
        
        elif method == DepreciationMethod.DECLINING_BALANCE:
            return DepreciationCalculator.calculate_declining_balance(
                opening_book_value, depreciation_rate_percent, period_years
            )
        
        elif method == DepreciationMethod.UNITS_OF_PRODUCTION:
            if total_estimated_units is None or units_produced_this_period is None:
                raise ValueError("Units of production method requires total_estimated_units and units_produced_this_period")
            return DepreciationCalculator.calculate_units_of_production(
                cost, salvage_value, total_estimated_units, units_produced_this_period
            )
        
        elif method == DepreciationMethod.ANNUITY:
            if interest_rate_percent is None:
                raise ValueError("Annuity method requires interest_rate_percent")
            return DepreciationCalculator.calculate_annuity(
                cost, salvage_value, useful_life_years, interest_rate_percent,
                opening_book_value, period_years
            )
        
        elif method == DepreciationMethod.DEPLETION:
            if total_estimated_units is None or units_produced_this_period is None:
                raise ValueError("Depletion method requires total_estimated_units and units_produced_this_period")
            return DepreciationCalculator.calculate_depletion(
                cost, salvage_value, total_estimated_units, units_produced_this_period
            )
        
        elif method == DepreciationMethod.SINKING_FUND:
            if interest_rate_percent is None:
                raise ValueError("Sinking fund method requires interest_rate_percent")
            return DepreciationCalculator.calculate_sinking_fund(
                cost, salvage_value, useful_life_years, interest_rate_percent, payments_per_year
            )
        
        else:
            raise ValueError(f"Unknown depreciation method: {method}")


# Depreciation rate lookup (as per Income Tax Act - can be customized)
DEPRECIATION_RATES = {
    "buildings": {
        "residential": 5.0,
        "non_residential": 10.0,
        "purely_residential": 5.0
    },
    "vehicles": {
        "motor_cars": 15.0,
        "motor_cycles": 20.0,
        "other_vehicles": 15.0
    },
    "furniture": 10.0,
    "computer": 40.0,
    "machinery": 15.0,
    "electrical_installations": 10.0,
    "plumbing": 10.0,
    "sound_lighting": 15.0
}


