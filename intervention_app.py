import streamlit as st
import pandas as pd
from intervention import (dishwasher, calculatron, intervention_identification, 
                          high_potential, skill_area_identification, load_config, save_config)

st.set_page_config(page_title='Intervention Analysis Tool', layout='wide')

def file_processor(filename):
    '''
        file (.csv file): 
            student data file

        returns: analyzed data
    '''
    try:
        df, grade, school_year = dishwasher(filename)
    except ValueError as e:
        st.error(f"Error processing '{filename.name}': {e}")
        return None

    benchmarks = load_config()
    overall_scores, skills, id_col, name_col, psat_cols, overall_cols = calculatron(df)

    intervention_targets = intervention_identification(overall_scores, skills, id_col, name_col, 
                                                       psat_cols, overall_cols, grade)

    high_growth = high_potential(overall_scores, skills, id_col, name_col, psat_cols, overall_cols, 
                                 grade, benchmarks, num_students=15)

    return {
        'grade': grade,
        'school_year': school_year,
        'intervention_targets': intervention_targets,
        'high_growth': high_growth,
        'skills': skills,
        'id_col': id_col,
        'grade': grade,
        'benchmarks': benchmarks
    }

def main():
    st.title('Intervention Analysis Tool')

    # Sidebar
    with st.sidebar:
        st.header('Upload Files')
        uploaded_files = st.file_uploader('Upload grade level CSV files',
                                          type='csv', accept_multiple_files=True)

        st.divider()

        # Benchmarks settings
        st.header('Benchmark Settings')
        benchmarks = load_config()
        updated_benchmarks = {}
        for skill, value in benchmarks.items():
            updated_benchmarks[skill] = st.number_input(skill, min_value=0, 
                                                        max_value=100, value=value, step=1)
        if st.button('Save Benchmarks'):
            save_config(updated_benchmarks)
            st.success('Benchmarks saved!')

        # Grade selector
        st.divider()
        st.header('Select Grade')

    # Process uploaded files
    if not uploaded_files:
        st.info('Please upload one or more grade level CSV files to get started.')
        return

    # Process all files and store results
    results = {}
    for file in uploaded_files:
        data = file_processor(file)
        if data:
            label = f"Grade {data['grade']} — {data['school_year']}"
            results[label] = data

    if not results:
        return

    # Grade selector dropdown in sidebar
    with st.sidebar:
        selected_grade = st.selectbox('Select Grade', options=list(results.keys()))

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
        include_priority = st.checkbox('Show Priority Areas', value=False)
    
        if include_priority:
            high_growth_with_priority = high_potential(
                pd.DataFrame(data['high_growth']),
                data['skills'],
                data['id_col'],
                data['intervention_targets'].columns[1],
                [col for col in data['high_growth'].columns if 'psat' in col.lower()],
                [col for col in data['high_growth'].columns if 'overall' in col.lower()
                 and col != 'Average Overall'],
                data['grade'],
                data['benchmarks'],
                num_students=15,
                include_priority_areas=True
            )
            st.dataframe(high_growth_with_priority, width='stretch')
        else:
            st.dataframe(data['high_growth'], width='stretch')
if __name__ == '__main__':
    main()