import logging
import datetime
import pytz

import qscollect.collectors.omnifocus.helpers as h


def TreeDeltaCalculator(left, right, state, debug=False):
    left_keys = left.keys()
    right_keys = right.keys()

    left_keys.sort()
    right_keys.sort()

    left_index = 0
    right_index = 0

    for left_key, right_key in zip(left_keys, right_keys):
        left[left_key] = h.normalize_date(left[left_key])
        right[right_key] = h.normalize_date(right[right_key])


    while left_index < len(left_keys) and right_index < len(right_keys):
        left_key, right_key = left_keys[left_index], right_keys[right_index]

        if left_key == right_key:
            # Same object, calculate difference, add to delta

            if left[left_key] != right[right_key]:
                # If they are not equal, calculate the delta
                state.update(left_key, left[left_key], right[right_key])

            left_index, right_index = left_index + 1, right_index + 1
        elif right_index +1 < len(right_keys) and left_key == right_keys[right_index + 1]:
            # Right key is a new task, add to delta
            state.add(right_key, right[right_key])
            right_index += 1
        elif left_index + 1 < len(left_keys) and right_key == left_keys[left_index + 1]:
            # Left key has been deleted from the right tree
            state.delete(left_key, left[left_key])
            left_index += 1
        else:
            logging.error("Delta Calculator is not working the way it is supposed to")
            left_index += 1

    if left_index < len(left_keys):
        # additional deleted items at end of list
        while left_index < len(left_keys):
            left_key = left_keys[left_index]
            state.delete(left_key, left[left_key])
            left_index += 1

    if right_index < len(right_keys):
        # Additional new items at end of list
        while right_index < len(right_keys):
            right_key = right_keys[right_index]
            state.add(right_key, right[right_key])
            right_index += 1

    return state.changes
