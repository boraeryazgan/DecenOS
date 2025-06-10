# DecenOS: Educational Operating System Simulator

## Overview

DecenOS is an innovative educational simulation platform designed to demonstrate fundamental operating system concepts through a game console-themed environment. This project serves as both a learning tool for computer science education and a practical demonstration of modern OS design principles.

## Features

- **Process Management:** Implement process creation, switching, and termination with a comprehensive Process Control Block (PCB) and Round Robin scheduler.
- **Memory Management:** Simulate virtual memory through paging mechanisms, supporting dynamic memory allocation and memory protection.
- **Concurrency & Synchronization:** Demonstrate concurrent programming principles through multi-threading, locks, condition variables, and producer-consumer patterns.
- **File System Implementation:** Implement a hierarchical file system with directory structure, file operations (create, read, write, delete), and security features (permissions, encryption).
- **Process Tamagotchi:** Each process is represented as a virtual “pet” that requires CPU time (feeding) and memory allocation. If neglected, the pet’s hunger increases and happiness decreases—eventually “dying” if not managed. This gamified mechanic reinforces resource scheduling and management concepts.
- **Bonus Features:** Themed process types (HACKER, MINER, VALIDATOR), real-time system monitoring, and interactive process management.

## Technology Stack

- **Backend:** Django 4.x
- **Core Language:** Python 3.9+
- **Database:** SQLite (Django ORM)
- **Frontend:** HTML5, CSS3, JavaScript, Bootstrap
- **Concurrency:** Python threading module

## Getting Started

### Prerequisites

- Python 3.9+
- Django 4.x
- SQLite

### Installation



### Process Management

- **Create Process:** Navigate to `/create/` to create a new process.
- **List Processes:** Navigate to `/list/` to view all processes.
- **Terminate Process:** Navigate to `/terminate/<int:pid>/` to terminate a specific process.
- **Run Scheduler:** Navigate to `/run_scheduler/` to run the Round Robin scheduler.

### Memory Management

- **Allocate Memory:** Navigate to `/allocate_memory/<int:pid>/?num_pages=<int>` to allocate memory to a process.
- **Free Memory:** Navigate to `/free_memory/<int:pid>/` to free memory allocated to a process.

### Concurrency & Synchronization

- **Start Concurrency:** Navigate to `/start_concurrency/` to start the producer-consumer simulation.
- **Stop Concurrency:** Navigate to `/stop_concurrency/` to stop the simulation.

### File System

- **File Explorer:** Navigate to `/explorer/` to view the file system.
- **Create File:** Navigate to `/api/file/create/` to create a new file.
- **View File:** Navigate to `/api/file/<int:file_id>/` to view file details.

## Bonus Features

- **Themed Process Types:** HACKER, MINER, VALIDATOR processes.
- **File Permissions & Encryption:** Comprehensive permission system and optional file encryption.

## Conclusion

DecenOS successfully demonstrates core operating system principles through an engaging, interactive simulation environment. The system implements comprehensive process management, advanced memory management, concurrent file system operations, and real-time monitoring, making complex OS concepts accessible to learners.

## Future Development

- GUI or visualization for the OS.
- Multi-core CPU simulation.
- AI-based or power-aware scheduler.

## License

This project is licensed under the MIT License - see the LICENSE file for details.
