class StateManager:
    def __init__(self):
        self.history = []
        self.current_state = -1

    def save_state(self, state):
        self.history = self.history[:self.current_state + 1]
        self.history.append(state)
        self.current_state += 1

    def undo(self):
        if self.current_state > 0:
            self.current_state -= 1
            return self.history[self.current_state]
        return None

    def redo(self):
        if self.current_state < len(self.history) - 1:
            self.current_state += 1
            return self.history[self.current_state]
        return None
