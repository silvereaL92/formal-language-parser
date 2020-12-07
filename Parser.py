import string

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
        self.input_sequence = input_sequence.translate({ord(c): None for c in string.whitespace})

        self.current_state = NORMAL_STATE
        self.current_symbol_pos = 0
        self.working_stack = list()
        self.input_stack = list()
        self.input_stack.append(self.start_symbol)

    def check_input_not_equal(self):
        return self.current_symbol_pos >= len(self.input_sequence) or \
               self.input_stack[-1] != self.input_sequence.strip()[
                                       self.current_symbol_pos:
                                       self.current_symbol_pos + len(self.input_stack[-1])]

    def check(self, sequence=None):
        self.current_state = NORMAL_STATE
        self.current_symbol_pos = 0
        self.working_stack = list()
        self.input_stack = list()
        self.input_stack.append(self.start_symbol)
        if sequence is not None:
            self.input_sequence = sequence.translate({ord(c): None for c in string.whitespace})

        while self.current_state != ERROR_STATE and self.current_state != FINAL_STATE:
            if self.current_state == NORMAL_STATE and self.current_symbol_pos == len(self.input_sequence) \
                    and len(self.input_stack) == 0:
                self.success()
            else:
                # noinspection PyBroadException
                try:
                    if self.input_stack[-1] in self.non_terminals and self.current_state == NORMAL_STATE:
                        self.expand()
                    else:
                        if self.input_stack[-1] in self.terminals and self.current_state == NORMAL_STATE:
                            if self.check_input_not_equal():
                                self.momentary_insuccess()
                            else:
                                self.advance()

                        if self.current_state == BACK_STATE:
                            if self.working_stack[-1] in self.terminals:
                                self.back()
                            else:
                                self.another_try()
                except Exception:
                    self.current_state = ERROR_STATE

        if self.current_state == ERROR_STATE:
            with open("out1.txt", "w") as out:
                out.writelines("Sequence denied\n")

        if self.current_state == FINAL_STATE:
            table = self.table()
            with open("out1.txt", "w") as out:
                out.writelines("Sequence accepted\n")
                for row in table:
                    out.writelines(str(row))
                    out.writelines("\n")

    def table(self):
        used_productions = list()
        for el in self.working_stack:
            if type(el) is dict:
                used_productions.append(el)

        table = list()
        table.append([0, self.start_symbol, None, None])

        current_state = [[self.start_symbol, 0]]
        univ_idx = 1
        for el in used_productions:
            for idx, element in enumerate(current_state):
                symbol = element[0]
                symbol_idx = element[1]
                production_index = el["production_index"]
                if symbol in self.non_terminals:
                    production = list()
                    sibling = None
                    for prod in self.transitions[symbol][production_index]:
                        table.append([univ_idx, prod, symbol_idx, sibling])
                        sibling = univ_idx
                        production.append([prod, univ_idx])
                        univ_idx += 1
                    current_state = current_state[:idx] + production + current_state[idx + 1:]
                    break
        return table

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
        self.current_symbol_pos += len(self.input_stack[-1])
        self.working_stack.append(self.input_stack.pop())

    def momentary_insuccess(self):
        self.current_state = BACK_STATE

    def back(self):
        self.current_symbol_pos -= len(self.working_stack[-1])
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

    def read(self):
        with open("g1.txt", "r") as input_file:
            grammar_line = input_file.readline()
            grammar_line = grammar_line[1:-2]
            non_terminals = grammar_line.split(",")
            self.result.append(non_terminals)
            grammar_line = input_file.readline()
            grammar_line = grammar_line[1:-2]
            terminals = grammar_line.split(",")
            self.result.append(terminals)
            grammar_line = input_file.readline()
            start_symbol = grammar_line[:-1]
            if start_symbol not in non_terminals:
                raise Exception("Start symbol is not in the set of non terminals")
            self.result.append(start_symbol)
            transitions = dict()
            for grammar_line in input_file:
                grammar_line = grammar_line.split("\;")
                transition_start = grammar_line[0]
                transition_destination = grammar_line[1]
                transition_destination = transition_destination.split()
                if transition_start not in non_terminals:
                    raise Exception("Production start symbol not in set of non terminals")
                for symbol in transition_destination:
                    if symbol not in non_terminals and symbol not in terminals:
                        print(symbol)
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
                            transition_string += token + " "
                        transition_string += "| "
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
    # p = Parser()
    # with open("pif.txt", "r") as f:
    #     program = ""
    #     for line in f:
    #         program += line.split(" --> ")[0] + " "
    #     p.check(program)
