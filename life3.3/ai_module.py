from random import randint, random

class AI:
    def __init__(self, input_nodes, output_nodes, middle_nodes=list(), nodes=None, mult_init=1.0, mult_muta=0.01):
        self.layers = [input_nodes] + middle_nodes + [output_nodes]
        self.mult_init = mult_init
        self.mult_muta = mult_muta
        self.nodes = nodes if nodes else self.gen_nodes()
        #node = [a, c, *weights]

    def gen_nodes(self):
        'Regenerates node weights and constants. Atribute "mult_init" changes max adjustment in both directions.'

        mult = self.mult_init
        nodes = []
        for i in range(len(self.layers)-1):
            layer = self.layers[i]
            next_layer = self.layers[i+1]
            for _ in range(layer):
                weights = [(random()-0.5)*2 * mult for _ in range(next_layer)]
                consts = [(random()-0.5)*2 * mult for _ in range(2)]
                node = consts + weights[:]
                nodes.append(node)
        return nodes

    def mutate(self):
        'Sligthly changes weights or constants. Atribute "mult_muta" changes max adjustment in both directions.'

        mult = self.mult_muta
        match randint(1,2):
            case 1:
                weights = self.nodes[randint(0, len(self.nodes)-1)][3:]
                weights[randint(0, len(weights)-1)] += (random()-0.5)*2 * mult
            case 2:
                self.nodes[randint(0, len(self.nodes)-1)][randint(0,1)] += (random()-0.5)*2 * mult

    def act(self, data):
        'Takes several float arguments as input data.'

        node_id = 0
        for layer_size in self.layers[1:]:
            new_data = [0.0] * layer_size
            for i, val in enumerate(data):
                node = self.nodes[node_id]
                a, c = node[:2]
                weights = node[2:]
                x = val + a
                value = x if x > 0 else c
                for j in range(layer_size):
                    new_data[j] += value * weights[j]
                node_id += 1
            data = new_data

        return data
