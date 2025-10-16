# pages/widgets/simulation_kernel.py
import numpy as np
import random

class SimulationKernel:
    """一个独立的仿真内核，模拟生产过程并返回结果"""
    def run(self, params):
        """
        接收参数并运行一次仿真。
        :param params: a dict like {'temp': 90.0, 'speed': 50.0}
        :return: a dict of results
        """
        temp = params['temp']
        speed = params['speed']
        
        # --- 独特的物理-数学模型 ---
        # 1. 产量模型 (与速度正相关)
        total_output = speed * 60 # 模拟1小时的产量 (米)
        
        # 2. 能耗模型 (与速度非线性相关)
        base_power = 20 # 基础功率 kW
        speed_power = (speed / 50)**2 * 15 # 速度相关的功率
        total_energy = (base_power + speed_power) * 1 # 1小时的能耗 kWh
        unit_energy = total_energy / total_output if total_output > 0 else 0
        
        # 3. 缺陷率模型 (温度偏离最佳值90度时，缺陷率指数上升)
        temp_deviation = abs(temp - 90)
        defect_rate = 0.005 + (temp_deviation / 10)**3 * 0.01
        
        return {
            'output': total_output,
            'energy': total_energy,
            'unit_energy': unit_energy,
            'defect_rate': defect_rate
        }

class GeneticOptimizer:
    """使用遗传算法寻找最优参数"""
    def __init__(self, kernel, param_ranges, population_size=20, generations=30, mutation_rate=0.1):
        self.kernel = kernel
        self.param_ranges = param_ranges # e.g., {'temp': (80, 100), 'speed': (40, 60)}
        self.population_size = population_size
        self.generations = generations
        self.mutation_rate = mutation_rate
        self.history = [] # 记录每一代的最佳适应度

    def _create_individual(self):
        """创建一个随机的个体（一组参数）"""
        return {
            'temp': random.uniform(*self.param_ranges['temp']),
            'speed': random.uniform(*self.param_ranges['speed'])
        }

    def _calculate_fitness(self, results):
        """适应度函数：产量越高越好，能耗和缺陷率越低越好"""
        if results['output'] == 0: return 0
        # 权重可以调整
        fitness = results['output'] / (results['unit_energy'] * 100 + results['defect_rate'] * 1000 + 1)
        return fitness

    def run_optimization(self):
        # 1. 初始化种群
        population = [self._create_individual() for _ in range(self.population_size)]
        
        for gen in range(self.generations):
            # 2. 评估适应度
            fitness_scores = []
            for individual in population:
                results = self.kernel.run(individual)
                fitness_scores.append(self._calculate_fitness(results))
            
            best_fitness_idx = np.argmax(fitness_scores)
            self.history.append(fitness_scores[best_fitness_idx])
            
            # 3. 选择 (选择最好的50%个体)
            sorted_indices = np.argsort(fitness_scores)[::-1]
            selected_population = [population[i] for i in sorted_indices[:self.population_size // 2]]
            
            # 4. 交叉和变异，产生新一代
            next_population = selected_population[:] # 复制精英个体
            while len(next_population) < self.population_size:
                parent1, parent2 = random.choices(selected_population, k=2)
                
                # 交叉
                child = {
                    'temp': random.choice([parent1['temp'], parent2['temp']]),
                    'speed': random.choice([parent1['speed'], parent2['speed']])
                }
                
                # 变异
                if random.random() < self.mutation_rate:
                    child['temp'] += random.uniform(-2, 2)
                    child['speed'] += random.uniform(-1, 1)
                
                # 确保参数在范围内
                child['temp'] = np.clip(child['temp'], *self.param_ranges['temp'])
                child['speed'] = np.clip(child['speed'], *self.param_ranges['speed'])
                
                next_population.append(child)
            
            population = next_population
            
        # 返回最后一代中最好的个体
        final_fitness = [self._calculate_fitness(self.kernel.run(p)) for p in population]
        best_individual = population[np.argmax(final_fitness)]
        return best_individual