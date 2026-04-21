
from fuel2power.calc import compute_power

def test_compute_power_basic():
    # 8,000 BTU/kWh, 8,000,000 BTU/day -> 1,000 kWh/day
    pr = compute_power(btu_per_day=8_000_000, heat_rate_btu_per_kwh=8_000, hours_per_day=10)
    assert abs(pr.kwh_per_day - 1000) < 1e-6
    assert abs(pr.avg_kw_24h - (1000/24)) < 1e-6
    assert abs(pr.operating_kw - (1000/10)) < 1e-6
