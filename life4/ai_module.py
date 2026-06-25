from lupa.luajit21 import LuaRuntime

lua = LuaRuntime()

lua.execute('rand = math.random')

ai_gen_weights = lua.eval('''
function(layers, mult)
    local weights = {}
    local id = 1
    for i = 1, #layers-1 do
        local layer = layers[i]
        local next_layer = layers[i+1]
        for j = 1, layer*(2+next_layer) do
            weights[id] = (rand()-0.5)*2*mult
            id = id + 1
        end
    end
    return weights
end
''')

ai_mutate = lua.eval('''
function(weights, mult)
    local id = math.random(1, #weights)
    weights[id] = weights[id] + (rand()-0.5)*2*mult
    return weights
end
''')

ai_act = lua.eval('''
function(layers, weights, data)
    local id = 1
    for i = 2, #layers do
        local layer = layers[i]
        local new_data = {}
        for j = 1, layer do
            new_data[j] = 0.0
        end
        for j = 1, layers[i-1] do
            local value = data[j] + weights[id]
            if value <= 0 then
                value = weights[id+1]
            end
            for k = 1, layer do
                new_data[k] = new_data[k] + value*weights[id+1+k]
            end
            id = id + 2 + layer
        end
        data = new_data
    end
    return data
end
''')

class AI:
    def __init__(self, layers, weights=None, mult_init=1.0, mult_muta=0.01):
        self.layers = layers
        self.mult_muta = mult_muta
        self.weights = weights if weights else ai_gen_weights(layers, mult_init)

    def mutate(self, mult=None):
        mult = mult if mult else self.mult_muta
        self.nodes = ai_mutate(self.weights, mult)

    def act(self, data, to_list=False):
        output_data = ai_act(self.layers, self.weights, lua.table_from(data))
        return list(output_data.values()) if to_list else output_data

def pr_w(ai):
    print(list(ai.weights.values()))
