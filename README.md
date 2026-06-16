# Intervention
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
