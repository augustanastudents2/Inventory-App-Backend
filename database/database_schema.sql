-- ASA Inventory App Database Schema

-- Users Table
CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    email TEXT UNIQUE NOT NULL,
    name TEXT,
    role TEXT NOT NULL DEFAULT 'Staff',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT timezone('utc'::text, now()) NOT NULL
);

-- Categories Table
CREATE TABLE categories (
    id BIGSERIAL PRIMARY KEY,
    name TEXT UNIQUE NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT timezone('utc'::text, now()) NOT NULL
);

-- Tags Table
CREATE TABLE tags (
    id BIGSERIAL PRIMARY KEY,
    name TEXT UNIQUE NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT timezone('utc'::text, now()) NOT NULL
);

-- Storage Locations Table
CREATE TABLE storage_locations (
    id BIGSERIAL PRIMARY KEY,
    area TEXT NOT NULL,
    sub TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT timezone('utc'::text, now()) NOT NULL,
    UNIQUE(area, sub)
);

-- Vendors Table
CREATE TABLE vendors (
    id BIGSERIAL PRIMARY KEY,
    name TEXT UNIQUE NOT NULL,
    contact TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT timezone('utc'::text, now()) NOT NULL
);

-- Products Table
CREATE TABLE products (
    id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    description TEXT,
    buyingPrice DECIMAL(10,2) DEFAULT 0.0,
    quantity INTEGER DEFAULT 0,
    unit TEXT DEFAULT 'Units',
    thresholdValue INTEGER DEFAULT 0,
    expiryDate TEXT,
    category TEXT,
    tags TEXT[],
    vendor JSONB DEFAULT '{"name": "", "contact": ""}'::jsonb,
    storage JSONB DEFAULT '{"area": "", "sub": ""}'::jsonb,
    availability TEXT,
    createdAt TIMESTAMP WITH TIME ZONE DEFAULT timezone('utc'::text, now()) NOT NULL,
    updatedAt TIMESTAMP WITH TIME ZONE DEFAULT timezone('utc'::text, now()) NOT NULL
);

-- Stock History Table
CREATE TABLE stock_history (
    id TEXT PRIMARY KEY,
    productId TEXT REFERENCES products(id) ON DELETE CASCADE,
    at TIMESTAMP WITH TIME ZONE DEFAULT timezone('utc'::text, now()) NOT NULL,
    delta INTEGER NOT NULL,
    reason TEXT NOT NULL
);

-- Initial Data
INSERT INTO users (email, name, role) VALUES ('admin@asa.com', 'ASA Admin', 'Admin');
INSERT INTO categories (name) VALUES ('Casino Night Event'), ('Art Supplies'), ('Food Service'), ('Cleaning'), ('General');
INSERT INTO tags (name) VALUES ('Casino Night'), ('Decor'), ('Kitchen'), ('Audio/Visual');
