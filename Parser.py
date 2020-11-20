NORMAL_STATE = "q"
BACK_STATE = "b"
FINAL_STATE = "f"
ERROR_STATE = "e"


class Parser:
    def __init__(self):
        self.result = list()
        self.read()
        self.non_terminals = self.result[0]
        self.terminals = self.result[1]
        self.start_symbol = self.result[2]
        self.transitions = self.result[3]

        self.current_state = NORMAL_STATE
        self.current_symbol_pos = 1
        self.working_stack = list()
        self.input_stack = list()
        self.input_stack.append(self.start_symbol)
        self.transition_indexes = list()

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
            self.result.append(start_symbol)
            transitions = dict()
            for line in input_file:
                line = line.split(";")
                transition_start = line[0]
                transition_destination = line[1]
                transition_destination = transition_destination.split()
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

    def production_for(self, non_terminal):
        if non_terminal not in self.transitions.keys():
            return None
        return self.transitions[non_terminal]
    #
    # def expand(self):
    #     self.working_stack.append(str(self.input_stack[0]) + str(self.current_symbol_pos))
    #     current_prod = self.transitions[self.input_stack[0]][self.transition_indexes[self.current_symbol_pos]]
    #     self.input_stack.reverse()
    #     self.input_stack = self.input_stack[:-1]
    #     current_prod = current_prod[::-1]
    #     self.input_stack.append(current_prod)
    #     self.input_stack.reverse()


if __name__ == "__main__":
    p = Parser()
    print(p.production_for("S"))
    p.menu()
