import sqlite3

class Car:
    def __init__(self, car_id, model, status, rate_per_day):
        self.id = car_id
        self.model = model
        self.status = status
        self.rate_per_day = rate_per_day

    def __str__(self):
        return f"Car{{id={self.id}, model='{self.model}', status='{self.status}', rate_per_day={self.rate_per_day}}}"


class Rental:
    def __init__(self, car_id, customer_name, rental_days, total_cost, status):
        self.car_id = car_id
        self.customer_name = customer_name
        self.rental_days = rental_days
        self.total_cost = total_cost
        self.status = status

    def __str__(self):
        return f"Rental{{car_id={self.car_id}, customer_name='{self.customer_name}', rental_days={self.rental_days}, total_cost={self.total_cost}, status='{self.status}'}}"


class CarRentalManager:
    DB_URL = "car_rental.db"

    def __init__(self):
        self.cars = {}
        self.rentals = []
        try:
            self.initialize_database()
            self.initialize_data()
        except sqlite3.Error as e:
            print(f"Initialization error: {e}")

    def initialize_database(self):
        try:
            with sqlite3.connect(self.DB_URL) as conn:
                cursor = conn.cursor()
                # Create `cars` table
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS cars (
                        id INTEGER PRIMARY KEY,
                        model TEXT NOT NULL,
                        status TEXT NOT NULL CHECK (status IN ('Available', 'Rented')),
                        rate_per_day REAL NOT NULL
                    )
                """)
                # Create `rentals` table
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS rentals (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        car_id INTEGER NOT NULL,
                        customer_name TEXT NOT NULL,
                        rental_days INTEGER NOT NULL,
                        total_cost REAL NOT NULL,
                        status TEXT NOT NULL CHECK (status IN ('Ongoing', 'Completed')),
                        FOREIGN KEY (car_id) REFERENCES cars (id)
                    )
                """)
                # Populate `cars` table with sample data if empty
                cursor.execute("SELECT COUNT(*) FROM cars")
                if cursor.fetchone()[0] == 0:
                    print("Populating cars table with sample data...")
                    cursor.executemany("""
                        INSERT INTO cars (id, model, status, rate_per_day) VALUES (?, ?, ?, ?)
                    """, [
                        (1, 'Toyota Corolla', 'Available', 50.0),
                        (2, 'Honda Civic', 'Available', 60.0),
                        (3, 'Ford Focus', 'Available', 55.0)
                    ])
        except sqlite3.Error as e:
            print(f"Database error during initialization: {e}")
            raise

    def initialize_data(self):
        try:
            with sqlite3.connect(self.DB_URL) as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT * FROM cars")
                for row in cursor.fetchall():
                    car_id, model, status, rate_per_day = row
                    self.cars[car_id] = Car(car_id, model, status, rate_per_day)
        except sqlite3.Error as e:
            print(f"Error loading data: {e}")
            raise

    def rent_car(self, car_id, customer_name, rental_days):
        car = self.cars.get(car_id)
        if car and car.status == 'Available':
            total_cost = car.rate_per_day * rental_days
            try:
                with sqlite3.connect(self.DB_URL) as conn:
                    cursor = conn.cursor()
                    cursor.execute("""
                        INSERT INTO rentals (car_id, customer_name, rental_days, total_cost, status)
                        VALUES (?, ?, ?, ?, ?)
                    """, (car_id, customer_name, rental_days, total_cost, 'Ongoing'))
                    cursor.execute("""
                        UPDATE cars SET status = ? WHERE id = ?
                    """, ('Rented', car_id))
                car.status = 'Rented'
                self.rentals.append(Rental(car_id, customer_name, rental_days, total_cost, 'Ongoing'))
                print(f"Car rented successfully! Total cost: ${total_cost:.2f}")
            except sqlite3.Error as e:
                print(f"Error during car rental: {e}")
        else:
            print("Car is not available for rent.")

    def return_car(self, car_id):
        car = self.cars.get(car_id)
        if car and car.status == 'Rented':
            try:
                with sqlite3.connect(self.DB_URL) as conn:
                    cursor = conn.cursor()
                    cursor.execute("""
                        UPDATE rentals SET status = ? WHERE car_id = ? AND status = ?
                    """, ('Completed', car_id, 'Ongoing'))
                    if cursor.rowcount > 0:
                        cursor.execute("""
                            UPDATE cars SET status = ? WHERE id = ?
                        """, ('Available', car_id))
                        car.status = 'Available'
                        print("Car returned successfully!")
                    else:
                        print("No ongoing rental found for this car.")
            except sqlite3.Error as e:
                print(f"Error during car return: {e}")
        else:
            print("Car is not rented.")

    def check_available_cars(self):
        print("Available Cars:")
        for car in self.cars.values():
            if car.status == 'Available':
                print(car)
