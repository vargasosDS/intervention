import streamlit as st
import pandas as pd
from intervention import (dishwasher, calculatron, intervention_identification, 
                          high_potential, skill_area_identification)

st.set_page_config(page_title='Intervention Analysis Tool', layout='wide')

def file_processor(filename, num_intervention, num_high_potential):
    '''
        file (.csv file): 
            student data file

        returns: analyzed data
    '''
    try:
        df, grade, school_year, subject = dishwasher(filename)
    except ValueError as e:
        st.error(f"Error processing '{filename.name}': {e}")
        print(f"ValueError: {e}")
        return None
    except Exception as e:
        st.error(f"Error processing '{filename.name}': {e}")
        print(f"ValueError: {e}")
        return None

    # ordinal and label handle file name processing
    ordinal = 'th' if grade not in [1,2,3] else ['st', 'nd', 'rd'][grade-1]
    label = f"{grade}{ordinal} Grade {subject} - {school_year}"
    overall_scores, skills, id_col, name_col, psat_cols, overall_cols = calculatron(df)
    intervention_targets = intervention_identification(overall_scores, skills, id_col, name_col, 
                                                       psat_cols, overall_cols, grade, num_students=num_intervention)

    high_growth = high_potential(overall_scores, skills, id_col, name_col, psat_cols, overall_cols, 
                                 grade, num_students=num_high_potential)

    return {
        'grade': grade,
        'school_year': school_year,
        'subject': subject,
        'label': label,
        'overall_scores': overall_scores,
        'intervention_targets': intervention_targets,
        'high_growth': high_growth,
        'skills': skills,
        'id_col': id_col
    }

def main():
    st.title('Intervention Analysis Tool')

    # Instructions
    with st.expander('Instructions'):
        st.markdown("""
A guide to using the intervention analysis tool

Website: https://intervention-tool.streamlit.app

# Step 1:
Log into PowerSchool, then go to Performance Matters (the box with an arrow pointing out of it on the upper right hand corner). Once in Performance Matters, go to Reports on the left hand side and select baseball card report.

# Step 2:
After selecting baseball card report, there will be a list of assessments on the left side and student names on the right hand side. We will need the student ID along with the names; click on Manage Columns and make sure the Student ID column (not the Student State ID) is toggled on, then click Apply. The student ID should appear next to student names on the report. 

This program will only work if each grade has their own file, so click on Add Student Filter, and select Current Grade under the Demographics tab. Select the desired grade level and click Apply. This will influence our files name later on when we have all of our data.

# Step 3:
Now you should have the assessments to the left and the student names and IDs to the right. We will start selecting our data. Click on the I-Ready Results folder, which will reveal Math and Reading results for I-Ready. Since the program can handle both Math and Reading, we will have to do this one folder at a time (i.e. we will have one file for 9th grade math and another for 9th grade english).

## Note:
These I-Ready results are from the students' 8th grade testing data, so make sure that the data selected corresponds with the school year in which they were in 8th grade. 9th graders will be one year prior, 10th graders will be two years prior, and 11th graders will be three years prior. Current 8th graders should display their 7th grade test results at the beginning of the year, with their 8th grade data becoming available as the year progresses.

## Note:
The PSAT 10 and PSAT/NMSQT are identical. Here is a quick reference for the different PSATs:
  PSAT 8-9 is given to 8th and 9th graders
  PSAT 10 is given to 10th graders in the spring
  PSAT/NMSQT is given to 11th graders in the fall

### If you select Math:
For this step we will be ignoring all columns that have 'Placement' in the name. We want to select the Fall, Winter, and Spring columns for each column type. Checkmark the following columns:
  Overall SS (Fall, Winter, Spring)
  Number and Op SS (Fall, Winter, Spring)
  Alg and Alg Thinking SS (Fall, Winter, Spring)
  Measure and Data SS (Fall, Winter, Spring)
  Geometry SS (Fall, Winter, Spring)

For this part of the step we will need to enter into one of the PSAT folders. Select the corresponding folder for the students' grade level and select the two most recent PSAT results. We only want the math section scores, which look like this:
  PSAT 8-9 Math Section Scores (160-760)

There should be 19 columns in total.

### If you select Reading:
For this step we will be ignoring all columns that have 'Placement' in the name as well as the Phonological Awareness column. We want to select the Fall, Winter, and Spring columns for each column type. Checkmark the following columns:
  Overall SS (Fall, Winter, Spring)
  Phonics SS (Fall, Winter, Spring)
  High Frequency Words (Fall, Winter, Spring)
  Vocabulary SS (Fall, Winter, Spring)
  Reading Comp: Lit SS (Fall, Winter, Spring)
  Reading Comp: Inform Text SS (Fall, Winter, Spring)

For this part of the step we will need to enter into one of the PSAT folders. Select the corresponding folder for the students' grade level and select the two most recent PSAT results. Again, we only want the reading section scores:
  PSAT 8-9 Section Scores (160-760): Evidence Based Reading and Writing

There should be 22 columns in total.

There should be two PSAT columns. 
  For 9th grade, they will have two PSAT 8-9 columns, from different school years. 
  For 10th grade, one will be the PSAT 8-9 and the other will be PSAT 10.
  For 11th grade, one will be the PSAT 10 and the other will be PSAT/NMSQT.
        
# Step 4:
Once you have confirmed that all columns are showing up, select Download. The file will be saved as BBCard.xlsx, which we will need to modify slightly so that the program is able to use it. Open the file in Excel, select File, then Save As. Select 'CSV UTF-8 (Comma delimited) (*.csv)' as we will be saving this file as a .csv file. Rename the file so that it follows this example:

For the 2025-2026 9th grade math file the file name would be 025026_9thmath.csv. 
For the 2026-2027 9th grade english file the file name would be 026027_9thenglish.csv

# Step 5:
Go to the website and click upload. Select your files and click open. The website will automatically analyze the student data. To change the amount of students in the intervention or the high potential list, adjust the respective quantities under List Settings. To change the file that is being shown on the main page, scroll down to the Select Grade dropdown menu, and select the desired file.

   
### Reminder: While this can identify intervention targets instantly, it is still a good idea to observe students for at least 10 school days to determine if the test results are accurate.
                                     """)

    # Upload files and List Settings section
    with st.sidebar:
        st.header('Upload Files')
        uploaded_files = st.file_uploader('Upload grade level CSV files',
                                          type='csv', accept_multiple_files=True)

        st.divider()

        st.header('List Settings')
        num_intervention = st.number_input('Number of Intervention Students', min_value=1,
                                           max_value=50, value=20, step=1)
        num_high_potential = st.number_input('Number of high potential students', min_value=1,
                                             max_value=50, value=15, step=1)
        
        st.divider()

    # If true, nothing has been uploaded
    # False, a file has been uploaded
    if not uploaded_files:
        st.info('Please upload one or more grade level CSV files to get started.')
        if 'results' in st.session_state:
            del st.session_state['results']
        return
    
    file_names = [f.name for f in uploaded_files]
    if ('results' not in st.session_state or
        st.session_state.get('file_names') != file_names or
        st.session_state.get('num_intervention') != num_intervention or
        st.session_state.get('num_high_potential') != num_high_potential):

    # Process all files and store results
        results = {}
        for file in uploaded_files:
            data = file_processor(file, num_intervention, num_high_potential)
            if data:
                results[data['label']] = data

        st.session_state['results'] = results
        st.session_state['file_names'] = file_names
        st.session_state['num_intervention'] = num_intervention
        st.session_state['num_high_potential'] = num_high_potential

    results = st.session_state['results']
    if not results:
        return

    # Grade selector
    with st.sidebar:
        st.header('Select Grade')
        selected_grade = st.selectbox('Select Grade', options=list(results.keys()))

    if not selected_grade:
        st.info('Please select a grade to view results.')
        return
    
    # Display selected grade
    data = results[selected_grade]
    st.header(f"{selected_grade}")

    # Sub tabs for intervention and high potential
    intervention_tab, high_potential_tab = st.tabs(['Intervention Targets', 'High Potential Targets'])

    with intervention_tab:
        st.subheader('Intervention Targets')
        st.dataframe(data['intervention_targets'], width='stretch')

    with high_potential_tab:
        st.subheader('High Potential Targets')
        if len(data['high_growth']) < num_high_potential:
            st.warning(f'Only {len(data['high_growth'])} students elgible after excluding intervention targets. Consider reducing the number of students for intervention.')

        include_priority = st.checkbox('Show Priority Areas', value=False)
        
        # Priority toggle for enrichment targets
        if include_priority:
            high_growth_with_priority = skill_area_identification(
                data['high_growth'],
                data['skills'],
                data['id_col'],
                data['grade'],
            )
            high_growth_with_priority.index = range(1, len(high_growth_with_priority) + 1)
            st.dataframe(high_growth_with_priority, width='stretch')
        else:
            st.dataframe(data['high_growth'], width='stretch')
if __name__ == '__main__':
    main()