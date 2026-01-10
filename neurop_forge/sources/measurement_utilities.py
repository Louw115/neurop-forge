"""
Copyright © 2026 Lourens Wasserman. All Rights Reserved.
Neurop Block Forge - https://neurop-forge.com
Commercial use requires a license. See LICENSE file.
"""

"""
Measurement Utilities - Pure functions for unit conversions and measurements.
All functions are pure, deterministic, and atomic.
"""

def meters_to_feet(meters: float) -> float:
    """Convert meters to feet."""
    return meters * 3.28084


def feet_to_meters(feet: float) -> float:
    """Convert feet to meters."""
    return feet / 3.28084


def miles_to_kilometers(miles: float) -> float:
    """Convert miles to kilometers."""
    return miles * 1.60934


def kilometers_to_miles(km: float) -> float:
    """Convert kilometers to miles."""
    return km / 1.60934


def inches_to_centimeters(inches: float) -> float:
    """Convert inches to centimeters."""
    return inches * 2.54


def centimeters_to_inches(cm: float) -> float:
    """Convert centimeters to inches."""
    return cm / 2.54


def yards_to_meters(yards: float) -> float:
    """Convert yards to meters."""
    return yards * 0.9144


def meters_to_yards(meters: float) -> float:
    """Convert meters to yards."""
    return meters / 0.9144


def pounds_to_kilograms(pounds: float) -> float:
    """Convert pounds to kilograms."""
    return pounds * 0.453592


def kilograms_to_pounds(kg: float) -> float:
    """Convert kilograms to pounds."""
    return kg / 0.453592


def ounces_to_grams(ounces: float) -> float:
    """Convert ounces to grams."""
    return ounces * 28.3495


def grams_to_ounces(grams: float) -> float:
    """Convert grams to ounces."""
    return grams / 28.3495


def fahrenheit_to_celsius(f: float) -> float:
    """Convert Fahrenheit to Celsius."""
    return (f - 32) * 5 / 9


def celsius_to_fahrenheit(c: float) -> float:
    """Convert Celsius to Fahrenheit."""
    return c * 9 / 5 + 32


def kelvin_to_celsius(k: float) -> float:
    """Convert Kelvin to Celsius."""
    return k - 273.15


def celsius_to_kelvin(c: float) -> float:
    """Convert Celsius to Kelvin."""
    return c + 273.15


def gallons_to_liters(gallons: float) -> float:
    """Convert US gallons to liters."""
    return gallons * 3.78541


def liters_to_gallons(liters: float) -> float:
    """Convert liters to US gallons."""
    return liters / 3.78541


def cups_to_milliliters(cups: float) -> float:
    """Convert cups to milliliters."""
    return cups * 236.588


def milliliters_to_cups(ml: float) -> float:
    """Convert milliliters to cups."""
    return ml / 236.588


def tablespoons_to_milliliters(tbsp: float) -> float:
    """Convert tablespoons to milliliters."""
    return tbsp * 14.7868


def teaspoons_to_milliliters(tsp: float) -> float:
    """Convert teaspoons to milliliters."""
    return tsp * 4.92892


def square_feet_to_square_meters(sqft: float) -> float:
    """Convert square feet to square meters."""
    return sqft * 0.092903


def square_meters_to_square_feet(sqm: float) -> float:
    """Convert square meters to square feet."""
    return sqm / 0.092903


def acres_to_hectares(acres: float) -> float:
    """Convert acres to hectares."""
    return acres * 0.404686


def hectares_to_acres(hectares: float) -> float:
    """Convert hectares to acres."""
    return hectares / 0.404686


def mph_to_kmh(mph: float) -> float:
    """Convert miles per hour to kilometers per hour."""
    return mph * 1.60934


def kmh_to_mph(kmh: float) -> float:
    """Convert kilometers per hour to miles per hour."""
    return kmh / 1.60934


def knots_to_kmh(knots: float) -> float:
    """Convert knots to kilometers per hour."""
    return knots * 1.852


def kmh_to_knots(kmh: float) -> float:
    """Convert kilometers per hour to knots."""
    return kmh / 1.852


def pascals_to_psi(pascals: float) -> float:
    """Convert pascals to PSI."""
    return pascals * 0.000145038


def psi_to_pascals(psi: float) -> float:
    """Convert PSI to pascals."""
    return psi / 0.000145038


def bar_to_psi(bar: float) -> float:
    """Convert bar to PSI."""
    return bar * 14.5038


def psi_to_bar(psi: float) -> float:
    """Convert PSI to bar."""
    return psi / 14.5038


def bytes_to_kilobytes(bytes_val: int) -> float:
    """Convert bytes to kilobytes."""
    return bytes_val / 1024


def bytes_to_megabytes(bytes_val: int) -> float:
    """Convert bytes to megabytes."""
    return bytes_val / (1024 * 1024)


def bytes_to_gigabytes(bytes_val: int) -> float:
    """Convert bytes to gigabytes."""
    return bytes_val / (1024 * 1024 * 1024)


def kilobytes_to_bytes(kb: float) -> int:
    """Convert kilobytes to bytes."""
    return int(kb * 1024)


def megabytes_to_bytes(mb: float) -> int:
    """Convert megabytes to bytes."""
    return int(mb * 1024 * 1024)


def gigabytes_to_bytes(gb: float) -> int:
    """Convert gigabytes to bytes."""
    return int(gb * 1024 * 1024 * 1024)


def format_bytes(bytes_val: int) -> str:
    """Format bytes to human readable."""
    if bytes_val < 1024:
        return f"{bytes_val} B"
    elif bytes_val < 1024 * 1024:
        return f"{bytes_val / 1024:.2f} KB"
    elif bytes_val < 1024 * 1024 * 1024:
        return f"{bytes_val / (1024 * 1024):.2f} MB"
    else:
        return f"{bytes_val / (1024 * 1024 * 1024):.2f} GB"


def radians_to_degrees(radians: float) -> float:
    """Convert radians to degrees."""
    import math
    return radians * 180 / math.pi


def degrees_to_radians(degrees: float) -> float:
    """Convert degrees to radians."""
    import math
    return degrees * math.pi / 180
