---

# 🧮 Super Secure Calculator

Welcome! This isn't just any calculator — it's a **Super Secure** one.
This project is a **full-stack web application** featuring a modern **FastAPI** backend and a responsive **React** frontend, all neatly containerized with **Docker**.

The app provides a **secure authentication system** and a simple, private way to perform and save calculations.
It’s designed as both a **boilerplate** and a **learning tool** for modern web development.

---

## ✨ Features

* 🔐 **Secure User Authentication** — JWT-based login and registration
* 👥 **Full User Management** — Create, read, update, and delete users
* 🧑‍💻 **Profile Management** — Users can view and update their own profiles and passwords
* 🧾 **Calculation History** — Users can perform calculations and view their history
* 🧭 **Interactive API Docs** — Auto-generated Swagger UI documentation
* 🐳 **Fully Containerized** — Backend, frontend, and database run in Docker
* 🔄 **Database Migrations** — Managed with Alembic

---

## 🛠️ Tech Stack

| Area         | Technology                        |
| ------------ | --------------------------------- |
| **Backend**  | FastAPI, Python 3.10, uv, Alembic |
| **Frontend** | React (Vite), Axios, Nginx        |
| **Database** | PostgreSQL                        |
| **DevOps**   | Docker & Docker Compose           |

---

## 🚀 Getting Started

### Prerequisites

Make sure you have **Docker** and **Docker Compose** installed on your machine.

### Installation & Setup

**1. Clone the repository**

```bash
git clone https://github.com/R0JSON/super-secure-calculator.git
cd super-secure-calculator
```

**2. Create the environment file**

```bash
cp .env.example .env
```

Then open the new `.env` file and customize your environment variables.
At minimum, set values for `POSTGRES_PASSWORD` and `SECRET_KEY`.
Defaults are fine for local development.

**3. Build and run the application**

```bash
docker compose up --build -d
```

* `--build`: Forces image rebuilds (useful if you’ve changed Dockerfiles or code)
* `-d`: Runs containers in detached mode

**4. Access the app**

| Service                       | URL                                                      |
| ----------------------------- | -------------------------------------------------------- |
| Frontend Website              | [http://localhost:3000](http://localhost:3000)           |
| Backend API                   | [http://localhost:8080](http://localhost:8080)           |
| Interactive API Docs          | [http://localhost:8080/docs](http://localhost:8080/docs) |
| Database Admin Tool (Adminer) | [http://localhost:8081](http://localhost:8081)           |

---

## 🔧 Environment Variables

| Variable                   | Description                               | Example                      |
| -------------------------- | ----------------------------------------- | ---------------------------- |
| `POSTGRES_SERVER`          | Hostname for PostgreSQL container         | `db`                         |
| `POSTGRES_USER`            | PostgreSQL username                       | `postgres`                   |
| `POSTGRES_PASSWORD`        | **Required.** PostgreSQL password         | `supersecretpassword`        |
| `POSTGRES_DB`              | Database name                             | `app`                        |
| `SECRET_KEY`               | **Required.** Secret key for signing JWTs | `your-super-secret-key-here` |
| `FIRST_SUPERUSER`          | Email for the initial superuser           | `admin@example.com`          |
| `FIRST_SUPERUSER_PASSWORD` | Password for the initial superuser        | `changethis`                 |
| `BACKEND_CORS_ORIGINS`     | JSON list of allowed CORS origins         | `["http://localhost:3000"]`  |
| `FRONTEND_PORT`            | Port for frontend website                 | `3000`                       |
| `BACKEND_PORT`             | Port for backend API                      | `8080`                       |

---

## 📂 Project Structure

```
├── backend/                  # FastAPI backend
│   ├── app/                  # Main application module
│   ├── alembic/              # Database migration scripts
│   ├── scripts/              # Helper scripts (e.g. prestart.sh)
│   └── Dockerfile            # Backend Dockerfile
│
├── frontend/                 # React frontend
│   ├── public/               # Static assets
│   ├── src/                  # Main React source code
│   ├── Dockerfile            # Frontend Dockerfile
│   └── nginx.conf            # Nginx configuration
│
├── .env                      # Local environment config (ignored by Git)
├── .env.example              # Example environment file
├── docker-compose.yml        # Defines services, networks, and volumes
└── README.md                 # This file
```

---

## 📜 License

This project is licensed under the **MIT License**.
See the [LICENSE](LICENSE) file for details.

---
