Check if two employees work at the same time
--------------------------------------------
Spans make working with intervals of time easy. In this example we want to list all hours where `Alice` and `Bob` work at the same time. 24 hour clock is used, as well as weeks starting on Monday.

.. testcode::

    import re
    from datetime import timedelta
    from spans import timedeltarange, timedeltarangeset


    def str_to_timedeltarange(string):
        """
        Convert a string from the format (HH:MM-HH:MM) into a ``timedeltarange``

        :param string: String time representation in the format HH:MM. Minutes and
                       the leading zero of the hours may be omitted.
        :return: A new ``timedeltarange`` instance
        """

        # NOTE: Error handling left as an exercise for the reader
        match = re.match(
            "^(\d{1,2}):?(\d{1,2})?-(\d{1,2}):?(\d{1,2})?$", string)

        start_hour, start_min = (int(v or 0) for v in match.group(1, 2))
        end_hour, end_min = (int(v or 0) for v in match.group(3, 4))

        return timedeltarange(
            timedelta(hours=start_hour, minutes=start_min),
            timedelta(hours=end_hour, minutes=end_min))


    def timedeltarange_to_str(span):
        """
        Convert a ``timedeltarange`` to a string representation (HH:MM-HH:MM).

        :param span: ``timedeltarange`` to convert
        :return: String representation
        """

        return "{:02}:{:02}-{:02}:{:02}".format(
            span.lower.seconds // 3600,
            (span.lower.seconds // 60) % 60,
            span.upper.seconds // 3600,
            (span.upper.seconds // 60) % 60
        )


    hours_alice = [
        ["8-12", "12:30-17"], # Monday
        ["8-12", "12:30-17"], # Tuesday
        ["8-12", "12:30-17"], # Wednesday
        ["8-12", "12:30-17"], # Thursday
        ["8-12", "12:30-15"], # Friday
        ["10-14"], # Saturday
        [], # Sunday
    ]

    hours_bob = [
        ["15-21"], # Monday
        ["15-21"], # Tuesday
        ["15-21"], # Wednesday
        ["15-21"], # Thursday
        ["12-18"], # Friday
        [], # Saturday
        ["10-14"], # Sunday
    ]


    schedule_alice = timedeltarangeset(
        str_to_timedeltarange(span).offset(timedelta(day))
        for day, spans in enumerate(hours_alice)
        for span in spans)

    schedule_bob = timedeltarangeset(
        str_to_timedeltarange(span).offset(timedelta(day))
        for day, spans in enumerate(hours_bob)
        for span in spans)


    # Print hours where both Alice and Bob work
    day_names = {
        0: "Monday",
        1: "Tuesday",
        2: "Wednesday",
        3: "Thursday",
        4: "Friday",
        5: "Saturday",
        6: "Sunday",
    }
    for span in schedule_alice.intersection(schedule_bob):
        print(u"{: <10} {}".format(
            day_names[span.lower.days],
            timedeltarange_to_str(span)))

This code outputs:

.. testoutput::

    Monday     15:00-17:00
    Tuesday    15:00-17:00
    Wednesday  15:00-17:00
    Thursday   15:00-17:00
    Friday     12:30-15:00
