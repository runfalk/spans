Check if two employees work at the same time
--------------------------------------------
Spans make working with intervals of time easy. In this example we want to list all hours where `Alice` and `Bob` work at the same time. 24 hour clock is used, as well as weeks starting on Monday.

.. testcode::

    import re
    from datetime import timedelta
    from spans import timedeltarange, timedeltarangeset

    alice = [
        ["8-12", "12:30-17"], # Monday
        ["8-12", "12:30-17"], # Tuesday
        ["8-12", "12:30-17"], # Wednesday
        ["8-12", "12:30-17"], # Thursday
        ["8-12", "12:30-15"], # Friday
        ["10-14"], # Saturday
        [], # Sunday
    ]

    bob = [
        ["15-21"], # Monday
        ["15-21"], # Tuesday
        ["15-21"], # Wednesday
        ["15-21"], # Thursday
        ["12-18"], # Friday
        [], # Saturday
        ["10-14"], # Sunday
    ]

    # Convert the data to timedeltarange
    def str_to_timedelta_range(string):
        # Error handling left as an excersize for the reader
        match = re.match(
            "^(\d{1,2}):?(\d{1,2})?-(\d{1,2}):?(\d{1,2})?$", string)

        return timedeltarange(
            timedelta(hours=int(match.group(1) or 0), minutes=int(match.group(2) or 0)),
            timedelta(hours=int(match.group(3) or 0), minutes=int(match.group(4) or 0)))

    schedule_alice = timedeltarangeset(
        str_to_timedelta_range(span).offset(timedelta(day))
        for day, spans in enumerate(alice)
        for span in spans)

    schedule_bob = timedeltarangeset(
        str_to_timedelta_range(span).offset(timedelta(day))
        for day, spans in enumerate(bob)
        for span in spans)

    # Print hours where both Alice and Bob work
    for span in schedule_alice.intersection(schedule_bob):
        print("%-9s %02d:%02d-%02d:%02d" % (
            {
                0: "Monday",
                1: "Tuesday",
                2: "Wednesday",
                3: "Thursday",
                4: "Friday",
                5: "Saturday",
                6: "Sunday",
            }[span.lower.days],
            span.lower.seconds // 3600,
            (span.lower.seconds // 60) % 60,
            span.upper.seconds // 3600,
            (span.upper.seconds // 60) % 60,
        ))

This code outputs:

.. testoutput::

    Monday    15:00-17:00
    Tuesday   15:00-17:00
    Wednesday 15:00-17:00
    Thursday  15:00-17:00
    Friday    12:30-15:00
