import paml_check.convert_constraints as pcc
from paml_check.constraints import binary_temporal_constraint
import pysmt
import pysmt.shortcuts
import uml

class DurationConstraintException(Exception):
    pass

def convert_duration_constraint(converter: 'pcc.ConstraintConverter',
                                constraint: uml.DurationConstraint):
    """
    Convert a uml.DurationConstraint into the pysmt equivalent

    If one constraint element is provided:
        Ignore firstEventValue and assume the duration is from the
        start of the event to the end of the event. This assumes that
        since a single element can only have a start or end event that
        it must be the case that the duration specified for the single
        provided element is between those two events.
    
    If two constraint elements are provided:
        If zero firstEventValues are provided:
            Assume the duration is from the end of the first element
            to the start of the second element.
        If one firstEventValue is provided:
            Assume the duration in from the {start|end} of the first
            event to the same event of the second element
        If two firstEventValues are provided:
            Assume the duration in from the {start|end} of the first
            event to the {start|end} of the second element (consuming
            the firstEventValues in index order)
    """
    start, end = get_start_and_end(converter, constraint)

    # collect min and max duration
    duration_interval = constraint.specification
    min_duration = converter.time_measure_to_seconds(get_min_duration(duration_interval))
    max_duration = converter.time_measure_to_seconds(get_max_duration(duration_interval))

    clause = binary_temporal_constraint(
        pysmt.shortcuts.Symbol(start.name, pysmt.shortcuts.REAL),
        [[min_duration, max_duration]],
        pysmt.shortcuts.Symbol(end.name, pysmt.shortcuts.REAL))
    return clause

def get_min_duration(duration_interval: uml.DurationInterval):
    """
    Extract the TimeMeasure object for the min duration of a DurationInterval
    """
    try:
        return duration_interval.min.expr.expr
    except Exception as e:
        raise DurationConstraintException(f"Failed to read min duration from {duration_interval.identity}: {e}")

def get_max_duration(duration_interval: uml.DurationInterval):
    """
    Extract the TimeMeasure object for the max duration of a DurationInterval
    """
    try:
        return duration_interval.max.expr.expr
    except Exception as e:
        raise DurationConstraintException(f"Failed to read max duration from {duration_interval.identity}: {e}")

def get_start_and_end(converter: 'pcc.ConstraintConverter', constraint: uml.DurationConstraint):
    ce = constraint.constrained_elements
    num_elements = len(ce)
    if not 1 <= num_elements <= 2:
        # TODO better error messaging
        raise DurationConstraintException("Expected a constrainted_element count of 1 or 2")

    for i, elt in enumerate(ce):
        if elt.index == 0:
            first = elt
            first_idx = i
        if elt.index == 1 or num_elements == 1:
            second = elt
            second_idx = i

    first_vars = converter.time_constraints.identity_to_time_variables(first.property_value)
    second_vars = converter.time_constraints.identity_to_time_variables(second.property_value)
    
    # defaults
    start_of_first = True
    start_of_second = False

    # in the case of two elements we may adjust which events we use
    if num_elements == 2:
        num_event_spec = len(constraint.firstEvent)
        if num_event_spec == 0:
            start_of_first = False
            start_of_second = True
        elif num_event_spec >= 1 and num_event_spec <= 2:
            for i, elt in enumerate(constraint.firstEvent):
                if elt.index == 0:
                    start_of_first = elt.property_value.value
                if elt.index == 1:
                    start_of_second = elt.property_value.value
        else:
            raise DurationConstraintException("Expected a firstEvent count of 0 or 1 or 2")

    start = first_vars.start if start_of_first else first_vars.end
    end = second_vars.start if start_of_second else second_vars.end
    return start, end
