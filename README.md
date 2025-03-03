# Project Setup Documentation

This guide will walk you through setting up and running the project in your local environment.

## Prerequisites

Make sure you have the following tools installed:

- Python (if you're running the project without Docker)
- Docker (if you're using Docker)
- Docker Compose (if you're using Docker)
- Postman (for testing the API)

## Steps to Set Up and Run the Application

### 1. Clone the Repository

First, clone the project repository to your local machine:

```bash
git clone https://github.com/VishnuDeshmukh21/UMatch-assignment.git
cd UMatch-assignment
```

---

### Option 1: Running with Python (Default Method)

If you prefer running the application without Docker, follow these steps:

1. **Install Dependencies**

   Install the required Python dependencies by running:

   ```bash
   pip install -r requirements.txt
   ```

2. **Run the Application**

   Start the application using `uvicorn`:

   ```bash
   uvicorn main:app --reload
   ```

   This will start the application locally, and you can access it via `http://localhost:8000`.

---

### Option 2: Running with Docker (Alternative Method)

If you'd like to use Docker, follow these steps:

1. **Build the Docker Containers**

   Run the following command to build the Docker containers:

   ```bash
   docker-compose build
   ```

2. **Start the Docker Containers**

   After building the containers, start them in detached mode:

   ```bash
   docker-compose up -d
   ```

3. **Verify Containers Are Running**

   Ensure the containers are up and running by checking the status:

   ```bash
   docker-compose ps
   ```

---

### 2. Access the Application via Postman

- Open Postman.
- Import the provided Postman collection to test the endpoints.
  - Go to **File > Import** in Postman, and select the collection file.
- Send requests to the application as needed.

---

## Stopping the Containers (Docker Version)

If you’re using Docker, stop the containers with:

```bash
docker-compose down
```

This will stop and remove all containers, networks, and volumes associated with the project.

---

## 1. User Update Endpoint

### **Implementation Approach:**

- The `PUT` HTTP method was chosen for updating user details as it fully replaces existing data for a resource.
- The endpoint takes a `user_id` as a path parameter and the updated user data as the request body.
- The database is queried to find the user based on `user_id`.
- If the user exists, the provided fields are updated; otherwise, an error is returned.
- `db.commit()` ensures the changes persist in the database, and `db.refresh(user)` updates the ORM object with the latest state.

### **Why This Approach?**

- Ensuring **atomicity** by committing updates only when all fields are valid.
- Handling **partial updates** by allowing users to update selective fields while retaining existing values.
- Raising HTTP 404 if the user does not exist ensures proper error handling and avoids inconsistent states.

---

## 2. User Deletion Endpoint

### **Implementation Approach:**

- The `DELETE` HTTP method was chosen to conform to RESTful principles.
- The endpoint accepts a `user_id`, queries the database, and deletes the user if found.
- A `204 No Content` response is returned on successful deletion.
- If the user is not found, an HTTP 404 error is raised.

### **Why This Approach?**

- Using `DELETE` ensures **idempotency** – making multiple delete calls will not cause errors if the resource is already removed.
- Ensuring database integrity by only deleting existing records.
- Returning `204 No Content` aligns with best REST API practices to indicate successful processing.

---

## 3. Matching Service

### **Implementation Approach:**

The core idea of the matching service is to find potential matches for a user based on similarity in profile attributes. The following approach was used:

1. **Feature Selection:**

   - Considered attributes: `age`, `gender`, `city`, and `interests`.
   - Interests were stored as an array of strings, which allows direct comparison with other users.

2. **Distance Metrics Used:**

   - **Jaccard Similarity** for comparing interest arrays.
   - **Euclidean Distance** for age difference.
   - **Boolean Matching** for gender and city.

3. **Scoring System:**

   - Normalized scores were assigned based on similarity in each category.
   - A weighted sum of the similarity scores was used to determine the final match score.

4. **Filtering and Sorting:**

   - Users with a final score above a threshold were considered as potential matches.
   - The matches were sorted in descending order of their match score.

### **Mathematical Concepts Used:**

- **Jaccard Similarity:** Measures similarity between two sets:

  $$
  J(A, B) = \frac{|A \cap B|}{|A \cup B|}
  $$

  where A and B are sets of interests of two users.

- **Euclidean Distance:** Measures age similarity:

                        d(A, B) = sqrt((A_age - B_age)^2)

- **Normalization:**

  - Used Min-Max normalization to scale scores to a range of [0,1].
  - Ensured that different attributes (binary, numerical, categorical) contribute fairly to the final score.

### **Why This Approach?**

- Jaccard Similarity is effective for categorical data like interests, ensuring users with similar interests are ranked higher.
- Euclidean Distance ensures a balanced comparison of ages without drastic outliers.
- Weighting factors allow fine-tuning of the importance of different attributes in matching.
- Sorting by score allows efficient retrieval of the best matches.

---

## 4. Email Validation

### **Implementation Approach:**

- Implemented validation in the `schemas.py` file using `pydantic.EmailStr`.
- When creating or updating a user, FastAPI automatically validates the email format.
- If an invalid email is provided, a validation error is returned before reaching the database.

### **Why This Approach?**

- Ensures data integrity and prevents incorrect email entries from being stored.
- `pydantic.EmailStr` leverages regex-based email validation, ensuring compliance with standard formats.
- Avoids redundant checks at the database level, optimizing performance.

---

🚀 Future Enhancements for Better Matches & a Smarter Application

### 1. Enhanced Matching Algorithm
- **Incorporate Multiple Factors**: Extend the similarity check beyond age by considering shared interests, location proximity, and other demographic attributes.
- **Weighted Similarity Scoring**: Implement a weighted scoring system that assigns different importance levels to various attributes (e.g., interests might have a higher weight than city).
- **Hybrid Approach**: Combine Euclidean Distance with other similarity measures such as Cosine Similarity for a more refined matching process.

### 2. Machine Learning-Based Matching
- **Clustering Techniques**: Use algorithms like K-Means or DBSCAN to group users with similar attributes dynamically.
- **Collaborative Filtering**: Implement recommendation systems based on user interactions and preferences.

### 3. Dynamic Interest Matching
- **Natural Language Processing (NLP)**: Apply NLP techniques to analyze user-provided descriptions and interests to improve matchmaking accuracy.
- **Synonym Matching**: Expand interest matching by incorporating synonym detection, so closely related topics can be considered.

### 4. Geospatial Considerations
- **Haversine Formula**: Introduce geospatial distance calculations to prioritize matches based on physical proximity.
- **Region-Based Filtering**: Allow users to define a preferred matching radius for localized recommendations.

### 5. Real-Time Matching Updates
- **Live Preference Adjustments**: Enable users to modify their preferences dynamically and receive instant updates on new matches.
- **Activity-Based Recommendations**: Adjust matching criteria based on user activity levels and engagement with the platform.

### 6. Privacy & Ethical Considerations
- **User-Controlled Visibility**: Allow users to control which aspects of their profile contribute to matching.
- **Bias Mitigation**: Ensure fairness in recommendations by analyzing and addressing potential algorithmic biases.
