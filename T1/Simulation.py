import yaml
import random

class Simulation:
    def __init__(self, name: str):
        self.name = name
        self.queue_list = []
        self.iterations = 0
        self.total_time = 0.0
        self.scheduler = None

    class Queue:
        def __init__(self, name: str, servers: int, minService: float, maxService: float, 
                 minArrival: float = 0.0, maxArrival: float = 0.0, capacity: int = 0):
            self.name = name
            self.servers = servers
            self.capacity = capacity
            self.minArrival = minArrival
            self.maxArrival = maxArrival
            self.minService = minService
            self.maxService = maxService
            self.connections = []
            self.sum_connections_probability = 0.0
            self.leave_probability = 0.0
            self.arrival = None
            self._status = 0
            self._loss = 0
            self.scheduler = None
            self._distribution = self.get_distribution_array()
            self._time = 0.0
            self._distribution_percent = None
            self._max_status = 0

        class Connection:
            def __init__(self,target: 'Simulation.Queue', probability: float = 1.0):
                self.target = target
                self.probability = probability

            def __str__(self):
                return (f"Source: {self.source}\n"
                        f"Target: {self.target}\n"
                        f"Probability: {self.probability}")
            
        def set_arrival(self, arrival: float):
            if arrival < 0:
                raise ValueError("Arrival value cannot be negative")
            self.arrival = arrival

        def update_distribution(self, time: float):
            if time < 0:
                raise ValueError("Time value cannot be negative")
            self._distribution[self._status] += time - self._time
            self._time = time

        def check_if_max_status_changed(self):
            if self._status > self._max_status:
                self._max_status = self._status
                self._distribution.update({self._status: 0.0})
            
        def process_arrival(self, time: float = None, source: 'Simulation.Queue' = -1):
            if time is None:
                time = self.arrival
                self.update_distribution(time)

            # Decrement the status of the source queue
            # If source is -1, it means the event is not from another queue
            if source != -1:
                source.update_distribution(time)
                source._status -= 1

                # Schedule the passage or leave event for the source queue
                if source._status >= source.servers:
                    # Generate rand
                    rand_network_src = source.scheduler.next_random()
                    if rand_network_src == None:
                        return
                    probability = 0.0
                    for connection in source.connections:
                        probability += connection.probability
                        if rand_network_src < probability:
                            rand_event_src = source.scheduler.next_random()
                            if rand_event_src == None:
                                return
                            event = {
                                'source': source.name,
                                'target': connection.target.name,
                                'time': rand_event_src * (source.maxService - source.minService) + source.minService + time,
                                'type': 'arrival',
                            }
                            source.scheduler.add_event(event)
                            break

                    # If no connection was made, process leaving
                    if rand_network_src > probability:
                        rand_event_src = source.scheduler.next_random()
                        if rand_event_src == None:
                            return
                        event = {
                            'source': source.name,
                            'target': -1,
                            'time': rand_event_src * (source.maxService - source.minService) + source.minService + time,
                            'type': 'leave',
                        }
                        source.scheduler.add_event(event)
            
            # Process arrival to the target queue
            rand_network_tgt = self.scheduler.next_random()
            if rand_network_tgt == None:
                return
            if self._status < self.capacity or self.capacity == 0:
                self.update_distribution(time)
                self._status += 1
                if self.capacity == 0:
                    self.check_if_max_status_changed()
                if self._status <= self.servers:
                    # Generate rand
                    probability = 0.0
                    for connection in self.connections:
                        probability += connection.probability
                        if rand_network_tgt < probability:
                            rand_event_tgt = self.scheduler.next_random()
                            if rand_event_tgt == None:
                                return
                            event = {
                                'source': self.name,
                                'target': connection.target.name,
                                'time': rand_event_tgt * (self.maxService - self.minService) + self.minService + time,
                                'type': 'arrival',
                            }
                            self.scheduler.add_event(event)
                            break

                    # If no connection was made, process leaving
                    if rand_network_tgt > probability:
                        rand_event_tgt = self.scheduler.next_random()
                        if rand_event_tgt == None:
                            return
                        event = {
                            'source': self.name,
                            'target': -1,
                            'time': rand_event_tgt * (self.maxService - self.minService) + self.minService + time,
                            'type': 'leave',
                        }
                        self.scheduler.add_event(event)
            else:
                self._loss += 1

            # If the queue has arrival and the source is -1, schedule the next arrival from outside
            if self.maxArrival > 0 and self.minArrival > 0 and source == -1:
                rand = self.scheduler.next_random()
                if rand == None:
                    return
                event = {
                    'source': -1,
                    'target': self.name,
                    'time': rand * (self.maxArrival - self.minArrival) + self.minArrival + time,
                    'type': 'arrival',
                }
                self.scheduler.add_event(event)

        def process_leave(self, time: float = None):
            self.update_distribution(time)
            self._status -= 1

            if self._status >= self.servers:
                # Generate rand
                rand_network = self.scheduler.next_random()
                if rand_network == None:
                    return
                probability = 0.0
                for connection in self.connections:
                    probability += connection.probability
                    if rand_network < probability:
                        rand_event = self.scheduler.next_random()
                        if rand_event == None:
                            return
                        event = {
                            'source': self.name,
                            'target': connection.target.name,
                            'time': rand_event * (self.maxService - self.minService) + self.minService + time,
                            'type': 'arrival',
                        }
                        self.scheduler.add_event(event)
                        break

                # If no connection was made, process leaving
                if rand_network > probability:
                    rand_event = self.scheduler.next_random()
                    if rand_event == None:
                        return
                    event = {
                        'source': self.name,
                        'target': -1,
                        'time': rand_event * (self.maxService - self.minService) + self.minService + time,
                        'type': 'leave',
                    }
                    self.scheduler.add_event(event)

        def establish_connection(self, target: 'Simulation.Queue', probability: float = 1.0):
            if probability + self.sum_connections_probability > 1.0:
                raise ValueError("Total probability of connections exceeds 1.0")
            connection = self.Connection(target, probability)
            self.sum_connections_probability += probability
            
            self.connections.append(connection)

        def calculate_leave_probability(self):
            if self.sum_connections_probability == 0.0:
                self.leave_probability = 1.0
            else:
                self.leave_probability = round(1.0 - self.sum_connections_probability, 2)

        def set_scheduler(self, scheduler: 'Simulation.Scheduler'):
            self.scheduler = scheduler

        def get_distribution_array(self):
            dict = {}
            for i in range(self.capacity + 1):
                dict.update({i: 0.0})
            return dict
        
        def calculate_distribution(self):
            self._distribution_percent = {}
            for i in range(self.capacity + 1):
                self._distribution_percent.update({i: 0.0})

            for key,value in self._distribution.items():
                self._distribution_percent[key] = round((value / self._time * 100),2)    

        def __str__(self):
            connections_str = "\n\t".join([f"Target: {conn.target.name}, Probability: {conn.probability}" for conn in self.connections])
            if connections_str:
                connections_str = "\t" + connections_str
            
            distribution_times = "\n\t".join([f"{key}: {value}" for key, value in self._distribution.items()])
            if distribution_times:
                distribution_times = "\t" + distribution_times

            distribution_percent = "\n\t".join([f"{key}: {value}" for key, value in self._distribution_percent.items()])
            if distribution_percent:
                distribution_percent = "\t" + distribution_percent

            return (f"Name: {self.name}\n"
                    f"Arrival: {self.arrival}\n"
                    f"Servers: {self.servers}\n"
                    f"Capacity: {self.capacity}\n"
                    f"Min Arrival: {self.minArrival}\n"
                    f"Max Arrival: {self.maxArrival}\n"
                    f"Min Service: {self.minService}\n"
                    f"Max Service: {self.maxService}\n"
                    f"Leave Probability: {self.leave_probability}\n"
                    f"Connections:\n {connections_str}\n"
                    f"Loss: {self._loss}\n"
                    f"Distribution Times:\n {distribution_times}\n"
                    f"Distribution Percent:\n {distribution_percent}\n")

    class Scheduler:
        def __init__(self, name: str):
            self.name = name
            self.queue_list = []
            self.event_list = []
            self.time = 0.0
            self.iterations = 0
            self.max_iterations = 0
            self.previous = random.randint(0, (2**32)-1)
            self.rand_number_generated = 0

        class Event:
            def __init__(self, source: str, target: str, time: float, event_type: str):
                self.source = source
                self.target = target
                self.time = time
                self.event_type = event_type

            def get_source_object(self, queue_list: list):
                if self.source != -1:
                    return next((q for q in queue_list if q.name == self.source), None)
                else:
                    return -1

            def __str__(self):
                return (f"\tSource: {self.source}\n"
                        f"\tTarget: {self.target}\n"
                        f"\tTime: {self.time}\n"
                        f"\tEvent Type: {self.event_type}")

        def add_queue(self, queue: 'Simulation.Queue'):
            self.queue_list.append(queue)

        def add_scheduler_to_queues(self):
            for queue in self.queue_list:
                queue.set_scheduler(self)

        def add_event(self, event : dict):
            new_event = self.Event(event['source'], event['target'], event['time'], event['type'])
            self.event_list.append(new_event)

        def next_event(self):
            if self.event_list:
                self.event_list.sort(key=lambda x: x.time)
                return self.event_list.pop(0)
            else:
                return None
            
        def set_iterations(self, iterations: int):
            if iterations < 0:
                raise ValueError("Iterations value cannot be negative")
            self.max_iterations = iterations

        
        def next_random(self):
            a = 1664525
            c = 1013904223
            M = 2**32
            self.previous = (a * self.previous + c) % M
            self.rand_number_generated += 1
            if self.rand_number_generated == self.max_iterations:
                return None
            return self.previous / M

        def run(self):
            for queue in self.queue_list:
                if queue.arrival is not None:
                    self.time = queue.arrival
                    queue.process_arrival()
            
            iteration = 0
            while True:
                event = self.next_event()
                if event is None:
                    break

                self.time = event.time
                if event.event_type == 'arrival':
                    queue = next((q for q in self.queue_list if q.name == event.target), None)
                    if queue:
                        queue.process_arrival(self.time, event.get_source_object(self.queue_list))
                elif event.event_type == 'leave':
                    queue = next((q for q in self.queue_list if q.name == event.source), None)
                    if queue:
                        queue.process_leave(self.time)

                iteration += 1

            for queue in self.queue_list:
                queue._time = self.time
                queue.calculate_distribution()

    def __str__(self):
        queue_str = "\n".join([str(queue) for queue in self.queue_list])
        return (f"Simulation Name: {self.name}\n"
                f"Queues:\n{queue_str}")

    def run_simulation(self):
        # Create a Scheduler object
        self.scheduler = self.Scheduler("Scheduler")
        self.scheduler.set_iterations(self.iterations)

        # Add the Queue objects to the Scheduler
        for queue in self.queue_list:
            self.scheduler.add_queue(queue)

        # Set the Scheduler in each Queue object
        self.scheduler.add_scheduler_to_queues()

        self.scheduler.set_iterations(self.iterations)

        # Run the simulation
        self.scheduler.run()

        self.exit_simulation()


    def exit_simulation(self):
        # Get the total time of the simulation
        self.total_time = self.scheduler.time

        # Write the results to a file
        self.write_results("T1/results.txt")

    def treat_yaml(self, data):

        # Instantiate the Queue objects based on the YAML data
        for queue in data['queues']:
            queue_name = queue
            queue_servers = data['queues'][queue]['servers']
            queue_capacity = data['queues'][queue].get('capacity', 0)
            queue_minArrival = data['queues'][queue].get('minArrival', 0)
            queue_maxArrival = data['queues'][queue].get('maxArrival', 0)
            queue_minService = data['queues'][queue]['minService']
            queue_maxService = data['queues'][queue]['maxService']

            queue_obj = self.Queue(queue_name, queue_servers, queue_minService, queue_maxService,
                                      queue_minArrival, queue_maxArrival, queue_capacity)

            self.queue_list.append(queue_obj)

        # Instatiate the Connections objects based on the YAML data
        for connection in data['network']:
            source = connection['source']
            target = connection['target']
            probability = connection.get('probability', 1.0)

            # Find the source and target queue objects
            source_queue = next((q for q in self.queue_list if q.name == source), None)
            target_queue = next((q for q in self.queue_list if q.name == target), None)
            if source_queue and target_queue:
                try:
                    source_queue.establish_connection(target_queue, probability)
                except ValueError as e:
                    print(f"Error: {e}")
            else:
                print(f"Warning: Connection from {source} to {target} could not be established.")

        for queue in self.queue_list:
            queue.calculate_leave_probability()

        # Get the arrival value from the YAML data
        for queue in data['arrivals']:
            arrival_value = data['arrivals'][queue]
            queue_obj = next((q for q in self.queue_list if q.name == queue), None)
            if queue_obj:
                queue_obj.set_arrival(arrival_value)
            else:
                print(f"Warning: Arrival value for {queue} could not be set.")

        # Get the iterations value from the YAML data
        self.iterations = data.get('iterations', {}).get('value', 1)

    def read_yaml(self, filename: str):
        
        with open(filename, 'r') as file:
            data = yaml.safe_load(file)

        return data
    
    def write_results(self, filename: str):
        with open(filename, 'w') as file:
            for queue in self.queue_list:
                file.write(queue.__str__())
                file.write("\n")
            file.write("Total Time: " + str(round(self.total_time,2)))


if __name__ == "__main__":
    # Create a Simulation object
    simulation = Simulation("Simulation")

    # Read the YAML file
    data = simulation.read_yaml("T1/config.yaml")

    # Treat the YAML data
    simulation.treat_yaml(data)

    # Run the simulation
    simulation.run_simulation()