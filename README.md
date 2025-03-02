
# Project Setup Documentation

This guide will walk you through setting up and running the project in your local environment.

## Prerequisites

Make sure you have the following tools installed:

- Docker
- Docker Compose
- Postman (for testing the API)

## Steps to Set Up and Run the Application

1. **Clone the Repository**

   First, clone the project repository to your local machine:

   ```bash
   git clone https://github.com/VishnuDeshmukh21/UMatch-assignment.git
   cd UMatch-assignment
   ```

2. **Build the Docker Containers**

   Run the following command to build the Docker containers:

   ```bash
   docker-compose build
   ```

   This will create the required images for the containers defined in your `docker-compose.yml` file.

3. **Start the Docker Containers**

   After building the containers, start them in detached mode:

   ```bash
   docker-compose up -d
   ```

   This will start the containers in the background, allowing you to interact with the application.

4. **Verify Containers Are Running**

   Ensure the containers are up and running by checking the status:

   ```bash
   docker-compose ps
   ```

   You should see your containers listed and their statuses.

5. **Access the Application via Postman**

   - Open Postman.
   - Import the provided Postman collection to test the endpoints.
     - Go to **File > Import** in Postman, and select the collection file.
   - Send requests to the application as needed. The API should now be accessible through the Docker containers.

## Stopping the Containers

When you’re done, you can stop the Docker containers by running:

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

