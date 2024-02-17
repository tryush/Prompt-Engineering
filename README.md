# Prompt-Engineering
This project is about leveraging prompt engineering to solve real world problem.
In this project, we had clinical notes and our task was to check what type of diagnosis has been done to a patient and whether sufficient informations regarding that diagnosis is present in the medical chart or not. If all the required information is present in the clinical notes then the clinical notes is clean otherwise it needs to be updated with additional information.

Approach:
a. Classify the clinical notes in different diagosis using prompt
b. Extraxt the required section which needs to be checked for the required information
c. Frame prompts in such a way that it responds with yes / no for every questions
d. save the output from the prompt in a json file or list
e. Frame rules based on the response of different questions to classify the chart in clean or non-clean / non-deficient or deficient.
