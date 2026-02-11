
Given the availability of modern AI-assisted tools such as Cursor, GitHub Copilot, or ChatGPT, you should be able to complete this exercise efficiently. Our goal is to understand your approach to backend architecture, data modeling, databases, Elasticsearch, and API design.
 
📋 Offline Assignment
Objective
Build a simple e-commerce REST API using any programming language of your choice, along with MySQL and Elasticsearch, using https://dummyjson.com/products as the source for dummy data.
 
📦 Task Details
You are required to build a basic e-commerce API with the following components:
1. Dockerized Setup
Create a Docker setup for:
Your web service
Elasticsearch
MySQL
The setup should be runnable out-of-the-box.
I should be able to run docker compose up and have the service running without any additional installation steps.
 
2. Data Fetch & Database Population Script
Fetch product data from:   https://dummyjson.com/products
Insert the data into MySQL
Design and implement a clean and sensible MySQL schema to store this data
 
3. Elasticsearch Indexing
Create an appropriate Elasticsearch index/mapping
Index all product data into Elasticsearch
This indexing step can be part of the same data ingestion script
 
4. REST API Endpoints
Build the following endpoints using either MySQL or Elasticsearch as the data source:
/categories → list all categories
/products → list all products
/products/{id} → fetch a single product by ID
/products?query={query} → full-text search using Elasticsearch
/products?category={category} → filter products by category
 
📂 Submission Instructions
Please share your solution in ZIP format or via a Google Drive link containing:
Your full codebase
A short README explaining:
How to run the app locally
Your design choices and thought process
Any trade-offs or known limitations
 