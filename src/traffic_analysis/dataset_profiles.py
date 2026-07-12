"""Dataset-specific semantics used to configure the GUI safely."""
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class DatasetProfile:
    kind: str = "Traffic observation"
    unit: str = "value"
    start_date: str | None = None
    zero_as_missing: bool = False
    z_threshold: float = 3.0
    note: str = "No reliable absolute start date is available; relative day labels are used."
    entity: str = "Road"


def profile_for(path) -> DatasetProfile:
    source = str(Path(path)).replace("\\", "/").lower()
    name = Path(path).name.lower()
    if "guangzhou" in source:
        return DatasetProfile("Speed", "km/h", "2016-08-01", True, 3.0,
                              "10-minute speeds; zeros represent missing observations.", "Road")
    if "birmingham" in source:
        return DatasetProfile("Parking occupancy", "vehicles", "2016-10-04", False, 3.5,
                              "Parking records from 2016-10-04 to 2016-12-19; zero can be valid.", "Car park")
    if "california" in source:
        return DatasetProfile("Speed", "speed value", None, True, 3.0,
                              "Seven days with 288 five-minute slots per day; absolute dates are unavailable.", "Road")
    if "energy" in source:
        return DatasetProfile("Electricity demand", "demand", None, False, 4.0,
                              "Hourly electricity demand; zero can be a valid observation.", "Client")
    if "hangzhou" in source:
        return DatasetProfile("Passenger flow", "passengers", None, False, 4.0,
                              "Metro passenger flow; zero can mean no passengers in that slot.", "Station")
    if "ngsim" in source:
        return DatasetProfile("Speed", "m/s", None, "missing" in name, 3.0,
                              "Files containing 'missing' use zero as an artificial missing-value marker.", "Vehicle trajectory")
    if "nyc" in source:
        return DatasetProfile("Taxi trip volume", "trips", None, False, 4.0,
                              "Zero can mean no trips for an OD pair in that time slot.", "OD pair")
    if "portland" in source:
        if "speed" in name:
            return DatasetProfile("Speed", "speed value", None, True, 3.0,
                                  "Speed matrix; zero is treated as a sensor gap by default.", "Detector")
        if "volume" in name:
            return DatasetProfile("Traffic volume", "vehicles", None, False, 4.0,
                                  "A zero traffic count can be valid.", "Detector")
        return DatasetProfile("Road occupancy", "occupancy", None, False, 3.5,
                              "Zero occupancy can be valid.", "Detector")
    if "temperature" in source:
        return DatasetProfile("Temperature", "temperature", None, False, 3.5,
                              "A zero temperature is a valid measurement.", "Location")
    if "pems" in source:
        return DatasetProfile("Speed", "speed value", None, True, 3.0,
                              "PeMS speed data; zero is treated as missing by default.", "Detector")
    if "seattle" in source:
        return DatasetProfile("Speed", "speed value", None, True, 3.0,
                              "Seattle speed data; the current files do not contain an exact start date.", "Detector")
    return DatasetProfile()
