def init(cap, param):
    init_input = None
    step_input = None
    return init_input, step_input


def step(i, frame, param, init_input, step_input):
    filtered_frame = frame
    step_input = None
    return filtered_frame, step_input
