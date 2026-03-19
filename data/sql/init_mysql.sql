CREATE DATABASE IF NOT EXISTS police_incident_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
USE police_incident_db;

CREATE TABLE IF NOT EXISTS incidents (
    id INT PRIMARY KEY AUTO_INCREMENT,
    incident_type VARCHAR(100) NOT NULL,
    dispatch_time DATETIME NOT NULL,
    address VARCHAR(255) NOT NULL,
    longitude DOUBLE NOT NULL,
    latitude DOUBLE NOT NULL,
    handling_duration_min INT NOT NULL,
    police_unit_count INT NOT NULL,
    status VARCHAR(50) NOT NULL DEFAULT 'closed',
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_incident_type (incident_type),
    INDEX idx_dispatch_time (dispatch_time),
    INDEX idx_address (address)
);

CREATE TABLE IF NOT EXISTS dispatch_assignments (
    id INT PRIMARY KEY AUTO_INCREMENT,
    incident_id INT NOT NULL,
    officer_id VARCHAR(50) NOT NULL,
    start_time DATETIME NOT NULL,
    end_time DATETIME NOT NULL,
    status VARCHAR(20) NOT NULL DEFAULT 'active',
    created_by VARCHAR(50) NOT NULL DEFAULT 'system',
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_incident_id (incident_id),
    INDEX idx_officer_id (officer_id),
    INDEX idx_start_time (start_time),
    INDEX idx_end_time (end_time)
);
