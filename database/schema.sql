-- Schema for Medical Text Extractor Database

-- Medications table
CREATE TABLE IF NOT EXISTS medications (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    medication_name TEXT,
    prescriber TEXT,
    administration TEXT,
    original_text TEXT,
    capture_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    confidence_score REAL DEFAULT 0.0
);

-- Create indexes for faster searching
CREATE INDEX IF NOT EXISTS idx_medication_name ON medications(medication_name);
CREATE INDEX IF NOT EXISTS idx_prescriber ON medications(prescriber);
CREATE INDEX IF NOT EXISTS idx_capture_date ON medications(capture_date);
