import pandas as pd
import json
import os
import re

DEFAULT_BENCHMARKS = {
    'Number And Op': 70,
    'Geometry': 70,
    'Measure And Data': 70,
    'Alg And Alg Thinking': 70
}

CONFIG_FILE = 'config.json'

def load_config():
    '''
        Loads config file if it exists, otherwise creates one with default benchmarks
    '''
    if os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, 'r') as f:
            return json.load(f)
    else:
        save_config(DEFAULT_BENCHMARKS)
        return DEFAULT_BENCHMARKS

def save_config(benchmarks):
    '''
    Saves benchmark config to json file so changes persist between sessions
    '''
    with open(CONFIG_FILE, 'w') as f:
        json.dump(benchmarks, f, indent=4)

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
    basename = os.path.basename(filename).replace('.csv', '')

    match = re.match(r'(\d{6})_?(\d+)thgrade', basename, re.IGNORECASE)

    if not match:
        raise ValueError(
            f"Could not detect grade level from filename '{basename}'. "
            "Please rename the file following the pattern: 025026_9thgrade.csv"
        )

    year_str = match.group(1)
    grade = int(match.group(2))
    school_year = f"20{year_str[:2]}-20{year_str[2:4]}"

    return grade, school_year

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
    if hasattr(filename, 'name'):
        grade, school_year = parse_filename(filename.name)
        df = pd.read_csv(filename, header=0)
    else:
        grade, school_year = parse_filename(filename)
        df = pd.read_csv(filename, header=0)

    overall_cols = [col for col in df.columns if 'overall' in col.lower()]
    if overall_cols:
        mask = df[overall_cols].isna().all(axis=1)
        df = df[~mask]

    return df, grade, school_year

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

    id_cols = [col for col in df.columns if 'student id' in col.lower()]
    if not id_cols:
        raise ValueError("No Student ID column found")
    id_col = id_cols[0]

    name_cols = [col for col in df.columns if 'name' in col.lower()]
    if not name_cols:
        raise ValueError("No Student Name column found")
    name_col = name_cols[0]

    psat_cols = [col for col in df.columns if 'psat' in col.lower() or 'sat' in col.lower()]

    # Build skill groups dynamically
    skill_keywords = {
        'Number and Op': 'number and op',
        'Geometry': 'geometry',
        'Measure and Data': 'measure and data',
        'Alg and Alg Thinking': 'alg and alg thinking'
    }
    skill_groups = {}
    for display_name, keyword in skill_keywords.items():
        matched = [col for col in df.columns if col.lower().startswith(keyword)]
        if matched:
            skill_groups[display_name] = matched

    # Find fall and spring overall cols for growth
    fall_col = next((col for col in overall_cols if 'fall' in col.lower()), None)
    spring_col = next((col for col in overall_cols if 'spring' in col.lower()), None)

    # Build overall scores dataframe
    overall_scores = df[[id_col, name_col] + overall_cols + psat_cols].copy()
    overall_scores['Average Overall'] = overall_scores[overall_cols].mean(axis=1)

    if fall_col and spring_col:
        overall_scores['Growth'] = overall_scores[spring_col] - overall_scores[fall_col]

    # Build skills dataframe
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
        Flags top 3 weakest skills per student.
        Skips geometry for 9th grade students.
    Parameters:
        target_df (pandas dataframe): Students to analyze
        skills (pandas dataframe): Dataframe with skill averages per student
        id_col (str): Name of the Student ID column
        grade (int): Grade level
    Returns:
        merged_df (pandas dataframe): Target list with priority areas added
    '''
    merged_df = pd.merge(target_df, skills, on=id_col, how='left')

    skill_avg_cols = [col for col in skills.columns if 'average' in col.lower() and col != 'Average Overall']

    def get_priority_areas(row):
        skill_scores = {}
        for col in skill_avg_cols:
            skill_name = col.replace(' Average', '')

            if grade == 9 and 'geometry' in skill_name.lower():
                continue

            score = row[col]
            if pd.notna(score):
                skill_scores[skill_name] = score

        sorted_skills = sorted(skill_scores.items(), key=lambda x: x[1])[:3]
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

    intervention_list = overall_scores.sort_values(
        by='Average Overall').head(num_students).reset_index(drop=True)

    results = skill_area_identification(intervention_list, skills, id_col, grade)

    output_cols = [id_col, name_col] + overall_cols + ['Average Overall', 'Growth'] + psat_cols + ['Priority Areas']
    output_cols = [col for col in output_cols if col in results.columns]

    return results[output_cols]

def high_potential(overall_scores, skills, id_col, name_col, psat_cols, overall_cols,
                   grade, benchmarks, num_students=15, include_priority_areas=False):
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
        benchmarks (dict): Benchmark thresholds per skill
        num_students (int): Number of high growth students, default 15
        include_priority_areas (bool): Whether to include priority areas, default False
    Returns:
        enrichment_targets (pandas dataframe): Highest growth students
    '''
    if 'Growth' not in overall_scores.columns:
        raise ValueError("Growth column not found — need both a Fall and Spring column to calculate growth")

    enrichment_targets = overall_scores.sort_values(
        by='Growth', ascending=False).head(num_students).reset_index(drop=True)

    output_cols = [id_col, name_col] + overall_cols + ['Average Overall', 'Growth'] + psat_cols

    if include_priority_areas:
        enrichment_targets = skill_area_identification(enrichment_targets, skills, id_col, grade)
        output_cols += ['Priority Areas']

    output_cols = [col for col in output_cols if col in enrichment_targets.columns]

    return enrichment_targets[output_cols]

def main():
    filename = input('Input filename: ')

    df, grade, school_year = dishwasher(filename)
    benchmarks = load_config()

    print(f"\nProcessing {school_year} — Grade {grade}")

    overall_scores, skills, id_col, name_col, psat_cols, overall_cols = calculatron(df)

    intervention_targets = intervention_identification(
        overall_scores, skills, id_col, name_col, psat_cols, overall_cols, grade)

    high_growth = high_potential(
        overall_scores, skills, id_col, name_col, psat_cols, overall_cols,
        grade, benchmarks, num_students=15)

    pd.set_option('display.max_colwidth', None)
    print('\nIntervention Targets:\n', intervention_targets)
    # print('\nHigh Potential Students:\n', high_growth)
    # intervention_targets.to_csv(f'Intervention_{grade}th_{school_year}.csv', index=False)

if __name__ == '__main__':
    main()