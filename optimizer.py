import numpy as np
import skfuzzy as fuzz
import skfuzzy.control as ctrl

class Particle:
    def __init__(self, bounds):
        self.position = np.array([np.random.uniform(low, high) for low, high in bounds])
        self.velocity = np.random.uniform(-1, 1, size=len(bounds))
        self.best_position = self.position.copy()
        self.best_value = float('inf')

class PSO:
    def __init__(self, obj_function, bounds, num_particles=30, max_iter=100, w=0.5, c1=1.3, c2=1.3):
        self.obj_function = obj_function
        self.bounds = bounds
        self.swarm = [Particle(bounds) for _ in range(num_particles)]
        self.global_best_position = None
        self.global_best_value = float('inf')
        self.max_iter = max_iter
        self.w = w
        self.c1 = c1
        self.c2 = c2

    def optimize(self):
        for _ in range(self.max_iter):
            for particle in self.swarm:
                value = self.obj_function(particle.position)
                if value < particle.best_value:
                    particle.best_value = value
                    particle.best_position = particle.position.copy()
                if value < self.global_best_value:
                    self.global_best_value = value
                    self.global_best_position = particle.position.copy()

            for particle in self.swarm:
                r1, r2 = np.random.rand(), np.random.rand()
                particle.velocity = (self.w * particle.velocity +
                                     self.c1 * r1 * (particle.best_position - particle.position) +
                                     self.c2 * r2 * (self.global_best_position - particle.position))
                particle.position += particle.velocity
                particle.position = np.clip(particle.position, [low for low, _ in self.bounds], [high for _, high in self.bounds])

        return self.global_best_position, self.global_best_value

temp = ctrl.Antecedent(np.arange(15, 35, 1), 'temperature')
occup = ctrl.Antecedent(np.arange(0, 21, 1), 'occupancy')
HVAC_setting = ctrl.Consequent(np.arange(0, 1.1, 0.1), 'HVAC_setting')

temp['comfortable'] = fuzz.trimf(temp.universe, [20, 22, 24])
temp['warm'] = fuzz.trimf(temp.universe, [23, 26, 29])
temp['hot'] = fuzz.trimf(temp.universe, [28, 32, 35])

occup['low'] = fuzz.trimf(occup.universe, [0, 5, 10])
occup['medium'] = fuzz.trimf(occup.universe, [8, 12, 16])
occup['high'] = fuzz.trimf(occup.universe, [14, 17, 20])

HVAC_setting['low'] = fuzz.trimf(HVAC_setting.universe, [0, 0.3, 0.5])
HVAC_setting['medium'] = fuzz.trimf(HVAC_setting.universe, [0.4, 0.6, 0.8])
HVAC_setting['high'] = fuzz.trimf(HVAC_setting.universe, [0.7, 0.9, 1])

rules = [
    ctrl.Rule(temp['hot'] & occup['high'], HVAC_setting['high']),
    ctrl.Rule(temp['warm'] & occup['medium'], HVAC_setting['medium']),
    ctrl.Rule(temp['comfortable'] & occup['low'], HVAC_setting['low']),
]

HVAC_control = ctrl.ControlSystem(rules)
HVAC_sim = ctrl.ControlSystemSimulation(HVAC_control)

def objective(HVAC_level):
    temperature = 26
    occupancy = 15
    HVAC_sim.input['temperature'] = temperature
    HVAC_sim.input['occupancy'] = occupancy
    HVAC_sim.compute()

    energy_usage = HVAC_level[0] * occupancy * abs(temperature - 22)
    comfort_penalty = abs(temperature - 22 - HVAC_level[0] * 5) * occupancy
    return energy_usage + comfort_penalty

# Optimizing with PSO
bounds = [(0, 1)]
pso = PSO(objective, bounds)
optimal_setting, optimal_value = pso.optimize()

print("Optimal HVAC setting:", optimal_setting)
print("Optimal value:", optimal_value)
