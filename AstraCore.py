import matplotlib.pyplot as mpl
import random as r

class RocketSim:
    def __init__(
        self,
        mass,
        burn_rate,
        exhaust_velocity,
        fuel,
        drag_coeff,
        area
    ):
        self.mass = mass
        self.dry_mass = mass
        self.initial_fuel = fuel
        self.fuel = fuel
        self.burn_rate = burn_rate
        self.exhaust_velocity = exhaust_velocity
        self.height = 0
        self.velocity = 0
        self.time = 0
        self.heights = []
        self.velocities = []
        self.times = []
        self.g0=9.81
        self.gravity = -9.81
        self.air_density = 1.225
        self.drag_coeff = drag_coeff
        self.area=area

    def get_air_density(self):
        density = 1.225 * (0.9999 ** self.height)
        return max(0, density)

    def cal_drag(self, velocity):
        air_density=self.get_air_density()
        return (
            0.5
            * air_density
            * self.drag_coeff
            * self.area
            * velocity
            * abs(velocity)
            )

    def get_thrust(self):
        if self.fuel <= 0:
            return 0
        return self.burn_rate * self.exhaust_velocity*self.g0

    def cal_acceleration(self, Fthrust, Fg, Fdrag):
        Fnet = Fthrust + Fg + Fdrag
        current_mass = self.dry_mass + self.fuel
        return Fnet / current_mass

    def update_state(self, acceleration):
        self.velocity += acceleration
        self.height += self.velocity

        if self.height < 0:
            self.height = 0
            self.velocity = 0

    def reset(self):
        self.height = 0
        self.velocity = 0
        self.time = 0
        self.heights = []
        self.velocities = []
        self.times = []
        self.fuel = self.initial_fuel

    def run_simulation(self):

        while self.fuel > 0:

            Fthrust = self.get_thrust()
            current_mass = self.dry_mass + self.fuel
            Fg = current_mass * self.gravity
            TWR = Fthrust / abs(Fg)
            if TWR < 1:
                break
            Fdrag = -self.cal_drag(self.velocity)

            acceleration = self.cal_acceleration(
                Fthrust,
                Fg,
                Fdrag
            )

            self.update_state(acceleration)

            self.heights.append(self.height)
            self.velocities.append(self.velocity)
            self.times.append(self.time)

            self.fuel -= self.burn_rate
            if self.fuel < 0:
                self.fuel = 0
            self.time += 1

        while self.height > 0:

            Fthrust = 0
            current_mass = self.dry_mass + self.fuel
            Fg = current_mass * self.gravity
            Fdrag = -self.cal_drag(self.velocity)

            acceleration = self.cal_acceleration(
                Fthrust,
                Fg,
                Fdrag
            )

            self.update_state(acceleration)

            self.heights.append(self.height)
            self.velocities.append(self.velocity)
            self.times.append(self.time)

            self.time += 1
            
        if len(self.velocities) > 0:
             max_velocity = max(
             abs(v)
             for v in self.velocities
           )
        else:
            max_velocity = 0

        result = (
            self.times,
            self.heights,
            self.velocities,
            max_velocity,
            apogee_time,
            flight_time
        )

        self.reset()
        return result


population = []

for i in range(50):

    population.append(
        (
            r.randint(30,80),
            r.randint(1,5),
            r.randint(80,200),
            r.randint(20,60),
            r.uniform(0.005,0.05),
            r.uniform(0.5,3)
        )
    )

generation_avg = []
generation_best_height = []
generation_best_fitness = []

best_height = 0
best_efficiency = 0
best_height_rocket = None
best_efficiency_rocket = None

for generation in range(20):

    mutation_strength = 2 - (1.5 * generation / 19)
    scored_population = []

    for rocket_data in population:

        mass, burn_rate, exhaust_velocity, fuel, drag_coeff, area = rocket_data

        rocket = RocketSim(
            mass,
            burn_rate,
            exhaust_velocity,
            fuel,
            drag_coeff,
            area
        )

        t, h, v, max_velocity, apogee_time, flight_time = rocket.run_simulation()

        if len(h) > 0:
            max_height = max(h)
        else:
            max_height = 0

        apogee_index=h.index(max_height)
        apogee_time=t[apogee_index]
        if len(t) > 0:
            flight_time = t[-1]
        else:
            flight_time = 0

        fitness_score = (
            max_height
            - mass * 3
            - fuel * 2
            - drag_coeff * 2000
            - area * 50
        )

        efficiency = max_height / (
            mass + fuel + drag_coeff * 100 + area * 10
        )

        if max_height > best_height:
            best_height = max_height
            best_height_rocket = (
                mass,
                burn_rate,
                exhaust_velocity,
                fuel,
                drag_coeff,
                area,
                t,
                h,
                v,
                max_velocity,
                apogee_time,
                flight_time
            )

        if efficiency > best_efficiency:
            best_efficiency = efficiency
            best_efficiency_rocket = (
                mass,
                burn_rate,
                exhaust_velocity,
                fuel,
                drag_coeff,
                area,
                t,
                h,
                v,
                max_velocity,
                apogee_time,
                flight_time
            )

        scored_population.append(
            (
                fitness_score,
                max_height,
                mass,
                burn_rate,
                exhaust_velocity,
                fuel,
                drag_coeff,
                area,
                t,
                h,
                v,
                max_velocity,
                apogee_time,
                flight_time
            )
        )

    scored_population.sort(reverse=True)
    elite = scored_population[:5]

    unique_designs = set(population)
    diversity_score = len(unique_designs)

    avg_generation_height = (
        sum(rocket[1] for rocket in scored_population)
        / len(scored_population)
    )

    generation_best_height.append(elite[0][1])
    generation_best_fitness.append(elite[0][0])
    generation_avg.append(avg_generation_height)

    print(
        "Generation",
        generation,
        "Best Fitness:",
        round(elite[0][0],2),
        "Best Height:",
        round(elite[0][1],2)
    )

    new_population = []

    for rocket in elite:
        new_population.append(rocket[2:8])

    while len(new_population) < 50:

        parent1, parent2 = r.sample(elite, 2)

        fitness1, height1, mass1, burn1, exhaust1, fuel1, drag1, area1, t1, h1, v1, maxv1 = parent1
        fitness2, height2, mass2, burn2, exhaust2, fuel2, drag2, area2, t2, h2, v2, maxv2 = parent2

        child_mass = r.choice([mass1, mass2])
        child_burn = r.choice([burn1, burn2])
        child_exhaust = r.choice([exhaust1, exhaust2])
        child_fuel = r.choice([fuel1, fuel2])
        child_drag = r.choice([drag1, drag2])
        child_area = r.choice([area1, area2])

        new_population.append(
            (
                max(10, child_mass + r.randint(int(-5*mutation_strength), int(5*mutation_strength))),
                max(1, child_burn + r.randint(int(-1*mutation_strength), int(1*mutation_strength))),
                max(50, child_exhaust + r.randint(int(-10*mutation_strength), int(10*mutation_strength))),
                max(5, child_fuel + r.randint(int(-5*mutation_strength), int(5*mutation_strength))),
                max(0.001, child_drag + r.uniform(-0.005*mutation_strength, 0.005*mutation_strength)),
                max(0.1, child_area + r.uniform(-0.2*mutation_strength, 0.2*mutation_strength))
            )
        )

    population = new_population

print("\nBEST HEIGHT ROCKET")
print("Mass:", best_height_rocket[0])
print("Burn Rate:", best_height_rocket[1])
print("Exhaust Velocity:", best_height_rocket[2])
print("Fuel:", best_height_rocket[3])
print("Drag:", best_height_rocket[4])
print("Area:", best_height_rocket[5])
print("Max Velocity:", round(best_height_rocket[9],2))
print("Apogee Time:", best_height_rocket[10])
print("Flight Time:", best_height_rocket[11])

print("\nBEST EFFICIENCY ROCKET")
print("Mass:", best_efficiency_rocket[0])
print("Burn Rate:", best_height_rocket[1])
print("Exhaust Velocity:", best_height_rocket[2])
print("Fuel:", best_height_rocket[3])
print("Drag:", best_height_rocket[4])
print("Area:", best_height_rocket[5])
print("Max Velocity:", round(best_height_rocket[9],2))
print("Apogee Time:", best_height_rocket[10])
print("Flight Time:", best_height_rocket[11])

mpl.plot(generation_best_height, label="Best Height")
mpl.plot(generation_avg, label="Average Height")
mpl.xlabel("Generation")
mpl.ylabel("Height")
mpl.title("Evolution Progress")
mpl.legend()
mpl.show()
