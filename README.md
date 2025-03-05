# SQL Chatbot Project

This project implements a chatbot that translates natural language questions into SQL queries and retrieves data from a SQL database. It leverages an NLP model fine-tuned on SQL-related tasks to generate SQL queries based on user input.

## Features
- Converts natural language questions into SQL queries.
- Retrieves relevant data from a database.
- Uses a fine-tuned LLaMA model for improved SQL generation.
- Provides an interactive interface using Gradio.

## Project Structure

- **`training.ipynb`**: Jupyter notebook for fine-tuning the LLaMA model on SQL tasks.
- **`interface.ipynb`**: Jupyter notebook with an interactive Gradio-based interface to ask questions and retrieve SQL query results.
- **`requirements.txt`**: Lists required Python dependencies.
- **`data/sqldb.db`**: SQLite database used for executing queries.
- **`data/fine_tuning/`**: Contains datasets used for fine-tuning the model, including synthetic text-to-SQL mappings.

## Installation

1. Clone the repository:
   ```bash
   git clone <repository-url>
   cd SQL_Chatbot_NLP_Project
   ```
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## How to Run

### Training the Model
1. Open `training.ipynb` in Jupyter Notebook.
2. Run all cells to fine-tune the LLaMA model using the provided SQL dataset.

### Using the Chatbot Interface
1. Open `interface.ipynb` in Jupyter Notebook.
2. Run the notebook to launch the Gradio interface.
3. Ask natural language questions and retrieve SQL query results.

## Example Usage

**Input:** "Show me all customers who made a purchase in 2023."

**Generated SQL Query:**
```sql
SELECT * FROM customers WHERE purchase_year = 2023;
```

**Output (Example):**
| Customer_ID | Name  | Purchase_Year |
|------------|-------|--------------|
| 101        | Alice | 2023         |
| 204        | Bob   | 2023         |

## Dataset Information
- The chatbot is trained on a dataset containing text-to-SQL pairs.
- The fine-tuning data includes synthetic SQL queries generated for diverse SQL tasks.


