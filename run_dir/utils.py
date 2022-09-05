from astropy.time import Time, TimeDelta


def get_start_time(ra0_deg, length_sec):
    """Returns optimal start time for field RA and observation length."""
    t = Time("2000-01-01 00:00:00", scale="utc", location=("116.764d", "0d"))
    dt_hours = (24.0 - t.sidereal_time("apparent").hour) / 1.0027379
    dt_hours += ra0_deg / 15.0
    start = t + TimeDelta(dt_hours * 3600.0 - length_sec / 2.0, format="sec")
    return start.value
