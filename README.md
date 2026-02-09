# About

The scope of this project is to gather and organize data on 7,921 US legislators, including:
- Federal
    - 435 Reps
    - 100 Sens
- State
    - 5,413 Reps
    - 1,973 Sens

This project has some limitations that may not be obvious, and limit the amount of data gathering that can be done. For one, the DOB of most state legislators is NOT public record. The data that will be gathered includes but is not limited to:
- Name
- State
- District
- Chamber
- Party
- Leadership Roles
- Committee Memberships
- Caucus Memberships
- Margin of Last Victory
- Voting Records
- Etc.

From the gathered data, this project seeks to organize and disseminate basic information about legislators in a readable format on sites like Wikipedia, Ballotpedia, and other sources. It will describe the positions legislators hold on particular subjects, including but not limited to:
- Abortion
- Capital Punishment
- Gun Control
- Immigration Enforcement
- Defense Spending
- Healthcare
- Etc.

The goal is that this will allow more informed voters, and potentially allow for the prediction of future votes in any given domain. 

# Download

You'll need PostgreSQL for storing, managing, and querying data:
- [PostgreSQL](https://www.postgresql.org/download/)

# See also

This repository relies on gathering its data on federal, state legislators, and voting records from these repos respectively:
- https://github.com/unitedstates/congress-legislators
- https://github.com/openstates/people
- https://github.com/qstin/LegiScanApiScripts

You may also be interested in browsing these other civic tech projects, sites, and articles:
- https://www.govtrack.us/
- https://www.opensecrets.org/
- https://chamberzero.com/
- https://www.billtracks.fyi/home
- https://voteview.com/
- https://en.wikipedia.org/wiki/NOMINATE_(scaling_method)
- https://thefreedomindex.org/