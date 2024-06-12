import pygame
import random

# Konstanta
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
BLUE = (0, 0, 255)
LIGHT_BLUE = (173, 216, 230)
SCREEN_WIDTH = 1400
SCREEN_HEIGHT = 600
STATION_POSITIONS = [100, 400, 700, 1000, 1300]
STATION_NAMES = ["Jogja", "Maguwo", "Klaten", "Gawok", "Solo"]
TRAIN_WIDTH = 145
TRAIN_HEIGHT = 15
PASSENGER_RADIUS = 2
STOP_TIME = 3000  # Durasi kereta berhenti di stasiun dalam milidetik
BOARDING_TIME = 3000  # Waktu untuk penumpang naik turun dalam milidetik
PASSENGER_SPEED = 2  # Kecepatan pergerakan penumpang
BOARDING_RADIUS = 50  # Radius dalam pixel untuk penumpang memasuki kereta
ROWS = 4  # Baris penumpang di dalam kereta
COLS = 36  # Kolom penumpang di dalam kereta


class Train:
    def __init__(self, capacity):
        self.capacity = capacity
        self.passengers = []
        self.direction = 1
        self.x = 50
        self.y = SCREEN_HEIGHT // 2
        self.target_position = STATION_POSITIONS[0]

    def move(self):
        if self.x < self.target_position:
            self.x += 2
        elif self.x > self.target_position:
            self.x -= 2
        for i, passenger in enumerate(self.passengers):
            col = i % COLS
            row = i // COLS
            passenger.position = (self.x + col * 2 * PASSENGER_RADIUS, self.y + row * 2 * PASSENGER_RADIUS)

    def set_target(self, position):
        self.target_position = position

    def board(self, passengers):
        space_left = self.capacity - len(self.passengers)
        boarded_passengers = passengers[:space_left]
        for passenger in boarded_passengers:
            passenger.on_train = True
        self.passengers.extend(boarded_passengers)
        available_seat = self.capacity - len(self.passengers)
        waiting_passenger = len(passengers) - len(boarded_passengers)
        return boarded_passengers

    def alight(self, number):
        alighted_passengers = self.passengers[:number]
        self.passengers = self.passengers[number:]
        for passenger in alighted_passengers:
            passenger.target = (passenger.position[0], passenger.position[1] + 50)  # Move down when alighting
            passenger.on_train = False
        return alighted_passengers

    def alight_all(self):
        alighted_passengers = self.passengers
        self.passengers = []
        for passenger in alighted_passengers:
            passenger.target = (passenger.position[0], passenger.position[1] + 50)  # Move down when alighting
            passenger.on_train = False
        return alighted_passengers

class Station:
    def __init__(self, name, position):
        self.name = name
        self.queue = random.randint(25, 144)
        self.position = position
        self.passenger_queue = [Passenger(self.position, SCREEN_HEIGHT // 2 + 100 + i * 2 * PASSENGER_RADIUS) for i in range(self.queue)]

    def generate_queue(self):
        self.queue = random.randint(25, 144)
        self.passenger_queue = [Passenger(self.position, SCREEN_HEIGHT // 2 + 100 + i * 2 * PASSENGER_RADIUS) for i in range(self.queue)]

    def get_passengers(self, capacity_left, train_x):
        queued = min(self.queue, capacity_left)
        eligible_passengers = [p for p in self.passenger_queue if abs(p.position[0] - train_x) <= BOARDING_RADIUS]
        passengers_to_board = eligible_passengers[:queued]
        self.passenger_queue = [p for p in self.passenger_queue if p not in passengers_to_board]
        self.queue -= len(passengers_to_board)
        return passengers_to_board

class Passenger:
    def __init__(self, x, y):
        self.position = (x, y)
        self.target = None
        self.on_train = False

    def move_to_target(self):
        if self.target:
            target_x, target_y = self.target
            current_x, current_y = self.position
            if current_x < target_x:
                current_x += PASSENGER_SPEED
            elif current_x > target_x:
                current_x -= PASSENGER_SPEED
            if current_y < target_y:
                current_y += PASSENGER_SPEED
            elif current_y > target_y:
                current_y -= PASSENGER_SPEED
            self.position = (current_x, current_y)
            if self.position == self.target:
                self.target = None

def draw_train(screen, x, y):
    pygame.draw.rect(screen, BLUE, [x, y, TRAIN_WIDTH, TRAIN_HEIGHT])

def draw_passenger(screen, x, y):
    pygame.draw.circle(screen, RED, (x, y), PASSENGER_RADIUS)

def animate_passengers(passengers, screen):
    for passenger in passengers:
        passenger.move_to_target()
        draw_passenger(screen, passenger.position[0], passenger.position[1])

def simulate(train, stations, station_index, alighting_passengers):
    station = stations[station_index]
    alighted_count = 0
    boarded_count = 0
    in_train_count = 0

    if station_index == 0:
        print(f"\nPerjalanan dari {stations[0].name} ke {stations[-1].name}")
        for station in stations:
            station.generate_queue()
        boarded_passengers = train.board(stations[0].get_passengers(train.capacity, train.x))
        for passenger in boarded_passengers:
            passenger.target = (train.x, train.y)
        boarded_count = len(boarded_passengers)
        print(f"Kereta berangkat dari {stations[0].name} dengan {boarded_count} penumpang")
    else:
        print(f"\nKereta tiba di stasiun {station.name}")

        if station_index == len(stations) - 1:
            alighted_passengers = train.alight_all()
            alighted_count = len(alighted_passengers)
            alighting_passengers.extend(alighted_passengers)  # Menambah penumpang yang turun ke dalam alighting_passengers
            print(f"Jumlah penumpang yang turun: {alighted_count}")
        else:
            passengers_to_alight = random.randint(0, len(train.passengers))
            alighted_passengers = train.alight(passengers_to_alight)
            alighted_count = len(alighted_passengers)
            alighting_passengers.extend(alighted_passengers)  # Menambah penumpang yang turun ke dalam alighting_passengers
            for passenger in alighted_passengers:
                passenger.target = (train.x, train.y - 50)  # Mengatur agar penumpang yang turun bergerak ke atas
            print(f"Jumlah penumpang yang turun: {alighted_count}")

            capacity_left = train.capacity - len(train.passengers)
            boarding_passengers = station.get_passengers(capacity_left, train.x)
            boarded_count = len(boarding_passengers)
            for passenger in boarding_passengers:
                passenger.target = (train.x, train.y)
            train.board(boarding_passengers)
            in_train_count = len(train.passengers)
            print(f"Jumlah penumpang yang naik: {boarded_count}")
            print(f"Jumlah penumpang dalam kereta: {in_train_count}")

            # Generate new queue of passengers at the station
            station.generate_queue()

    return alighted_count, boarded_count, in_train_count

def animate(train, stations):
    pygame.init()

    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("Simulasi Kereta Api")

    clock = pygame.time.Clock()
    running = True

    station_index = 0
    direction = 1
    move = True
    wait_time = 0
    alighting_passengers = []  # Definisikan alighting_passengers di sini
    boarding_passengers = []
    boarding = False

    alighted_count = 0
    boarded_count = 0
    in_train_count = 0

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        screen.fill(WHITE)

        # Menggambar st        screen.fill(WHITE)

        # Menggambar stasiun sebagai garis horizontal
        pygame.draw.line(screen, LIGHT_BLUE, (0, train.y), (SCREEN_WIDTH, train.y), 5)
        for i, station in enumerate(stations):
            font = pygame.font.Font(None, 36)
            text = font.render(station.name, True, BLACK)
            screen.blit(text, (STATION_POSITIONS[i] - 20, train.y + 10))

        # Menggerakkan kereta ke stasiun berikutnya
        if move:
            if 0 <= station_index < len(STATION_POSITIONS):
                train.set_target(STATION_POSITIONS[station_index])
                train.move()
                if train.x == STATION_POSITIONS[station_index]:
                    move = False
                    boarding = True
                    wait_time = pygame.time.get_ticks() + BOARDING_TIME
                    stations[station_index].generate_queue()  # Generate new queue of passengers at the station
            else:
                direction *= -1
                station_index += direction
        else:
            if boarding:
                if pygame.time.get_ticks() >= wait_time:
                    alighted_count, boarded_count, in_train_count = simulate(train, stations,
                    station_index, alighting_passengers)
                    boarding = False
                    wait_time = pygame.time.get_ticks() + STOP_TIME
            else:
                if pygame.time.get_ticks() >= wait_time:
                    move = True
                    station_index += direction

        draw_train(screen, train.x, train.y)

        # Menggambar penumpang yang menunggu di stasiun
        for station in stations:
            for passenger in station.passenger_queue:
                passenger.move_to_target()
                draw_passenger(screen, passenger.position[0], passenger.position[1])

        # Menggerakkan penumpang yang naik dan turun
        animate_passengers(alighting_passengers, screen)
        animate_passengers(boarding_passengers, screen)
        animate_passengers(train.passengers, screen)

        # Menampilkan keterangan jumlah penumpang yang turun dan naik
        if not move and not boarding:
            if station_index < len(stations):
                font = pygame.font.Font(None, 24)
                alighted_text = font.render(f"Jumlah penumpang yang turun: {alighted_count}", True, BLACK)
                boarded_text = font.render(f"Jumlah penumpang yang naik: {boarded_count}", True, BLACK)
                in_train_text = font.render(f"Jumlah penumpang dalam kereta: {in_train_count}", True, BLACK)
                screen.blit(alighted_text, (70, 10))
                screen.blit(boarded_text, (70, 40))
                screen.blit(in_train_text, (70, 70))

        pygame.display.flip()
        clock.tick(60)

    pygame.quit()

def main():
    train = Train(capacity=ROWS * COLS)
    stations = [Station(name, pos) for name, pos in zip(STATION_NAMES, STATION_POSITIONS)]
    animate(train, stations)

if __name__ == "__main__":
    main()

