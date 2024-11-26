Latest updates:

I made another round of edits/improvements:
•	Autofill based on Compound ID. 
•	Changed to plotly plotting library for interactive (hover over) plots.
o	Displays aggregated counts on hover over.
o	Distinguishes between compound through color, study id through marker, and strain with dashed lines (This can be modified depending on feedback).
•	Made code modular by separating out plotting, fitting, and filtering functions into separate .py files.
•	Cleaned up code and updated to Google Python Standard

Other features/ideas based off Werner’s feedback as well as my suggestions which I have not had the chance to work on:
•	Display relevant PK parameters (clearance, distribution, CX, etc) on right
•	Choose between autofill based on Compound ID, or other (SRD_STUDY). This will take some work.
•	Fit functions (bi-exponential decay)
•	Have option to aggregate or not. Like have the user be able to aggregate by SRD Study, Animal, etc and customize plots
•	New visualization tab to (bar graphs for clearance, how molecules compare)
•	Export graphs, customizable graphs (dimensions, etc)
•	Reach goal:  automate report summaries.


Sometimes cache needs to be cleared to see updates.
Remove-Item -Recurse -Force .\__pycache__