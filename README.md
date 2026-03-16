# Data Viewer

## Overview
The **Data Viewer** is an administrator interface that allows users to review student grading results by rater.  
It is designed to help monitor grading progress and easily compare evaluation results across different raters.

---

## Main Features

### 1. Rater-based Result Viewing
- Users can view student grading results grouped by rater.
- This allows administrators to review how each rater evaluated student responses.

### 2. Grading Result Verification
Users can check the following grading results for each student:

- AI grading scores
- Expert grading scores
- Final scores

Each score is stored according to the following rubric:

- **Scientific Knowledge(과학적 지식)**
- **Critical Thinking(비판적 사고)**

### 3. Grading Status Monitoring
The following information can be reviewed for each record:

- Student ID
- Rater ID
- AI grading result
- Expert grading result
- Final score

---

## System Architecture

The Data Viewer operates based on the following database tables.

| Table | Description |
|------|-------------|
| studentDB | Stores student information |
| raterDB | Stores rater information |
| ai_scoreDB | Stores AI grading results |
| expert_scoreDB | Stores expert grading results |
| final_scoreDB | Stores final scores |

---

## Purpose

- Monitor grading progress  
- Review grading results by rater  
- Verify AI grading results  
- Compare AI grading with expert grading
