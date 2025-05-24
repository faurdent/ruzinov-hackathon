import streamlit as st
from calendar import monthcalendar

SPACE_HEATER_KW = 1.50
HVAC_UNIT_KW = 3.00
INCANDESCENT_BULB_KW = 0.06

HEATER_COVERAGE_M2 = 14
HVAC_COVERAGE_M2 = 37

EFFICIENCY_MULTIPLIER = {
    "A": 1.00,
    "B": 1.20,
    "C": 1.40,
}

P_FORGET_LIGHTS = 0.10
P_FORGET_HEATER = 0.05
P_WINDOW_OPEN = 0.10
WINDOW_PENALTY = 0.10

WORK_HOURS_PER_DAY = 8

LED_BULB_KW_SM           = 0.010   
SPACE_HEATER_KW_SM       = 1.50    
HVAC_UNIT_KW_SM          = 3.00    

HEATER_COVERAGE_M2_SM    = 14       
HVAC_COVERAGE_M2_SM      = 37

EFFICIENCY_MULTIPLIER_SM = {'A': 1.00,
                            'B': 1.15,  
                            'C': 1.30}

P_FORGET_LIGHTS_SM       = 0.01  
P_FORGET_HVAC_SM         = 0.005  
P_WINDOW_OPEN_SM         = 0.05   
WINDOW_PENALTY_SM        = 0.10

OCCUPANCY_DUTY_LIGHTS_SM = 0.90 
      

WORK_HOURS_PER_DAY_SM    = 8

from calendar import monthcalendar

def weekdays_in_month_sm(year: int, month: int) -> int:
    """Monday-to-Friday days in the month (v2 helper)."""
    return sum(1 for wk in monthcalendar(year, month) for d in wk[:5] if d)

def days_in_month_sm(year: int, month: int) -> int:
    """Length of the given calendar month (v2 helper)."""
    return max(d for wk in monthcalendar(year, month) for d in wk)


def smart_monthly_energy_usage(*,
                               n_heaters: int,
                               n_hvac: int,
                               area_m2: float,
                               n_leds: int,
                               season: str,              # "winter" | "summer"
                               efficiency_class: str,    # "A" | "B" | "C"
                               hvac_hours_per_day: int,   # e.g. 6 or 7
                               year: int,
                               month: int,
                               lights_on_duty: float = OCCUPANCY_DUTY_LIGHTS_SM
                               ) -> float:
    """
    kWh for one month of operation with smart controls.
    """

    # -- calendar -------------------------------------------------------------
    workdays   = weekdays_in_month_sm(year, month)
    total_days = days_in_month_sm(year, month)
    weekends   = total_days - workdays
    off_hours  = 24 - WORK_HOURS_PER_DAY_SM
    off_hours_hvac = 24 - hvac_hours_per_day

    # -- envelope -------------------------------------------------------------
    envelope = EFFICIENCY_MULTIPLIER_SM[efficiency_class.upper()]

    # -- lighting -------------------------------------------------------------
    light_kw = n_leds * LED_BULB_KW_SM

    kwh_lights_work = (light_kw * WORK_HOURS_PER_DAY_SM *
                       workdays * lights_on_duty)

    kwh_lights_forget = (light_kw * off_hours *
                         workdays * P_FORGET_LIGHTS_SM)

    kwh_lights_weekend = (light_kw * 24 * weekends *
                          (P_FORGET_LIGHTS_SM / 2))

    kwh_lighting = (kwh_lights_work +
                    kwh_lights_forget +
                    kwh_lights_weekend)

    if season.lower() == "winter":
        base_kw   = n_heaters * SPACE_HEATER_KW_SM
        cover_kw  = (area_m2 / HEATER_COVERAGE_M2_SM) * SPACE_HEATER_KW_SM
    else:  # summer
        base_kw   = n_hvac * HVAC_UNIT_KW_SM
        cover_kw  = (area_m2 / HVAC_COVERAGE_M2_SM) * HVAC_UNIT_KW_SM

    duty = 0.0 if base_kw == 0 else min(1.0, cover_kw / base_kw)

    core_use = base_kw * duty * hvac_hours_per_day * workdays

    window_loss = core_use * P_WINDOW_OPEN_SM * WINDOW_PENALTY_SM

    kwh_forget = (base_kw * duty * off_hours_hvac *
                  workdays * P_FORGET_HVAC_SM)

    kwh_weekend = (base_kw * duty * 24 * weekends *
                   (P_FORGET_HVAC_SM / 2))

    kwh_hvac_heat = ((core_use + window_loss +
                      kwh_forget + kwh_weekend) * envelope)

    return kwh_lighting + kwh_hvac_heat


def weekdays_in_month(year: int, month: int) -> int:
    """Count Monday–Friday days in the given calendar month."""
    return sum(
        1
        for week in monthcalendar(year, month)
        for day in week[:5]
        if day != 0
    )


def days_in_month(year: int, month: int) -> int:
    """Total number of days in the calendar month."""
    return max(day for week in monthcalendar(year, month) for day in week)

def monthly_energy_usage(
    *,
    n_heaters: int,
    n_hvac: int,
    area_m2: float,
    n_bulbs: int,
    season: str,
    efficiency_class: str,
    year: int,
    month: int,
) -> float:
    """Return total electricity consumption for the specified month (kWh)."""

    # calendar stats
    workdays = weekdays_in_month(year, month)
    total_days = days_in_month(year, month)
    weekends = total_days - workdays
    off_hours = 24 - WORK_HOURS_PER_DAY

    envelope = EFFICIENCY_MULTIPLIER[efficiency_class.upper()]

    # lighting
    light_kw = n_bulbs * INCANDESCENT_BULB_KW
    kwh_lights_work = light_kw * WORK_HOURS_PER_DAY * workdays
    kwh_lights_forget = light_kw * off_hours * workdays * P_FORGET_LIGHTS
    kwh_lights_weekend = light_kw * 24 * weekends * (P_FORGET_LIGHTS / 2)
    kwh_lighting = kwh_lights_work + kwh_lights_forget + kwh_lights_weekend

    # heating / cooling
    if season.lower() == "winter":
        base_kw = n_heaters * SPACE_HEATER_KW
        cover_kw = (area_m2 / HEATER_COVERAGE_M2) * SPACE_HEATER_KW
    else:
        base_kw = n_hvac * HVAC_UNIT_KW
        cover_kw = (area_m2 / HVAC_COVERAGE_M2) * HVAC_UNIT_KW

    if base_kw == 0:
        duty = 0.0
    else:
        duty = min(1.0, cover_kw / base_kw)

    kwh_core = base_kw * duty * WORK_HOURS_PER_DAY * workdays
    kwh_window_loss = kwh_core * P_WINDOW_OPEN * WINDOW_PENALTY
    kwh_forget = base_kw * duty * off_hours * workdays * P_FORGET_HEATER
    kwh_weekend = base_kw * duty * 24 * weekends * (P_FORGET_HEATER / 2)

    kwh_hvac_heat = (kwh_core + kwh_window_loss + kwh_forget + kwh_weekend) * envelope

    return kwh_lighting + kwh_hvac_heat

st.title("Electric Consumption Estimator")

with st.form("energy_form"):
    area_m2 = st.number_input("Room size (m²)", min_value=1)
    n_bulbs = st.number_input("Number of Bulbs", min_value=0)
    n_heaters = st.number_input("Number of Space Heaters", min_value=0)
    n_hvac = st.number_input("Number of HVAC Units", min_value=0)
    season = st.selectbox("Season", ["winter", "summer"])
    efficiency_class = st.selectbox("Building Efficiency Class", list(EFFICIENCY_MULTIPLIER.keys()))
    year = st.number_input("Year", min_value=2000, max_value=2100, value=2025)
    month = st.number_input("Month", min_value=1, max_value=12, value=1)

    submitted = st.form_submit_button("Calculate")

if submitted:
    kwh = monthly_energy_usage(
        n_heaters=n_heaters,
        n_hvac=n_hvac,
        area_m2=area_m2,
        n_bulbs=n_bulbs,
        season=season,
        efficiency_class=efficiency_class,
        year=year,
        month=month,
    )
    kwh_smart = smart_monthly_energy_usage(
        n_heaters=n_heaters,
        n_hvac=n_hvac,
        area_m2=area_m2,
        n_leds=n_bulbs,            
        season=season,
        efficiency_class=efficiency_class,
        hvac_hours_per_day=6, 
        year=2025,
        month=1
    )
    st.subheader("Estimated Monthly Consumption")
    
    st.write(f"{kwh:.1f} kWh")

    st.subheader("Estimated Monthly Optimized")

    st.write(f"{kwh_smart:.1f} kWh")
