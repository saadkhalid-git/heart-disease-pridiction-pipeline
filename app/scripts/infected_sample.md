# Data Corruption Techniques

This project introduces various data corruption techniques to test the robustness of machine learning models. Below are the techniques applied and examples showing the effects.

### 1. **Missing Values**
Randomly replaces values with `NaN` in different columns.

**Example:**

Before:
| age | cholesterol | gender |
|-----|-------------|--------|
| 45  | 200         | Male   |
| 54  | 250         | Female |

After:
| age | cholesterol | gender |
|-----|-------------|--------|
| 45  | NaN         | Male   |
| 54  | 250         | Female |

### 2. **Outliers**
Introduces extreme values by multiplying the mean of a numerical column by 10.

**Example:**

Before:
| age | cholesterol |
|-----|-------------|
| 45  | 200         |
| 54  | 250         |

After (extreme outlier):
| age | cholesterol |
|-----|-------------|
| 45  | 2000        |
| 54  | 250         |

### 3. **Value Swapping**
Swaps values between two randomly selected columns.

**Example:**

Before:
| age | cholesterol | gender |
|-----|-------------|--------|
| 45  | 200         | Male   |
| 54  | 250         | Female |

After (swapped age and cholesterol):
| age | cholesterol | gender |
|-----|-------------|--------|
| 200 | 45          | Male   |
| 54  | 250         | Female |

### 4. **Inconsistent Categories**
Inserts invalid categorical values like "INVALID" in string-based columns.

**Example:**

Before:
| age | gender |
|-----|--------|
| 45  | Male   |
| 54  | Female |

After:
| age | gender |
|-----|--------|
| 45  | INVALID|
| 54  | Female |

### 5. **Noise Addition**
Adds Gaussian noise to numerical values, simulating random measurement errors.

**Example:**

Before:
| age | cholesterol |
|-----|-------------|
| 45  | 200         |
| 54  | 250         |

After (with noise):
| age | cholesterol |
|-----|-------------|
| 45  | 205.4       |
| 54  | 246.7       |

### 6. **Random Characters in Categorical Columns**
Inserts random characters into categorical (string) columns, disrupting the original labels.

**Example:**

Before:
| age | gender |
|-----|--------|
| 45  | Male   |
| 54  | Female |

After:
| age | gender  |
|-----|---------|
| 45  | MaleXYZ |
| 54  | FemaleQW|

### 7. **Shuffling within Columns**
Randomly reorders values within a column, which disrupts any correlation with other columns.

**Example:**

Before:
| age | cholesterol |
|-----|-------------|
| 45  | 200         |
| 54  | 250         |

After (shuffled cholesterol):
| age | cholesterol |
|-----|-------------|
| 45  | 250         |
| 54  | 200         |
