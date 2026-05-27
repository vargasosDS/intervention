import pandas as pd
#! Don't need periods
#! handle student IDs instead of names
#! Don't include students with no data in intervention lists, can handle in dishwasher
#! Only need overall scores, subcategories and SAT scores are not necessary for analysis

def dishwasher(filename):
    '''
        Function: Loads and cleans csv files, drops rows where all overall columns are NaN

        Paramters: 
            filepath (string): path to the csv file

        Returns: 
            df (Pandas Dataframe): cleaned dataframe

    '''
    try:
        df = pd.read_csv(filename, header=0)
    except Exception as e:
        print(f'Unable to read CSV: {e}')

    return df

# Creates copy of overall subject scores and calculates the mean and growth over the Fall-Spring period
def calculatron(df):
    '''
    Function:
        calculates averages for multiple categories and the growth over the course of the three exams

    Parameters:
        math_subject (pandas dataframe): contains names and scores across different categories
        skill_groups (dictionary): 4 different categories across Fall, Winter, and Spring

    Returns:
        overall_scores (pandas dataframe): contains overall and average scores, as well as growth in points from Fall to Spring
        skills (pandas dataframe): contains average skill scores
    '''
    # Handles dropping rows that do not have values for the overall columns. If one such column has a value, it will keep the rows
    overall_cols = [col for col in df.columns if 'overall' in col.lower()]
    id_col = [col for col in df.columns if 'id' in col.lower()][0]
    keywords = ['Number and Op', 'Geometry', 'Measure and Data', 'Alg and Alg Thinking']
    skill_groups = {}
    for word in keywords:
        matched = [col for col in df.columns if word in col.lower() and 'overall' not in col.lower()]
        if matched:
            skill_groups[word.title()] = matched

    if overall_cols:
        mask = df[overall_cols].isna().all(axis=1)
        df = df[~mask]

    overall_scores = df[[id_col] + overall_cols].copy()
    overall_scores['Average Overall'] = overall_scores[overall_cols].mean(axis=1)

    fall_col = next((col for col in overall_cols if 'fall' in overall_cols.lower()), None)
    spring_col = next((col for col in overall_cols if 'spring' in overall_cols.lower()), None)

    if fall_col and spring_col:
        overall_scores['Growth'] = overall_scores[spring_col] - overall_scores[fall_col]

    skills = pd.DataFrame()
    skills[id_col] = df[id_col]
    for skill, columns in skill_groups.items():
        valid_cols = [col for col in columns if col in df.columns]
        if valid_cols:
            skills[skill + ' Average'] = df[valid_cols].mean(axis=1)
    
    return overall_scores, skills

def intervention_identification(overall_scores, num_students=7):
    '''
    Function: 
        Creates list of 7 intervention targets, sorted by Average Overall score. To change number of intervention targets, change num_students

    Parameters: 
        overall_scores (pandas dataframe): Dataframe consisting of average overall scores and growth variable

    Returns: 
        intervention_list (list): Contains intervention targets 
    '''
    if 'Average Overall' not in overall_scores.columns:
        raise ValueError('Average Overall column not found')
    
    intervention_list = overall_scores.sort_values(by='Average Overall').head(num_students).reset_index(drop=True)
    return intervention_list

def high_potential(overall_scores, num_students=15):
    '''
    Function:
        Sorts overall scores by growth

    Parameters:
        overall_scores (pandas dataframe): Dataframe consisting of average overall scores and growth variable
        num_students (int): Number of students in high growth list, mutable

    Returns: 
        enrichment_targets (pandas dataframe): Dataframe sorted by growth variable
    '''
    if 'Growth' not in overall_scores.columns:
        raise ValueError('Growth column not found - need both Fall and Spring to calculate growth')
    
    enrichment_targets = overall_scores.sort_values(by='Growth', ascending=False).head(num_students).reset_index(drop=True)
    return enrichment_targets

def main():
    filename = input('Input filename: ')
    df = dishwasher(filename, header=0)


if __name__ == '__main__':

    main()