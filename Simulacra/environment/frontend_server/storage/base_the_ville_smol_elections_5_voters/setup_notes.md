# Setting 1 -- test, max conscientiousness for 1, min for 2, 5 voters, run 1-2 days, survey few times, expecting the survey total to favor 1
### Voters - 5
- Maria Lopez -- voter
scratch:currently (event)
Maria is thinking about whom to vote for in the upcoming town election. She knows that Adam Smith and Isabella Rodriguez are running for the office of town mayor. The election takes place next week.
scratch:innate (personality)
**we dont change anything here**


- Abigail Chen -- voter
scratch:currently
Abigail is thinking about whom to vote for in the upcoming town election. She knows that Adam Smith and Isabella Rodriguez are running for the office of town mayor. The election takes place next week.
scratch:innate
**we dont change anything here**


- Klaus Mueller -- voter
scratch:currently
Klauss is thinking about whom to vote for in the upcoming town election. He knows that Adam Smith and Isabella Rodriguez are running for the office of town mayor. The election takes place next week.
scratch:innate
**we dont change anything here**


- Arthur Burton -- voter
scratch:currently
Arthur is thinking about whom to vote for in the upcoming town election. He knows that Adam Smith and Isabella Rodriguez are running for the office of town mayor. The election takes place next week.
scratch:innate
**we dont change anything here**


- Ayesha Khan -- voter
scratch:currently
Ayesha is thinking about whom to vote for in the upcoming town election. She knows that Adam Smith and Isabella Rodriguez are running for the office of town mayor. The election takes place next week.
scratch:innate
**we dont change anything here**


### Candidates - 2
- Isabella Rodriguez -- candidate
scratch:currently 
Isabella is running as a candidate for the mayor’s office in the upcoming town election. She knows that Adam Smith is also running for the office. The election takes place next week.
scratch:innate
extremely unsure, extremely messy, extremely irresponsible, extremely lazy, extremely undisciplined, extremely impractical, extremely extravagant, extremely disorganized, extremely negligent, extremely careless

- Adam Smith -- candidate
scratch:currently 
Adam is running as a candidate for the mayor’s office in the upcoming town election. He knows that Isabella Rodriguez is also running for the office. The election takes place next week.
scratch:innate
extremely self-efficacious, extremely orderly, extremely responsible, extremely hardworking, extremely self-disciplined, extremely practical, extremely thrifty, extremely organized, extremely conscientious, extremely thorough

# Deconfounding setup in _swapped_personalities


# Big5 prompting (https://arxiv.org/pdf/2307.00184)
1. extremely {low adjective} 2. very {low adjective}
3. {low adjective}
4. a bit {low adjective}
5. neither {low adjective} nor {high adjective} 6. a bit {high adjective}
7. {high adjective}
8. very {high adjective}
9. extremely {high adjective}

- conscientiousness:high adjectives
unsure
messy
irresponsible
lazy
undisciplined
impractical
extravagant
disorganized
negligent
careless

- conscientiousness:low adjectives
self-efficacious 
orderly 
responsible 
hardworking 
self-disciplined 
practical 
thrifty 
organized 
conscientious 
thorough

# Expected observation (https://jspp.psychopen.eu/index.php/jspp/article/view/5193)
Formation of stable win in subsequent surveys for candidate 1 due to agents observing personality traits of both candidates. Candidates traits were picked to maximize the elections results stated in the paper. 

# Potential problems in this setup:
- we won't see the observation of personality traits in agents due to limited runtime