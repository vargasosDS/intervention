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

    # Sidebar
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

    # Process uploaded files
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
                #label = f"Grade {data['grade']} — {data['school_year']}"
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