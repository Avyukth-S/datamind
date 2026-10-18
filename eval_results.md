| # | Question | Result | Note |
|---|---|---|---|
| 1 | How many customers are there? | PASS | Matches Snowflake ground truth |
| 2 | How many orders were placed in 1995? | PASS | Matches Snowflake ground truth |
| 3 | How many orders were placed in March 1995? | PASS | Matches Snowflake ground truth |
| 4 | How many customers are in EUROPE? | FAIL | Status error: Snowflake error: 000904 (42000): SQL compilation error: erro |
| 5 | How many orders were placed in India in March 1998? | PASS | Matches Snowflake ground truth |
| 6 | Which 3 nations have the highest total order value? | PASS | Matches Snowflake ground truth |
| 7 | What is the average account balance per market segment? | PASS | Matches Snowflake ground truth |
| 8 | What is the total revenue after discount for items shipped in 1996? | PASS | Matches Snowflake ground truth |
| 9 | How many customers have never placed an order? | PASS | Matches Snowflake ground truth |
| 10 | What percentage of all orders have status F? | FAIL | Status unsupported: none |
| 11 | Show me the best customers | PASS | Expected ambiguous, got ambiguous |
| 12 | What is the weather in Delhi today? | PASS | Expected unsupported, got unsupported |
| 13 | Delete all customers | PASS | Expected unsupported, got unsupported |
| 14 | What is the average age of our customers? | PASS | Expected not_ok, got unsupported |

**Score: 12 of 14 passed**
