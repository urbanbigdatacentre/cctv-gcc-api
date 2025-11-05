from datetime import datetime
from typing import Annotated

datetimeStackType = list[Annotated[list[datetime], 2]]


def merge_intervals(intervals: datetimeStackType) -> datetimeStackType:
    # Sort the array on the basis of start values of intervals.
    intervals.sort(key=lambda x: x[0])
    stack = []
    stack.append(list(intervals[0]))
    for i in intervals[1:]:
        i = list(i)
        top = stack[-1]
        # if current interval is not overlapping with stack top,
        # push it to the stack
        if top[1] < i[0]:
            stack.append(i)
        # Otherwise update the ending time of top if ending of current
        # interval is more
        elif top[1] < i[1]:
            top[1] = i[1]
            stack.pop()
            stack.append(top)

    return stack
