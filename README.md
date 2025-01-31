Railway Ticket Reservation API
This is a RESTful API for managing railway ticket reservations. It allows users to book tickets, cancel tickets, view booked tickets, and check available tickets. The API enforces constraints such as berth allocation, waiting list limits, and priority for certain passengers.

Features
Book a Ticket: Book a ticket with passenger details.

Cancel a Ticket: Cancel a booked ticket.

View Booked Tickets: Get details of all booked tickets.

View Available Tickets: Get details of available berths.

Technologies Used
Python: Programming language.

Flask: Web framework for building the API.

SQLite: Relational database for storing ticket and passenger data.

Docker: Containerization for easy deployment.

Setup and Installation
Prerequisites
Docker and Docker Compose installed on your machine.

Steps to Run the Application
Clone the Repository: git clone https://github.com/adityapathak499/railway-ticket-reservation.git
cd railway-ticket-reservation

Build and Run the Docker Containers:
docker-compose up --build

Access the API:

The API will be available at http://localhost:5000.

Stop the Application:

docker-compose down

API Endpoints
1. Book a Ticket
Endpoint: POST /api/v1/tickets/book

Description: Book a ticket with passenger details.

Request Body:

json

{
  "passengers": [
    {"name": "Aditya Pathak", "age": 30, "gender": "male"},
    {"name": "Aditya Pathak", "age": 25, "gender": "female"}
  ]
}
Response:

json

{
  "ticket_id": 1,
  "status": "confirmed",
  "berth_number": 1,
  "passengers": [
    {"name": "Aditya Pathak", "age": 30, "gender": "male"},
    {"name": "Aditya Pathak", "age": 25, "gender": "female"}
  ]
}

2. Cancel a Ticket
Endpoint: POST /api/v1/tickets/cancel/{ticketId}

Description: Cancel a booked ticket.

Response:

json

{
  "message": "Ticket canceled successfully"
}

3. View Booked Tickets
Endpoint: GET /api/v1/tickets/booked

Description: Get details of all booked tickets.

Response:

json

[
  {
    "ticket_id": 1,
    "status": "confirmed",
    "berth_number": 1,
    "passengers": [
      {"name": "Aditya Pathak", "age": 30, "gender": "male"},
      {"name": "Ananya Pathak", "age": 25, "gender": "female"}
    ]
  }
]

4. View Available Tickets
Endpoint: GET /api/v1/tickets/available

Description: Get details of available berths.

Response:

json

{
  "available_berths": [
    {"berth_number": 2, "type": "lower"},
    {"berth_number": 3, "type": "lower"}
  ]
}
Database Schema
The database consists of the following tables:

Passengers:

id: Unique identifier for the passenger.

name: Name of the passenger.

age: Age of the passenger.

gender: Gender of the passenger.

ticket_id: Foreign key referencing the ticket.

Tickets:

id: Unique identifier for the ticket.

status: Status of the ticket (confirmed, RAC, waiting).

berth_number: Berth number allocated to the ticket.

created_at: Timestamp when the ticket was created.

Berths:

id: Unique identifier for the berth.

berth_number: Unique berth number.

type: Type of berth (lower, side-lower, upper).

is_occupied: Boolean indicating whether the berth is occupied.

Constraints and Business Logic
Berth Allocation:

Total confirmed berths: 63.

Total RAC berths: 9 (18 passengers, 2 per side-lower berth).

Maximum waiting list tickets: 10.

Priority for Lower Berths:

Passengers aged 60+.

Ladies with children (if lower berths are available).

Cancellation Logic:

When a confirmed ticket is canceled, the next RAC ticket is promoted to confirmed.

When an RAC ticket is promoted, the next waiting-list passenger is moved to RAC.

Concurrency Handling:

Database transactions ensure that no two users can book the same berth simultaneously.

Sample Requests
Book a Ticket

curl -X POST http://localhost:5000/api/v1/tickets/book \
-H "Content-Type: application/json" \
-d '{
  "passengers": [
    {"name": "Aditya Pathak", "age": 30, "gender": "male"},
    {"name": "Ananya Pathak", "age": 25, "gender": "female"}
  ]
}'
Cancel a Ticket

curl -X POST http://localhost:5000/api/v1/tickets/cancel/1
View Booked Tickets

curl http://localhost:5000/api/v1/tickets/booked
View Available Tickets

curl http://localhost:5000/api/v1/tickets/available
