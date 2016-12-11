def init(cap, param, selection):
    init_input = None
    step_input = {'computed_selection': selection}
    return init_input, step_input


def step(i, frame, param, init_input, step_input):
    computed_selection = step_input['computed_selection']
    tracked_frame = frame
    step_input = {'computed_selection': computed_selection}
    return tracked_frame, step_input
