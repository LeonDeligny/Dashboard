Layout is dynamic, key argument is -- ?admin --.

There are 4 pages, Homepage, (Micro-Machining, Post-Processing, Overall Scrap), where all corresponding scripts are in their respective folers.
In each Folder we define the layout, which may contain different tabs (e.g. Micro-Machining contains Mismatches, Trends, Equipment etc.), and references to graphs of specific tabs.
Each corresponding script will define the layout of each graphs (when the user did not pass the argument ?admin we only apply a style = {'display': 'none'} on the filters that we did not use).

Database (db) connections are made in scripts : smc_load, pp_load, erp_load and utils (for the filter labels and defaults access).