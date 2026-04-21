from fuel2power.calc import compute_required_fuel_energy

def test_compute_required_fuel_energy():
    # target 100 kW for 10 h/day => 1000 kWh/day
    # at 8,000 BTU/kWh => 8,000,000 BTU/day
    req = compute_required_fuel_energy(target_operating_kw=100, hours_per_day=10, heat_rate_btu_per_kwh=8000)
    assert abs(req.required_kwh_per_day - 1000) < 1e-6
    assert abs(req.required_btu_per_day - 8_000_000) < 1e-6
