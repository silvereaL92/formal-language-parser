NORMAL_STATE = "q"
BACK_STATE = "b"
FINAL_STATE = "f"
ERROR_STATE = "e"


class Parser:
    def __init__(self, input_sequence=""):
        self.result = list()
        self.read()
        self.non_terminals: set = self.result[0]
        self.terminals: set = self.result[1]
        self.start_symbol: str = self.result[2]
        self.transitions: dict = self.result[3]
        self.input_sequence = input_sequence

        self.current_state = NORMAL_STATE
        self.current_symbol_pos = 0
        self.working_stack = list()
        self.input_stack = list()
        self.input_stack.append(self.start_symbol)

    def check(self, sequence=None):
        self.current_state = NORMAL_STATE
        self.current_symbol_pos = 0
        self.working_stack = list()
        self.input_stack = list()
        self.input_stack.append(self.start_symbol)
        if sequence is not None:
            self.input_sequence = sequence

        while self.current_state != ERROR_STATE and self.current_state != FINAL_STATE:
            if self.current_state == NORMAL_STATE and self.current_symbol_pos == len(self.input_sequence) \
                    and len(self.input_stack) == 0:
                self.success()
                self.printall()
            else:
                # noinspection PyBroadException
                try:
                    if self.input_stack[-1] in self.non_terminals and self.current_state == NORMAL_STATE:
                        self.expand()
                        self.printall()
                    else:
                        if self.input_stack[-1] in self.terminals and self.current_state == NORMAL_STATE:
                            if self.current_symbol_pos >= len(self.input_sequence) or \
                                    self.input_stack[-1] != self.input_sequence[self.current_symbol_pos]:
                                self.momentary_insuccess()
                                self.printall()
                            else:
                                self.advance()
                                self.printall()

                        if self.current_state == BACK_STATE:
                            if self.working_stack[-1] in self.terminals:
                                self.back()
                                self.printall()
                            else:
                                self.another_try()
                                self.printall()
                except Exception:
                    self.current_state = ERROR_STATE

        if self.current_state == ERROR_STATE:
            print("Sequence denied")

        if self.current_state == FINAL_STATE:
            print("Sequence accepted")

    def production_for(self, non_terminal):
        if non_terminal not in self.transitions.keys():
            return None
        return self.transitions[non_terminal]

    def expand(self):
        current_non_terminal = self.input_stack.pop()
        self.working_stack.append(
            {
                "symbol": current_non_terminal,
                "production_index": 0
            }
        )
        current_production: list = self.transitions[current_non_terminal][0][:]
        current_production.reverse()
        for symbol in current_production:
            self.input_stack.append(symbol)

    def advance(self):
        self.current_symbol_pos += 1
        self.working_stack.append(self.input_stack.pop())

    def momentary_insuccess(self):
        self.current_state = BACK_STATE

    def back(self):
        self.current_symbol_pos -= 1
        self.input_stack.append(self.working_stack.pop())

    def another_try(self):
        current = self.working_stack.pop()
        current_index = current["production_index"]
        current_symbol = current["symbol"]
        last_production = self.transitions[current_symbol][current_index]
        for i in range(len(last_production)):
            self.input_stack.pop()

        # there is another production
        if current_index + 1 < len(self.transitions[current_symbol]):
            current_index += 1
            self.current_state = NORMAL_STATE
            self.working_stack.append(
                {
                    "symbol": current_symbol,
                    "production_index": current_index
                }
            )
            current_production: list = self.transitions[current_symbol][current_index][:]
            current_production.reverse()
            for sym in current_production:
                self.input_stack.append(sym)
        # no more productions available
        else:
            # back to the start without new productions -> not a match
            if self.current_symbol_pos == 0 and current_symbol == self.start_symbol:
                self.current_state = ERROR_STATE
                return
            self.input_stack.append(current_symbol)

    def success(self):
        self.current_state = FINAL_STATE

    def printall(self):
        print(self.current_state)
        print(self.current_symbol_pos)
        print(self.working_stack)
        print(self.input_stack)

    def read(self):
        with open("grammar.txt", "r") as input_file:
            line = input_file.readline()
            line = line[1:-2]
            non_terminals = line.split(",")
            self.result.append(non_terminals)
            line = input_file.readline()
            line = line[1:-2]
            terminals = line.split(",")
            self.result.append(terminals)
            line = input_file.readline()
            start_symbol = line[:-1]
            if start_symbol not in non_terminals:
                raise Exception("Start symbol is not in the set of non terminals")
            self.result.append(start_symbol)
            transitions = dict()
            for line in input_file:
                line = line.split(";")
                transition_start = line[0]
                transition_destination = line[1]
                transition_destination = transition_destination.split()
                if transition_start not in non_terminals:
                    raise Exception("Production start symbol not in set of non terminals")
                for symbol in transition_destination:
                    if symbol not in non_terminals and symbol not in terminals:
                        raise Exception("Production result symbol not in the set of terminals or non terminals")
                if transition_start not in transitions.keys():
                    transitions[transition_start] = list()
                transitions[transition_start].append(transition_destination)
            self.result.append(transitions)

    def menu(self):
        print("Please select an option:")
        print("1 - non terminals")
        print("2 - terminals")
        print("3 - start symbol")
        print("4 - transitions")
        print("x - exit")
        user_option = None
        while user_option != "x":
            user_option = input()
            if user_option == "1":
                print(self.non_terminals)
                continue
            if user_option == "2":
                print(self.terminals)
                continue
            if user_option == "3":
                print(self.start_symbol)
                continue
            if user_option == "4":
                for key in self.transitions.keys():
                    transition_string = ""
                    for option in self.transitions[key]:
                        for token in option:
                            transition_string += token
                        transition_string += " | "
                    transition_string = transition_string[:-3]
                    print(key, "->", transition_string)
                continue
            if user_option == "5":
                while True:
                    non_terminal = input("input the non terminal you want to see the productions for: ")
                    if non_terminal not in self.non_terminals:
                        print("symbol not in set of non terminals, please try again")
                        continue
                    print(self.production_for(non_terminal))
                    break


if __name__ == "__main__":
    p = Parser("aacbc")
    p.check()
