import pandas as pd
import os
import re

def parse_filename(filename):
    '''
        Function:
            Infers grade level and school year from filename
        Parameters:
            filename (str): Name of the file being processed
        Returns:
            grade (int): Grade level inferred from filename
            school_year (str): School year inferred from filename
    '''
    # Strips .csv from file name and infers year and grade
    basename = os.path.basename(filename).replace('.csv', '')
    match = re.match(r'(\d{6})_?(\d+)th(\w+)', basename, re.IGNORECASE)

    # If file name doesn't match expected naming scheme, throw error
    if not match:
        raise ValueError(
            f"Could not detect grade level from filename '{basename}'. "
            "Please rename the file following the pattern: 025026_9thgrade_subject.csv"
        )

    # .group(1) refers to the first group of parenthesis in match, set to the year
    # .group(2) refers to the second group of parenthesis in match, set to the grade
    year_str = match.group(1)
    grade = int(match.group(2))
    subject = match.group(3).title()
    school_year = f"20{year_str[1:3]}-20{year_str[4:]}"
    return grade, school_year, subject

def dishwasher(filename):
    '''
        Function:
            Loads and cleans the data, drops rows where all overall columns are NaN
        Parameters:
            filename (str or UploadedFile): Path to the CSV file or Streamlit UploadedFile
        Returns:
            df (pandas dataframe): Cleaned dataframe
            grade (int): Grade level inferred from filename
            school_year (str): School year inferred from filename
    '''
    # If true, filename is a streamlit UploadedFile (an object with a .name attribute)
    # If false, filename is a string
    # This is necessary in order to run program from terminal and streamlit app without crashing
    if hasattr(filename, 'name'):
        grade, school_year, subject = parse_filename(filename.name)
        df = pd.read_csv(filename, header=0)
    else:
        grade, school_year, subject = parse_filename(filename)
        df = pd.read_csv(filename, header=0)

    df.columns = df.columns.str.replace('\n', ' ').str.strip()
    # Creates list of columns with 'Overall' in the column name, removes rows where all overall columns are NaN
    overall_cols = [col for col in df.columns if 'overall' in col.lower()]
    if overall_cols:
        mask = df[overall_cols].notna().sum(axis=1) < 2
        df = df[~mask]

    return df, grade, school_year, subject

def calculatron(df):
    '''
    Function:
        Dynamically finds overall and skill columns, calculates averages and growth
    Parameters:
        df (pandas dataframe): Cleaned dataframe
    Returns:
        overall_scores (pandas dataframe): Dataframe with average overall scores and growth
        skills (pandas dataframe): Dataframe with skill averages per student
        id_col (str): Name of the Student ID column
        name_col (str): Name of the Student Name column
        psat_cols (list): List of PSAT column names
        overall_cols (list): List of overall score column names
    '''
    overall_cols = [col for col in df.columns if 'overall' in col.lower()]

    # Creates list of columns where student ID is in the column name, throwing an error when no student ID column is found
    id_cols = [col for col in df.columns if 'student id' in col.lower()]
    if not id_cols:
        raise ValueError("No Student ID column found")
    
    id_col = id_cols[0]
    name_cols = [col for col in df.columns if 'name' in col.lower()]

    # Same as overall_cols and id_cols, throws error if not student name column is found
    if not name_cols:
        raise ValueError("No Student Name column found")
    
    name_col = name_cols[0]
    psat_cols = [col for col in df.columns if 'psat' in col.lower() or 'sat' in col.lower()]

    # Build skill groups dynamically
    skill_keywords = {
        'Number and Op': 'number and op',
        'Geometry': 'geometry',
        'Measure and Data': 'measure and data',
        'Alg and Alg Thinking': 'alg and alg thinking',
        'Phonics': 'phonics',
        'High Frequency Words': 'high frequency words',
        'Vocabulary' : 'vocabulary',
        'Reading Comp: Lit': 'reading comp: lit',
        'Reading Comp: Inform Text': 'reading comp: inform text'
    }
    skill_groups = {}
    for display_name, keyword in skill_keywords.items():
        matched = [col for col in df.columns if keyword in col.lower() and 'overall' not in col.lower()]
        if matched:
            skill_groups[display_name] = matched

    # Find fall and spring overall cols for growth
    fall_col = next((col for col in overall_cols if 'fall' in col.lower()), None)
    winter_col = next((col for col in overall_cols if 'winter' in col.lower()), None)
    spring_col = next((col for col in overall_cols if 'spring' in col.lower()), None)

    # Build overall scores dataframe, calculate averages and growth
    overall_scores = df[[id_col, name_col] + overall_cols + psat_cols].copy()
    overall_scores['Average Overall'] = overall_scores[overall_cols].mean(axis=1)
    
    def calculate_growth(row):
        fall = row[fall_col] if fall_col else None
        winter  = row[winter_col] if winter_col else None
        spring = row[spring_col] if spring_col else None

        if pd.notna(fall) and pd.notna(spring):
            return spring - fall
        elif pd.notna(winter) and pd.notna(spring):
            return spring - winter
        elif pd.notna(fall) and pd.notna(winter):
            return winter - fall
        else:
            return None
        
    overall_scores['Growth'] = overall_scores.apply(calculate_growth, axis=1)

    # Build skills dataframe, 
    skills = pd.DataFrame()
    skills[id_col] = df[id_col]
    for skill, columns in skill_groups.items():
        valid_cols = [col for col in columns if col in df.columns]
        if valid_cols:
            skills[skill + ' Average'] = df[valid_cols].mean(axis=1)

    return overall_scores, skills, id_col, name_col, psat_cols, overall_cols

def skill_area_identification(target_df, skills, id_col, grade):
    '''
        Function:
            Flags top 2 weakest skills per student.
            Skips geometry for 9th grade students.
        Parameters:
            target_df (pandas dataframe): Students to analyze
            skills (pandas dataframe): Dataframe with skill averages per student
            id_col (str): Name of the Student ID column
            grade (int): Grade level
        Returns:
            merged_df (pandas dataframe): Target list with priority areas added
    '''
    # Merges skill averages with student dataframe
    # Creates list of skill averages, excluding average overall columns
    merged_df = pd.merge(target_df, skills, on=id_col, how='left')
    skill_avg_cols = [col for col in skills.columns if 'average' in col.lower() and col != 'Average Overall']

    def get_priority_areas(row):
        # Iterates through columns in skill averages df and strips the 'Average', skips 'Geometry' priority for 9th graders
        skill_scores = {}
        for col in skill_avg_cols:
            skill_name = col.replace(' Average', '')

            if grade == 9 and 'geometry' in skill_name.lower():
                continue

            # As long as score is not NaN, add to skill_score dictionary
            score = row[col]
            if pd.notna(score):
                skill_scores[skill_name] = score

        if not skill_scores:
            return 'Not enough skill data available'

        # Sorts skills so list goes from worst to best, pulls top 2 skills (2 worst skills)
        # Extracts skill names and combines in a single comma separated string
        sorted_skills = sorted(skill_scores.items(), key=lambda x: x[1])[:2]
        return ', '.join([skill for skill, _ in sorted_skills]) if sorted_skills else 'No skill data available'

    merged_df['Priority Areas'] = merged_df.apply(get_priority_areas, axis=1)
    return merged_df

def intervention_identification(overall_scores, skills, id_col, name_col,
                                psat_cols, overall_cols, grade, num_students=7):
    '''
        Function:
            Returns top N lowest scoring students with overall scores, PSAT scores and priority areas
        Parameters:
            overall_scores (pandas dataframe): Dataframe with average overall scores and growth
            skills (pandas dataframe): Dataframe with skill averages per student
            id_col (str): Name of the Student ID column
            name_col (str): Name of the Student Name column
            psat_cols (list): List of PSAT column names
            overall_cols (list): List of overall score column names
            grade (int): Grade level
            num_students (int): Number of intervention targets, default 7
        Returns:
            results (pandas dataframe): Lowest scoring students with all relevant columns
    '''
    if 'Average Overall' not in overall_scores.columns:
        raise ValueError("Average Overall column not found")

    # Sorts overall scores to identify students in need of intervention and pulls number of students specified with num_students
    intervention_list = overall_scores.sort_values(
        by='Average Overall').head(num_students).reset_index(drop=True)

    results = skill_area_identification(intervention_list, skills, id_col, grade)

    output_cols = [id_col, name_col] + overall_cols + ['Average Overall', 'Growth'] + psat_cols + ['Priority Areas']
    output_cols = [col for col in output_cols if col in results.columns]
    results.index = range(1, len(results) + 1)
    return results[output_cols]

def high_potential(overall_scores, skills, id_col, name_col, psat_cols, overall_cols,
                   grade, num_students=15, include_priority_areas=False):
    '''
        Function:
            Returns top N highest growth students
        Parameters:
            overall_scores (pandas dataframe): Dataframe with average overall scores and growth
            skills (pandas dataframe): Dataframe with skill averages per student
            id_col (str): Name of the Student ID column
            name_col (str): Name of the Student Name column
            psat_cols (list): List of PSAT column names
            overall_cols (list): List of overall score column names
            grade (int): Grade level
            num_students (int): Number of high growth students, default 15
            include_priority_areas (bool): Whether to include priority areas, default False
        Returns:
            enrichment_targets (pandas dataframe): Highest growth students
    '''
    if 'Growth' not in overall_scores.columns:
        raise ValueError("Growth column not found — need both a Fall and Spring column to calculate growth")
    
    # Checks intervention list to prevent students from being in high potential list if true
    intervention_list = intervention_identification(overall_scores, skills, id_col, name_col, psat_cols, overall_cols, grade)
    intervention_ids = intervention_list[id_col].tolist()
    elgible_students = overall_scores[~overall_scores[id_col].isin(intervention_ids)]

    # Sorts overall scores to identify students with high potential and pulls number of students specified with num_students
    enrichment_targets = elgible_students.sort_values(
        by='Growth', ascending=False).head(num_students).reset_index(drop=True)

    output_cols = [id_col, name_col] + overall_cols + ['Average Overall', 'Growth'] + psat_cols

    # Toggle to include priority areas for students with high potential
    if include_priority_areas:
        enrichment_targets = skill_area_identification(enrichment_targets, skills, id_col, grade)
        output_cols += ['Priority Areas']

    output_cols = [col for col in output_cols if col in enrichment_targets.columns]
    enrichment_targets.index = range(1, len(enrichment_targets) + 1)
    return enrichment_targets[output_cols]

def main():
    filename = input('Input filename: ')
    df, grade, school_year = dishwasher(filename)

    print(f"\nProcessing {school_year} — Grade {grade}")

    overall_scores, skills, id_col, name_col, psat_cols, overall_cols = calculatron(df)

    intervention_targets = intervention_identification(
        overall_scores, skills, id_col, name_col, psat_cols, overall_cols, grade)

    high_growth = high_potential(
        overall_scores, skills, id_col, name_col, psat_cols, overall_cols,
        grade, num_students=15)

    pd.set_option('display.max_colwidth', None)
    print('\nIntervention Targets:\n', intervention_targets)
    print('\nHigh Potential Students:\n', high_growth)

if __name__ == '__main__':
    main()